# Q: import Requests kicks me out of  python interpreter. (Python 3.14.0a5)
**Source:** https://github.com/psf/requests/issues/7041

## The Problem / Request
<!-- Summary. -->

## Expected Result

Python 3.14.0a5 (main, Feb 12 2025, 14:50:24) [MSC v.1942 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import requests
>>> exit()
(standard bash prompt)

## Actual Result

Python 3.14.0a5 (main, Feb 12 2025, 14:50:24) [MSC v.1942 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import requests
(standard bash prompt) 

## Reproduction Steps

tried the same with: 'import os' which works fine
```python
import os
```

## System Information

    $ python -m requests.help

```json
{
system = "windows 11"
requires-python = ">=3.14"
dependencies = [
 "requests>=2.32.5",
]
}
```
<-- -->


## The Solution / Discussion
### Response 1
I would like to solve this issue

### Response 2
I wasnt able to repro this issue on Mac running python 3.14

### Response 3
@diazerium Are you able to reproduce this with a GA version of Python 3.14? The early alpha builds are not explicitly supported as we did not test those and they often have open bugs that lead to unexpected behaviors. The current latest version is Python 3.14.2.

### Response 4
Hi Nate and Bismeet: retried on later GA release and same script now works.
Seems to be an early quirk. Thanks for the feedback and the good work!

On Fri, Jan 9, 2026 at 7:25 PM Nate Prewitt ***@***.***>
wrote:

> *nateprewitt* left a comment (psf/requests#7041)
> <https://github.com/psf/requests/issues/7041#issuecomment-3730075673>
>
> @diazerium <https://github.com/diazerium> Are you able to reproduce this
> with a GA version of Python 3.14? The early alpha builds are not explicitly
> supported as we did not test those and they often have open bugs that lead
> to unexpected behaviors. The current latest version is Python 3.14.2.
>
> —
> Reply to this email directly, view it on GitHub
> <https://github.com/psf/requests/issues/7041#issuecomment-3730075673>, or
> unsubscribe
> <https://github.com/notifications/unsubscribe-auth/AANZVWAXIHPNKWQFF3WGBET4F7XBTAVCNFSM6AAAAACI3LZKPWVHI2DSMVQWIX3LMV43OSLTON2WKQ3PNVWWK3TUHMZTOMZQGA3TKNRXGM>
> .
> You are receiving this because you were mentioned.Message ID:
> ***@***.***>
>


