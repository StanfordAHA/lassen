from setuptools import setup
import sys

setup(
    name='lassen',
    version='0.0.1',
    url='https://github.com/StanfordAHA/lassen',
    license='MIT',
    maintainer='Priyanka Raina',
    maintainer_email='praina@stanford.edu',
    description='PE for the CGRA written in Peak',
    packages=[
        "lassen",
    ],
    install_requires=[
        "peak",
        "mantle"
    ],
    python_requires='>=3.6'
)
