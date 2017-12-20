.PHONY: test upload clean

install:
	mkdir -p ~/.bodylogger/users
	sudo python setup.py install
	cp -u bodylogger/users/* ~/.bodylogger/users

uninstall:
	sudo rm -rf ~/.bodylogger
	sudo pip uninstall bodylogger

test:
	nosetests -v -w bodylogger/tests/

clean:
	sudo rm -rf build dist bodylogger.egg-info
