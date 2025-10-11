#!/usr/bin/env python3

"""
Gemini AI service for content summarization.

Handles interactions with Google's Gemini API for text and PDF summarization.
"""

import os
from typing import Optional
from google import genai
from google.genai import types
from django.conf import settings


class GeminiService:
    """Service class to handle Gemini API interactions for summarization."""

    def __init__(self):
        """Initialize Gemini client with API key from environment."""
        api_key = os.getenv('GEMINI_API_KEY') or settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment or settings")

        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.5-flash"

    def summarize_text(self, text: str, max_length: Optional[int] = None) -> str:
        """
        Summarize text content using Gemini API.

        Args:
            text: The text content to summarize
            max_length: Optional maximum length for the summary in words

        Returns:
            Summarized text

        Raises:
            Exception: If API call fails
        """
        if not text or not text.strip():
            raise ValueError("Text content cannot be empty")

        # Build prompt
        prompt = "Please provide a concise summary of the following text:\n\n"
        if max_length:
            prompt = f"Please provide a concise summary (max {max_length} words) of the following text:\n\n"

        prompt += text

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,  # Lower temperature for more focused summaries
                    max_output_tokens=500,
                )
            )

            return response.text.strip()

        except Exception as e:
            raise Exception(f"Failed to summarize text: {str(e)}")

    def summarize_pdf(self, pdf_path: str, max_length: Optional[int] = None) -> str:
        """
        Extract text from PDF and summarize it using Gemini API.

        Args:
            pdf_path: Path to the PDF file
            max_length: Optional maximum length for the summary in words

        Returns:
            Summarized text from PDF

        Raises:
            Exception: If PDF extraction or API call fails
        """
        try:
            # Extract text from PDF
            extracted_text = self._extract_text_from_pdf(pdf_path)

            if not extracted_text or not extracted_text.strip():
                raise ValueError("No text could be extracted from the PDF")

            # Summarize the extracted text
            return self.summarize_text(extracted_text, max_length)

        except Exception as e:
            raise Exception(f"Failed to summarize PDF: {str(e)}")

    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF file using PyPDF library.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text from all pages

        Raises:
            Exception: If PDF extraction fails
        """
        try:
            from pypdf import PdfReader

            reader = PdfReader(pdf_path)
            text = ""

            # Extract text from all pages
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

            return text.strip()

        except ImportError:
            raise Exception("pypdf library not installed. Install with: pip install pypdf")
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")


# Singleton instance
_gemini_service = None

def get_gemini_service() -> GeminiService:
    """Get or create GeminiService singleton instance."""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
