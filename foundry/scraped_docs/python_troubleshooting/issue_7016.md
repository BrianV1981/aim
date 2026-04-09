# Q: recursive dependency involving fixture 'httpbin' detected when running tests
**Source:** https://github.com/psf/requests/issues/7016

## The Problem / Request
`recursive dependency involving fixture 'httpbin' detected` when running tests

## Expected Result

tests run or provide actionable error report

## Actual Result

Large part of tests failing to run because of 'recursive dependency'

## Reproduction Steps

`make ci`

```
______________________________________________________________________________________ ERROR at setup of test_content_length_for_string_data_counts_bytes _______________________________________________________________________________________
file /home/hramrach/requests/tests/test_requests.py, line 3032
  @pytest.mark.skipif(
      is_urllib3_1,
      reason="urllib3 2.x encodes all strings to utf-8, urllib3 1.x uses latin-1",
  )
  def test_content_length_for_string_data_counts_bytes(httpbin):
file /home/hramrach/requests/tests/conftest.py, line 25
  @pytest.fixture
  def httpbin(httpbin):
E       recursive dependency involving fixture 'httpbin' detected
>       available fixtures: anyio_backend, anyio_backend_name, anyio_backend_options, cache, capfd, capfdbinary, caplog, capsys, capsysbinary, doctest_namespace, httpbin, httpbin_secure, monkeypatch, nosan_server, pytestconfig, record_property, record_testsuite_property, record_xml_attribute, recwarn, tmp_path, tmp_path_factory, tmpdir, tmpdir_factory
>       use 'pytest --fixtures [testpath]' for help on them.
```

Probably `httpbin` is missing and because of the way httpbin is used in the test code this cryptic message is produced.

## System Information

    $ python3 -m requests.help

```json
{
  "chardet": {
    "version": "5.2.0"
  },
  "charset_normalizer": {
    "version": "3.4.2"
  },
  "cryptography": {
    "version": "44.0.3"
  },
  "idna": {
    "version": "3.10"
  },
  "implementation": {
    "name": "CPython",
    "version": "3.13.5"
  },
  "platform": {
    "release": "6.12.0-160000.19-rt",
    "system": "Linux"
  },
  "pyOpenSSL": {
    "openssl_version": "30500000",
    "version": "25.0.0"
  },
  "requests": {
    "version": "2.32.4"
  },
  "system_ssl": {
    "version": "30500000"
  },
  "urllib3": {
    "version": "2.5.0"
  },
  "using_charset_normalizer": false,
  "using_pyopenssl": true
}
```



## The Solution / Discussion
### Response 1
I can't speak specifically to what you're seeing, but there isn't enough information here to help debug it for you.

Our last CI run was 3 days ago and all tests succeeded. I don't know if our last run managed to be on a different version of `pytest` and you're on a newer version or if some other version changed between then and your run, but there seems to be little for us to help you with.

---

If I were to take posit a theory, I'd argue that the problem is likely due to us creating a test fixture that collides with another fixture provided by a third-party and so `pytest` is uncertain which one takes precedence/is desired by various tests. I'd also argue that's a regression for `pytest` but I can see that this behaviour is fairly more _explicit_ than before and so we _may_ need to rename the fixture in your stack trace.

### Response 2
The error is resolved by installing `pytest-httpbin` but it' not clear from the error message that this is the problem.

### Response 3
I went and checked https://requests.readthedocs.io/en/latest/dev/contributing/#steps-for-submitting-code and I think we're missing a step that explains how to ensure dependencies are installed for running the tests. 

Namely, one _should_ create a virtual environment and _must_ run `pip install -r requirements-dev.txt`. Alternatively, one installs `tox` and then uses that to manage virtual environments and test executions.

### Response 4
I see nothing there about venv nor tox, nor requirements-dev.txt for that matter.

Obviously, you do need some tools for running the tests, and the tests won't run when the tools are not present.

In most cases the error would be about failed import which is easy to diagnose.

Here an incomprehensible error about recursive dependency.

### Response 5
>  I think we're missing a step that explains how to ensure dependencies are installed for running the tests.

Why are you aggressively responding this way when the above is what I said? 

### Response 6
@hramrach please make sure you've installed the [development dependencies](https://github.com/psf/requests/blob/47914226c2968802f2cdee3f6f0f6e06e4472f64/requirements-dev.txt#L4) before running the test suite. You're missing pytest-httpbin.

