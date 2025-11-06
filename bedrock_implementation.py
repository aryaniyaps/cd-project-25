import json
import os
import boto3
from llm_interface import LLMInterface


class BedrockImplementation(LLMInterface):
    def __init__(self, model_id="anthropic.claude-3-5-sonnet-20240620-v1:0", region_name="us-east-1"):
        """
        Initialize the AWS Bedrock LLM implementation.

        Args:
            model_id (str): The model ID to use for generating responses.
                          Default is Claude 3.5 Sonnet.
            region_name (str): AWS region name. Default is us-east-1.
        """
        # Get AWS credentials from environment variables
        aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        
        if not aws_access_key_id or not aws_secret_access_key:
            raise ValueError(
                "AWS credentials not found. Please set AWS_ACCESS_KEY_ID and "
                "AWS_SECRET_ACCESS_KEY environment variables."
            )
        
        # Initialize Bedrock Runtime client
        self.client = boto3.client(
            service_name="bedrock-runtime",
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        self.model_id = model_id

    def generate_response(self, conversation_history, specific_prompt=None):
        """
        Generate a response using AWS Bedrock API with Claude.

        Args:
            conversation_history (list): A list of conversation messages in the format:
                                         [{"role": "user", "content": "message"}, ...]
            specific_prompt (str, optional): An additional system-level prompt to guide the response.

        Returns:
            str: The generated response from the Bedrock API.
        """
        try:
            # Prepare messages for Claude format
            messages = []
            system_prompt = None
            
            # Extract system messages and convert conversation history
            for msg in conversation_history:
                if msg["role"] == "system":
                    if system_prompt is None:
                        system_prompt = msg["content"]
                    else:
                        system_prompt += "\n" + msg["content"]
                else:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Add specific prompt to system message if provided
            if specific_prompt:
                if system_prompt is None:
                    system_prompt = specific_prompt
                else:
                    system_prompt = specific_prompt + "\n" + system_prompt
            
            # Prepare the request body
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "temperature": 0.7,
                "messages": messages
            }
            
            # Add system prompt if it exists
            if system_prompt:
                request_body["system"] = system_prompt
            
            # Invoke the model
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            # Parse the response
            response_body = json.loads(response["body"].read())
            
            # Extract the text content from the response
            if "content" in response_body and len(response_body["content"]) > 0:
                return response_body["content"][0]["text"].strip()
            else:
                return "Error: No content in response"
                
        except Exception as e:
            return f"Error: {str(e)}"
