# ansible-cluster-setup
 Ansible Cluster Setup for OnTap 9.6+

Intro & Requirements:
A 0-day cluster setup and configuration with REST and Ansible.
The scripts consists of 2 playbooks:
	1. Cluster Setup using REST API (supported from OnTap 9.6+). 
	2. Cluster Configuration supported from OnTap 9.1+)
	
To run this script you will need :

- Linux server (we've tested on CentOS 7.6)
- Ansible installed (2.6+)
- pyhton3. 
- NetApp Ansible Modules (netapp-lib 2008.11.13):
	• Install using ‘pip3 install netapp-lib’
	• Download from: https://pypi.org/project/netapp-lib/
- NetApp collections:
	• sudo ansible-galaxy collection install netapp.ontap -p /usr/share/ansible/collections
- ONTAP 9.6+
- Run the 'node-mgmt' setup (only setting an IP for the node mgmt. - not 'cluster setup' wizard)
- Set the admin password

Configuration files - edit this files for your cluster configuration:
-ansible_playbook/vars/main.yaml
