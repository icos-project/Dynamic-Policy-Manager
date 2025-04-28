# Usage

An [API HTTP REST](api.md) is implemented to manage the communication and the work of the Dynamic Policy Manager. 

All URIs are relative to http://localhost:8080/api/v1.

Mainly the Dynamic Policy Manager use in the first version the method get 
for to return one or all policies created, and post to create a new policies.

## API calls for the DPM

Several API endpoints are provided in this component, as shown in the following. 
For a full definition of the URL and the schema on this REST calls see the [Annexes documentation](https://www.icos-project.eu/files/deliverables/D3.2-Meta-Kernel_Layer_Module_Developed_IT-2_v1.0.pdf).

<table>
<tr style="background-color:blue;color:white;">
<td><strong>HTTP Request</strong></td>
<td><strong>Description</strong></td>
</tr>
<tr>
<td>GET/policies/{id}</td>
<td>Get a policy id</td>
</tr>
<tr>
<td>GET/policies/</td>
<td>Return the list of policies created/updated</td>
</tr>
<tr>
<td>POST/policies/</td>
<td>Add new policy</td>
</tr>
<tr>
<td>GET/policies/status</td>
<td>Read items</td>
</tr>
<tr>
<td>POST/alertmanager/</td>
<td>AlertManager Webhooks</td>
</tr>
<tr>
<td>POST/registry/icos</td>
<td>ICOS Process App descriptor </td>
</tr>
</table>

## Endpoints

### GET/registry/api/v1/policies/{id}

- *Parameters*: an authorization access token is requested as String
- *Request body* is provided from the following schema;

<table>
<tr  style="background-color:blue;color:white;">
<td><strong>AttributeName</strong></td>
<td><strong>Type</strong></td>
<td><strong>Description</strong></td>
</tr>
<tr>
<td>id</td>
<td>Long</td>
<td>Unique identifier of the deployment</td>
</tr>
</table>


### GET /registry/api/v1/policies/ 

- *Parameters*: an authorization access token is requested as String.
- No schema is provided.

### POST/registry/ap1/v1/policies/{policy}

- *Parameters*: an authorization access token is requested as String.
- *Request body* is provided from the following schema;

<table>
<tr  style="background-color:blue;color:white;">
<td ><strong>AttributeName</strong></td>
<td ><strong>Type</strong></td>
<td ><strong>Description</strong></td>
</tr>
<tr>
<td>subject</td>
<td>Subject[]</td>
<td>Provides a set of information about the type of <br>application, name of the application, component and instance</td>
</tr>
<tr>
<td>spec</td>
<td>Spec[]</td>
<td>Set of information about the template used</td>
</tr>
<tr>
<td>action</td>
<td>Action[]</td>
<td>Set of information about the action to provided.<br>[DEFAULT] is webhook.</td>
</tr>
<tr>
<td>variables</td>
<td>Variables[]</td>
<td>[OPTIONAL] addtional properties. It can a string, an integer or a number.<br>[DEFAULT] is {}.</td>
</tr>
<tr>
<td>properties</td>
<td>Properties[]</td>
<td>[OPTIONAL] additional properties [DEFAULT] is {}.</td>
</tr>
</table>

**Subject[]**
<table>
<tr  style="background-color:blue;color:white;">
<td><strong>AttributeName</strong></td>
<td><strong>Type</strong></td>
<td><strong>Description</strong></td>
</tr>
<tr>
<td>type</td>
<td>const</td>
<td>Default is "app" <p> Name of app </td>
</tr>
<td>appName</td>
<td>String</td>
<td>Name of app </td>
</tr>
<tr>
<td>appComponent</td>
<td>String</td>
<td>Component of app</td>
</tr>
<tr>
<td>appInstance</td>
<td>String</td>
<td>Instance of app</td>
</tr>
</table>

**Spec[]**
<table>
<tr style="background-color:blue;color:white;">
<td><strong>AttributeName</strong></td>
<td><strong>Type</strong></td>
<td><strong>Description</strong></td>
</tr>
<tr>
<td>type<p>description</td>
<td>String</td>
<td>[DEFAULT] is empty</td>
</tr>
<tr>
<td>type</td>
<td>Const</td>
<td>[DEFAULT] is template</td>
</tr>
<tr>
<td>templateName</td>
<td>String</td>
<td>Name of template</td>
</tr>
</table>

Http methods from the following RFCs are all observed:

- **RFC 7231**: Hypertext Transfer Protocol (HTTP/1.1), obsoletes 2616
- **RFC 5789**: PATCH Method for HTTP

Allowed values are : ***CONNECT***, ***DELETE***, ***GET***, ***HEAD***, ***OPTIONS***, 
***PATCH***, ***POST***,***PUT***, ***TRACE***.

**Variables[]**
<table>
<tr style="background-color:blue;color:white;">
<td><strong>AttributeName</strong></td>
<td><strong>Type</strong></td>
<td><strong>Description</strong></td>
</tr>
<tr>
<td>#0</td>
<td>String</td>
<td>[OPTIONAL]</td>
</tr>
<tr>
<td>#1</td>
<td>integer</td>
<td>[OPTIONAL]</td>
</tr>
<tr>
<td>#2</td>
<td>number</td>
<td>[OPTIONAL]</td>
</tr>
</table>

**Properties[]**
<table>
<tr style="background-color:blue;color:white;">
<td><strong>AttributeName</strong></td>
<td><strong>Type</strong></td>
<td><strong>Description</strong></td>
</tr>
<tr>
<td>oneoff</td>
<td>boolean</td>
<td>boolean</td>
</tr>
<tr>
<td>interval</td>
<td>String</td>
<td>Interval where the policy should be acts</td>
</tr>
<tr>
<td>pendingInterval </td>
<td>String</td>
<td>Information about the interval status</td>
</tr>
</table>

### POST/registry/api/v1/icos/

- *Parameters*: authorization access token
- *Request body* is provided from the following schema:

<table>
<tr style="background-color:blue;color:white;">
<td><strong>AttributeName</strong></td>
<td><strong>Type</strong></td>
<td><strong>Description</strong></td>
</tr>
<tr>
<td>app_descriptor</td>
<td>App_descriptor[]</td>
<td>Object that provided a set of information.</td>
</tr>
<tr>
<td>app_instance</td>
<td>String</td>
<td>Instance name of the app descriptor.</td>
</tr>
<tr>
<td>common_action </td>
<td>Common_action[]</td>
<td>Object that provides a set of information about the service, specifically for the icos-service.</td>
</tr>
<tr>
<td>service </td>
<td>String</td>
<td>name of the service</td>
</tr>
</table>

**app_descriptor[]**
<table>
<tr style="background-color:blue;color:white;">
<td><strong>AttributeName</strong></td>
<td><strong>Type</strong></td>
<td><strong>Description</strong></td>
</tr>
<tr>
<td>name</td>
<td>String</td>
<td>Name of the app descripton</td>
</tr>
<tr>
<td>description</td>
<td>String</td>
<td>[DEFAULT] is “”.</td>
</tr>
<tr>
<td>components </td>
<td>Components[]</td>
<td>Object that providesa a set of information about.</td>
</tr>
<tr>
<td>policies</td>
<td>Policies[]</td>
<td>Object that provided a set of information about the policies</td>
</tr>
</table>

**Component[]**
<table>
<tr style="background-color:blue;color:white;">
<td><strong>name</strong></td>
<td><strong>Name of the component</strong></td>
<td><strong>Object that provided a set of information.</strong></td>
</tr>
<tr>
<td>type</td>
<td>String</td>
<td>Type of the component</td>
</tr>
<tr>
<td>policies</td>
<td>policies[]</td>
<td>Array Object that providesa a set of information about the policies for the icos service.. [DEFAULT ] is empty : []</td>
</tr>
</table>

**Policies[]**
<table>
<tr style="background-color:blue;color:white;">
<td><strong>name</strong></td>
<td><strong>Name of the component</strong></td>
<td><strong>Object that provided a set of information.</strong></td>
</tr>
<tr>
<td>name</td>
<td>string</td>
<td>Name of the policies</td>
</tr>
<tr>
<td>component</td>
<td>string</td>
<td>It can be Null</td>
</tr>
<tr>
<td>fromTemplate</td>
<td>string</td>
<td>It can be null</td>
</tr>
<tr>
<td>spec</td>
<td>Spec[]</td>
<td>Object provides a set of information about policies template, telemetry and constraints.</td>
</tr>
<tr>
<td>remediation</td>
<td>string</td>
<td>It can be null</td>
</tr>
<tr>
<td>variables</td>
<td>Variables[]</td>
<td>[DEFAULT] is {}</td>
</tr>
<tr>
<td>properties</td>
<td>Properties[]</td>
<td>[DEFAULT] is {}</td>
</tr>
</table>

**common_action[]**
<table>
<tr style="background-color:blue;color:white;">
<td>Attribute Name</td>
<td>Type</span></td>
<td>Description</td>
</tr>
<tr>
<td>uri</td>
<td>String</td>
<td>Link to the alermanager</td>
</tr>
<tr>
<td>type</td>
<td>Const</td>
<td>[DEFAULT] is &ldquo;icos-service&rdquo;</td>
</tr>
<tr>
<td>httpMethod</td>
<td>String</td>
<td>[DEFAULT] is &ldquo;CONNECT&rdquo;</td>
</tr>
<tr>
<td>extraParams</td>
<td>[]</td>
<td>Additional properties. [DEFAULT] is empty {}</td>
</tr>
<tr>
<td>includeAccessToken</td>
<td>boolean</td>
<td>Token to acces to the webhook, default is FALSE</td>
</tr>
</table>

### POST/watcher/api/v1/webhooks/alertmanager
- **Parameters**: access token
<table>
<tr style="background-color:blue;color:white;">
<td>Attribute Name</td>
<td>Type</td>
<td>Description</td>
</tr>
<tr>
<td>version</td>
<td>String</td>
<td>&nbsp;</td>
</tr>
<tr>
<td>groupKey</td>
<td>string</td>
<td>&nbsp;</td>
</tr>
<tr>
<td>truncatedAlerts</td>
<td>0</td>
<td>&nbsp;</td>
</tr>
<tr>
<td>status</td>
<td>String</td>
<td>&nbsp;</td>
</tr>
<tr>
<td>receiver</td>
<td>String</td>
<td>&nbsp;</td>
</tr>
<tr>
<td>groupLabels</td>
<td>GroupLabels[]</td>
<td>[DEFAULT] is {}</td>
</tr>
<tr>
<td>commonLabels</td>
<td>CommonLabels[]</td>
<td>DEFAULT] is {}</td>
</tr>
<tr>
<td>commonAnnotations</td>
<td>CommonAnnotations[]</td>
<td>DEFAULT] is {}</td>
</tr>
<tr>
<td>externalURL</td>
<td>string</td>
<td>&nbsp;</td>
</tr>
<tr>
<td>alerts</td>
<td>AlertsArray&lt;object&gt;</td>
<td>Array Object provides items as status, label, ... </td>
</tr>
</table>

**Grouplabels[]**
<table>
<tr style="background-color:blue;color:white;">
<td>Attribute Name</span></td>
<td>Type</td>
<td>Description</td>
</tr>
<tr>
<td>Additional properties</td>
<td>String</td>
<td>[DEFAULT] : {}</td>
</tr>
</table>

**CommonLabels[]**
<table>
<tr style="background-color:blue;color:white;">
<td>Attribute Name</td>
<td>Type</td>
<td>Description</td>
</tr>
<tr>
<td>Additional properties</td>
<td>String</td>
<td>[DEFAULT] : {}</td>
</tr>
</table>

**CommonAnnotations[]**
<table>
<tr style="background-color:blue;color:white;">
<td>Attribute Name</td>
<td>Type</td>
<td>Description</td>
</tr>
<tr>
<td>Additional properties</td>
<td>String</td>
<td>[DEFAULT] : {}</td>
</tr>
</table>

**Alerts[]**
<table>
<tr style="background-color:blue;color:white;">
<td>Attribute Name</td>
<td>Type</td>
<td>Description</td>
</tr>
<tr>
<td>Items</td>
<td>Items[]</td>
<td>-</td>
</tr>
</table>

**Items []**
<table>
<tr style="background-color:blue;color:white;">
<td>Attribute Name</td>
<td>Type</td>
<td>Description</td>
</tr>
<tr>
<td>status</td>
<td>String</td>
<td>It can be null</td>
</tr>
<tr>
<td>labels</td>
<td>Labels[]</td>
<td>Additional properties</td>
</tr>
<tr>
<td>annotations</td>
<td>Annotations[]</td>
<td>Additional properties</td>
</tr>
<tr>
<td>startsAt</td>
<td>String</td>
<td>It provides the date-times when the policies started.</td>
</tr>
<tr>
<td>endsAt</td>
<td>String</td>
<td>It provides the date-time when the policies ended.</td>
</tr>
<tr>
<td>generatorUrl</td>
<td>String</td>
<td>Url of the generator</td>
</tr>
<tr>
<td>fingerprint</td>
<td>String</td>
<td>It can be null.</td>
</tr>
</table>

**Labels**
<table>
<tr style="background-color:blue;color:white;">
<td>Attribute Name</td>
<td>Type</td>
<td>Description</td>
</tr>
<tr>
<td>Additional properties</td>
<td>String</td>
<td>[DEFAULT] : {}</td>
</tr>
</table>

**Annotations[]**
<table>
<tr style="background-color:blue;color:white;">
<td>Attribute Name</td>
<td>Type</td>
<td>Description</td>
</tr>
<tr>
<td>Additional properties</td>
<td>String</td>
<td>[DEFAULT] : {}</td>
</tr>
</table>

## GET/status/
- **Parameters**: access token

## Reference
Designed and architecture refer to the deliverable [D3.1 Meta-kernel Layer Module Developed (IT-1)](https://www.icos-project.eu/files/deliverables/D3.1_Meta_Kernel_Module_IT-1_v1.0.pdf) provides about the implementation.
API models and how to work refer to the deliverable [D3.2 Metakernel Layer Module Develope (IT-2)](https://www.icos-project.eu/files/deliverables/D3.2-Meta-Kernel_Layer_Module_Developed_IT-2_v1.0.pdf)
