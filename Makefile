.PHONY : all clean cleandata

all: clean
	test -L botSettings.py || ln -s botSettingsDemo.py botSettings.py
	coverage run -p --branch --source . -m py.test \
        PerformanceListenerTest.py RetweetListenerTest.py
	time coverage run -p --branch --source . -m py.test -vv -s integrationTest.py
	coverage combine && coverage report && coverage html
	pyflakes *py
	pep8 *py

clean:
	rm -rf __pycache__/ *.pyc htmlcov/ .coverage \
        perfCountersTest.pydat RetweetListenerTest.txt

cleandata:
	rm -vf RetweetListener.txt perfCounters.pydat
