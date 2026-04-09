# Q: `NOTICE` file missing in wheel
**Source:** https://github.com/psf/requests/issues/7034

## The Problem / Request
The notice files is missing in wheels although (afaik) it is required to include it due to the APACHE license and it seemed to be the intention of the authors to include it:

https://github.com/psf/requests/blob/420d16bc7ef326f7b65f90e4644adc0f6a0e1d44/setup.py#L69

(This line has no effect because `LICENSE` and `NOTICE` are not located in the package folder.)

There is already #7012, which fixes the issue (and also includes `AUTHORS.txt`). If changing the build-backend (or just switching to pyproject.toml) is not imminent, please let me know if you want me to create a PR to fix the issue with minimal changes to `setup.py`/`setup.cfg`.

## The Solution / Discussion
### Response 1
I can fix this with a minimal PR! The issue is that `package_data` in setup.py looks for files inside the package directory (`src/requests/`), but LICENSE and NOTICE are in the root.

**Proposed fix:**
1. Move LICENSE, NOTICE, and AUTHORS.txt into `src/requests/`
2. Update `package_data` to: `{"requests": ["LICENSE", "NOTICE", "AUTHORS.txt"]}`

This will ensure the files are included in wheel packages without changing the build system.

@maintainers Should I proceed with this approach?

### Response 2
I just created #7046.

@tommasobaiocchi I think your proposal may not lead to the desired result: If I do not miss anything, the license files would be put into the package itself. However, they should be put into the `dist-info` directory.

### Response 3
@radoering Thanks for the correction and for creating #7046! You're right - the files need to go in the dist-info directory, not the package itself.

I'll follow your PR to learn the proper approach for including license files in Python packages.

### Response 4
This should be addressed in the [pyproject.toml](https://github.com/psf/requests/blob/47914226c2968802f2cdee3f6f0f6e06e4472f64/pyproject.toml#L64-L65).  The omission of the NOTICE wasn't intentional for the wheel distribution but the AUTHORS.rst was. Generally, that's only included in the sdist and source repo. I think we can close this as completed.

