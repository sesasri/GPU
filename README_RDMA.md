# RDMA Troubleshooting Guide for OKE on Self Managed Ubuntu Nodes (In draft)

## Assumptions

+ OKE Node has been created with self-managed Ubuntu nodes
+ Cluster Network has been created
+ Ubuntu nodes are part of the cluster network

## Basic Troubleshooting

### Ensure the nodes are part of the OKE Cluster

Logon to the operator or bastion node
Ensure bastion/operator node has OCI SDK/CLI, Kubectl installed
Ensure kubeconfig file has been created

We are just worried about RDMA capable GPU shapes. Run the below command to validate if the GPU shapes are part of the cluster

kubectl get nodes -l 'node.kubernetes.io/instance-type in (BM.GPU.H100.8, BM.GPU.A100-v2.8, BM.GPU4.8, BM.GPU.B4.8)'  -o wide

Sample Output
NAME          STATUS   ROLES    AGE   VERSION   INTERNAL-IP   EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION       CONTAINER-RUNTIME
10.0.147.26   Ready    <none>   47h   v1.29.1   10.0.147.26   <none>        Ubuntu 22.04.5 LTS   5.15.0-122-generic   cri-o://1.29.1
10.0.156.13   Ready    <none>   7d    v1.29.1   10.0.156.13   <none>        Ubuntu 22.04.5 LTS   5.15.0-122-generic   cri-o://1.29.1

Now that we have validated that you have GPU shapes as part of the OKE cluster, you can troubleshoot RDMA status further. It should be noted that the above kubectl 
can be tweaked to provide wealth of information

### Logon to the GPU Nodes

#### Back to basics

#### Run the following commands

+ ip addr
+ ip link

The above should indicate if the RDMA interfaces are available and have proper IP address, link status etc.,

You can also check the RDMA link status by running the below command

#### rdma link

#Sample output below
link mlx5_0/1 state ACTIVE physical_state LINK_UP netdev rdma0
link mlx5_1/1 state ACTIVE physical_state LINK_UP netdev rdma1
link mlx5_2/1 state ACTIVE physical_state LINK_UP netdev eth0
link mlx5_3/1 state ACTIVE physical_state LINK_UP netdev rdma2
link mlx5_4/1 state ACTIVE physical_state LINK_UP netdev rdma3
link mlx5_5/1 state ACTIVE physical_state LINK_UP netdev rdma4
link mlx5_6/1 state ACTIVE physical_state LINK_UP netdev rdma5
link mlx5_7/1 state ACTIVE physical_state LINK_UP netdev rdma6
link mlx5_8/1 state ACTIVE physical_state LINK_UP netdev rdma7s
link mlx5_9/1 state ACTIVE physical_state LINK_UP netdev rdma8
link mlx5_10/1 state ACTIVE physical_state LINK_UP netdev rdma9
link mlx5_11/1 state ACTIVE physical_state LINK_UP netdev eth1
link mlx5_12/1 state ACTIVE physical_state LINK_UP netdev rdma10
link mlx5_13/1 state ACTIVE physical_state LINK_UP netdev rdma11
link mlx5_14/1 state ACTIVE physical_state LINK_UP netdev rdma12
link mlx5_15/1 state ACTIVE physical_state LINK_UP netdev rdma13
link mlx5_16/1 state ACTIVE physical_state LINK_UP netdev rdma14
link mlx5_17/1 state ACTIVE physical_state LINK_UP netdev rdma15


### run oke commands

Run the below command to check if the bootstrap happened properly with the OKE control plane

oke bootstrap

It should provide information on the OKE config and should end with messages similar to one  shown below

INFO[2025-01-22T05:45:07Z] Updated configuration                         command=bootstrap path=/etc/systemd/system/kubelet.service.d/00-default.conf
INFO[2025-01-22T05:45:07Z] Updated configuration                         command=bootstrap path=/etc/kubernetes/kubelet-config.json
DEBU[2025-01-22T05:45:07Z] Loaded configuration                          command=bootstrap entries=9 path=/etc/proxymux/config.yaml
INFO[2025-01-22T05:45:07Z] Updated configuration                         command=bootstrap path=/etc/proxymux/config.yaml
DEBU[2025-01-22T05:45:07Z] Reloading                                     command=bootstrap task=systemd
DEBU[2025-01-22T05:45:08Z] Enabling services                             command=bootstrap services="[crio.service]" task=systemd
DEBU[2025-01-22T05:45:08Z] Starting service                              command=bootstrap service=crio.service task=systemd
DEBU[2025-01-22T05:45:08Z] Start job running                             command=bootstrap job=61893 service=crio.service task=systemd
DEBU[2025-01-22T05:45:08Z] Reloading                                     command=bootstrap task=systemd
DEBU[2025-01-22T05:45:08Z] Enabling services                             command=bootstrap services="[kubelet.service]" task=systemd
DEBU[2025-01-22T05:45:08Z] Starting service                              command=bootstrap service=kubelet.service task=systemd
DEBU[2025-01-22T05:45:08Z] Start job running                             command=bootstrap job=61983 service=kubelet.service task=systemd
DEBU[2025-01-22T05:45:08Z] Finish                                        command=bootstrap durationMs=2718

### Oracle Cloud Agent

OCA plays a major role in configuring, maintaining RDMA network.

OCA ensures WPA authentication, configuration etc.,

#### Check status of OCA

snap services oracle-cloud-agent
Service                                        Startup  Current  Notes
oracle-cloud-agent.oracle-cloud-agent          enabled  active   -
oracle-cloud-agent.oracle-cloud-agent-updater  enabled  active   -









