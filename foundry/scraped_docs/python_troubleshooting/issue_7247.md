# Q: New chardet version
**Source:** https://github.com/psf/requests/issues/7247

## The Problem / Request
I apologise in advance for what may be a complete non-issue. I do not have the skills or the time to comb through the chardet codebase for potential backdoors.

The chardet project has recently released a new version(7) that was "rewritten from the ground up". Although most of the buzz around this is about the license changing from LGPL to MIT, I am concerned that a trusted component of practically every python internet-connected application has been swapped out for a completely new codebase. And it seems requests has accepted this by bumping the chardet version requirement to < 8.0.

If someone wanted to compromise every python app in the world, backdooring chardet would seem to be a great solution, given it processes every piece of user data. Making an incremental change to do this would risk easy discovery, so claiming a complete rewrite makes verification a massively harder (and therefore more unlikely) job.

I really hope someone smarter than me can explain why this could not happen. Otherwise it would seem prudent to move the chardet version requirement back to < 7.0 until chardet has been reliably vetted.

## The Solution / Discussion
### Response 1
Hi @foxylad, I'm not going to weigh into the issue open in chardet currently. That said, the author of the PR has been the _sole_ author of the library in question for pretty much the entirety of Requests existence. If there was an intent to backdoor, he's had every opportunity for the entire time you (or the rest of the world) have used this project. The amount of code in question is quite small (~3000 lines) and can be audited pretty easily in a couple hours (I already read through it before we merged the PR).

I hear your concern, we're not planning a release with the new version pin until the dust settles. I don't think there's any realistic cause for alarm though in terms of code compromise.

### Response 2
In which case I apologise in retrospect as well! 

Thanks for putting my mind at rest, particularly with holding the version until the new chardet code has been examined more extensively - better safe than sorry.

### Response 3
Hi, thanks for looking into this. I've followed the chardet situation fairly closely, and when you mentioned the Chardet 7 has only 3000 lines of code, I decided to poke around the source code myself.

I noticed that Chardet 7 introduced binary files to run the models with (https://github.com/chardet/chardet/tree/main/src/chardet/models). I don't think this was the case in Chardet 6, where the models are in Python (example: https://github.com/chardet/chardet/blob/6.0.0/chardet/langenglishmodel.py).

I'm wondering how the contents of these binary files have been verified. Given the sensitivity of the library, it would be very useful if they could be independently re-created from source files.

### Response 4
@heyitsbrib this isn't the appropriate place for this discussion

### Response 5
Just to be clear, the .bin files in question _are_ auditable. They are produced from the [scripts/train.py](https://github.com/chardet/chardet/blob/main/scripts/train.py) and [scripts/confusion_training.py](https://github.com/chardet/chardet/blob/main/scripts/confusion_training.py) training files using data that is publicly available. Those files are just byte-packed bigrams/byte-maps, the contents should be deterministic as long as it's run on the same data set so content validation is straight forward. The format is also fully reversible, so looking at the contents of the file is relatively trivial.

