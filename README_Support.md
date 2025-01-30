# OCI Support Requests can be created with OCI APIs, OCI SDK or OCI CLI

## Creating Support Requests with OCI CLI 

oci support incident create \
                    --compartment-id ocid1.tenancy.oc1..aaaaaaaaubrkzed3mXXXnfgmcmoh5mm7XXXXX --description "test this is for demo" \
                    --csi <CSI#> \
                    --problem-type "TECH" \
                    --severity "MEDIUM" \
                    --title "Test Support Request Broken Node blah for demo" \
                    --homeregion us-ashburn-1 --ocid ocid1.user.oc1..aaaaaaaanclxin4XXXXxxjy5jgkroipp36xiq56s4q \
                    --region us-ashburn-1

### Use the Support Management CLI to manage support requests with oci support call 

   Options available are
         • incident
         • create
         • get
         • list
         • update
       • incident-resource-type
         • list
       • validation-response
         • validate-user

#### Example Output is given below 
```
{
  "data": {
    "compartment-id": null,
    "contact-list": {
      "contact-list": [
        {
          "contact-email": null,
          "contact-name": null,
          "contact-phone": null,
          "contact-type": "PRIMARY",
          "email": "seshadri.dehalisan@oracle.com"
        }
      ]
    },
    "incident-type": null,
    "key": "4-0000097951",
    "problem-type": "TECH",
    "referrer": null,
    "tenancy-information": {
      "customer-support-key": "216780908",
      "tenancy-id": "ocid1.tenancy.oc1..aaaaaaaaubXXXXnfgmcmoh5mm7r6r33e3joefrayjnrmf7oa"
    },
    "ticket": {
      "description": "test this is for demo",
      "lifecycle-details": "PENDING_WITH_ORACLE",
      "lifecycle-state": "ACTIVE",
      "resource-list": null,
      "severity": "MEDIUM",
      "ticket-number": null,
      "time-created": 1731424915,
      "time-updated": 1731424915,
      "title": "Test Support Request Broken Node blah for demo"
    }
  }
}
```

### Listing Support Tickets 

 oci support incident list --compartment-id ocid1.tenancy.oc1..aaaaaaaaubrkzed3mXXXXr33e3joefrayjnrmf7oa  --csi 21450908 --ocid ocid1.user.oc1..aaaaaaaanclxin474nk5w6jtfuxxxxxpp36xiq56s4q --region us-ashburn-1 --all

```
{
  "data": [
    {
      "compartment-id": null,
      "contact-list": {
        "contact-list": [
          {
            "contact-email": null,
            "contact-name": null,
            "contact-phone": null,
            "contact-type": "PRIMARY",
            "email": "seshadri.dehalisan@oracle.com"
          }
        ]
      },
      "incident-type": null,
      "key": "4-0000097951",
      "problem-type": "TECH",
      "tenancy-information": {
        "customer-support-key": "21970908",
        "tenancy-id": "ocid1.tenancy.oc1..aaaaaaaaubrkzed3mzqxtsxx4qnfgmcmoh5mm7r6r33e3joefrayjnrmf7oa"
      },
      "ticket": {
        "description": "test this is for demo",
        "lifecycle-details": "PENDING_WITH_ORACLE",
        "lifecycle-state": "ACTIVE",
        "resource-list": null,
        "severity": "MEDIUM",
        "ticket-number": null,
        "time-created": 1731424915,
        "time-updated": 1731424915,
        "title": "Test Support Request Broken Node blah for demo"
      }
    }
  ]
}
```
## Creating Support Tickets with OCI Python-SDK
```
import oci
config = oci.config.from_file()


# Initialize service client with default config file
cims_client = oci.cims.IncidentClient(config)


# Send the request to service, some parameters are not required, see API
# doc for more info
create_incident_response = cims_client.create_incident(
    create_incident_details=oci.cims.models.CreateIncident(
        compartment_id="ocid1.tenancy.oc1..aaaaaaaaubrkzed3mzqxtsxxxxxxxxxxoh5mm7r6r33e3joefrayjnrmf7oa",
        ticket=oci.cims.models.CreateTicketDetails(
            severity="LOW", # ['HIGHEST', 'HIGH', 'MEDIUM', 'LOW']
            title="Demo SR for Customer",
            description="No action needed, just close it"),
        problem_type="TECH", # TECH|ACCOUNT|LIMIT
        csi="21xxxxx8", # CSI Specific to Customer
        contacts=[
            oci.cims.models.Contact( # Self Explanatory
                contact_name="John Doe",
                contact_email="john.doe@joedoe.com",
                email="john.doe@oracle.com",
                contact_phone="469-000-0000",
                contact_type="ADMIN")],
        ),
    ocid="ocid1.user.oc1..aaaaaaaanclxin474nk5w6jxxxxxrhwfu3dycpnjy5jgkroipp36xiq56s4q", # User OCID should have manage any ticket in tenancy (preferably) or compartment
    homeregion="us-ashburn-1",  # Region
    )

# Get the data from response
print(create_incident_response.data)

```


## Document References

https://docs.oracle.com/en-us/iaas/api/#/en/incidentmanagement/20181231/Incident/CreateIncident
https://docs.oracle.com/en-us/iaas/api/#/en/incidentmanagement/20181231/Incident/GetIncident
https://docs.oracle.com/en-us/iaas/api/#/en/incidentmanagement/20181231/IncidentResourceType/

