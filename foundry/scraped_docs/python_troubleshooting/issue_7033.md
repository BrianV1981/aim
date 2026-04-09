# Q: requests with self signed certs broken
**Source:** https://github.com/psf/requests/issues/7033

## The Problem / Request
specifying a cert bundle in 2.28.1 works fine, but in 2.32.5 fails with requests.exceptions.SSLError

## Expected Result

Response 200

## Actual Result

Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/usr/local/lib/python3.11/site-packages/requests/api.py", line 73, in get
    return request("get", url, params=params, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/requests/api.py", line 59, in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/requests/sessions.py", line 589, in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/requests/sessions.py", line 703, in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/requests/adapters.py", line 675, in send
    raise SSLError(e, request=request)
requests.exceptions.SSLError: HTTPSConnectionPool(host='lal-apps', port=443): Max retries exceeded with url: / (Caused by SSLError(SSLError(1, '[SSL: SSLV3_ALERT_HANDSHAKE_FAILURE] sslv3 alert handshake failure (_ssl.c:1016)')))

## Reproduction Steps

```python
import requests
url = '<YOUR SERVER WITH A SELF SIGNED CERT'
r = requests.get(url)
```

## System Information

    REQUESTS_CA_BUNDLE set to valid cert bundle, works with 2.28.1

```json
{
  "chardet": {
    "version": null
  },
  "charset_normalizer": {
    "version": "3.4.3"
  },
  "cryptography": {
    "version": ""
  },
  "idna": {
    "version": "3.10"
  },
  "implementation": {
    "name": "CPython",
    "version": "3.11.12"
  },
  "platform": {
    "release": "5.14.0-503.22.1.el9_5.x86_64",
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
    "version": "1010117f"
  },
  "urllib3": {
    "version": "2.5.0"
  },
  "using_charset_normalizer": true,
  "using_pyopenssl": false
}
```




## The Solution / Discussion
### Response 1
There isn't remotely enough information here to reproduce this. 

Furthermore we use self-signed certificates in some of our tests which still pass

