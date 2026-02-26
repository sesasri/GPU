# OCI Generative AI Authentication & OpenAI Compatible Code Examples

## OCI Authentication Methods

The following authentication methods are supported in Oracle Cloud Infrastructure (OCI):

| Auth Type              | Where Used              | Notes |
|------------------------|-------------------------|-------|
| `API_KEY`              | Local Dev, Scripts      | Requires private/public keys |
| `INSTANCE_PRINCIPAL`   | OCI Compute             | Compute instance is trusted via IAM |
| `RESOURCE_PRINCIPAL`   | OCI Managed Services    | Used by OCI Agent Hub, Functions, etc. |
| `SECURITY_TOKEN`       | Token-based auth        | Based on OCI Console authentication |

> These are standard OCI authentication methods.

📘 Official documentation:  
https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdk_authentication_methods.htm

---

## OCI Generative AI API Keys

OCI Generative AI supports **secure credential tokens** that provide:

- API key-based access to specific LLMs
- OpenAI SDK compatibility
- Access to frontier models via OCI Generative AI

This allows you to use OpenAI-compatible SDK patterns while authenticating through OCI.

---

# Example: Chat Completions Example with OCI and Langchain

```python
from openai import OpenAI
from oci_openai import (
    OciOpenAI,
    OciSessionAuth,
    OciInstancePrincipalAuth,
    OciUserPrincipalAuth,
    OciResourcePrincipalAuth,
)
from langchain_oci.chat_models.oci_generative_ai import ChatOCIGenAI

def __init__(self, model_name: str = "openai.gpt-oss-120b"):
    """Initialize the agent with OCI Generative AI model"""

    self.llm = ChatOCIGenAI(
        model_id=model_name,
        compartment_id="ocid1.compartment.oc1..aaaaaaaXXXXXXkzis4yogjtqkd6zzyoafngyv2647pfa",
        # temperature=0,
        # service_endpoint=os.getenv("OCI_SERVICE_ENDPOINT"),
        # auth_type=os.getenv("OCI_AUTH_TYPE", "API_KEY"),
        # auth_profile=os.getenv("OCI_AUTH_PROFILE", "DEFAULT"),
        auth_type=os.getenv("OCI_AUTH_TYPE", "INSTANCE_PRINCIPAL"),
    )
```

# Example: Responsive API example with OCI

```
print(f"{Fore.GREEN}Demo Mode for Authentication is: {demo_mode}{Style.RESET_ALL}")

if (demo_mode == 'API'):
    # Initialize OpenAI client
    if api_key is None:
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')

        if not api_key:
            raise ValueError("OpenAI API key is required")

        INF_URL = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/20231130/actions/v1"

        print(f"{Fore.GREEN}API Key is : {api_key}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Inference URL is : {INF_URL}{Style.RESET_ALL}")

        self.client = OpenAI(api_key=api_key, base_url=INF_URL)

elif (demo_mode == 'IP'):

    self.client = OciOpenAI(
        region="us-chicago-1",
        auth=OciInstancePrincipalAuth(),
        compartment_id="ocid1.compartment.oc1..aaaaaaaamXXXXXur3zwnkzis4yogjtqkd6zzyoafngyv2647pfa",
    )

elif (demo_mode == 'SP'):

    self.client = OciOpenAI(
        region="us-chicago-1",
        auth=OciSessionAuth(profile_name="gendemo"),
        compartment_id="ocid1.compartment.oc1..aaaaaaaamjxXXXXXXis4yogjtqkd6zzyoafngyv2647pfa",
    )

else:

    self.client = OciOpenAI(
        region="us-chicago-1",
        auth=OciUserPrincipalAuth(profile_name="DEFAULT"),
        compartment_id="ocid1.compartment.oc1..aaaaaaaamjxynn55q2nddbeur3zwnkzis4yogjtqkd6zzyoafngyv2647pfa",
    )

```

📘 Langchain Full Example code:  https://github.com/sesasri/GPU/blob/main/langchain_conv_example_calc.py

📘 OpenAI Full Example code:  https://github.com/sesasri/GPU/blob/main/langchain_conv_example_calc.py
