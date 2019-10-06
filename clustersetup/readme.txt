To run this script you will need :

- Linux server
- Ansible installed
- NetApp Ansible Modules
- ONTAP 9.6+
- Run the nodemgmt setup (only setting an IP - not cluster wizzard)

python cluster_install_RESTv2.py clustersetup_light2.json

The script will :

- Create the cluster based on REST Api
- Modify the cluster_mgmt lif to match a custom port
- Add a second node to the cluster
- launch ansible Elbit Playbook located in /opt/ansible-playbook/

Njoy 