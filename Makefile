check:
	python -m flake8 --max-complexity 10 declxml.py
	python -m flake8 --max-complexity 10 tests/
	python -m pydocstyle declxml.py

coverage:
	python -m coverage run tests/run_tests.py
	# A few lines only run depending on whether it is Python 2 or Python 3
	python -m coverage report --fail-under=99

docbuild:
	$(MAKE) -C docs html

doccheck: docbuild
	doc8 docs/*.rst
	
html-coverage:
	python -m coverage run tests/run_tests.py
	python -m coverage html
	rm -rf /tmp/htmlcov && mv htmlcov /tmp/
	open /tmp/htmlcov/index.html

prcheck: check pylint doccheck coverage 

pylint:
	python -m pylint --rcfile .pylintrc declxml.py

test:
	python -m pytest -v
