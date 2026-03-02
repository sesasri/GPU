from langchain_oci import (
    ChatOCIGenAI,
    load_image,
    encode_image,
    is_vision_model,
)
from langchain_core.messages import HumanMessage,SystemMessage
import requests
import pandas as pd

# Vision-capable model
model_id = "google.gemini-2.5-pro"

# Optional but recommended: verify vision support
if not is_vision_model(model_id):
    raise ValueError(f"{model_id} does not support vision inputs")

# Initialize OCI GenAI chat model
llm = ChatOCIGenAI(
    model_id=model_id,
    compartment_id="ocid1.compartment.oc1..aaaaaaaamjxynn55q2nddbeur3zwnkzis4yogjtqkd6zzyoafngyvxxxxxfa",
    service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
)

df = pd.read_excel("demodata.xlsx",sheet_name="GiftRecords")

# ----------------------------
# Load Data
# ----------------------------
table_data = df.to_markdown()
user_query=f"""
You are a data analyst. I will give you a small sample of an Excel export
as CSV text. Each row has Allocation Subcategory,City,College,Gift Allocation,Gift Amount,Gift Date,Major,Prospect ID,State

Data:
{table_data}

Tasks:
1) Summarize total gift received by City, College
2) List the top 5 Allocation Categories receiving highest gifts
3) Describe any obvious trends you notice.
Return your answer in markdown with clear headings and tables.
"""

message = [
HumanMessage(user_query)
]

result = llm.invoke(message)
print(result.content)

