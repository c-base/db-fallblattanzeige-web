#!/bin/sh

cd ansible/
ansible-playbook -i hosts site.yml
cd ..
