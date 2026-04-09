# Q: CVE-2026-21441 pypi:urllib3/2.5.0 to urllib3 2.6.3
**Source:** https://github.com/psf/requests/issues/7276

## The Problem / Request
<!-- Summary. -->
 **pypi:urllib3/2.5.0** is vulnerable to **CVE-2026-21441**
https://nvd.nist.gov/vuln/detail/CVE-2026-21441

## Expected Result

While scanning psf-requests2.32.4
We see reference of urllib32.5.0 which needs to be upgraded to  urllib3 2.6.3

Please help resolve this issue


## The Solution / Discussion
### Response 1
@rsrinivasanhome you're free to upgrade urllib3. Requests supports all versions of urllib3 2.x. What you install is not under our control.

