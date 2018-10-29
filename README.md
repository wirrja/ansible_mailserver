<h1> Installation

<h3>Environment</h3>

* sudo apt update
* sudo apt install python3-pip
* python3 -m venv venv
* source venv/bin/activate
* pip install -r requirements.txt

<h3> Ansible </h3>

* ansible-playbook mailserver.yml

<h4> Don't forget to edit "hosts" and "group_vars/all" file</h4>

Init database and creating accounts:

smailcli initdb

smailcli adduser <user@domain.com>