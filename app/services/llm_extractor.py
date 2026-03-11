import json
import logging
import re
from datetime import datetime
from openai import OpenAI

from app.core.config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

client = OpenAI(api_key=OPENAI_API_KEY)


class LLMExtractor:
    """
    Service for extracting structured data from document text using LLM
    """

    @staticmethod
    def extract_invoice_data(text: str) -> dict:
        """
        Extract invoice fields from raw document text
        """

        try:
            logger.info(f"Starting LLM extraction for text of length: {len(text)} characters")
            
            prompt = f"""
            You are a document extraction system specializing in invoice processing.

            Extract the following fields from the invoice text below. Return a JSON response with ALL of these fields:

            Required fields:
            - invoice_number: The invoice or document number (string)
            - vendor_name: The company/vendor name that issued the invoice (string)
            - invoice_date: The invoice date in YYYY-MM-DD format (string)
            - total_amount: The total amount as a number WITHOUT currency symbols (float, e.g., 2665.18)
            - tax_amount: The tax amount as a number WITHOUT currency symbols (float)
            - currency: The currency code (e.g., USD, EUR, GBP) - extract from the amount values

            Instructions:
            1. For amounts: Remove ALL currency symbols ($, €, £, etc.) and return just the number
            2. For dates: Convert to YYYY-MM-DD format
            3. If a field is not found, use null
            4. Return ONLY valid JSON, no additional text

            Invoice text:
            {text}

            Return JSON only (no markdown, no explanations):
            """

            logger.debug("Sending request to OpenAI API")
            logger.debug(f"API Key configured: {bool(OPENAI_API_KEY)}")
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a precise document extraction system. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )

            content = response.choices[0].message.content
            logger.info(f"Received LLM response of length: {len(content)} characters")
            logger.debug(f"Raw LLM response------>>>>>: {content}")

            # Parse JSON response
            parsed_data = json.loads(content)
            logger.info(f"Successfully parsed LLM response into JSON with keys: {list(parsed_data.keys())}")
            
            # Clean and validate the extracted data
            cleaned_data = LLMExtractor._clean_extracted_data(parsed_data)
            logger.info(f"Cleaned data: {cleaned_data}")

            return cleaned_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            logger.error(f"Raw content that failed to parse: {content if 'content' in locals() else 'N/A'}")
            return {"error": f"JSON parsing failed: {str(e)}"}
        except Exception as e:
            logger.error(f"LLM extraction failed: {str(e)}", exc_info=True)
            return {"error": str(e)}

    @staticmethod
    def _clean_extracted_data(data: dict) -> dict:
        """
        Clean and validate extracted data to ensure correct types and format
        """
        cleaned = {}
        
        # Invoice number - keep as string
        cleaned['invoice_number'] = data.get('invoice_number')
        
        # Vendor name - keep as string
        cleaned['vendor_name'] = data.get('vendor_name')
        
        # Invoice date - convert to YYYY-MM-DD format
        invoice_date = data.get('invoice_date')
        if invoice_date:
            try:
                # Try parsing common date formats
                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%B %d, %Y', '%b %d, %Y']:
                    try:
                        parsed_date = datetime.strptime(invoice_date, fmt)
                        cleaned['invoice_date'] = parsed_date.strftime('%Y-%m-%d')
                        break
                    except ValueError:
                        continue
                else:
                    logger.warning(f"Could not parse date: {invoice_date}")
                    cleaned['invoice_date'] = invoice_date
            except Exception as e:
                logger.warning(f"Error parsing invoice_date: {str(e)}")
                cleaned['invoice_date'] = invoice_date
        else:
            cleaned['invoice_date'] = None
        
        # Total amount - convert to float, remove currency symbols
        total_amount = data.get('total_amount')
        if total_amount:
            try:
                if isinstance(total_amount, str):
                    # Remove currency symbols and commas
                    amount_str = re.sub(r'[^\d.-]', '', total_amount)
                    cleaned['total_amount'] = float(amount_str)
                else:
                    cleaned['total_amount'] = float(total_amount)
            except ValueError as e:
                logger.warning(f"Could not parse total_amount '{total_amount}': {str(e)}")
                cleaned['total_amount'] = None
        else:
            cleaned['total_amount'] = None
        
        # Tax amount - convert to float, remove currency symbols
        tax_amount = data.get('tax_amount')
        if tax_amount:
            try:
                if isinstance(tax_amount, str):
                    amount_str = re.sub(r'[^\d.-]', '', tax_amount)
                    cleaned['tax_amount'] = float(amount_str)
                else:
                    cleaned['tax_amount'] = float(tax_amount)
            except ValueError as e:
                logger.warning(f"Could not parse tax_amount '{tax_amount}': {str(e)}")
                cleaned['tax_amount'] = None
        else:
            cleaned['tax_amount'] = None
        
        # Currency - keep as string
        cleaned['currency'] = data.get('currency')
        
        return cleaned