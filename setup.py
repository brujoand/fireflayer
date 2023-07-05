import os
from distutils.core import setup
VERSION = open(os.path.join(os.path.dirname(__file__),  'version')).read().strip()
setup(
    name='fireflayer',
    version=VERSION,
    license='BSD3',
    packages=['fireflayer'],
    scripts=['fireflayer.app'],
)

