# Q: Quoted charset values are not detected by `get_encoding_from_headers`
**Source:** https://github.com/psf/requests/issues/7234

## The Problem / Request
 `requests.utils.get_encoding_from_headers` fails to detect charset values when they are surrounded by single or double quotes in the Content-Type header. In such cases, the function returns `None` instead of the correct encoding string.
Unquoted charset values continue to behave correctly.

## Expected Result

When a quoted charset is present in the `Content-Type` header, the function should return the unquoted charset value.
Example:
   `
headers = {
    "Content-Type": 'text/html; charset="utf-8"'
}`

Expected:
 `"utf-8"`

## Actual Result

The function returns: 
  `None`
for quoted charset values such as:

-      `charset= "utf-8"`
-      `charset= 'utf-8'`

Unquoted charset values (e.g., `charset=utf-8`) behave correctly.

## Reproduction Steps

```python
from requests.utils import get_encoding_from_headers

headers = {
    "Content-Type": 'text/html; charset="utf-8"'
}

print(get_encoding_from_headers(headers))
```

Output:
`None`

## System Information

    $ python -m requests.help

```json
{
  "chardet": {
    "version": null
  },
  "charset_normalizer": {
    "version": "3.4.4"
  },
  "cryptography": {
    "version": ""
  },
  "idna": {
    "version": "3.11"
  },
  "implementation": {
    "name": "CPython",
    "version": "3.12.12"
  },
  "platform": {
    "release": "6.6.87.2-microsoft-standard-WSL2",
    "system": "Linux"
  },
  "pyOpenSSL": {
    "openssl_version": "",
    "version": null
  },
  "requests": {
    "version": "2.32.5"
  },
  "system_ssl": {
    "version": "30500040"
  },
  "urllib3": {
    "version": "2.6.3"
  },
  "using_charset_normalizer": true,
  "using_pyopenssl": false
}
```

<!-- This command is only available on Requests v2.16.4 and greater. Otherwise,
please provide some basic information about your system (Python version,
operating system, &c). -->


## The Solution / Discussion
### Response 1
I think I see what's going on here. Going to put together a fix.

### Response 2
Hi @jmdotdev, the issue you're hitting is because your key casing (`Content-Type`) is different than what Requests is looking for in the code (`content-type`). Your casing is arguably more correct, but Requests specifically has headers designed as a [CaseInsensitiveDict](https://github.com/psf/requests/blob/0e4ae38f0c93d4f92a96c774bd52c069d12a4798/src/requests/structures.py#L13-L80) since casing can vary based on different implementations, testing frameworks, etc.

You cannot reach this code in Requests without the headers being in a CaseInsensitiveDict. Using it as a standalone utility right now though, it's under-defined. We already have work underway that should make that contract clearer going forward. For the time being you'll either want to use `CaseInsensitiveDict` as intended or lowercase your dict keys if you cannot.

