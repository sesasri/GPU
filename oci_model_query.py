#!/usr/bin/env python3
"""
Simple script to use Gemini 2.5 Pro via OCI Generative AI service.
Reads a prompt from a file and returns the response with timing information.
"""

import argparse
import time
import oci


def load_prompt(prompt_file: str) -> str:
    """Load prompt from a file."""
    with open(prompt_file, "r", encoding="utf-8") as f:
        return f.read().strip()


def call_model(prompt: str, compartment_id: str, endpoint: str, model_id: str) -> tuple[str, float]:
    """
    Call Gemini 2.5 Pro via OCI Generative AI and return response with elapsed time.
    
    Returns:
        tuple: (response_text, elapsed_time_seconds)
    """
    config = oci.config.from_file()
    
    generative_ai_client = oci.generative_ai_inference.GenerativeAiInferenceClient(
        config=config,
        service_endpoint=endpoint
    )
    
    chat_request = oci.generative_ai_inference.models.ChatDetails(
        compartment_id=compartment_id,
        serving_mode=oci.generative_ai_inference.models.OnDemandServingMode(
#            model_id="google.gemini-2.5-pro"
            model_id=model_id
        ),
        chat_request=oci.generative_ai_inference.models.GenericChatRequest(
            messages=[
                oci.generative_ai_inference.models.UserMessage(
                    content=[
                        oci.generative_ai_inference.models.TextContent(text=prompt)
                    ]
                )
            ],
            max_tokens=8192,
            temperature=0.7,
            top_p=0.9
        )
    )
    
    start_time = time.perf_counter()
    response = generative_ai_client.chat(chat_request)
    elapsed_time = time.perf_counter() - start_time
    
    #response_text = response.data.chat_response.choices[0].message.content[0].text
    response_text = response.data.chat_response
    
    return response_text, elapsed_time


def main():
    parser = argparse.ArgumentParser(
        description="Query Gemini 2.5 Pro or Grok models via OCI with a prompt file"
    )
    parser.add_argument(
        "prompt_file",
        help="Path to the file containing the prompt"
    )
    parser.add_argument(
        "--compartment-id",
        required=True,
        help="OCI compartment OCID"
    )
    parser.add_argument(
        "--model",
        required=True,
        help="OCI Model"
    )
    parser.add_argument(
        "--endpoint",
        default="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
        help="OCI Generative AI service endpoint (default: us-chicago-1)"
    )
    
    args = parser.parse_args()
    
    prompt = load_prompt(args.prompt_file)
    print(f"Prompt loaded ({len(prompt)} characters)")
    print("-" * 50)
    
    response, elapsed = call_model(prompt, args.compartment_id, args.endpoint, args.model)
    
    print("Response:")
    print(response)
    print("-" * 50)
    print(f"Time taken: {elapsed:.2f} seconds")


if __name__ == "__main__":
    main()
