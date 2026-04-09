# Q: Cannot use LWPCookiejar with requests
**Source:** https://github.com/psf/requests/issues/7014

## The Problem / Request
There is no way to put cookies into a standard cookiejar.

## Expected Result

Cookies can be stored in LWP format

## Actual Result

Cookies are provided in multiple unusable formats, no way to store to a standard jar.

## Reproduction Steps

Make a request that returns multiple cookies. (This is not verified, I do not know how to access _actual headers_ from a `Response` object.)

```
        r = requests.request(method, self.url + path, *args, **kwargs)
        if hasattr(self, 'cookiejar'):
            if 'Set-Cookie' in r.headers or 'Set-Cookie2' in r.headers:
                def get_all(self, name, default=[]):
                    return [self.get(name, default)]  # it's a dictionary, can only have one match anyway
                if not hasattr(r.headers, 'get_all'):
                    r.headers.get_all = types.MethodType(get_all, r.headers)

                self.cookiejar.extract_cookies(requests.cookies.MockResponse(r.headers),
                                               requests.cookies.MockRequest(r.request))
```

`Response` has a `cookies` property but this returns a custom cookie jar which cannot be saved in **LWP** format.

The standard `LWPCookieJar` provides interface for iterating cookies but not storing cookies, only for extracting cookies from headers.

The `Response` object has a `headers` property but this is a **dictionary**, and cannot store _multiple headers_ of the same name correctly. There is nothing stopping the server from sending _multiple_ `Set-Cookie` headers, the standard only requests that no two cookies with the same name be sent. When it does the `Response` `headers` property has a mangled `Set-Cookie` header, and it cannot be parsed by `LWPCookieJar`. `Response` does not provide access to _unmangled headers_ in any way I can find in the documentation.

## System Information

Linux, python 3.6~3.11

```json
{
  "chardet": {
    "version": null
  },
  "charset_normalizer": {
    "version": "3.1.0"
  },
  "cryptography": {
    "version": "41.0.3"
  },
  "idna": {
    "version": "3.4"
  },
  "implementation": {
    "name": "CPython",
    "version": "3.11.13"
  },
  "platform": {
    "release": "6.4.0-150600.23.47-default",
    "system": "Linux"
  },
  "pyOpenSSL": {
    "openssl_version": "30100040",
    "version": "23.2.0"
  },
  "requests": {
    "version": "2.31.0"
  },
  "system_ssl": {
    "version": "30100040"
  },
  "urllib3": {
    "version": "2.0.7"
  },
  "using_charset_normalizer": true,
  "using_pyopenssl": true
}
```


## The Solution / Discussion
### Response 1
https://datatracker.ietf.org/doc/html/rfc7230#section-3.2.2 notes that Set-Cookie fields are an exception to the rule that fields of the same name can be appended. And that seems to be exactly what is happening here. The Set-Cookie fields are appended leading to an invalid header, and inability to parse the cookies.

### Response 2
@hramrach will you please assign to me

### Response 3

```
        r = requests.request(method, self.url + path, *args, **kwargs)
        if hasattr(self, 'cookiejar'):
            if 'Set-Cookie' in r.headers or 'Set-Cookie2' in r.headers:
                if not hasattr(r.headers, 'get_all'):
                    headers = email.message.EmailMessage(policy=email.policy.HTTP)
                    for k in r.headers.keys():
                        if k.lower() == 'set-cookie' or k.lower() == 'set-ccokie2':
                            cookies = r.headers[k].split(',')  # https://github.com/psf/requests/issues/7014
                            for c in cookies:
                                headers[k] = c
                        headers[k] = r.headers[k]
                else:
                    headers = r.headers

                self.cookiejar.extract_cookies(requests.cookies.MockResponse(headers),
                                               requests.cookies.MockRequest(r.request))
```
Works perfectly when cookies happen to be comma-free (not aware of anything preventing fields like `path` or `expire` from containing commas).

https://github.com/alexdutton/www-authenticate could be probably massaged to cover most cases but if the `headers` field was constructed as `EmailMessage` to start with this would just work. That's even what `MockResponse` expects and it fails when the custom dictionary used for `headers` is passed in. To not break other users that rely on concatenated headers the headers other than cookies can still be concatenated.

### Response 4
I do not have the permissions to assign

### Response 5
Hi @hramrach, this seems like it may be a bit of API confusion.

If you're trying to use an LWPCookieJar, that is supported. You can add you cookies before the request and pass them into `cookies` through your current requests.get() call. That is intended for transmitting cookies though, not receiving.

If you're trying to get persistence of cookies across requests, you'll want to do something like this with a `Session`. You should find they're all separated. Reparsing the headers isn't going to give you what you want in this case.

```python
jar = LWPCookieJar()
s = requests.Session()
s.cookies = jar

r = s.get('https://example.com')

for cookie in jar:
    print(cookie.name, cookie.value)
```

### Response 6
Thanks. If that works correctly it can workaround the problem that the cookie headers returned by requests are broken.

Not sure why parsing the cookie headers would not work if the headers weren't broken. I switched to another library to get correct cookie headers and parsing them works fine. It does not support sessions, though.

