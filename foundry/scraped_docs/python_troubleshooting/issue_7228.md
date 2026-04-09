# Q: RequestsCookieJar shouldn't inherit from MutableMapping
**Source:** https://github.com/psf/requests/issues/7228

## The Problem / Request
<!-- Summary. -->

`RequestsCookieJar` currently inherits from both `CookieJar` and `MutableMapping`, but these classes are incompatible. `CookieJar.__iter__` iterates over `Cookies`, whereas `MutableMapping` expects `__iter__` to iterate over the key type (`str`).

## Expected Result

`RequestsCookieJar` does not inherit from `MutableMapping`

(or the values produced by `__iter__` can be passed to `__getitem__`)

## Actual Result

`__iter__` produces `Cookie`s, and `__getitem__` raises `KeyError` if any non-`str` is passed

## Reproduction Steps

```python
from collections.abc import MutableMapping
import requests

# this function should work with any object that correctly implements MutableMapping
def example(some_obj):
    print(f"example(some_obj:{type(some_obj).__name__})")
    if isinstance(some_obj, MutableMapping):
        for key in some_obj:
            print(f"some_obj[{key!r}] = {some_obj[key]!r}")

example("")
example({"foo": 1})

cookie_jar = requests.cookies.RequestsCookieJar()
cookie_jar["foo"] = "1"
example(cookie_jar) # raises KeyError
```

## System Information

    $ python -m requests.help

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
    "version": "3.11"
  },
  "implementation": {
    "name": "CPython",
    "version": "3.13.11"
  },
  "platform": {
    "release": "6.12.70",
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
    "version": "30600010"
  },
  "urllib3": {
    "version": "2.5.0"
  },
  "using_charset_normalizer": true,
  "using_pyopenssl": false
}
```

but this should apply to any version since 4d6871d9176c13affe625b1885278d396a39f21d

## Additional context

This is particularly a problem for correctly typing `RequestsCookieJar`, which is how I ran into this. See https://github.com/python/typeshed/issues/15457

## The Solution / Discussion
### Response 1
Hi @shelvacu, thanks for reaching out. You're correct the typing here is messy, but it _is_ correct from when it was implemented.

Way back in [Python 2.6](https://docs.python.org/2.6/library/collections.html#abcs-abstract-base-classes), when this was written, the requirements for MutableMapping were very different than what's evolved in the standard library. You needed to implement a handful of methods (that MutableMapping currently does) and behave _like_ a dict. RequestsCookieJar fully covered that when it was shipped in #565.

Now 14 years have gone by, CPython has become much more specific of what MutableMapping is but Requests is still here. Removing the typing is a runtime breakage so it's a non-starter to do that. I have some work underway to make the typing here clean(_er_) but we're likely not going to get to an exact match.

### Response 2
Appreciate the detailed report, very helpful

On Tue, Mar 17, 2026, 1:08 AM Nate Prewitt ***@***.***> wrote:

> *nateprewitt* left a comment (psf/requests#7228)
> <https://github.com/psf/requests/issues/7228#issuecomment-4072370772>
>
> Hi @shelvacu <https://github.com/shelvacu>, thanks for reaching out.
> You're correct the typing here is messy, but it *is* correct from when it
> was implemented.
>
> Way back in Python 2.6
> <https://docs.python.org/2.6/library/collections.html#abcs-abstract-base-classes>,
> when this was written, the requirements for MutableMapping were very
> different than what's evolved in the standard library. You needed to
> implement a handful of methods (that MutableMapping currently does) and
> behave *like* a dict. RequestsCookieJar fully covered that when it was
> shipped in #565 <https://github.com/psf/requests/pull/565>.
>
> Now 14 years have gone by, CPython has become much more specific of what
> MutableMapping is but Requests is still here. Removing the typing is a
> runtime breakage so it's a non-starter to do that. I have some work
> underway to make the typing here clean(*er*) but we're likely not going
> to get to an exact match.
>
> —
> Reply to this email directly, view it on GitHub
> <https://github.com/psf/requests/issues/7228#issuecomment-4072370772>, or
> unsubscribe
> <https://github.com/notifications/unsubscribe-auth/B7GEOJIY62A43SSEIZRU4X34RDMU7AVCNFSM6AAAAACWCJBK7KVHI2DSMVQWIX3LMV43OSLTON2WKQ3PNVWWK3TUHM2DANZSGM3TANZXGI>
> .
> You are receiving this because you are subscribed to this thread.Message
> ID: ***@***.***>
>


### Response 3
I'm going to close this our since we haven't heard anything back in a couple weeks. There's a PR #7272 migrating typing into Requests makes some of the behavior a bit clearer, but as I said before, the delta will likely remain going forward.

