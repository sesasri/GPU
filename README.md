# Changing RDMA IP Range for GPU

## RDMA Config Details

The RDMA configuration is maintained in "/etc/oracle-cloud-agent/plugins/oci-hpc/oci-hpc-configure/rdma_network.json" file.

## CIDR Range Requirements

The minimum CIDR size should be 4 times that of the VCN Range. If the VCN CIDR Range is /16, the RDMA CIDR should be /12

## Changing CIDR Range to avoid duplication

The configuration is maintqined in "/etc/oracle-cloud-agent/plugins/oci-hpc/oci-hpc-configure/rdma_network.json" 

Below block refers to the default settings 

```
"default-settings": {
            "rdma_network": "**10.224.0.0/12**",
            "overwrite_config_files": false,
            "single_subnet": true,
            "modify_subnet": true,
            "modify_arp": true
        },
        "subnet-settings": {
            "netmask": "**255.240.0.0**",
            "override_netconfig_netmask": "**255.240.0.0**"
        },
```

Depending on the VCN size, the RDMA network can be changed to ensure it does not conflict with the existing CIDR range.

## Activating the updated RDMA block

Once the RDMA CIDR and network/override netmask are changed to desired value, run the below command

**snap restart oracle-cloud-agent**

Validate the changes are in effect by running ip addr 

Please note that the existing workload on the GPU node could get impacted.

## Validate IP address change ##

```
for i in {0..15};
do
   rdmaip=$(ip addr show dev rdma$i|egrep inet|egrep -v inet6 |awk '{print $2}');echo $rdmaip ;
done

```

