import os
import argparse
from dotenv import load_dotenv
from Agent import MedicalCodingAgent
from bedrock_implementation import BedrockImplementation

# Load environment variables from .env file
load_dotenv()

def main():
    """Main entry point for the CLI."""
    # Parse CLI arguments
    tesseract_cmd = os.getenv('TESSERACT_CMD', '/usr/bin/tesseract')  # Default for Linux
    poppler_path = os.getenv('POPPLER_PATH', '/usr/bin')  # Default for Linux
    llm = BedrockImplementation()

    # Inject configurations into the MedicalCodingAgent
    agent = MedicalCodingAgent(
        tesseract_cmd=tesseract_cmd,
        poppler_path=poppler_path,
        llm=llm,
    )
    agent.start_conversation()

if __name__ == "__main__":
    main()