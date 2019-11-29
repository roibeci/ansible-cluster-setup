#!/usr/bin/python3

# Authors:             David BENADIBA, Roi Becidan
# Date:                 Aug 18th, 2019
# Description:  Cluster setup on JSON input with ONTAP 9.6

from threading import Thread
import sys
import time
import json
import requests
import subprocess
import os
import urllib3

sys.path.append("./NetApp")
from NaServer import NaServer, NaElement

### Global Settings/Vars
urllib3.disable_warnings()
status_retry_count = 10

import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context


def print_usage():
    print("\nUsage: " + __file__ + " <config_file>\n")
    print("<config_file> -- JSON file with setup parameters\n")


if (len(sys.argv) != 2):
    print_usage()
    sys.exit(1)

try:
    with open(sys.argv[1]) as json_file:
        json_data = json.load(json_file)
except:
    sys.exit("JSON cloud not be loaded. Exiting NOW!")


def handle_job(s, response):
    if (response.status_code == 200):
        return "success"

    if (response.status_code == 201):
        return "success"

    elif (response.status_code == 202):
        print(response.json())
        for i in range(0, status_retry_count):
            job_details = s.get(url=s.url + response.json()["job"]["_links"]["self"]["href"])
            print(job_details.json())
            if (job_details.status_code == 200):
                if (job_details.json()["state"] == "success" or job_details.json()["state"] == "failure"):
                    break
                else:
                    time.sleep(10)
                    continue
            else:
                time.sleep(5)
                continue
        if (job_details.json()["state"] == "success"):
            return job_details.json()["state"]
        else:
            return job_details.json()["state"] + " - " + job_details.json()["message"]

    else:
        try:
            return response.json()["error"]["message"]
        except:
            return str(response.status_code) + " - undefined error"


def cluster_setup(cluster):
    print("> " + cluster["cluster-name"] + ": Creating Cluster ")

    for node in cluster["cluster-nodes"]:

        print("---> " + node["node-name"] + ": Working on node ")
        # Building Session - REST
        s = requests.Session()
        s.url = "https://{}".format(node["ip"])
        s.verify = False
        s.auth = (node["user"], node["password"])
        s.headers = {
            "Content-Type": "application/hal+json",
            "Accept": "application/hal+json"
        }

        # Building Session - ZAPI
        session = NaServer(node["ip"], 1, 140)
        session.set_server_type("Filer")
        session.set_admin_user(node["user"], node["password"])
        session.set_transport_type("HTTPS")

        # STEP: Create cluster
        if ("-01" in node["node-name"]):
            print("---> " + node["node-name"] + ": Creating cluster...")

            # create cluster API
            api = "/api/cluster"

            # creating body
            body = {
                "contact": cluster["contact"],
                "location": cluster["location"],
                "name": cluster["cluster-name"],
                "password": cluster["password"],
                "management_interface": {}
            }
            # add cluster mgmt
            for lif in cluster["net-interfaces"]:
                if (lif["role"] == "cluster-mgmt"):
                    body["management_interface"]["ip"] = {
                        "address": lif["address"],
                        "netmask": lif["netmask"]
                    }
                    for route in cluster["net-routes"]:
                        if (route["destination"] == "0.0.0.0/0"):
                            body["management_interface"]["ip"]["gateway"] = route["gateway"]
                            break
                        else:
                            continue
                    break
                else:
                    continue
            # add ntp server
            # if (cluster.get("ntp-servers")):
            #        for ntp_server in cluster["ntp-servers"]:
            #                body["ntp_servers"].append(ntp_server["server-name"])
            # add licenses
            # for ontap_license in cluster["licenses"]:
            #       body["licenses"].append(cluster["licenses"][ontap_license])

            response = s.post(url=s.url + api, data=json.dumps(body))
            print("URL==" + s.url + api)  # debug
            print("BODY==" + json.dumps(body))  # debug
            if response:
                print(response.json())
            else:
                print("NO RESPONSE FROM NODE " + body["management_interface"]["ip"] + ". Exiting..")
                sys.exit()
            status = handle_job(s, response)
            if (status == "success"):
                print("---> " + node["node-name"] + ": SUCCESS")
            else:
                print("---> " + node["node-name"] + ": " + status)
                sys.exit()

        # STEP: Reading cluster LIF IP for joining additional nodes later
        if ("-01" in node["node-name"]):
            print("--- " + node["node-name"] + ": Reading cluster LIF IP for joining further nodes later...")
            api = NaElement("net-interface-modify")
            for lif in cluster["net-interfaces"]:
                if (lif["role"] == "cluster-mgmt"):
                    api.child_add_string("home-port", lif["home-port"])
                    api.child_add_string("interface-name", "cluster_mgmt")
                    api.child_add_string("vserver", cluster["cluster-name"])
                else:
                    continue
            xo = session.invoke_elem(api)
            if (xo.results_status() == "failed"):
                print("Error:\n")
                print(xo.sprintf())
                sys.exit(1)
            print("Received:\n")
            print(xo.sprintf())
            api1 = NaElement("net-interface-revert")
            api1.child_add_string("interface-name", "cluster_mgmt")
            api1.child_add_string("vserver", cluster["cluster-name"])
            xo1 = session.invoke_elem(api1)
            if (xo1.results_status() == "failed"):
                print("Error:\n")
                print(xo1.sprintf())
                sys.exit(1)
            print("Received:\n")
            print(xo1.sprintf())
            api = "/api/network/ip/interfaces"
            url_params = "?fields=services,ip.address&services=cluster_core&max_records=1"
            response = s.get(url=s.url + api + url_params)
            status = handle_job(s, response)
            if (status == "success"):
                clus_lif_ip = response.json()["records"][0]["ip"]["address"]
                print("---> " + node["node-name"] + ": SUCCESS")
            else:
                print("---> " + node["node-name"] + ": " + status)
                sys.exit(1)

        # STEP: Join nodes to cluster
        if (not "-01" in node["node-name"]):
            print("--- " + node["node-name"] + ": Joining node to cluster...")
            zapi_post = NaElement("cluster-join")
            zapi_post.child_add_string("cluster-ip-address", clus_lif_ip)
            zapi_post_return = session.invoke_elem(zapi_post)
            if (zapi_post_return.results_status() == "failed"):
                print("---> " + node["node-name"] + ": " + zapi_post_return.sprintf().strip())
                sys.exit(1)
            else:
                zapi_get = NaElement("cluster-create-join-progress-get")
                is_complete = ""
                join_iterator = 1
                while is_complete != "true" and \
                        join_iterator < 13:
                    time.sleep(10)
                    zapi_get_return = session.invoke_elem(zapi_get)
                    is_complete = zapi_get_return.child_get("attributes").child_get(
                        "cluster-create-join-progress-info").child_get_string("is-complete")
                    action_status = zapi_get_return.child_get("attributes").child_get(
                        "cluster-create-join-progress-info").child_get_string("status")
                    join_iterator = join_iterator + 1
                if (is_complete == "true") and (action_status == "success"):
                    print("---> " + node["node-name"] + ": SUCCESS")
                else:
                    print("---> " + node["node-name"] + ": " + zapi_get.sprintf().strip())
                    print("---> " + node["node-name"] + ": " + zapi_get_return.sprintf().strip())
                    sys.exit(1)


# Start threads (install cluster by cluster)
setup_threads = []
for cluster in json_data["clusters"]:
    try:
        t = Thread(target=cluster_setup, args=(cluster,))
        t.start()
        setup_threads.append(t)
    except:
        print("> " + cluster["cluster-name"] + ": Error: Unable to start setup thread")

for x in setup_threads:
    x.join()

print("Cluster Setup Finished succesfully !! Let's Run Ansible playbook..")

os.system('rm -rf nohup.out')
#os.system('../ansible_playbook/ansible-playbook-command.sh')
os.system('nohup ansible-playbook ../ansible_playbook/tasks/main.yml  --extra-vars=@../ansible_playbook/vars/main.yml -v &')
# os.system('tail -f nohup.out')
