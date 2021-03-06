#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ["pip==19.0.3","Click==7.0", "Jinja2==2.10.1", "MarkupSafe==1.1.1", "PyYAML==5.1", "argh==0.26.2", "arrow==0.13.2", "binaryornot==0.4.4", "certifi==2019.3.9", "chardet==3.0.4", "cookiecutter==1.6.0", "distconfig==0.1.0", "future==0.17.1", "googleapis-common-protos==1.5.10", "grpcio==1.20.1", "idna==2.8", "jinja2-time==0.2.0", "logzero==1.5.0", "numpy==1.16.3", "opencv-python==4.1.0.25", "pathlib==1.0.1", "pathtools==0.1.2", "poyo==0.4.2", "prometheus-client==0.6.0", "python-consul==1.1.0", "python-dateutil==2.8.0", "pytoml==0.1.20", "requests==2.22.0", "scipy==1.3.0", "setuptools==40.8.0", "six==1.12.0", "ujson==1.35", "urllib3==1.25.2", "videt-dar-tools==0.1.3", "videt-grpc-interceptor==0.1.0", "videt-idl==0.17.2", "videt-protos==2.0.1", "videt-py-conf==1.0.0", "vyper-config==0.3.3", "watchdog==0.9.0", "whichcraft==0.5.2"]

setup_requirements = []

test_requirements = []

setup(
    author="ZHANG XUANRUI",
    author_email='xuanrui.zhang@videt.cn',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    description="RbIE",
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords="videt-rule-based-information-extraction",
    name="videt-rule-based-information-extraction",
    packages=find_packages(include=["v_rule_based_information_extraction", "v_rule_based_information_extraction.*"]),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url="https://git.videt.cn/zxrtt/videt-rule-based-information-extraction",
    version='1.0.0',
    zip_safe=False,
)
