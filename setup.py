from setuptools import setup, find_packages

setup(
    name="datalint",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "click>=8.0.0",
        "pyyaml>=6.0"
    ],
    entry_points={
        'console_scripts': [
            'datalint=datalint.cli:main',
        ],
    },
)