#!/usr/bin/python
from setuptools import setup, find_packages
import os

EXTRAS_REQUIRES = dict(
    test=[
        'fudge>=1.1.1',
        'nose>=1.3.7',
        ],
    dev=[
        'ipython>=5.5.0',
        ],
    )

# Pypi package documentation
root = os.path.dirname(__file__)
path = os.path.join(root, 'README.rst')
with open(path) as fp:
    long_description = fp.read()

setup(
    name='pyusps',
    version='0.0.7',
    description='pyusps -- Python bindings for the USPS Ecommerce APIs',
    long_description=long_description,
    author='Andres Buritica',
    author_email='andres@thelinuxkid.com',
    maintainer='Andres Buritica',
    maintainer_email='andres@thelinuxkid.com',
    url='https://github.com/thelinuxkid/pyusps',
    license='MIT',
    packages = find_packages(),
    namespace_packages = ['pyusps'],
    test_suite='nose.collector',
    install_requires=[
        'setuptools>=0.6c11',
        'lxml>=2.3.3',
        ],
    extras_require=EXTRAS_REQUIRES,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5'
    ],
)
