#!/usr/bin/env python

from distutils.core import setup, Command
from unittest import TextTestRunner, TestLoader
import wpolyanna.test

cmdclasses = dict()

class TestCommand(Command):
    """ Run unit tests """

    user_options = []
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        loader = TestLoader()
        t = TextTestRunner()
        t.run(loader.loadTestsFromModule(wpolyanna.test))

cmdclasses['test'] = TestCommand

setup(cmdclass = cmdclasses,
      name="WPolyanna",
      version="0.1",
      author="Paidi Creed",
      author_email="paidi.work@gmail.com",
      packages=["wpolyanna"],
      package_dir={"wpolyanna":"wpolyanna"},      
      requires=["cdd","pulp"])
