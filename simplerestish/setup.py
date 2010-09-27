from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='simplerestish',
      version=version,
      description="A really simple interface to restish",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='restish REST',
      author='Eric Moritz',
      author_email='eric@themoritzfamily.com',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      test_suite="nose.collector",
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
