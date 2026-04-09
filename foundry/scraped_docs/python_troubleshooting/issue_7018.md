# Q: Remove unused argument from _urllib3_request_context
**Source:** https://github.com/psf/requests/issues/7018

## The Problem / Request
in `src/requests/adapters.py` the `_urllib3_request_context` takes a 4th argument `poolmanger` that is not used in the function at all.

The `_urllib3_request_context` is only used in one place (in the same file). I can make a PR to remove the extra argument, if that's okay?

I took the liberty of making the change on my machine and got `595 passed, 15 skipped, 1 xfailed, 18 warnings in 72.78s (0:01:12)` as the result.

## The Solution / Discussion
### Response 1
No thanks, we don't accept minor cosmetic contributions 

