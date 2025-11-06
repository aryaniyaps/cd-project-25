import json
import os
import boto3
from llm_interface import LLMInterface


class BedrockImplementation(LLMInterface):
    def __init__(self, model_id="amazon.nova-pro-v1:0", region_name="us-east-1"):
        """
        Initialize the AWS Bedrock LLM implementation.

        Args:
            model_id (str): The model ID to use for generating responses.
                          Default is Amazon Nova Pro.
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
        Generate a response using AWS Bedrock API with Amazon Nova.

        Args:
            conversation_history (list): A list of conversation messages in the format:
                                         [{"role": "user", "content": "message"}, ...]
            specific_prompt (str, optional): An additional system-level prompt to guide the response.

        Returns:
            str: The generated response from the Bedrock API.
        """
        try:
            # Prepare messages for Nova format
            messages = []
            system_list = []
            
            # Extract system messages and convert conversation history
            for msg in conversation_history:
                if msg["role"] == "system":
                    system_list.append({"text": msg["content"]})
                else:
                    # Convert content to Nova format
                    if isinstance(msg["content"], str):
                        content = [{"text": msg["content"]}]
                    else:
                        content = msg["content"]
                    
                    messages.append({
                        "role": msg["role"],
                        "content": content
                    })
            
            # Add specific prompt to system list if provided
            if specific_prompt:
                system_list.insert(0, {"text": specific_prompt})
            
            # Prepare the request body for Nova
            request_body = {
                "schemaVersion": "messages-v1",
                "messages": messages,
                "inferenceConfig": {
                    "maxTokens": 1000,
                    "temperature": 0.7,
                    "topP": 0.9
                }
            }
            
            # Add system prompt if it exists
            if system_list:
                request_body["system"] = system_list
            
            # Invoke the model
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            # Parse the response
            response_body = json.loads(response["body"].read())
            
            # Extract the text content from the Nova response
            if "output" in response_body and "message" in response_body["output"]:
                message = response_body["output"]["message"]
                if "content" in message and len(message["content"]) > 0:
                    return message["content"][0]["text"].strip()
            
            return "Error: No content in response"
                
        except Exception as e:
            return f"Error: {str(e)}"
