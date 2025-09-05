"""
Ollama client for local LLM communication
"""

import requests
import json
from typing import Dict, Any, Optional


class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama client
        
        Args:
            base_url: Base URL for Ollama API (default: http://localhost:11434)
        """
        self.base_url = base_url.rstrip('/')
        
    def generate(self, model: str, prompt: str, stream: bool = False) -> str:
        """
        Generate text using Ollama model
        
        Args:
            model: Model name (e.g., 'llama2', 'mistral')
            prompt: Input prompt
            stream: Whether to stream response
            
        Returns:
            Generated text response
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            if stream:
                # Handle streaming response
                result = ""
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line.decode('utf-8'))
                        if 'response' in data:
                            result += data['response']
                return result
            else:
                # Handle non-streaming response
                data = response.json()
                return data.get('response', '')
                
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to Ollama: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid response from Ollama: {e}")
    
    def chat(self, model: str, messages: list, stream: bool = False) -> str:
        """
        Chat with Ollama model
        
        Args:
            model: Model name
            messages: List of message dictionaries with 'role' and 'content'
            stream: Whether to stream response
            
        Returns:
            Generated response
        """
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            if stream:
                result = ""
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line.decode('utf-8'))
                        if 'message' in data and 'content' in data['message']:
                            result += data['message']['content']
                return result
            else:
                data = response.json()
                return data.get('message', {}).get('content', '')
                
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to Ollama: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid response from Ollama: {e}")
    
    def list_models(self) -> list:
        """
        List available models
        
        Returns:
            List of available model names
        """
        url = f"{self.base_url}/api/tags"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to Ollama: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid response from Ollama: {e}")
    
    def is_available(self) -> bool:
        """
        Check if Ollama is available
        
        Returns:
            True if Ollama is running and accessible
        """
        try:
            self.list_models()
            return True
        except:
            return False