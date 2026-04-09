# Q: One request fails, but others don't; it also succeeds in terminal
**Source:** https://github.com/psf/requests/issues/7029

## The Problem / Request
I checked a lot of trouble-shoot topics, but didn't find what might be wrong here...

I'm going off this API documentation: https://kritsel.github.io/tado-openapispec-v2/swagger

This code:
```
import requests
import json


url1 = "https://my.tado.com/api/v2/homes/[myzone]/zones/2/schedule/activeTimeTable"
url2 = "https://my.tado.com/api/v2/homes/[myzone]/zones/2/details"

token = "[mytoken]"

headers = {
    'Authorization': "Bearer "+token,
    'User-Agent': 'python/libtado',
}

data1 = {"id": 1}
data2 = {"name": "Eetkamer"}


timeout = 15

r1 = requests.put(url1, headers=headers, json=data1, timeout=timeout)
r2 = requests.put(url2, headers=headers, json=data2, timeout=timeout)

print("###################")

print(r1)
print("-------------------")
r1.status_code
print("-------------------")
print(r1)

print("###################")

print(r2)
print("-------------------")
r2.status_code
print("-------------------")
print(r2)

print("###################")
```
... results in this output:
```
PS C:\Git\requests-set-schedule-tado> python requests-test.py
###################
<Response [403]>
-------------------
-------------------
<Response [403]>
###################
<Response [200]>
-------------------
-------------------
<Response [200]>
###################
```

But when I make that HTTP request to `https://my.tado.com/api/v2/homes/[myzone]/zones/2/schedule/activeTimeTable` in PowerShell, the response is `200`...:
```
PS C:\Git\requests-set-schedule-tado> Invoke-WebRequest -UseBasicParsing -Uri "https://my.tado.com/api/v2/homes/[myzone]/zones/2/schedule/activeTimetable" `
>> -Method "PUT" `
>> -WebSession $session `
>> -Headers @{
>>   "accept"="application/json"
>>   "authorization"="Bearer [mytoken]"
>> } `
>> -ContentType "application/json" `
>> -Body "{`"id`":1}"

StatusCode        : 200
StatusDescription : OK
Content           : {"id":1,"type":"THREE_DAY"}
RawContent        : HTTP/1.1 200 OK
                    Date: Fri, 12 Sep 2025 17:57:29 GMT
                    Transfer-Encoding: chunked
                    Connection: keep-alive
                    Vary: origin
                    Vary: access-control-request-method
                    Vary: access-control-request-headers
                    Vary:…
Headers           : {[Date, System.String[]], [Transfer-Encoding, System.String[]], [Connection, System.String[]], [Vary, System.String[]]…}
Images            : {}
InputFields       : {}
Links             : {}
RawContentLength  : 27
RelationLink      : {}
```

Could someone guide me to a solution?

Thanks in advance!

PS Obviously, [myzone] and [mytoken] are placeholders for privacy reasons.

## The Solution / Discussion
### Response 1
As described in the template, we won't be able to answer questions on this issue tracker. Please use [Stack Overflow](https://stackoverflow.com/)

