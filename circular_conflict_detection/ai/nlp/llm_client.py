import os
import json
from typing import Dict, Any

try:
    from google import genai
    from google.genai import types
except ImportError:
    raise ImportError("Please install the new generative AI package: pip install google-genai")

from .prompt_gen import generate_conflict_prompt


class ConflictDetectionLLM:
    """
    Handles communication with the LLM API to perform the probabilistic conflict detection.
    Updated to use the new google-genai SDK.
    """
    def __init__(self, api_key: str = None, model_name: str = "gemini-3.5-flash"):
        # Use provided key or fallback to environment variable
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("API Key is missing. Set GEMINI_API_KEY environment variable.")
            
        self.model_name = model_name
        
        # Initialize the new Google GenAI client
        self.client = genai.Client(api_key=self.api_key)

    def analyze_conflict(self, new_clause: str, retrieved_clause: str) -> Dict[str, str]:
        """
        Sends the clauses to the LLM and returns the parsed JSON response.
        """
        prompt = generate_conflict_prompt(new_clause, retrieved_clause)
        
        try:
            # Use the new models.generate_content API format
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            # Parse the JSON string returned by the API
            result_dict = json.loads(response.text)
            return result_dict
            
        except json.JSONDecodeError:
            return {
                "conflict_type": "Error",
                "explanation": "Failed to parse LLM response into JSON."
            }
        except Exception as e:
            return {
                "conflict_type": "Error",
                "explanation": f"API Call Failed: {str(e)}"
            }