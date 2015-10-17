.PHONY : all clean cleandata replay plot

all: clean
	test -L botSettings.py || ln -s botSettingsDemo.py botSettings.py
	coverage run -p --branch --source src/ -m py.test \
        tst/PerformanceListenerTest.py tst/RetweetListenerTest.py tst/sillyTest.py
	time coverage run -p --branch --source src/ -m py.test -vv -s tst/integrationTest.py
	coverage combine && coverage report && coverage html
	pyflakes *py */*.py
	pep8 *py */*.py
	git ls-files | grep '[a-z].py' | xargs yapf -i

clean:
	find . -name '*.pyc' | xargs rm -rf 
	rm -rf htmlcov/ .coverage perfCountersTest.pydat \
        RetweetListenerTest.txt RetweetListenerTest.pydat

cleandata:
	rm -vf RetweetListener.txt RetweetListener.pydat perfCounters.pydat

replay: clean cleandata
	time coverage run --branch --source src/ replayTest.py
	coverage report && coverage html

plot:
	time python3 plotLogs.py
