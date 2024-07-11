# Usage

An [API HTTP REST](api.md) is implemented to manage the communication and the work of the Dynamic Policy Manager. 

All URIs are relative to http://localhost:8080/api/v1.

Mainly the Dynamic Policy Manager use in the first version the method get for to return one or all policies created, and post to create a new policies.



| Methods          | HTTP request   | Description                                |
| ---------------- | -------------  | ------------------------------             |
| get_policy       | GET/policy_id  | Return a specific policy                   |
| list_policies    | GET/           | Return the list of policies created/updated|
| create_policies  | POST/{policy}  | Add new Policy                             |


## Reference

The  document [D3.1 Meta-kernel Layer Module Developed (IT-1)](https://www.icos-project.eu/files/deliverables/D3.1_Meta_Kernel_Module_IT-1_v1.0.pdf) provides about the implementation.


