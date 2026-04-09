# Q: About request.Session
**Source:** https://github.com/psf/requests/issues/7024

## The Problem / Request
Hi, I have a special scenarios that there is a process called A continuously produces data while a process called B post the data to a url, The following is a fragment of  process B pseudocode:
```
with requests.Session as session:
  while True:
    data = queue.get()
    response = make_request(data, session)

```
The loop above is expected to continue even if an exception occurs, so the question is:
If something wrong causes session invalid, does it throw exceptions ？ if so, how to handle it so the loop continues ?

## The Solution / Discussion
### Response 1
As described in the template, we won't be able to answer questions on this issue tracker. Please use [Stack Overflow](https://stackoverflow.com/)

