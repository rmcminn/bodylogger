from setuptools import setup, find_packages
setup(
    name="bodylogger",
    version="0.8.0",
    packages=find_packages(),
    install_requires=[
        "click",
        "numpy",
        "pandas",
        "matplotlib",
        "statsmodels",
        "colorama"
    ],
    entry_points={
        'console_scripts': [
            'bodylogger = bodylogger.bodylogger:bodylogger',
        ],
    },

    # metadata
    author="Ryder McMinn",
    author_email="mcminnra@gmail.com",
    description="Maintains a database of body weight measurements while giving stats and predictions based on trends.",
    license="MIT",
    keywords="weight body logger fitness health statistics tracking tracker",
    url="https://github.com/rmcminn/bodylogger",
)
