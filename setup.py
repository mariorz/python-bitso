import os
from distutils.core import setup

if os.path.exists('README.md'):
    long_description = open('README.md').read()
else:
    long_description = 'A python wrapper for the Bitso API.'

setup(
    name='python-bitso',
    version='0.1.3',
    author='Mario Romero',
    author_email='mario@romero.fm',
    packages=['bitso', 'tests'],
    url='https://github.com/mariorz/python-bitso',
    license='LICENSE.txt',
    description='A python wrapper for the Bitso API.',
    long_description=long_description,
    install_requires=[
        "requests >= 2.2.1",
    ],
)
