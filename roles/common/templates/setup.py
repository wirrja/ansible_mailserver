#!/usr/bin/python3
from setuptools import setup

setup(
    name="smailcli",
    version="0.1",
    author="Denis Davydov",
    author_email="denis@wirr.ru",
    py_modules=["smailcli"],
    install_requires=["click", "sqlalchemy", "psycopg2-binary", "sqlalchemy_utils"],
    entry_points={"console_scripts": ["smailcli = smailcli:cli"]},
)
