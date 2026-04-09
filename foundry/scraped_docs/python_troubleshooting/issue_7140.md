# Q: Request for clarification: URL parsing behavior in Requests (RFC 3986 vs WHATWG)
**Source:** https://github.com/psf/requests/issues/7140

## The Problem / Request
Hello Requests maintainers,

Thank you for maintaining Requests and for the extensive discussions around URL parsing behavior over the years.

I am seeking clarification regarding which specification(s) Requests follows for URL parsing, particularly for HTTP(S) URLs, as I have observed behaviors that appear to align with different standards.

In previous discussions, Requests developers have noted that the library primarily follows RFC-based specifications. For example, in [#5886](https://github.com/psf/requests/issues/5886), it is stated that:
> RFC 3986 is the standard that Requests and urllib3 primarily use as a reference for their URL parsers.

This suggests that Requests' URL parsing logic is grounded in RFC 3986, with HTTP semantics further informed by RFC 7230.

However, I have observed a behavior in Requests that seems closer to the WHATWG URL Standard.

Specifically, when parsing HTTP URLs whose hostname contains a backslash (\), Requests appears to treat \ as a delimiter equivalent to /, effectively separating the authority from the path.
This behavior is consistent with the WHATWG URL Standard's definition of the authority parsing state (see: https://url.spec.whatwg.org/#authority-state).

<img width="812" height="803" alt="Image" src="https://github.com/user-attachments/assets/94354e6d-0e70-4207-923a-42b4e57fecb3" />

**By contrast:** RFC 3986 treats \ as a disallowed character in URLs and does not define it as a structural delimiter. Many RFC-oriented parsers (e.g., urllib.parse.urlparse) either reject such URLs or treat \ as an ordinary character, rather than as a path/authority separator.

<img width="606" height="754" alt="Image" src="https://github.com/user-attachments/assets/bba396ba-b4b5-4ad5-ba2f-25b1ccea6929" />

### Question

Could you please clarify:
Whether Requests intentionally references or aligns with the WHATWG URL Standard for any part of its URL parsing behavior (especially hostname handling)?
Or whether the observed behavior is still considered RFC 3986–based, but with pragmatic extensions or legacy compatibility considerations?

Understanding this would be very helpful for accurately characterizing Requests' parsing semantics and for reasoning about cross-component URL parsing consistency.

Thank you very much for your time and clarification.

## The Solution / Discussion
### Response 1
As described in the template, we won't be able to answer questions on this issue tracker. Please use [Stack Overflow](https://stackoverflow.com/)

