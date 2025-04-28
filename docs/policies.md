
# Policies

The policies consist of three main parts:

- **Subject**: Defines the entity to which the policy applies (e.g., an application or a host).
- **Specification**: Describes the policy's details, including conditions and triggers.
- **Action**: Specifies the action to be taken when a policy violation occurs (e.g., sending a webhook).

In addition, policies can include **variables** and **properties** for further customization. 

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

The example below outlines a policy that monitors CPU usage on a specific host and triggers a webhook action 
if the usage exceeds a predefined threshold:

```json
{
  "name": "cpu_usage-for-agent",
  "subject": {
    "type": "host",
    "hostId": "57e17cac94714bf6976f1e071d64d586",
    "agentId": "icos-agent-1"
  },
  "spec": {
    "description": "Monitor CPU usage",
    "type": "telemetryQuery",
    "expr": "avg without (mode,cpu) (1 - rate(node_cpu_seconds_total{mode=\"idle\", icos_agent_id=\"icos-agent-1\", icos_host_id=\"unique_node_id\"}[2m])) > 0.5",
    "violatedIf": null,
    "thresholds": null
  },
  "action": {
    "type": "webhook",
    "url": "https://localhost:3246/",
    "httpMethod": "POST",
    "extraParams": {},
    "includeAccessToken": false
  },
  "variables": {
    "maxCpu": "0.5"
  },
  "properties": {}
}
```
