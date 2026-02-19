"""
AI Agent for Discharge Quantity Validation

This module implements an AI-powered validation agent that uses Azure OpenAI
to intelligently validate discharge quantities from documents.

The agent:
1. Receives document text from Azure Document Intelligence
2. Receives user-entered quantity from API header
3. Uses GPT-4 to understand context and validate quantities
4. Returns validation result with confidence score and reasoning
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from openai import AzureOpenAI


class ValidationAgent:
    """AI Agent for intelligent quantity validation."""
    
    def __init__(self, 
                 endpoint: str = None,
                 api_key: str = None,
                 deployment: str = None):
        """
        Initialize the Validation Agent.
        
        Args:
            endpoint: Azure OpenAI endpoint
            api_key: Azure OpenAI API key
            deployment: Name of the GPT deployment
        """
        self.endpoint = endpoint or os.getenv('AZURE_OPENAI_ENDPOINT')
        self.api_key = api_key or os.getenv('AZURE_OPENAI_KEY')
        self.deployment = deployment or os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4o')
        
        if self.endpoint and self.api_key:
            self.client = AzureOpenAI(
                azure_endpoint=self.endpoint,
                api_key=self.api_key,
                api_version="2024-02-15-preview"
            )
            self.enabled = True
        else:
            self.client = None
            self.enabled = False
    
    def validate(self, 
                 document_text: str,
                 entered_quantity: float,
                 extracted_quantities: List[float]) -> Optional[Dict]:
        """
        Use AI to validate the entered quantity against document content.
        
        Args:
            document_text: Full text extracted from the document
            entered_quantity: Quantity entered by the user
            extracted_quantities: All numerical values found in the document
        
        Returns:
            Dictionary with validation result or None if agent is disabled
        """
        if not self.enabled:
            return None
        
        try:
            prompt = self._build_validation_prompt(
                document_text, 
                entered_quantity, 
                extracted_quantities
            )
            
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system", 
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return self._process_ai_response(result)
            
        except Exception as e:
            print(f"AI Agent validation error: {str(e)}")
            return None
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the AI agent."""
        return """You are an expert AI agent specializing in validating discharge quantities from SAP documents.

Your role:
- Analyze document text to find discharge quantity information
- Compare user-entered values with document content
- Consider context to distinguish discharge quantities from other numbers (dates, IDs, etc.)
- Provide accurate validation with confidence scores
- Explain your reasoning clearly

Always respond in valid JSON format."""
    
    def _build_validation_prompt(self,
                                  document_text: str,
                                  entered_quantity: float,
                                  extracted_quantities: List[float]) -> str:
        """Build the validation prompt for the AI."""
        # Limit document text to avoid token limits
        doc_preview = document_text[:1500] if len(document_text) > 1500 else document_text
        
        return f"""Validate a discharge quantity from a document.

DOCUMENT TEXT:
{doc_preview}

EXTRACTED NUMERICAL VALUES:
{extracted_quantities}

USER ENTERED QUANTITY:
{entered_quantity}

TASK:
Determine if the entered quantity ({entered_quantity}) accurately matches a discharge quantity in the document.

CONSIDERATIONS:
1. Look for explicit "discharge quantity" mentions
2. Consider formatting variations (1234.56 vs 1,234.56)
3. Ignore numbers that are clearly dates, IDs, or other non-quantity values
4. Consider units and context

RESPOND IN JSON FORMAT:
{{
    "is_valid": <boolean>,
    "matched_value": <number or null>,
    "confidence": <0-100>,
    "reasoning": "<brief explanation>",
    "field_location": "<where in document the value was found>"
}}
"""
    
    def _process_ai_response(self, ai_result: Dict) -> Dict:
        """Process and validate the AI response."""
        return {
            'is_valid': ai_result.get('is_valid', False),
            'matched_value': ai_result.get('matched_value'),
            'confidence': min(100, max(0, ai_result.get('confidence', 0))),
            'reasoning': ai_result.get('reasoning', 'No reasoning provided'),
            'field_location': ai_result.get('field_location', 'Unknown')
        }
    
    def analyze_document_structure(self, document_text: str) -> Dict:
        """
        Analyze document structure to identify key fields.
        This helps in understanding document layout.
        """
        if not self.enabled:
            return {'error': 'AI Agent not enabled'}
        
        try:
            prompt = f"""Analyze this discharge document and identify key fields:

{document_text[:1000]}

Identify and extract:
1. Document type/title
2. Discharge quantity field and value
3. Date
4. Any reference numbers
5. Material/product information

Respond in JSON format with fields and their values."""

            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": "You are a document analysis expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=800,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            return {'error': str(e)}


# Singleton instance
_agent_instance: Optional[ValidationAgent] = None


def get_validation_agent() -> ValidationAgent:
    """Get or create the validation agent singleton."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = ValidationAgent()
    return _agent_instance
