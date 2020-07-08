""" 
Copyright (c) 2020 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
           https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

"""

import meraki
from webexteamssdk import WebexTeamsAPI
import credentials

api_key = credentials.api_key
access_token = credentials.access_token
room_id = credentials.room_id

# instantiating the webex and meraki objects provding the access token and API key
teamsapi = WebexTeamsAPI(access_token=access_token)
dashboard = meraki.DashboardAPI(api_key=api_key, print_console=False,output_log=False)

my_orgs = dashboard.organizations.getOrganizations()

for org in my_orgs:
    print("Org name: ", org["name"],"Org ID: ", org["id"])

input_org_id = input("Enter Organization ID: ")

networks = dashboard.organizations.getOrganizationNetworks(organizationId=input_org_id)


for network in networks:
    group_policies = dashboard.networks.getNetworkGroupPolicies(networkId=network["id"])

    group_policy_id = ""

    # declare the policy name to be provision
    provision_policy = "SmartPhone Group Policy"

    # grabbing the policy ID of interest 
    for group_policy in group_policies:
        if group_policy["name"] == provision_policy:
            group_policy_id = group_policy["groupPolicyId"]

    # grabbing all clients from the past 24 hrs (deafult)
    clients = dashboard.networks.getNetworkClients(networkId=network["id"])


    print("Printing Clients for Network ",network["name"])

    # checking the current policy for each client 
    # and 
    # applying the desired policy for all clients with operating system of Apple iPhone or Android that do not have the policy
    for client in clients:
        client_policy = dashboard.networks.getNetworkClientPolicy(networkId=network["id"],clientId=client["id"])

        if client["os"] == "Apple iPhone" or client["os"] == "Android":
            print("Mac address: ", client['mac'], " Operating System: ",client['os'])

            if client_policy["devicePolicy"] == "Group Policy" or "Normal":
                if client_policy["devicePolicy"] == "Group policy":
                    if client_policy["groupPolicyId"] != group_policy_id:
                        print("This Client does not have the correct group policy, changing policy")

                        try:
                            dashboard.networks.provisionNetworkClients(networkId=network["id"],clients=[{"clientId":client["id"],"mac":client["mac"]}],devicePolicy="Group policy",groupPolicyId=group_policy_id)
                        except Exception as e:
                            print("Error changing policy")
                            print(e)
                        try:
                            message = "policy change onto client " + client["description"] + " with policy " + provision_policy + "\n" + "Mac: " + client["mac"] + "\n" + "Operating System: " + client["os"] 
                            teamsapi.messages.create(roomId=room_id,text=message)
                        except Exception as e:
                            print("Error sending Webex Message")
                            print(e)
                else:
                    try:
                        dashboard.networks.provisionNetworkClients(networkId=network["id"],clients=[{"clientId":client["id"],"mac":client["mac"]}],devicePolicy="Group policy",groupPolicyId=group_policy_id)
                    except Exception as e:
                        print("Error changing policy")
                        print(e)
                    
                    try:
                        message = "policy change onto client " + client["description"] + " with policy " + provision_policy + "\n" + "Mac: " + client["mac"] + "\n" + "Operating System: " + client["os"] 
                        teamsapi.messages.create(roomId=room_id,text=message)
                    except Exception as e:
                        print("Error sending Webex Message")
                        print(e)