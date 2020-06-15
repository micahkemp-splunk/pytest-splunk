from setuptools import setup, find_packages

setup(
    name="splunktester",
    packages=find_packages(),
    install_requires=['splunk-sdk==1.6.13', 'colorama']
)
