from setuptools import setup, find_packages
import sys

setup(
    name='lassen',
    version='0.0.1',
    url='https://github.com/StanfordAHA/lassen',
    license='MIT',
    maintainer='Priyanka Raina',
    maintainer_email='praina@stanford.edu',
    description='PE for the CGRA written in Peak',
    packages=find_packages(),
    install_requires=[
        "peak",
        "mantle"
    ],
    python_requires='>=3.6'
)
