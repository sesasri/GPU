
# OCI Dedicated AI Cluster

## Table of Contents
- What is Dedicated AI Cluster?
- Key properties
- What is Data Science?
- Permissions and Limits for Dedicated AI Cluster (DAC)
- DAC vs OCI DS

---

## What is Dedicated AI Cluster?

An OCI Dedicated AI Cluster (DAC) is a private, fully managed generative AI environment with its own dedicated GPUs, endpoints, and security boundary inside OCI.

### Key properties:

- Single tenant, isolated AI cluster  
  - You get a dedicated set of GPUs and associated infrastructure; models and data are not shared with other tenants.

- Purpose built for GenAI and LLMs

- Use to fine-tune custom models or to host endpoints for the pretrained base models, custom models, and imported models in OCI Generative AI  
  - A single cluster can host many fine tuned variants (up to roughly dozens per base model) for different use cases while reusing the same GPU pool.

- Oracle manages cluster lifecycle, scaling, patching, and model infrastructure; model endpoints are available via APIs and console.

- The endpoints can be public or private and both are subject to Generative AI authorization schemes

### Benefits:

- Low, predictable latency and high throughput (contact centers, document analysis, RAG for business apps)

- Strict data privacy guarantees: your prompts, fine tuning data, and model weights stay inside your cluster and region

- Fine tune on the available models in DaC

- Ability to control and retain model versions

---

## What is Data Science?

Oracle Cloud Infrastructure (OCI) Data Science is a fully managed platform for teams of data scientists to build, train, deploy, and manage machine learning (ML) models using Python and open source tools. Use a JupyterLab-based environment to experiment and develop models. Scale up model training with NVIDIA GPUs and distributed training. Take models into production and keep them healthy with ML operations (MLOps) capabilities, such as automated pipelines, model deployments, and model monitoring. Quick Actions in Data Science simplify use of foundation models with the new OCI Data Science AI Quick Actions feature. It’s designed to let anyone easily deploy, fine-tune, and evaluate open-source foundation models.

### Key Capabilities

- Interactive workbenches  
- Training and experimentation  
- MLOps: pipelines, deployment, monitoring  

---

## Permissions and Limits for Dedicated AI Cluster (DAC)

DAC runs typically on NVIDIA A10, A100 or H100 GPUs. The number of accelerator cards are dependent on the model card and the number of model replica can be chosen based on the needs. Customers might not have the limits available for setting up DAC.

The appropriate limits can be requested from the limits page:  
https://cloud.oracle.com/support/create/limit?source=chat&region=us-chicago-1  
or CLI.

### Typical limits:

- A100-40G Dedicated unit count  
- A100-80G Dedicated unit count  
- H100 Dedicated unit count  
- H200 Dedicated unit count  

---

## Models and Availability

| Model | Link |
|------|------|
| openai-gpt-oss-120b | https://docs.oracle.com/en-us/iaas/Content/generative-ai/openai-gpt-oss-120b.htm |
| openai-gpt-oss-20b | https://docs.oracle.com/en-us/iaas/Content/generative-ai/openai-gpt-oss-20b.htm |
| Cohere Models | https://docs.oracle.com/en-us/iaas/Content/generative-ai/cohere-models.htm |
| Meta Models | https://docs.oracle.com/en-us/iaas/Content/generative-ai/meta-models.htm |
| NVIDIA-Nemotron-3-Super-120B-A12B-FP8 | https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-FP8 |
| nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16 | https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16 |

---

## Permissions needed for setting up DAC

Specific permissions are needed to create DAC. Broad permission can be granted as shown below:

```markdown

allow group <generative-ai-administrators> to manage generative-ai-family in tenancy

```

or

```markdown

allow group <generative-ai-administrators> to manage generative-ai-family in compartment genai

```

In environments that need fine grained control, you can provide specific permissions:

```markdown

allow group <generative-ai-administrators> to manage generative-ai-family in tenancy

```

Details:  
https://docs.oracle.com/en-us/iaas/Content/generative-ai/iam-policies.htm

---

## DAC vs OCI DS

| | Dedicated AI Cluster | OCI Data Science |
|--|---------------------|-----------------|
| What is it? | OCI is fully managed LLM hosting platform; Oracle manages infrastructure, inference stack and provides pre-provisioned capacity (no autoscale yet) | Data Science is a fully managed and serverless platform for data science teams to build, train, and manage machine learning models |
| What are the typical use cases? | LLM inference, Large-scale training, High-throughput GenAI workloads | Notebooks (Jupyter), Model development, Training jobs, Experiment tracking |
