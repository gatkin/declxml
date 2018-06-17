coverage:
	coverage run tests/run_tests.py

coverage-report:
	coverage run tests/run_tests.py
	coverage report

coverage-html:
	coverage run tests/run_tests.py
	coverage html
	rm -rf /tmp/htmlcov && mv htmlcov /tmp/
	open /tmp/htmlcov/index.html

test:
	pytest -v
