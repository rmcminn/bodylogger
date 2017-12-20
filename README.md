# Body Logger

Command line app that logs body weight and other personal measurements.

## Getting Started

### Prerequisites

You'll need to install tkinter, pip, and setuptools.

#### Arch

```bash
sudo pacman -S tk python-pip && sudo pip install setuptools
```

### Installing

#### Manual Installation

Download the latest release tarball from [here](https://github.com/rmcminn/bodylogger/releases), and unzip - Then run:

```bash
make install
```

This will install bodylogger and the needed python prerequisites from pip.

To uninstall, simply run:

```bash
make uninstall
```

**WARNING**: This will uninstall user database files as well. Backup `~/.bodylogger/users` if you want to retain these files.


## Running the tests (TODO)

We use [nose](http://nose.readthedocs.io/en/latest/) for our tests

To install, simply run:
```bash
sudo pip install nose
```

and then to test, run:

```bash
make test
```

tests are located in `/bodylogger/tests`

## Built With

* [Pandas](http://pandas.pydata.org/) - Used for measurement projections
* [StatsModels](http://www.statsmodels.org/stable/index.html) - Used for measurement projections
* [Click](http://click.pocoo.org/5/) - CLI Framework
* [sqlite3](https://www.sqlite.org/) - Database for user data
* [matplotlib](https://matplotlib.org/) - Plotting

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/rmcminn/bodylogger/tags).

## Authors

* **Ryder McMinn** - *Creator / Maintainer* - [rmcminn](https://github.com/rmcminn)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

* Shout out to anyone trying to be healthier
