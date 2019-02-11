from setuptools import setup
import sys

setup(
    name='whitney',
    version='0.0.1',
    url='https://github.com/StanfordAHA/whitney',
    license='MIT',
    maintainer='Priyanka Raina',
    maintainer_email='praina@stanford.edu',
    description='PE for the CGRA written in Peak',
    packages=[
        "whitney",
    ],
    install_requires=[
        "peak"
    ],
    python_requires='>=3.6'
)
