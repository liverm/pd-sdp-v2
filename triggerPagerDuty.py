import requests
import sys
import json
import datetime
import shutil

infile = str(sys.argv[1])
with open(infile) as data_file:
    params = json.load(data_file)
requestobj = params["request"]

print(requestobj)

# Dump the JSON to a temporary file
outfile = r"params.json"
shutil.copyfile(infile, outfile)

# Assign values from the request object fields to variables.These values can be used in constructing the JSON for creating the Change
workorderid = requestobj["WORKORDERID"]
requester = requestobj["REQUESTER"]
createdby = requestobj["CREATEDBY"]
createdtime = requestobj["CREATEDTIME"]
requesttype = requestobj["REQUESTTYPE"]
status = requestobj["STATUS"]
level = requestobj["LEVEL"]
group = requestobj["GROUP"]
servicecategory = requestobj["SERVICE"]
category = requestobj["CATEGORY"]
subcategory = requestobj["SUBCATEGORY"]
item = requestobj["ITEM"]
impact = requestobj["IMPACT"]
impactdetails = requestobj["IMPACTDETAILS"]
priority = requestobj["PRIORITY"]
urgency = requestobj["URGENCY"]
sla = requestobj["SLA"]
subject = requestobj["SUBJECT"]
description = requestobj["DESCRIPTION"]
shortdescription = requestobj["SHORTDESCRIPTION"]

# Create human readable incident creation time
creationtime = datetime.datetime.fromtimestamp(
    int(createdtime) / 1e3).strftime("%d %b %Y, %H:%M:%S")

routing_key = "<INSERT ROUTING KEY HERE>"
dedup_key = "SDP-" + workorderid
url = "https://events.pagerduty.com/v2/enqueue"

header = {
    "Content-Type": "application/json"
}

payload = {
    "payload": {
        "summary": subject,
        "severity": "critical",
        "source": subcategory,
        "component": category,
        "group": group,
        "class": servicecategory,
        "custom_details": {
            "description": shortdescription,
            "requesttype": requesttype,
            "requester": requester,
            "createdby": createdby,
            "createdtime": creationtime,
            "status": status,
            "level": level,
            "group": group,
            "servicecategory": servicecategory,
            "category": category,
            "subcategory": subcategory,
            "item": item,
            "impact": impact,
            "impactdetails": impactdetails,
            "priority": priority,
            "urgency": urgency,
            "sla": sla
        }
    },
    "routing_key": routing_key,
    "dedup_key": dedup_key,
    "event_action": "trigger",
    "client": "ManageEngine ServiceDesk Plus",
    "client_url": "http://localhost:8080/WorkOrder.do?woMode=viewWO&woID=" + workorderid
}

response = requests.post(url, data=json.dumps(payload), headers=header)

if response.json()["status"] == "success":
    print('Incident Created')
else:
    print(response.text)  # print error message if not successful
