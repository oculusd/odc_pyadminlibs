from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='odc_pyadminlibs',  # Required
    version='0.0.3',  # Required
    description='OculusD Python Admin Library',  # Optional
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    url='https://www.oculusd.com/',  # Optional
    author='OculusD',  # Optional
    author_email='info@oculusd.com',  # Optional
    classifiers=[  # Optional
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='cli library iot oculusd',  # Optional
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required
    install_requires=['odc_pycommons'],  # Optional
    extras_require={  # Optional
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
    project_urls={  # Optional
        'Bug Reports': 'https://www.oculusd.com/',
        'Funding': 'https://www.oculusd.com/',
        'Say Thanks!': 'https://www.oculusd.com/',
        'Source': 'https://www.oculusd.com/',
    },
)
