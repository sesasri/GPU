# OCI Support Requests can be created with OCI APIs, OCI SDK or OCI CLI

## Creating Support Requests with OCI CLI 

oci support incident create \
                    --compartment-id ocid1.tenancy.oc1..aaaaaaaaubrkzed3mzqxtsxx4qnfgmcmoh5mm7XXXXX --description "test this is for demo" \
                    --csi <CSI#> \
                    --problem-type "TECH" \
                    --severity "MEDIUM" \
                    --title "Test Support Request Broken Node blah for demo" \
                    --homeregion us-ashburn-1 --ocid ocid1.user.oc1..aaaaaaaanclxin474nk5wasasyxxjy5jgkroipp36xiq56s4q \
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

## Document References

https://docs.oracle.com/en-us/iaas/api/#/en/incidentmanagement/20181231/Incident/CreateIncident
https://docs.oracle.com/en-us/iaas/api/#/en/incidentmanagement/20181231/Incident/GetIncident
https://docs.oracle.com/en-us/iaas/api/#/en/incidentmanagement/20181231/IncidentResourceType/

