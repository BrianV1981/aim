# Q: chardet 6 triggers RequestsDependencyWarning on stderr
**Source:** https://github.com/psf/requests/issues/7219

## The Problem / Request
<!-- Summary. -->

chardet 6.0.0 was just released, but requests only supports < 6.

This just broke our CI with:

```
/opt/hostedtoolcache/Python/3.12.12/x64/lib/python3.12/site-packages/requests/__init__.py:113:

RequestsDependencyWarning: urllib3 (2.6.3) or chardet (6.0.0dev0)/charset_normalizer (3.4.4) doesn't match a supported version!\n"
```

I also reported that strange "dev0" to the chardet project, that shouldn't be there when just doing "pip install chardet".

CI log: https://github.com/borgbackup/borg/actions/runs/22275930673/job/64439274108?pr=9397

## Reproduction Steps

Not sure, we do not directly use requests, it is just pulled in by some stuff we use.

And something installs the latest chardet and requests stumbles over it, spilling out unexpected output on stderr.


## The Solution / Discussion
### Response 1
It doesn't _break_ requests. We raise a warning because we haven't specifically tested it such that we raised the cap.

It _fails_ your testsuite because the warning is configured by your test suite to error on warnings - which I agree with.

Requests would not necessarily break if this was used in practice.

### Response 2
Yeah, I phrased it badly. The unexpected output broke our CI.

Nevertheless, it would be nice if requests supported chardet 6.

### Response 3
I faced this issue and just wanted to comment everything works fine in my environment with [chardet 6.0.0](https://github.com/chardet/chardet/releases/tag/6.0.0).

### Response 4
Would it be possible to publish a release that includes this fix? I think this issue has a relatively large impact.

### Response 5
The fact that the warning is emitted on `requests.__init__` means that the obvious way of suppressing warnings in pytest doesn't work, which is unfortunate.

I have something like this in my pyproject.toml
```toml
[tool.pytest.ini_options]
filterwarnings = [
    # https://docs.pytest.org/en/stable/how-to/capture-warnings.html#controlling-warnings
    # When a warning matches more than one option in the list, the action for the last matching option is performed.
    "error", # Implicitly coerce all non-fatal warnings into fatal exceptions.
    "ignore::requests.exceptions.RequestsDependencyWarning",
]
```

When running pytest it tries to parse the configuration, which requires loading requests, and receives the warning before finishing parsing, so it errors.

```
ERROR: while parsing the following warning configuration:
                                                                                                                                                                                                                                                                                                     
  ignore::requests.exceptions.RequestsDependencyWarning                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                     
This error occurred:                                                                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                                                                     
Traceback (most recent call last):                                                                                                                                                                                                                                                                   
  File "requests\__init__.py", line 109, in <module>                                                                                                                                                                                                     
    check_compatibility(                                                                                                                                                                                                                                                                             
    ~~~~~~~~~~~~~~~~~~~^                                                                                                                                                                                                                                                                             
        urllib3.__version__, chardet_version, charset_normalizer_version                                                                                                                                                                                                                             
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^                                                                                                                                                                                                                             
    )                                                                                                                                                                                                                                                                                                
    ^                                                                                                                                                                                                                                                                                                
  File "requests\__init__.py", line 79, in check_compatibility                                                                                                                                                                                           
    assert (3, 0, 2) <= (major, minor, patch) < (6, 0, 0)                                                                                                                                                                                                                                            
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^                                                                                                                                                                                                                                            
AssertionError                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                     
During handling of the above exception, another exception occurred:                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                                                                                     
Traceback (most recent call last):                                                                                                                                                                                                                                                                   
  File "_pytest\config\__init__.py", line 2121, in parse_warning_filter                                                                                                                                                                                  
    category: type[Warning] = _resolve_warning_category(category_)                                                                                                                                                                                                                                   
                              ~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^                                                                                                                                                                                                                                   
  File "_pytest\config\__init__.py", line 2168, in _resolve_warning_category                                                                                                                                                                             
    m = __import__(module, None, None, [klass])                                                                                                                                                                                                                                                      
  File "requests\__init__.py", line 113, in <module>                                                                                                                                                                                                     
    warnings.warn(                                                                                                                                                                                                                                                                                   
    ~~~~~~~~~~~~~^                                                                                                                                                                                                                                                                                   
        "urllib3 ({}) or chardet ({})/charset_normalizer ({}) doesn't match a supported "                                                                                                                                                                                                            
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^                                                                                                                                                                                                            
    ...<3 lines>...                                                                                                                                                                                                                                                                                  
        RequestsDependencyWarning,                                                                                                                                                                                                                                                                   
        ^^^^^^^^^^^^^^^^^^^^^^^^^^                                                                                                                                                                                                                                                                   
    )                                                                                                                                                                                                                                                                                                
    ^                                                                                                                                                                                                                                                                                                
requests.exceptions.RequestsDependencyWarning: urllib3 (2.6.3) or chardet (7.2.0)/charset_normalizer (3.4.6) doesn't match a supported version!   
```

Instead I have to use a hacky string matching

```toml
[tool.pytest.ini_options]
filterwarnings = [
    # https://docs.pytest.org/en/stable/how-to/capture-warnings.html#controlling-warnings
    # When a warning matches more than one option in the list, the action for the last matching option is performed.
    "error", # Implicitly coerce all non-fatal warnings into fatal exceptions.
    "ignore:.*urllib3.*doesn't match a supported version!:",
]
```

### Response 6
> The fact that the warning is emitted on `requests.__init__` means that the obvious way of suppressing warnings in pytest doesn't work, which is unfortunate.
> 
> I have something like this in my pyproject.toml
> 
> [tool.pytest.ini_options]
> filterwarnings = [
>     # https://docs.pytest.org/en/stable/how-to/capture-warnings.html#controlling-warnings
>     # When a warning matches more than one option in the list, the action for the last matching option is performed.
>     "error", # Implicitly coerce all non-fatal warnings into fatal exceptions.
>     "ignore::requests.exceptions.RequestsDependencyWarning",
> ]
> When running pytest it tries to parse the configuration, which requires loading requests, and receives the warning before finishing parsing, so it errors.
> 
> ```
> ERROR: while parsing the following warning configuration:
>                                                                                                                                                                                                                                                                                                      
>   ignore::requests.exceptions.RequestsDependencyWarning                                                                                                                                                                                                                                              
>                                                                                                                                                                                                                                                                                                      
> This error occurred:                                                                                                                                                                                                                                                                                 
>                                                                                                                                                                                                                                                                                                      
> Traceback (most recent call last):                                                                                                                                                                                                                                                                   
>   File "requests\__init__.py", line 109, in <module>                                                                                                                                                                                                     
>     check_compatibility(                                                                                                                                                                                                                                                                             
>     ~~~~~~~~~~~~~~~~~~~^                                                                                                                                                                                                                                                                             
>         urllib3.__version__, chardet_version, charset_normalizer_version                                                                                                                                                                                                                             
>         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^                                                                                                                                                                                                                             
>     )                                                                                                                                                                                                                                                                                                
>     ^                                                                                                                                                                                                                                                                                                
>   File "requests\__init__.py", line 79, in check_compatibility                                                                                                                                                                                           
>     assert (3, 0, 2) <= (major, minor, patch) < (6, 0, 0)                                                                                                                                                                                                                                            
>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^                                                                                                                                                                                                                                            
> AssertionError                                                                                                                                                                                                                                                                                       
>                                                                                                                                                                                                                                                                                                      
> During handling of the above exception, another exception occurred:                                                                                                                                                                                                                                  
>                                                                                                                                                                                                                                                                                                      
> Traceback (most recent call last):                                                                                                                                                                                                                                                                   
>   File "_pytest\config\__init__.py", line 2121, in parse_warning_filter                                                                                                                                                                                  
>     category: type[Warning] = _resolve_warning_category(category_)                                                                                                                                                                                                                                   
>                               ~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^                                                                                                                                                                                                                                   
>   File "_pytest\config\__init__.py", line 2168, in _resolve_warning_category                                                                                                                                                                             
>     m = __import__(module, None, None, [klass])                                                                                                                                                                                                                                                      
>   File "requests\__init__.py", line 113, in <module>                                                                                                                                                                                                     
>     warnings.warn(                                                                                                                                                                                                                                                                                   
>     ~~~~~~~~~~~~~^                                                                                                                                                                                                                                                                                   
>         "urllib3 ({}) or chardet ({})/charset_normalizer ({}) doesn't match a supported "                                                                                                                                                                                                            
>         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^                                                                                                                                                                                                            
>     ...<3 lines>...                                                                                                                                                                                                                                                                                  
>         RequestsDependencyWarning,                                                                                                                                                                                                                                                                   
>         ^^^^^^^^^^^^^^^^^^^^^^^^^^                                                                                                                                                                                                                                                                   
>     )                                                                                                                                                                                                                                                                                                
>     ^                                                                                                                                                                                                                                                                                                
> requests.exceptions.RequestsDependencyWarning: urllib3 (2.6.3) or chardet (7.2.0)/charset_normalizer (3.4.6) doesn't match a supported version!   
> ```
> 
> Instead I have to use a hacky string matching
> 
> [tool.pytest.ini_options]
> filterwarnings = [
>     # https://docs.pytest.org/en/stable/how-to/capture-warnings.html#controlling-warnings
>     # When a warning matches more than one option in the list, the action for the last matching option is performed.
>     "error", # Implicitly coerce all non-fatal warnings into fatal exceptions.
>     "ignore:.*urllib3.*doesn't match a supported version!:",
> ]

Explicitly specifying the exception type would indeed fail because attempting to import `requests` would trigger that very exception. However, you can instead indicate where the exception originates — namely, within the `requests` package itself:
```toml
[tool.pytest]
addopts = [ "-p no:legacypath" ]
filterwarnings = [
  "error",
  "ignore:urllib3 \\(.*\\) or chardet \\(.*\\)/charset_normalizer \\(.*\\) doesn't match a supported version!::requests",
]
```


