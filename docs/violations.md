
# Violation Actions

An action is triggered whenever an active policy enter into the `Violation` state. At the moment, the only implemented action is [Webhook](#webhook).

## Webhook

Send a webhook to a predefined URL. This action must be configured when the [policy is created](policies.md#policies) and accepts the following parameters:

```json
  
{
  ...
  "action": {
    "type": "webhook",
    
    "url": "https://localhost:3246/",
    "httpMethod": "POST", #a valid HTTP method
    
    # dict of custom parameters to add
    "extraParams": {
      "remediation": "scale-up",
      "another-param": "custom-value"
    },

    # whether to add a JWT token to the call obtained
    # from the configured Keycloak server
    "includeAccessToken": false
  },
  ...
}
```

When the policy is violated, an HTTP request will be made at the specified `url` with the following payload (values provided are just an example):

```json
{

    "id": "0c2f0381-b4ef-40b6-9ff0-b66ebf0ddeff",
    "currentValue": "235.365",
    "threshold": "warning",
    "policyName": "compss-low-performance-20",
    "policyId": "fd745e25-0ca3-418b-b310-257693e3f3bf",
    "measurementBackend": "prom-1",
    
    # subject of the policy that has been violated
    "subject": {
        "type": "app",
        "appName": "compss-example-app",
        "appInstance": "compss-example-app-002",
        "appComponent": "component1"
    },

    # additional labels present in the metrics. They come directly
    # from the measurement backend (i.e. Prometheus/Thanos). They are
    # all the labels remaining in the measured expression after removing
    # the ones used to match the subject
    "extraLabels": {
      "remediation": "scale-up",
      "another-param": "custom-value"
    },

    # additional static parameters added as "extraParams" during the
    # creation of the policy
    "remediation": "scale-up"
}
```
