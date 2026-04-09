# Q: About connection release when maintaining sessions
**Source:** https://github.com/psf/requests/issues/7045

## The Problem / Request
While using the requests library for HTTP requests, I noticed that there were many TCP connections in the FIN_WAIT2 state on the server. Through code analysis, I found that these connections originated from the connection pool created by the underlying urllib3 library used by the requests library.

The application needs to provide services at any time, so it created a session object that is reused throughout the entire process lifecycle, and it does not actively call the `session.close()` method before the process ends.

After reading the source code, I discovered that the requests library only retrieves a connection from the connection pool when making a new HTTP request. It checks whether the connection is available, and if not, it immediately closes the connection and creates a new one. After receiving an HTTP response, the connection is returned to the connection pool. These connections remain idle until the next request arrives.

Is this the actual situation?

If so, then when the server actively closes the connection (by sending a FIN packet at the TCP protocol layer), the requests library does not detect this state change (it does not have a daemon thread continuously checking the connection status). As a result, the server sees many connections in the FIN_WAIT2 state that have been open for a long time. What is the rationale behind this design?

Thank you very much!

## The Solution / Discussion
### Response 1
As described in the template, we won't be able to answer questions on this issue tracker. Please use [Stack Overflow](https://stackoverflow.com/)

