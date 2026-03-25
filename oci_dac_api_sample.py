from openai import OpenAI
import os

API_KEY=os.getenv("OPENAI_API_KEY")
MODEL_ID=os.getenv("DAC_MODEL_ID")

client = OpenAI(
    api_key=API_KEY,
    base_url="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com/openai/v1",
)


# Completion API
response = client.chat.completions.create(
    model=MODEL_ID,
    messages=[{
        "role": "user",
        "content": "Write a one-sentence bedtime story about a unicorn."
        }
    ]
)
print(response)
