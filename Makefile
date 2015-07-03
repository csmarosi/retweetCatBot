.PHONY : all clean cleandata

all:
	test -L botSettings.py || ln -s botSettingsDemo.py botSettings.py
	python3 PerformanceListenerTest.py
	python3 RetweetListenerTest.py
	time python3 -m pytest -vv -s integrationTest.py
	pyflakes3 *py
	pep8 *py

clean:
	rm -rf __pycache__/ *.pyc perfCountersTest.pydat RetweetListenerTest.txt

cleandata:
	rm -vf RetweetListener.txt perfCounters.pydat
