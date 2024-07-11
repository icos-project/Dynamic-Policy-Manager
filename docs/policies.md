
# Policies

A common model for expressing the policies is adopted and used to store the policies internally and to transfer
the policies in the ICOS MetaOS system. 
Specifically, a policy is made of three essential parts:

  - a subject (subject)
  - a specification (spec)
  - an action (action)

In addition we have other information as :
 - varaibles
 - properties
  
  
The group of information, for the policy, are collected in a json format file:


```json

{
	"name": "string",
	"subject": {
		"type": "app",
		"appName": "string",
		"appComponent": "string",
		"appInstance": "string"
	},
	"spec": {
		"description": "",
		"type": "template",
		"templateName": "string"
	},
	"action": {
		"type": "webhook",
		"url": "string",
		"httpMethod": "CONNECT",
		"extraParams": {},
		"includeAccessToken": false
	},
	"variables": {},
	"properties": {}
}

```

For exmaple we can create a policy with the following characteristic:

```json
policy = {
        "name": "cpu_usage-for-agent",
         "subject": {
            "type": "host",
            "hostId": "57e17cac94714bf6976f1e071d64d586",
            "agentId": "icos-agent-1"
        },
        "spec": {
            "description": "",
            "type": "telemetryQuery",
            "expr": "avg without (mode,cpu) (1 - rate(node_cpu_seconds_total{mode=\"idle\", icos_agent_id=\"icos-agent-1\", icos_host_id=\"57e17cac94714bf6976f1e071d64d586\"}[2m])) > 0.5",
            "violatedIf": None,
            "thresholds": None
        },
        "action": {
            "type": "webhook",
            "url": "https://localhost:3246/",
            "httpMethod": "POST",
            "extraParams": {},
            "includeAccessToken": False
        },
        "variables": {
            "maxCpu": "0.5"
        },
        "properties": {}
    }
```
