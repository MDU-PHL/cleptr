"""
cleptr - a nomenclature generating tool for cgMLST clusters
"""
from sys import exit, version_info
from setuptools import setup, find_packages
from os import environ
import logging
import cleptr




with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="cleptr",
    version="0.0.1",
    description="Generate semi-consistent names for cgMLST clusters for public health",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MDU-PHL/cleptr",
    author="Kristy Horan",
    author_email="kristyhoran15@gmail.com",
    maintainer="Kristy Horan",
    maintainer_email="kristyhoran15@gmail.com",
    python_requires=">=3.7, <4",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    zip_safe=False,
    install_requires=["pandas","xlsxwriter"],
    test_suite="nose.collector",
    tests_require=["nose", "pytest"],
    entry_points={
        "console_scripts": [
            "cleptr=cleptr.cleptr:main"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: Implementation :: CPython",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    # package_data={"cleptr": ["db/*"]}
)
