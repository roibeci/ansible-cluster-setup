# ansible-cluster-setup
 Ansible Cluster Setup for OnTap 9.6+


Intro & Requirements:
A 0-day cluster setup and configuration with REST and Ansible.
The scripts consists of 2 parts:
	1. Cluster Setup using REST API (supported from OnTap 9.6+). 
	2. Cluster Configuration using Ansible (supported from OnTap 9.1+)
	
To run this script you will need :

- Linux server (we've tested on CentOS 7.6)
- Ansible installed (2.6+)
- pyhton2 / pyhton3. 
- NetApp Ansible Modules (netapp-lib 2008.11.13):
	• Install using ‘pip install netapp-lib’
	• Download from: https://pypi.org/project/netapp-lib/
- ONTAP 9.6+
- Run the 'node-mgmt' setup (only setting an IP for the node mgmt. - not 'cluster setup' wizard)
- Set the admin password

Configuration files - edit this files for your cluster configuration:
-clustersetup/clustersetup_light2.json
-ansible_playbook/vars/main.yaml
