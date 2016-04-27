from setuptools import find_packages, setup

from setuptools.command.test import test as TestCommand
import sys


class PyTest(TestCommand):
    def finalize_options(self):
        super().finalize_options()
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        sys.exit(pytest.main(self.test_args))


def read(filename):
    with open(filename) as f:
        return f.read()

setup(
    name='Henson-AMQP',
    version='0.5.0',
    author='Andy Dirnberger, Jon Banafato, and others',
    author_email='henson@iheart.com',
    url='https://henson-amqp.rtfd.org',
    description='A library for interacting with AMQP with a Henson application.',
    long_description=read('README.rst'),
    license='Apache License, Version 2.0',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'Henson>=1.0.0,<2.0.0',
        'aioamqp>=0.5.1,<1.0.0',
    ],
    tests_require=[
        'pytest',
        'pytest-asyncio',
    ],
    cmdclass={
        'test': PyTest,
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ]
)
