#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import setuptools

from setuptools.command.build_py import build_py
from shutil import copyfile

NAME = "ciopath"
DESCRIPTION = "Object-oriented platform-transparent path manipulations."
URL = "https://github.com/ConductorTechnologies/sequence"
EMAIL = "info@conductortech.com"
AUTHOR = "conductor"
REQUIRED = ["future>=0.18.2"]
HERE = os.path.abspath(os.path.dirname(__file__))


with open(os.path.join(HERE, 'README.md')) as readme_file:
    long_description = readme_file.read()

with open(os.path.join(HERE, 'VERSION')) as version_file:
    VERSION = version_file.read().strip()

class BuildCommand(build_py):
    def run(self):
        build_py.run(self)

        if not self.dry_run:
            target_dir = os.path.join(self.build_lib, NAME)
            for fn in ["VERSION", "LICENSE", "README.md"]:
                copyfile(os.path.join(HERE, fn), os.path.join(target_dir,fn))


setuptools.setup(
    author=AUTHOR,
    author_email=EMAIL,
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python"
    ],
    cmdclass={"build_py": BuildCommand},
    description=DESCRIPTION,
    install_requires=REQUIRED,
    long_description=long_description,
    long_description_content_type="text/markdown",
    name=NAME,
    package_dir={"": "."},
    packages=setuptools.find_packages(where="."),
    options={"bdist_wheel": {"universal": True}},
    include_package_data=True, 
    url=URL,
    version=VERSION,
    zip_safe=False
)
