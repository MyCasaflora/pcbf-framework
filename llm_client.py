"""
PCBF 2.1 Framework - LLM Client für OpenRouter API
"""
import time
import json
import logging
from typing import Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import config

logger = logging.getLogger(__name__)


class LLMClient:
    """Client für OpenRouter API mit Retry-Logik"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialisiert LLM-Client.
        
        Args:
            api_key: OpenRouter API-Key (default: aus config)
            model: Modell-Name (default: aus config)
        """
        self.api_key = api_key or config.OPENROUTER_API_KEY
        self.base_url = config.OPENROUTER_BASE_URL
        self.model = model or config.DEFAULT_MODEL
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY nicht gesetzt!")
        
        # Session mit Retry-Logik
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
    
    def call(self, prompt: str, system_prompt: Optional[str] = None, 
             temperature: float = 0.7, max_tokens: int = 2000) -> Dict[str, Any]:
        """
        Ruft LLM-API auf.
        
        Args:
            prompt: User-Prompt
            system_prompt: System-Prompt (optional)
            temperature: Temperatur (0-1)
            max_tokens: Maximale Token-Anzahl
            
        Returns:
            Dictionary mit Response und Metadaten
        """
        start_time = time.time()
        
        # Messages zusammenstellen
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Request-Body
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            logger.debug(f"LLM API-Aufruf: Model={self.model}, Prompt-Länge={len(prompt)}")
            
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            
            result = response.json()
            latency_ms = (time.time() - start_time) * 1000
            
            # Response extrahieren
            content = result['choices'][0]['message']['content']
            
            logger.debug(f"LLM API-Erfolg: Latenz={latency_ms:.0f}ms, Response-Länge={len(content)}")
            
            return {
                'success': True,
                'content': content,
                'latency_ms': latency_ms,
                'model': self.model,
                'usage': result.get('usage', {}),
                'error': None
            }
            
        except requests.exceptions.RequestException as e:
            latency_ms = (time.time() - start_time) * 1000
            error_msg = f"LLM API-Fehler: {str(e)}"
            logger.error(error_msg)
            
            return {
                'success': False,
                'content': None,
                'latency_ms': latency_ms,
                'model': self.model,
                'usage': {},
                'error': error_msg
            }
        
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            error_msg = f"Unerwarteter Fehler: {str(e)}"
            logger.error(error_msg)
            
            return {
                'success': False,
                'content': None,
                'latency_ms': latency_ms,
                'model': self.model,
                'usage': {},
                'error': error_msg
            }
    
    def parse_json_response(self, response: Dict[str, Any]) -> Optional[Dict]:
        """
        Parst JSON aus LLM-Response.
        
        Args:
            response: LLM-Response
            
        Returns:
            Geparste JSON-Daten oder None bei Fehler
        """
        if not response['success'] or not response['content']:
            return None
        
        content = response['content'].strip()
        
        # JSON-Block extrahieren (falls in Markdown-Code-Block)
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()
        
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"JSON-Parse-Fehler: {str(e)}\nContent: {content[:200]}...")
            return None


# Singleton-Instanz
_llm_client = None


def get_llm_client() -> LLMClient:
    """
    Gibt Singleton-Instanz des LLM-Clients zurück.
    
    Returns:
        LLMClient-Instanz
    """
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client

