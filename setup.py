
"""
AROUNDVISION
============

The AROUNDVISION is a tool to visualize 360 images from an API
in different projections. Additionally, it allows the user to
select some region of interest to visualize that area in more
detail.
"""

import io
import sys

from setuptools import find_packages
from distutils.core import setup

from aroundvision import __version__

# check python 3
PY3 = sys.version_info[0] == 3

# minimal python version sanity check
v = sys.version_info
if v[0] >= 3 and v[:2] < (3, 6):
    print("ERROR: Aroundvision required Python version 3.6 or above.",
          file=sys.stderr)
    sys.exit(1)

# use readme for long description
with io.open('README.md', encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()


# Setup args
setup(
    name="aroundvision",
    version=__version__,
    description='AROUNDVISION: visualize 360 images',
    long_description=LONG_DESCRIPTION,
    url='check if we can set url..',
    author='Critical Software',
    author_email='check email to set..',
    keywords='360 images PyQt5 video',
    platforms=["Windows", "Linux"],
    packages=find_packages(exclude=["*.tests", '*.tests.*']),
    include_package_data=True,
    classifiers=['Operating System :: POSIX :: Linux',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 'Intended Audience :: Science/Research',
                 'Intended Audience :: Developers',
                 'Topic :: Engineering'],
    install_requires=[],
    extras_require={'test:platform_system == "Linux"': ['pytest-xvfb'],
                    'test:platform_system == "Windows"': ['pywin32'],
                    'test': ['coverage<5.0',
                             'pytest<5.0',
                             'pytest-cov',
                             'pytest-mock',
                             'pytest-qt']},
    entry_points={
         "gui_scripts": [
             "aroundvision = aroundvision.main:main"
         ]
     },
)
