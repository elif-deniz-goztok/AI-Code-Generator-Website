import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self):
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("LLM_MODEL", "llama3.2:latest")
        
    def generate_code(self, prompt):
        """
        Generate code using Ollama with Llama 3.2
        """
        system_prompt = """
        You are an AI assistant that helps generate Python code based on user prompts.
        The code should extend the Job class from s4e.job by implementing its methods.
        
        The basic Job class is:
        
        ```python
        from s4e.config import *
        from s4e.task import Task

        class Job(Task):
           def run(self):
               asset = self.asset
               self.output['detail'] = []  # It is detailed result from job
               self.output['compact'] = []  # It is short result from job
               self.output['video'] = []  # It is the steps, commands, etc for doing the job

           def calculate_score(self):
               # It is a number between 0 and 10
               # if score == 1  information
               # if 1 < score < 4 low
               # if 4 <= score < 7 medium
               # if 7 <= score < 9 high
               # if 9 <= score < 11 critical
               # set score to something meaningful
               self.score = self.param['max_score']
        ```
        
        Based on the user's prompt, you must:
        1. Generate a meaningful Python class that extends this Job class
        2. Implement the run and calculate_score methods appropriately
        3. Return your response in the following JSON format:
        {
            "title": "A short descriptive title for the code",
            "code": "The full Python code (as a string)"
        }
        
        Your response must be valid JSON that can be parsed by Python's json.loads().
        """
        
        # Prepare request to Ollama
        url = f"{self.ollama_base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "format": "json",
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Extract the response
            if "response" in data:
                try:
                    # Parse the JSON string from the model
                    result = json.loads(data["response"])
                    return result
                except json.JSONDecodeError:
                    # If the model didn't return valid JSON, try to extract code and create our own response
                    content = data["response"]
                    # Fallback parsing if model doesn't return proper JSON
                    return self._extract_code_and_title(content)
        except Exception as e:
            print(f"Error generating code: {str(e)}")
            return {
                "title": "Error generating code",
                "code": f"# An error occurred: {str(e)}"
            }
    
    def _extract_code_and_title(self, content):
        """Fallback method to extract code and title if JSON parsing fails"""
        lines = content.split('\n')
        title = "Generated Python Code"
        code_lines = []
        in_code_block = False
        
        for line in lines:
            if "# Title:" in line or "Title:" in line:
                title = line.split(":", 1)[1].strip()
            elif "```python" in line:
                in_code_block = True
            elif "```" in line and in_code_block:
                in_code_block = False
            elif in_code_block:
                code_lines.append(line)
        
        code = "\n".join(code_lines) if code_lines else "# No code was generated"
        
        return {
            "title": title,
            "code": code
        } 