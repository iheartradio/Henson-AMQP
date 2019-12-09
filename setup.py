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
    version='0.8.0',
    author='Leonard Bedner, Christian Paul, and others',
    author_email='henson@iheart.com',
    url='https://henson-amqp.readthedocs.io',
    description='A library for interacting with AMQP with a Henson application.',
    long_description=read('README.rst'),
    license='Apache License, Version 2.0',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'Henson>=1.0.0,<2.0.0',
        'aioamqp>=0.5.1,<1.0.0,!=0.14.0',
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
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ]
)
