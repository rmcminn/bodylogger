.PHONY: test upload clean

build:
	sudo python setup.py build

install:
	mkdir -p ~/.bodylogger/users
	sudo python setup.py install
	cp -u bodylogger/users/* ~/.bodylogger/users

uninstall:
	sudo pip uninstall bodylogger

test:
	nosetests -v -w bodylogger/tests/

clean:
	sudo rm -rf build dist bodylogger.egg-info
