****# Contributing to option

:+1::tada: First off, thanks for taking the time to contribute! :tada::+1:

## Code of Conduct

Please note that this project has a [Contributor Covenant Code of Conduct]. By
participating in this project you agree to abide by its terms. Instances of
abusive, harassing, or otherwise unacceptable behavior may be reported to the
community leaders responsible for enforcement at
[mgcummings@yahoo.com](mailto:mgcummings@yahoo.com).

## Styleguide

### Documentation

TODO

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or fewer
* Reference issues and pull requests liberally after the first line
* When only changing documentation, include `[ci skip]` in the commit title
* Consider starting the commit message with an applicable emoji from [gitmoji].
  You can find a useful cheatsheet at [kapeli].

### Python Styleguide

Please lint your code by running

```shell
ruff check
```

on all code submissions. There is a section in the `pyproject.toml` file which
will help polish the code before the CI workflow sees it and possibly starts
screaming :scream: at you.

Running

```shell
ruff format
```

as well from time to time will help keep the code consistent.


[ruff]: https://docs.astral.sh/ruff/

[Contributor Covenant Code of Conduct]: CODE_OF_CONDUCT.md

[gitmoji]: https://gitmoji.dev/

[kapeli]: https://kapeli.com/cheat_sheets/Gitmoji.docset/Contents/Resources/Documents/index
