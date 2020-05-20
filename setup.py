#!/usr/bin/env python

import io
import os
import sys
from codecs import open
from shutil import rmtree

from setuptools import setup, Command

here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()


class PublishCommand(Command):
    """Support setup.py publish."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds...')
            rmtree(os.path.join(here, 'dist'))
        except FileNotFoundError:
            pass

        self.status('Building Source and Wheel (universal) distribution...')
        os.system('{} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine...')
        os.system('twine upload dist/*')

        sys.exit()

requires = ['requests',
            'rich']
version = '0.0.1.1'


def read(f):
    return open(f, encoding='utf-8').read()

setup(
    name='simfinweb',
    version=version,
    description='SimFin API helper',
    long_description=read('README.md') + '\n\n' + read('NOTES.md'),
    author='Joseph Letts',
    author_email='git@letts.me',
    url='https://github.com/entrepreneurj/simfinweb',
    py_modules=['simfinweb'],
    package_data={'': ['LICENSE']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['simfin=simfin:cli'],
    },
    install_requires=requires,
    extras_require={
        # Nothing to see here
    },
    license="",
    zip_safe=False,
    classifiers=(
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
    ),
    cmdclass={
        'publish': PublishCommand,
    }
)