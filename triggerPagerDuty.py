import requests
import sys
import json
from datetime import datetime
import shutil

# Read request data from temporary file on ServiceDesk Plus server
# infile = str(sys.argv[1])
# with open(infile) as data_file:
#     params = json.load(data_file)
# requestobj = params["request"]

# Read sample request data file from local disk - enable for testing
infile = 'sdp_test_params.json'
with open(infile) as data_file:
	params = json.load(data_file)
requestobj = params["request"]

# Dump the JSON to a temporary file - enable for debug
# outfile = r"params.json"
# shutil.copyfile(infile, outfile)

# Assign values from the request object fields to variables
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


# Set values for PagerDuty event parameters

# Set payload.summary
pd_summary = subject
if subject.strip() == "":
	pd_summary = "Not Specified"
else:
	pd_summary = subject

# Set payload.timestamp
# # Assumes that on MS Windows createdtime is the timestamp in milliseconds so need timestamp/1000
pd_timestamp = datetime.utcfromtimestamp(int(createdtime) / 1e3).isoformat("T","milliseconds") + "Z"

# Set payload.severity by mapping urgency to severity
# If Urgency is not specified in ServiceDesk Plus PagerDuty will default to High
pd_severity = "critical"
if (urgency.lower() == "urgent" or urgency.lower() == "high"):
    pd_severity = "critical"
elif (urgency.lower() == "normal" or urgency.lower() == "low"):
    pd_severity = "warning"
else:
	pd_severity = "critical"

# Set payload.source
pd_source = subcategory
if subcategory == "":
	pd_source = "Not Specified"

# Set payload.component
pd_component = category
if category == "":
	pd_component = "Not Specified"

# Set payload.group
pd_group = group
if group == "":
	pd_group = "Not Specified"

# Set and payload.class
pd_class = servicecategory
if servicecategory == "":
	pd_class = "Not Specified"

# Set routing_key
pd_routing_key = "R02A20EW6O6TFRI1QLBKB9VBC040W45B"

# Set dedup_key
# This is required for auto-resolving of incidents in PagerDuty when request is resolved in ServiceDesk Plus
pd_dedup_key = "SDP-#" + workorderid

# Set event_action based on request/inicident state
pd_event_action = "trigger"

if (status.lower() == "cancelled" or status.lower() == "closed" or status.lower() == "resolved"):
	pd_event_action = "resolve"
else:
	pd_event_action = "trigger"


# Construct JSON payload
url = "https://events.pagerduty.com/v2/enqueue"

header = {
    "Content-Type": "application/json"
}

payload = {
    "payload": {
        "summary": pd_summary,
        "severity": pd_severity,
        "source": pd_source,
        "component": pd_component,
        "group": pd_group,
        "class": pd_class,
        "custom_details": {
            "description": shortdescription,
            "requesttype": requesttype,
            "requester": requester,
            "createdby": createdby,
            "createdtime": pd_timestamp,
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
    "routing_key": pd_routing_key,
    "dedup_key": pd_dedup_key,
    "event_action": pd_event_action,
    "client": "ManageEngine ServiceDesk Plus",
    "client_url": "http://localhost:8080/WorkOrder.do?woMode=viewWO&woID=" + workorderid
}

response = requests.post(url, data=json.dumps(payload), headers=header)

if response.json()["status"] == "success":
    print('Incident Created')
else:
    print(response.text)  # print error message if not successful
