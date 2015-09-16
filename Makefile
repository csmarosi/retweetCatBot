.PHONY : all clean cleandata replay

all: clean
	test -L botSettings.py || ln -s botSettingsDemo.py botSettings.py
	coverage run -p --branch --source src/ -m py.test \
        tst/PerformanceListenerTest.py tst/RetweetListenerTest.py tst/sillyTest.py
	time coverage run -p --branch --source src/ -m py.test -vv -s tst/integrationTest.py
	coverage combine && coverage report && coverage html
	pyflakes *py */*.py
	pep8 *py */*.py

clean:
	find . -name '*.pyc' | xargs rm -rf 
	rm -rf htmlcov/ .coverage perfCountersTest.pydat RetweetListenerTest.txt

cleandata:
	rm -vf RetweetListener.txt perfCounters.pydat

replay: clean cleandata
	time coverage run --branch --source src/ replayTest.py | tee replayOut
	diff replayOut RetweetListener_expected.txt ; rm -f replayOut
	coverage report && coverage html && rm -f RetweetListener.txt
