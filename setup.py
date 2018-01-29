# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()


version = '0.3.0'
setup(

  name = 'screepsautospawner',

  version = version,
  packages=find_packages(),

  description = 'Automatically Respawn Screeps Player',
  long_description=long_description,
  python_requires='>=3',

  author = 'Robert Hafner',
  author_email = 'tedivm@tedivm.com',
  url = 'https://github.com/tedivm/ScreepsAutoSpawner',
  download_url = "https://github.com/tedivm/ScreepsAutoSpawner/archive/v%s.tar.gz" % (version),
  keywords = 'screeps games',

  classifiers = [
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: MIT License',

    'Intended Audience :: Developers',

    'Programming Language :: Python :: 3',
    'Environment :: Console',
  ],

  install_requires=[
    'click>=5.0,<6.0',
    'PyYAML>=3.12,<3.13',
    'requests>=2.18.0,<2.19',
    'screepsapi>=0.5.0'
  ],

  extras_require={
    'dev': [
      'pypandoc',
      'twine',
      'wheel'
    ],
  },

  entry_points={
    'console_scripts': [
      'screepsautospawner=autospawner.cli:cli',
    ],
  },

)
