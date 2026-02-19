"""
AI Agent for Delivery Quantity Validation

This module implements an AI-powered validation agent that uses Azure OpenAI
to intelligently validate delivery quantities from delivery-order documents.

The agent:
1. Receives document text extracted by Azure Document Intelligence
2. Receives the delivery quantity entered in SAP
3. Uses GPT-4 to understand context and validate quantities
4. Returns validation result with confidence score and reasoning
"""

import os
import json
import time
import logging
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
                api_version="2024-10-21"
            )
            self.enabled = True
        else:
            self.client = None
            self.enabled = False
    
    def validate(self, 
                 document_text: str,
                 entered_quantity: float,
                 extracted_quantities: List[float],
                 cargo_discharged_weight: float = None) -> Optional[Dict]:
        """
        Use AI to validate the entered quantity against document content.
        
        Args:
            document_text: Full text extracted from the document
            entered_quantity: Quantity entered by the user
            extracted_quantities: All numerical values found in the document
            cargo_discharged_weight: Value extracted from the 'Weight of Cargo Discharged' field (if found)
        
        Returns:
            Dictionary with validation result or None if agent is disabled
        """
        if not self.enabled:
            return None
        
        try:
            prompt = self._build_validation_prompt(
                document_text, 
                entered_quantity, 
                extracted_quantities,
                cargo_discharged_weight
            )

            messages = [
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt},
            ]

            # Retry up to 2 times on 429 rate-limit errors
            max_retries = 2
            for attempt in range(max_retries + 1):
                try:
                    response = self.client.chat.completions.create(
                        model=self.deployment,
                        messages=messages,
                        temperature=0.1,
                        max_tokens=500,
                        response_format={"type": "json_object"},
                    )
                    break  # success
                except Exception as api_err:
                    if '429' in str(api_err) and attempt < max_retries:
                        wait = 15 * (attempt + 1)
                        logging.warning("OpenAI 429 rate limit – retrying in %ds (attempt %d/%d)",
                                        wait, attempt + 1, max_retries)
                        time.sleep(wait)
                    else:
                        raise

            result = json.loads(response.choices[0].message.content)
            return self._process_ai_response(result)
            
        except Exception as e:
            logging.warning("AI Agent validation error: %s", e)
            return None
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the AI agent."""
        return """You are an expert AI agent specializing in validating delivery quantities against shipping, cargo, and discharge documents.

Your primary role:
- Find the discharged cargo weight, quantity, or value in the document text.
  Common field names include (but are not limited to):
    • WEIGHT OF CARGO DISCHARGED
    • CARGO DISCHARGED WEIGHT / QTY / QUANTITY
    • DISCHARGED WEIGHT / QTY / QUANTITY
    • QUANTITY DISCHARGED
    • TOTAL DISCHARGED / NET DISCHARGED
    • DELIVERED QTY / DELIVERED WEIGHT
  The exact wording varies across documents.
- Compare that value against the delivery quantity entered in SAP.
- If the values match (within rounding tolerance), the validation is successful.
- If they don't match, the validation fails.
- Provide clear reasoning about where you found the value and why it matches or not.

Always respond in valid JSON format."""
    
    def _build_validation_prompt(self,
                                  document_text: str,
                                  entered_quantity: float,
                                  extracted_quantities: List[float],
                                  cargo_discharged_weight: float = None) -> str:
        """Build the validation prompt for the AI."""
        # Limit document text to avoid token limits
        doc_preview = document_text[:2000] if len(document_text) > 2000 else document_text

        cargo_info = (
            f"REGEX-EXTRACTED DISCHARGED WEIGHT: {cargo_discharged_weight}"
            if cargo_discharged_weight is not None
            else "REGEX-EXTRACTED DISCHARGED WEIGHT: Not found by regex — please locate it in the text yourself."
        )

        return f"""Validate a delivery quantity against a cargo/shipping document.

DOCUMENT TEXT:
{doc_preview}

{cargo_info}

ALL EXTRACTED NUMERICAL VALUES:
{extracted_quantities}

DELIVERY QUANTITY ENTERED IN SAP:
{entered_quantity}

TASK:
1. Locate the discharged cargo weight / quantity / value in the document.
   Look for fields like: "Weight of Cargo Discharged", "Cargo Discharged Qty",
   "Discharged Quantity", "Quantity Discharged", "Total Discharged",
   "Delivered Qty", "Net Discharged", or any equivalent.
2. Determine whether the SAP delivery quantity ({entered_quantity}) matches that value.
3. Consider formatting variations (e.g. 1234.56 vs 1,234.56) and unit labels (MT, KG, LT, BBL, etc.).
4. Ignore numbers that are clearly dates, reference IDs, vessel numbers, or unrelated fields.

RESPOND IN JSON FORMAT:
{{
    "is_valid": <boolean — true if SAP quantity matches the discharged weight/qty>,
    "matched_value": <the discharged weight/qty number from the document, or null>,
    "confidence": <0-100>,
    "reasoning": "<brief explanation of where you found the value and why it matches or not>",
    "field_location": "<exact text snippet where the value appears>"
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
            prompt = f"""Analyze this delivery-order document and identify key fields:

{document_text[:1000]}

Identify and extract:
1. Document type/title
2. Delivery quantity field and value
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
