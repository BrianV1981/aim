# Q: Add `simplejson` as an optional extra
**Source:** https://github.com/psf/requests/issues/7032

## The Problem / Request
Would you be open to adding `simplejson` as an optional extra?
This would allow users to install it via `poetry add requests[simplejson]`. Having it as an official extra would make the dependency relationship explicit.

## The Solution / Discussion
### Response 1
Support for it is purely historical. An optional extra would be something I would consider if we wanted to give folks a nudge to consider using it which isn't our position as a project. Also we don't actively test against it so support is barely best effort

### Response 2
@sigmavirus24 It is not an explicit dependency of `requests`library, so probably people don't even know about it. If someone removes the `simplejson` package blindly from their project (because it is not used anywhere explicitly), it can cause requests to fail with JSON serialisation errors. (`Decimal` serialisation, for example).

**I think there are 2 ways to resolve this:**
- keep the `simplejson` as a dependency, but as an explicit extra (staying backward compatible)
- remove it from the `requests` library as a breaking change

### Response 3
You're missing the third way: 

Change nothing because folks aren't sanitizing days that they're sending properly and that's a bug in their systems

### Response 4
Hi, I’m interested in working on this. If maintainers are okay with having simplejson as an optional extra, I can prepare a PR adding it along with documentation updates.

### Response 5
Hi maintainers, I'd like to take up this issue and prepare a PR for adding
`simplejson` as an optional extra, along with the required documentation updates.

I have gone through the discussion above and can implement it cleanly.
Please let me know if I may proceed.


### Response 6
As was already noted, this is a historical dependency that we don't want to encourage for further usage. I don't think we have plans to add this as an extra going forward. Thanks for your interest though.

