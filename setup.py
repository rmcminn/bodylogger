from setuptools import setup, find_packages
setup(
    name="bodylogger",
    version="0.4.1",
    packages=find_packages(),
    
    entry_points={
        'console_scripts': [
            'bodylogger = bodylogger.bodylogger:bodylogger',
        ],
    },

    # metadata
    author="Ryder McMinn",
    author_email="mcminnra@gmail.com",
    description="Command line app that logs body weight and other personal measurements.",
    license="MIT",
    keywords="weight body logger fitness health statistics tracking tracker",
    url="https://github.com/rmcminn/bodylogger",
)
