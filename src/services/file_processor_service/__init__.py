"""
File Processor Service.

This service processes retail files from Kafka messages,
extracts product and pricing data, and publishes processed items.
"""

import os
import sys

# Add the service directory to the Python path if not already there
service_dir = os.path.dirname(__file__)
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)

try:
    from file_processor import ExtractedPriceProductItem, process_xml_file
except ImportError:
    # If running from project root, try relative imports
    try:
        from .file_processor import ExtractedPriceProductItem, process_xml_file
    except ImportError:
        # If that fails too, we're in a different context
        ExtractedPriceProductItem = None
        process_xml_file = None

__all__ = ["process_xml_file", "ExtractedPriceProductItem"]
