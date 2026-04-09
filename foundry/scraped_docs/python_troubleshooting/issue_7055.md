# Q: Could not find a suitable TLS CA certificate bundle, invalid path: /agents/python/common/certifi/cacert.pem
**Source:** https://github.com/psf/requests/issues/7055

## The Problem / Request
```
2025-10-21T10:12:14.3082809Z ERROR:    Exception in ASGI application
2025-10-21T10:12:14.3083028Z Traceback (most recent call last):
2025-10-21T10:12:14.3083065Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/uvicorn/protocols/http/httptools_impl.py", line 409, in run_asgi
2025-10-21T10:12:14.3083091Z     result = await app(  # type: ignore[func-returns-value]
2025-10-21T10:12:14.3083115Z              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-21T10:12:14.3083142Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__
2025-10-21T10:12:14.3083165Z     return await self.app(scope, receive, send)
2025-10-21T10:12:14.3083188Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-21T10:12:14.3083214Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/fastapi/applications.py", line 1133, in __call__
2025-10-21T10:12:14.3083239Z     await super().__call__(scope, receive, send)
2025-10-21T10:12:14.3083277Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/starlette/applications.py", line 113, in __call__
2025-10-21T10:12:14.3083301Z     await self.middleware_stack(scope, receive, send)
2025-10-21T10:12:14.3083329Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/starlette/middleware/errors.py", line 186, in __call__
2025-10-21T10:12:14.3083351Z     raise exc
2025-10-21T10:12:14.3083377Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/starlette/middleware/errors.py", line 164, in __call__
2025-10-21T10:12:14.30834Z     await self.app(scope, receive, _send)
2025-10-21T10:12:14.3083426Z   File "/agents/python/common/opentelemetry/instrumentation/asgi/__init__.py", line 768, in __call__
2025-10-21T10:12:14.3083451Z     await self.app(scope, otel_receive, otel_send)
2025-10-21T10:12:14.3083478Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/starlette/middleware/errors.py", line 186, in __call__
2025-10-21T10:12:14.3083499Z     raise exc
2025-10-21T10:12:14.3083526Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/starlette/middleware/errors.py", line 164, in __call__
2025-10-21T10:12:14.3083565Z     await self.app(scope, receive, _send)
2025-10-21T10:12:14.3083594Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
2025-10-21T10:12:14.3083622Z     await self.app(scope, receive, send)
2025-10-21T10:12:14.3083651Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 63, in __call__
2025-10-21T10:12:14.3083676Z     await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
2025-10-21T10:12:14.3083705Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
2025-10-21T10:12:14.3083726Z     raise exc
2025-10-21T10:12:14.3083751Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
2025-10-21T10:12:14.3083774Z     await app(scope, receive, sender)
2025-10-21T10:12:14.30838Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/fastapi/middleware/asyncexitstack.py", line 18, in __call__
2025-10-21T10:12:14.3083834Z     await self.app(scope, receive, send)
2025-10-21T10:12:14.3083861Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/starlette/routing.py", line 716, in __call__
2025-10-21T10:12:14.3083884Z     await self.middleware_stack(scope, receive, send)
2025-10-21T10:12:14.308391Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/starlette/routing.py", line 736, in app
2025-10-21T10:12:14.3083932Z     await route.handle(scope, receive, send)
2025-10-21T10:12:14.3083957Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/starlette/routing.py", line 290, in handle
2025-10-21T10:12:14.308398Z     await self.app(scope, receive, send)
2025-10-21T10:12:14.3084004Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/fastapi/routing.py", line 123, in app
2025-10-21T10:12:14.3084029Z     await wrap_app_handling_exceptions(app, request)(scope, receive, send)
2025-10-21T10:12:14.3084055Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
2025-10-21T10:12:14.3084089Z     raise exc
2025-10-21T10:12:14.3084116Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
2025-10-21T10:12:14.308414Z     await app(scope, receive, sender)
2025-10-21T10:12:14.3084166Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/fastapi/routing.py", line 109, in app
2025-10-21T10:12:14.3084189Z     response = await f(request)
2025-10-21T10:12:14.3084212Z                ^^^^^^^^^^^^^^^^
2025-10-21T10:12:14.3084239Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/fastapi/routing.py", line 379, in app
2025-10-21T10:12:14.3084262Z     solved_result = await solve_dependencies(
2025-10-21T10:12:14.3084285Z                     ^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-21T10:12:14.3084312Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/fastapi/dependencies/utils.py", line 651, in solve_dependencies
2025-10-21T10:12:14.3084335Z     solved_result = await solve_dependencies(
2025-10-21T10:12:14.3084369Z                     ^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-21T10:12:14.3084397Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/fastapi/dependencies/utils.py", line 675, in solve_dependencies
2025-10-21T10:12:14.3084635Z     solved = await run_in_threadpool(call, **solved_result.values)
2025-10-21T10:12:14.3084661Z              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-21T10:12:14.308469Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/starlette/concurrency.py", line 38, in run_in_threadpool
2025-10-21T10:12:14.3084714Z     return await anyio.to_thread.run_sync(func)
2025-10-21T10:12:14.3084737Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-21T10:12:14.3084765Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/anyio/to_thread.py", line 56, in run_sync
2025-10-21T10:12:14.308479Z     return await get_async_backend().run_sync_in_worker_thread(
2025-10-21T10:12:14.3084826Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-21T10:12:14.3084853Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 2485, in run_sync_in_worker_thread
2025-10-21T10:12:14.3084876Z     return await future
2025-10-21T10:12:14.3084898Z            ^^^^^^^^^^^^
2025-10-21T10:12:14.3084925Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 976, in run
2025-10-21T10:12:14.3084947Z     result = context.run(func, *args)
2025-10-21T10:12:14.308497Z              ^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-21T10:12:14.3084994Z   File "/tmp/8de1086b7810c73/main.py", line 159, in get_session_id
2025-10-21T10:12:14.3085018Z     log_function(f"in get_session_id")
2025-10-21T10:12:14.3085043Z   File "/tmp/8de1086b7810c73/logging_utility.py", line 27, in log_function
2025-10-21T10:12:14.3085067Z     existing = blob_client.download_blob().readall()
2025-10-21T10:12:14.3085105Z                ^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-21T10:12:14.3085132Z   File "/agents/python/common/azure/core/tracing/decorator.py", line 138, in wrapper_use_tracer
2025-10-21T10:12:14.3085159Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/azure/storage/blob/_blob_client.py", line 779, in download_blob
2025-10-21T10:12:14.3085184Z     return StorageStreamDownloader(**options)
2025-10-21T10:12:14.3085206Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-21T10:12:14.3085233Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/azure/storage/blob/_download.py", line 403, in __init__
2025-10-21T10:12:14.3085256Z     self._response = self._initial_request()
2025-10-21T10:12:14.308528Z                      ^^^^^^^^^^^^^^^^^^^^^^^
2025-10-21T10:12:14.3085307Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/azure/storage/blob/_download.py", line 456, in _initial_request
2025-10-21T10:12:14.3085332Z     location_mode, response = cast(Tuple[Optional[str], Any], self._clients.blob.download(
2025-10-21T10:12:14.3085369Z                                                               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-21T10:12:14.3085395Z   File "/agents/python/common/azure/core/tracing/decorator.py", line 138, in wrapper_use_tracer
2025-10-21T10:12:14.3085423Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/azure/storage/blob/_generated/operations/_blob_operations.py", line 1639, in download
2025-10-21T10:12:14.308545Z     pipeline_response: PipelineResponse = self._client._pipeline.run(  # pylint: disable=protected-access
2025-10-21T10:12:14.3085478Z                                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-21T10:12:14.3085503Z   File "/agents/python/common/azure/core/pipeline/_base.py", line 242, in run
2025-10-21T10:12:14.3085529Z   File "/agents/python/common/azure/core/pipeline/_base.py", line 98, in send
2025-10-21T10:12:14.3085554Z   File "/agents/python/common/azure/core/pipeline/_base.py", line 98, in send
2025-10-21T10:12:14.308558Z   File "/agents/python/common/azure/core/pipeline/_base.py", line 98, in send
2025-10-21T10:12:14.3085604Z   [Previous line repeated 2 more times]
2025-10-21T10:12:14.3085641Z   File "/agents/python/common/azure/core/pipeline/policies/_redirect.py", line 205, in send
2025-10-21T10:12:14.3085667Z   File "/agents/python/common/azure/core/pipeline/_base.py", line 98, in send
2025-10-21T10:12:14.3085694Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/azure/storage/blob/_shared/policies.py", line 566, in send
2025-10-21T10:12:14.3085719Z     response = self.next.send(request)
2025-10-21T10:12:14.3085743Z                ^^^^^^^^^^^^^^^^^^^^^^^
2025-10-21T10:12:14.3085768Z   File "/agents/python/common/azure/core/pipeline/_base.py", line 98, in send
2025-10-21T10:12:14.3085793Z   File "/agents/python/common/azure/core/pipeline/_base.py", line 98, in send
2025-10-21T10:12:14.3085818Z   File "/agents/python/common/azure/core/pipeline/_base.py", line 98, in send
2025-10-21T10:12:14.3085842Z   [Previous line repeated 1 more time]
2025-10-21T10:12:14.308587Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/azure/storage/blob/_shared/policies.py", line 309, in send
2025-10-21T10:12:14.3085894Z     response = self.next.send(request)
2025-10-21T10:12:14.3085929Z                ^^^^^^^^^^^^^^^^^^^^^^^
2025-10-21T10:12:14.3085955Z   File "/agents/python/common/azure/core/pipeline/_base.py", line 98, in send
2025-10-21T10:12:14.308598Z   File "/agents/python/common/azure/core/pipeline/_base.py", line 98, in send
2025-10-21T10:12:14.3086006Z   File "/agents/python/common/azure/core/pipeline/_base.py", line 130, in send
2025-10-21T10:12:14.3086034Z   File "/tmp/8de1086b7810c73/antenv/lib/python3.11/site-packages/azure/storage/blob/_shared/base_client.py", line 360, in send
2025-10-21T10:12:14.3086123Z     return self._transport.send(request, **kwargs)
2025-10-21T10:12:14.308615Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-21T10:12:14.3086177Z   File "/agents/python/common/azure/core/pipeline/transport/_requests_basic.py", line 365, in send
2025-10-21T10:12:14.3086203Z   File "/agents/python/common/requests/sessions.py", line 589, in request
2025-10-21T10:12:14.3086227Z     resp = self.send(prep, **send_kwargs)
2025-10-21T10:12:14.3086262Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-21T10:12:14.3086291Z   File "/agents/python/common/opentelemetry/instrumentation/requests/__init__.py", line 228, in instrumented_send
2025-10-21T10:12:14.3086316Z     return wrapped_send(self, request, **kwargs)
2025-10-21T10:12:14.3086339Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-21T10:12:14.3086363Z   File "/agents/python/common/requests/sessions.py", line 703, in send
2025-10-21T10:12:14.3086385Z     r = adapter.send(request, **kwargs)
2025-10-21T10:12:14.3086408Z         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-10-21T10:12:14.3086431Z   File "/agents/python/common/requests/adapters.py", line 616, in send
2025-10-21T10:12:14.3086455Z     self.cert_verify(conn, request.url, verify, cert)
2025-10-21T10:12:14.308648Z   File "/agents/python/common/requests/adapters.py", line 303, in cert_verify
2025-10-21T10:12:14.3086515Z     raise OSError(
2025-10-21T10:12:14.3086542Z OSError: Could not find a suitable TLS CA certificate bundle, invalid path: /agents/python/common/certifi/cacert.pem
```
## System Information

this is a python azure webapp, running python 3.11


Let me know if you need any more information i will provide it

## The Solution / Discussion
### Response 1
It looks like `/agents/python/common/` exists (e.g., `2025-10-21T10:12:14.308648Z   File "/agents/python/common/requests/adapters.py", line 303, in cert_verify`). I have no explanation though as to what creates that directory structure though nor do I have an explanation as to why the certifi library's data file is missing. It depends on how you packaged everything and shipped it to Azure but this is not a bug in Requests by any stretch of the imagination. It's also not a bug in certifi. It's certainly a bug in how you're shipping libraries/code to Azure.

