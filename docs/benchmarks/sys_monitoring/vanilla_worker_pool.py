import asyncio
import sys
import time
from typing import TypeVar, Callable, Awaitable, Generic, Iterable, Any, Dict, List

T = TypeVar('T')
R = TypeVar('R')

class CoroutineProfiler:
    """
    Uses the sys.monitoring API (PEP 669) to profile async function execution times
    without the overhead of decorators. Accurately tracks active execution time by
    pausing the timer when the coroutine yields (awaits) and resuming when it wakes up.
    """
    def __init__(self, target_funcs: Iterable[str]) -> None:
        self.tool_id = sys.monitoring.PROFILER_ID
        self.target_funcs = set(target_funcs)
        self.metrics: Dict[str, float] = {func: 0.0 for func in target_funcs}
        self._frame_starts: Dict[Any, float] = {}

    def _py_start_resume(self, code: Any, instruction_offset: int) -> None:
        if code.co_name in self.target_funcs:
            self._frame_starts[code] = time.perf_counter()

    def _py_yield_return(self, code: Any, instruction_offset: int, retval: Any) -> None:
        if code.co_name in self.target_funcs:
            start_time = self._frame_starts.pop(code, None)
            if start_time is not None:
                duration = time.perf_counter() - start_time
                self.metrics[code.co_name] += duration

    def _py_unwind(self, code: Any, instruction_offset: int, exception: Any) -> None:
        self._py_yield_return(code, instruction_offset, None)

    def enable(self) -> None:
        sys.monitoring.use_tool_id(self.tool_id, "WorkerProfiler")
        events = (
            sys.monitoring.events.PY_START |
            sys.monitoring.events.PY_RESUME |
            sys.monitoring.events.PY_YIELD |
            sys.monitoring.events.PY_RETURN |
            sys.monitoring.events.PY_UNWIND
        )
        sys.monitoring.set_events(self.tool_id, events)
        
        # Register hooks for starting/resuming coroutines
        sys.monitoring.register_callback(self.tool_id, sys.monitoring.events.PY_START, self._py_start_resume)
        sys.monitoring.register_callback(self.tool_id, sys.monitoring.events.PY_RESUME, self._py_start_resume)
        
        # Register hooks for yielding/returning from coroutines
        sys.monitoring.register_callback(self.tool_id, sys.monitoring.events.PY_YIELD, self._py_yield_return)
        sys.monitoring.register_callback(self.tool_id, sys.monitoring.events.PY_RETURN, self._py_yield_return)
        
        # Register exception unwinding
        sys.monitoring.register_callback(self.tool_id, sys.monitoring.events.PY_UNWIND, self._py_unwind)

    def disable(self) -> None:
        sys.monitoring.set_events(self.tool_id, 0)
        sys.monitoring.free_tool_id(self.tool_id)


class WorkerPool(Generic[T, R]):
    def __init__(
        self,
        worker_func: Callable[[T], Awaitable[R]],
        concurrency: int,
    ) -> None:
        self.worker_func = worker_func
        self.concurrency = concurrency
        self._queue: asyncio.Queue[T] = asyncio.Queue()
        self._results: List[R] = []
        # Profile specifically the inner logic of the worker function
        self._profiler = CoroutineProfiler([worker_func.__name__])

    async def _worker(self) -> None:
        """Background worker task."""
        while True:
            try:
                item = await self._queue.get()
                try:
                    result = await self.worker_func(item)
                    self._results.append(result)
                except Exception as e:
                    print(f"[{self.worker_func.__name__}] Task failed with error: {e}")
                finally:
                    self._queue.task_done()
            except asyncio.CancelledError:
                # Expected when the pool initiates graceful shutdown
                break

    async def execute(self, items: Iterable[T]) -> List[R]:
        """Execute tasks concurrently using asyncio.TaskGroup without legacy gather."""
        self._profiler.enable()
        
        for item in items:
            self._queue.put_nowait(item)
            
        try:
            async with asyncio.TaskGroup() as tg:
                # Spawn worker tasks
                workers = [tg.create_task(self._worker(), name=f"worker-{i}") for i in range(self.concurrency)]
                
                # Wait for all queued items to be processed
                await self._queue.join()
                
                # Gracefully cancel workers now that the queue is empty
                for w in workers:
                    w.cancel()
                    
        except asyncio.CancelledError:
            print("Execution was cancelled externally. Forwarding cancellation...")
            raise
        except ExceptionGroup as eg:
            print(f"TaskGroup encountered exceptions: {eg.exceptions}")
            raise
        finally:
            self._profiler.disable()
            print(f"\nProfiled metrics (Active CPU execution time in seconds):")
            for func_name, total_time in self._profiler.metrics.items():
                print(f" - {func_name}: {total_time:.6f}s")

        return self._results


# --- Example Usage ---

async def process_item(item: int) -> int:
    """Simulated workload combining CPU and I/O work."""
    # CPU work: Tracked continuously by sys.monitoring
    _ = sum(i * i for i in range(200_000))
    
    # I/O work: sys.monitoring pauses tracking while sleeping/yielding
    await asyncio.sleep(0.05)
    
    return item * 2

async def main() -> None:
    pool: WorkerPool[int, int] = WorkerPool(worker_func=process_item, concurrency=3)
    
    print(f"Starting worker pool with concurrency {pool.concurrency}...")
    start_time = time.perf_counter()
    
    results = await pool.execute(range(10))
    
    wall_time = time.perf_counter() - start_time
    print(f"\nProcessed {len(results)} items successfully.")
    print(f"Total wall-clock time: {wall_time:.4f}s")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
