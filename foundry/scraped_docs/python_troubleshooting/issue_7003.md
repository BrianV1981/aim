# Q: When using RequestsCookieJar to set a cookie with an empty string ('') or 0 as the value, it cannot be retrieved properly afterward.
**Source:** https://github.com/psf/requests/issues/7003

## The Problem / Request
When using RequestsCookieJar to set a cookie with an empty string ('') or 0 as the value, it cannot be retrieved properly afterward.

## Expected Result

It can be retrieved properly after being set.

## Actual Result

It cannot be retrieved properly after being set.

## Reproduction Steps

```python
from requests.cookies import RequestsCookieJar

jar = RequestsCookieJar()

jar.set('token', 0, domain='example.com', path='/')

print("Jar contents:", list(jar.items()))  # [('token', 0)]
print("jar.get:", jar.get('token', domain='example.com', path='/'))  # it should return 0 instead of None.

try:
    print("jar['token']:", jar['token'])  # it should return 0 instead of raising an error.
except KeyError as e:
    print("KeyError raised unexpectedly:", e)

```

## System Information

    $ python -m requests.help

```json
{
  "chardet": {
    "version": null
  },
  "charset_normalizer": {
    "version": "2.0.12"
  },
  "cryptography": {
    "version": ""
  },
  "idna": {
    "version": "3.7"
  },
  "implementation": {
    "name": "CPython",
    "version": "3.6.8"
  },
  "platform": {
    "release": "3.10.0-1160.119.1.el7.x86_64",
    "system": "Linux"
  },
  "pyOpenSSL": {
    "openssl_version": "",
    "version": null
  },
  "requests": {
    "version": "2.27.1"
  },
  "system_ssl": {
    "version": "100020bf"
  },
  "urllib3": {
    "version": "1.26.19"
  },
  "using_charset_normalizer": true,
  "using_pyopenssl": false
}

```


## The Solution / Discussion
### Response 1
Resolving as a duplicate of #5950. I believe there's already a PR open for this as well.

