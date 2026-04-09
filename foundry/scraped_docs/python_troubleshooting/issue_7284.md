# Q: Clarify problematic chardet dependency warning
**Source:** https://github.com/psf/requests/issues/7284

## The Problem / Request
## How to reproduce

Install requests and chardet in a clean environment:

```bash
mkdir test && cd test && uv init
uv add requests chardet
uv run python -c "import requests"
```

At the time of writing (requests=2.32.5, chardet=7.2.0), this gives a warning which is hard to understand, and is not actionable:

> RequestsDependencyWarning: urllib3 (2.6.3) or chardet (7.2.0)/charset_normalizer (3.4.6) doesn't match a supported version!


## Explanation

I spent around 15 minutes trying to get rid of this warning, thinking that maybe my network requests would somehow be broken. I tried to install different versions of urllib3, chardet and charset-normalizer. After reading issues and docs, I found the full explanation to be: requests uses `chardet` only if it's installed (optional dependency). Otherwise it uses `charset-normalizer`. I think this behavior is questionable - consider that I didn't even install chardet myself, one of my other dependencies had chardet as its dependency. Why would that alter the behavior of requests?

Furthermore, I had to go into requests code to understand what chardet version was actually supported, which is not a very good developer experience.

## Suggestion

If existing behavior is kept, I suggest to at least reword the warning, e.g.:
> The requests library uses chardet as an optional dependency. You have chardet==7.2.0, but requests supports chardet<6. Please install chardet<6 to silence this warning.



## The Solution / Discussion
### Response 1
Related: #7223, #7219, https://github.com/psf/requests/commit/b2a1d33f571518ca9a6148e7da787cc5827f897a

### Response 2
Hi @matangover, I provided a quick response [here](https://github.com/psf/requests/pull/7291#issuecomment-4122747269). We're aware of the warning, we normally have these addressed same day. There's just been a [large amount of visibility](https://github.com/chardet/chardet/issues/327) around this release (coupled with a couple other issues) that have delayed it.

> I think this behavior is questionable - consider that I didn't even install chardet myself, one of my other dependencies had chardet as its dependency. Why would that alter the behavior of requests?

We agree, this was never behavior we intended to have. Apache forced this behavior through in https://github.com/psf/requests/pull/5797 which has been a source of pain for users since. Unfortunately there's not a lot to do about it currently.

As I said in the other comment, we're working on a release and should have this addressed shortly.

