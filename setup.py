import os
from setuptools import setup, find_packages

__version__ = '0.0.1'

requirements_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'requirements.txt')
with open(requirements_path) as requirements_file:
    requirements = requirements_file.readlines()

setup(
    name='ab-metadata-publisher',
    version=__version__,
    description='Simple metadata pusher using amundsendatabuilder',
    url='',
    maintainer_email='ciwnyg0815@gmail.com',
    packages=find_packages(exclude=['tests*']),
    dependency_links=[],
    install_requires=requirements,
    python_requires=">=3.6",
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
