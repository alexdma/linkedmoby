#!/usr/bin/env python

from setuptools import setup, find_packages


# So you can use either pip or this setup script
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(name='LinkedMoby: MobyGames Linked Data generator',
      version='0.1',
      description='Generates linked datasets out of the MobyGames video game database',
      long_description=readme,
      author='Alessandro Adamou',
      author_email='alexdma@apache.org',
      url='https://github.com/alexdma/extractor',
      license=license,
      packages=find_packages(exclude=('tests', 'docs')),
      install_requires=requirements,
)
