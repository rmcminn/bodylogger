# Body Logger

Command line app that logs body weight and other personal measurements.

## Getting Started

### Prerequisites

You'll need to install tkinter, pip, and setuptools

#### Arch

```bash
sudo pacman -S tk python-pip && sudo pip install setuptools
```

### Installing

#### Manual Installation

Download the latest release tarball, and unzip - Then run:

```bash
make install
```

This will install bodylogger and the need python prerequisites from pip.

To Uninstall, simply run:

```bash
make uninstall
```

**WARNING**: This is uninstall user database files as well. Backup `~/.bodylogger/users` if you want to retain these files.


## Running the tests (TODO)

Explain how to run the automated tests for this system

### Break down into end to end tests (TODO)

Explain what these tests test and why

```
Give an example
```

### And coding style tests (TODO)

Explain what these tests test and why

```
Give an example
```

## Built With

* [Pandas](http://pandas.pydata.org/) - Used for measurement projections
* [StatsModels](http://www.statsmodels.org/stable/index.html) - Used for measurement projections
* [Click](http://click.pocoo.org/5/) - CLI Framework
* [sqlite3](https://www.sqlite.org/) - Database for user data
* [matplotlib](https://matplotlib.org/) - plotting

## Contributing (TODO)

Please read [CONTRIBUTING.md](#) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/rmcminn/bodylogger/tags).

## Authors

* **Ryder McMinn** - *Initial work* - [rmcminn](https://github.com/rmcminn)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

* Shout out to anyone trying to be healthier
