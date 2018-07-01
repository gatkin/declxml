"""Runs CI checks."""
import subprocess
import sys


def run_all_checks():
    """Runs the full suite of CI checks."""
    subprocess.check_call('pipenv run make prcheck', shell=True)


def run_only_tests():
    """Runs only unit tests with coverage."""
    subprocess.check_call('pipenv run make coverage', shell=True)


# Maps from Python version number to the function to run to perform the CI
# checks. Some static analysis tools do not work on all Python versions, but
# we still want to at the very least run the full test suite across all
# supported Python versions.
_PYTHON_VERSION_TO_CHECKS = {
    '2.7': run_all_checks,
    '3.4': run_only_tests,
    '3.5': run_all_checks,
    '3.6': run_all_checks,
    '3.7': run_only_tests,
}


if __name__ == '__main__':
    _PYTHON_VERSION = '{}.{}'.format(
        sys.version_info.major, sys.version_info.minor
    )

    _PYTHON_VERSION_TO_CHECKS[_PYTHON_VERSION]()
