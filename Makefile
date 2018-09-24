check:
	python -m flake8 --max-complexity 10 declxml.py
	python -m flake8 --max-complexity 10 tests/
	python -m pydocstyle --add-ignore=D105 declxml.py

coverage:
	python -m coverage run tests/run_tests.py --junit-xml=test-results.xml
	# A few lines only run depending on whether it is Python 2 or Python 3
	python -m coverage xml --fail-under=99 -o coverage.xml
	python -m coverage html
	python -m coverage report

docbuild:
	$(MAKE) -C docs html

doccheck: docbuild
	doc8 docs/*.rst

html-coverage:
	python -m coverage run tests/run_tests.py
	python -m coverage html
	rm -rf /tmp/htmlcov && mv htmlcov /tmp/
	open /tmp/htmlcov/index.html

html-doc: docbuild
	open docs/_build/html/index.html

install:
	python -m pip install -U pip
	python -m pip install -U pipenv
	python -m pipenv install --dev

lint: check pylint typecheck

mutation-test:
	cosmic-ray init cosmic-ray.yml session
	cosmic-ray --verbose exec session
	cosmic-ray dump session | cr-report

package:
	python setup.py sdist

prcheck: check pylint doccheck coverage package

pylint:
	python -m pylint --rcfile .pylintrc declxml.py

test:
	python -m pytest -vv --junit-xml=test-results.xml

typecheck:
	python -m mypy declxml.py
	python -m mypy --py2 declxml.py
