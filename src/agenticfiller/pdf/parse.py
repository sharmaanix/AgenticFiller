"""LLM-driven structured extraction from PDF text.

Given a JSON schema and a chunk of PDF text, ask Claude to produce a
matching dict. Filled in during Step 6.
"""

from __future__ import annotations


def extract_fields(pdf_path: str, schema: dict) -> dict:
    """Extract fields from *pdf_path* matching *schema*.

    To be implemented in Step 6.
    """
    raise NotImplementedError("Implemented in Step 6.")
