# Contributing

If you have found a bug, would like to request a new feature, or update the
documentation, please feel free to open a new [issue](https://github.com/gatkin/declxml/issues)
or submit a new [pull request](https://github.com/gatkin/declxml/pull).

## Contributing Code

All new pull requests must run cleanly through `make prcheck` which uses several
tools to perform tests and code analysis including

- [pytest](https://docs.pytest.org/en/latest/) - executes tests
- [coverage.py](https://coverage.readthedocs.io/en/latest/) - measures code coverage
- [flake8](http://flake8.pycqa.org/en/latest/) - checks for pep8 compliance and performs linting
- [doc8](https://pypi.org/project/doc8/) - checks styling of sphinx docs
- [pydocstyle](http://www.pydocstyle.org/en/latest/) - checks styling of docstrings
- [pylint](https://www.pylint.org/) - performs additional linting beyond flake8

On every commit and PR, `make prcheck` is executed as part of the [Travis CI build](https://travis-ci.org/gatkin/declxml).
Additionally, all tests are executed on Windows as part of the [Appveyor CI build](https://ci.appveyor.com/project/gatkin/declxml).

## Development Environment Setup

[Pipenv](https://docs.pipenv.org/) is used to manage dependencies. To setup up a
development environment to work with declxml, first ensure pipenv is installed

```bash
pip install pipenv
```

Then install all development dependencies

```bash
pipenv install --dev
```

Next activate the virtual environment created by pipenv

```bash
pipenv shell
```

Now you can run all tests and code analyses

```bash
make test
make prcheck
```