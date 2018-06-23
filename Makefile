check:
	flake8 --max-complexity 10 declxml.py
	flake8 --max-complexity 10 tests/
	pydocstyle declxml.py

coverage:
	coverage run tests/run_tests.py
	# A few lines only run depending on whether it is Python 2 or Python 3
	coverage report --fail-under=99

docbuild:
	$(MAKE) -C docs html

doccheck: docbuild
	doc8 docs/*.rst
	
html-coverage:
	coverage run tests/run_tests.py
	coverage html
	rm -rf /tmp/htmlcov && mv htmlcov /tmp/
	open /tmp/htmlcov/index.html

prcheck: check pylint doccheck coverage 

pylint:
	pylint --rcfile .pylintrc declxml.py

test:
	pytest -v
