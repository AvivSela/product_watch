"""
File Processor Service.

This service processes retail files from Kafka messages,
extracts product and pricing data, and publishes processed items.
"""

from .file_processor import ExtractedPriceProductItem, process_xml_file
from .main import app

__all__ = ["app", "process_xml_file", "ExtractedPriceProductItem"]
