#!/usr/bin/env python
import base64
import click
import datetime
import getpass
import hashlib
import os
from sqlalchemy import create_engine, Column, DateTime, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import exists, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import create_database, database_exists

DOMAIN = "wirr.ru"
PSGSQL_URI = "postgresql://user:password@0.0.0.0/test"


def warnings(warn):
    return {
        "db_not_found": lambda: print(
            "Database doesn't exists or not available, please use --help to create database and tables\n"
        ),
        "db_created": lambda: print(
            "Database created, you can work with accounts, see --help\n"
        ),
        "db_already_exists": lambda: print(
            "Database already exists, you can work with accounts, see --help\n"
        ),
        "tb_not_found": lambda: print(
            "Tables are not created, please use --initdb to create tables\n"
        ),
        "tb_exists": lambda: print(
            "Tables are created, you can work with accounts, see --help\n"
        ),
        "usr_not_found": lambda: print(
            "User not found in database, you can create new user by --adduser <USERNAME> <MAILDIR>\n"
        ),
        "usr_already_exists": lambda: print(
            "User already in database, you can create new user by --adduser <USERNAME> <MAILDIR>\n"
        ),
        "usr_created": lambda: print("Acount created\n"),
        "maildir_already_exists": lambda: print(
            "This mail directory already exists! Please recreate user by --adduser <USERNAME> <MAILDIR>\n"
        ),
        "pwd_neq": lambda: print("Passwords don't match, please try again\n"),
    }.get(warn, lambda: None)()


Base = declarative_base()
try:
    engine = create_engine(PSGSQL_URI)
    conn = engine.connect()
except:
    warnings("db_not_found")


def create_tables():
    try:
        Base.metadata.create_all(engine)
        warnings("tb_exists")
    except:
        warnings("tb_not_found")


def init_database():
    if database_exists(PSGSQL_URI):
        warnings("db_already_exists")
    else:
        create_database(PSGSQL_URI)
        warnings("db_created")

    if not engine.dialect.has_table(engine, "users"):
        warnings("tb_not_found")
        create_tables()


Session = sessionmaker(bind=engine)
session = Session()


class Alias(Base):
    __tablename__ = "aliases"
    id = Column(Integer, primary_key=True)
    alias = Column(String(64), nullable=False)
    email = Column(String(64), nullable=False)

    def __repr__(self):
        return "<Alias(id='%s', email='%s')>" % (self.id, self.email)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(64), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    maildir = Column(String(32), unique=True, nullable=False)
    created = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return (
            "<User)id='%s', email='%s', password='%s', maildir='%s', created='%s')>"
            % (self.id, self.email, self.password, self.maildir, self.created)
        )


def convert_password(password):
    salt = os.urandom(5)
    sha = hashlib.sha512()
    sha.update(password.encode())
    sha.update(salt)
    ssha512 = base64.b64encode(sha.digest() + salt)
    hash_password = "{{SSHA512}}{}".format(ssha512.decode())
    return hash_password


def create_account(username, hash_password, maildir):
    user = User(email=username, password=hash_password, maildir=maildir)
    if session.query(exists().where(User.email == username)).scalar():
        warnings("usr_already_exists")
    elif session.query(exists().where(User.maildir == maildir)).scalar():
        warnings("maildir_already_exists")
    else:
        session.add(user)
        session.commit()
        warnings("usr_created")


@click.group()
def cli():
    pass


@click.command(help="create database and tables or check for existence")
def initdb():
    click.echo("Checking databases")
    init_database()
    create_tables()


@click.command(help="create new account: adduser <USERNAME> <MAILDIR>")
@click.argument("username")
@click.argument("maildir")
def adduser(username, maildir):
    click.echo("Add new user " + username.lower())
    password1 = getpass.getpass("Enter password: ")
    password2 = getpass.getpass("Retype password: ")
    if password2 == password1:
        hash_password = convert_password(password2)
        email = str("{}@{}".format(username, DOMAIN)).lower()
        maildir = str("{}/".format(maildir)).lower()
        create_account(username=email, hash_password=hash_password, maildir=maildir)
    else:
        warnings("pwd_neq")


@click.command(help="print all accounts (email, maildir, when created), no argumens")
def show_users():
    for instance in session.query(User).order_by(User.id):
        print(instance.email, instance.password, instance.maildir, instance.created)


cli.add_command(initdb)
cli.add_command(show_users)
cli.add_command(adduser)
cli()
