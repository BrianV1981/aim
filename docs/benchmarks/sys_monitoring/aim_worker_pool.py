import asyncio
import sys
import time
import contextvars
from typing import (
    Any,
    Callable,
    Coroutine,
    Dict,
    Generic,
    List,
    Optional,
    Tuple,
    TypeVar,
)

T = TypeVar("T")

class TaskStats:
    def __init__(self) -> None:
        self.start_time: float | None = None
        self.resume_time: float | None = None
        self.total_time: float = 0.0

current_task_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "current_task_id", default=None
)

# Global stats dictionary so sys.monitoring callbacks can access it quickly
_task_stats: Dict[str, TaskStats] = {}

def _on_start(code: Any, instruction_offset: int) -> Any:
    task_id = current_task_id.get()
    if task_id is not None:
        _task_stats[task_id] = TaskStats()
        _task_stats[task_id].start_time = time.perf_counter()
    return sys.monitoring.DISABLE

def _on_resume(code: Any, instruction_offset: int, *args: Any) -> Any:
    task_id = current_task_id.get()
    if task_id is not None and task_id in _task_stats:
        _task_stats[task_id].resume_time = time.perf_counter()

def _on_yield(code: Any, instruction_offset: int, *args: Any) -> Any:
    task_id = current_task_id.get()
    if task_id is not None and task_id in _task_stats:
        stat = _task_stats[task_id]
        now = time.perf_counter()
        if stat.resume_time is not None:
            stat.total_time += now - stat.resume_time
            stat.resume_time = None
        elif stat.start_time is not None:
            stat.total_time += now - stat.start_time
            stat.start_time = None

def _on_return(code: Any, instruction_offset: int, retval: Any, *args: Any) -> Any:
    task_id = current_task_id.get()
    if task_id is not None and task_id in _task_stats:
        stat = _task_stats[task_id]
        now = time.perf_counter()
        if stat.resume_time is not None:
            stat.total_time += now - stat.resume_time
            stat.resume_time = None
        elif stat.start_time is not None:
            stat.total_time += now - stat.start_time
            stat.start_time = None

class WorkerPoolProfiler:
    def __init__(self) -> None:
        self.tool_id: int = sys.monitoring.PROFILER_ID
        self._setup()

    def _setup(self) -> None:
        try:
            sys.monitoring.use_tool_id(self.tool_id, "worker_pool_profiler")
        except ValueError:
            pass
        sys.monitoring.register_callback(
            self.tool_id, sys.monitoring.events.PY_START, _on_start
        )
        sys.monitoring.register_callback(
            self.tool_id, sys.monitoring.events.PY_RESUME, _on_resume
        )
        sys.monitoring.register_callback(
            self.tool_id, sys.monitoring.events.PY_YIELD, _on_yield
        )
        sys.monitoring.register_callback(
            self.tool_id, sys.monitoring.events.PY_RETURN, _on_return
        )

    def track_coroutine(self, coro: Coroutine[Any, Any, Any]) -> None:
        if hasattr(coro, "cr_code"):
            code = coro.cr_code
            try:
                sys.monitoring.set_local_events(
                    self.tool_id,
                    code,
                    sys.monitoring.events.PY_START
                    | sys.monitoring.events.PY_RESUME
                    | sys.monitoring.events.PY_YIELD
                    | sys.monitoring.events.PY_RETURN,
                )
            except ValueError:
                pass


class AsyncWorkerPool(Generic[T]):
    """
    An asynchronous worker pool that utilizes asyncio.TaskGroup for concurrency.
    Implements graceful cancellation and uses sys.monitoring to profile task execution time.
    """
    def __init__(self, concurrency_limit: int) -> None:
        self.semaphore = asyncio.Semaphore(concurrency_limit)
        self.profiler = WorkerPoolProfiler()
        self.results: Dict[str, T] = {}
        self.errors: Dict[str, Exception] = {}

    async def _run_task(
        self, task_id: str, task_factory: Callable[[], Coroutine[Any, Any, T]]
    ) -> None:
        async with self.semaphore:
            coro = task_factory()
            self.profiler.track_coroutine(coro)

            token = current_task_id.set(task_id)
            try:
                result = await coro
                self.results[task_id] = result
            except asyncio.CancelledError:
                # Handle graceful cancellation
                print(f"Task {task_id} was cancelled gracefully.")
                self.errors[task_id] = asyncio.CancelledError()
                raise
            except Exception as e:
                self.errors[task_id] = e
            finally:
                current_task_id.reset(token)

    async def execute(
        self, tasks: List[Tuple[str, Callable[[], Coroutine[Any, Any, T]]]]
    ) -> None:
        """
        Executes a list of tasks utilizing asyncio.TaskGroup for concurrency.
        Replaces legacy asyncio.gather.
        """
        try:
            async with asyncio.TaskGroup() as tg:
                for task_id, task_factory in tasks:
                    tg.create_task(self._run_task(task_id, task_factory))
        except asyncio.CancelledError:
            print("Worker pool execution cancelled gracefully.")
            raise
        except ExceptionGroup as e:
            print(f"Worker pool encountered errors: {e.exceptions}")

    def get_execution_times(self) -> Dict[str, float]:
        """Returns the active execution time in seconds for each task."""
        return {tid: stat.total_time for tid, stat in _task_stats.items()}
