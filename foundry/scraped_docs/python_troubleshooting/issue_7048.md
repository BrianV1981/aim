# Q: Cloudflare blocks my api bot, but not when I use http.client?
**Source:** https://github.com/psf/requests/issues/7048

## The Problem / Request
I apologize for the long title, I was sending api requests to thingiverse.com but my bot wasn't responding back and found out cloudflare is blocking my bot, I did a quick test using http.client library and was getting return code 200. I dug a little deeper and found requests adds user-agent, and tried this work around here https://github.com/psf/requests/issues/5671#issuecomment-1006735307 but still had no luck. Is there anyway I can check what gets sent either from requests or urllib3 since something clearly does if I don't get blocked when I use http.client. I would like to resolve this with requests library so I am not essentially relying on only one method. 


## The Solution / Discussion
### Response 1
As described in the template, we won't be able to answer questions on this issue tracker. Please use [Stack Overflow](https://stackoverflow.com/)

