"""
File processing logic for retail-file-processor.
"""

# Standard library imports
import gzip
import io
import logging
import xml.etree.ElementTree as etree
import zipfile
from datetime import datetime, timedelta
from typing import Callable, List

# Third-party imports
from pydantic import BaseModel, Field

# Local application imports
from s3_client import S3Client

logger = logging.getLogger(__name__)


def simple_filter_items(item: "ExtractedPriceProductItem") -> bool:
    """Filter items to only include those with price < 5 and updated within last 3 days."""

    # Date filter: only include items updated within last 3 days
    three_days_ago = datetime.now() - timedelta(days=7)
    date_ok = item.price_update_date >= three_days_ago

    return date_ok


def default_filter_items(item: "ExtractedPriceProductItem") -> bool:
    return True


def process_xml_file(
    file_url: str,
    file_id: str,
    s3_client: S3Client,
    filter_items: Callable[["ExtractedPriceProductItem"], bool] = default_filter_items,
) -> List["ExtractedPriceProductItem"]:
    """
    Process XML file from S3 - download GZ file, parse XML, extract items.

    Args:
        file_path: Path to the file in S3
        file_id: ID of the file (from the event)
        s3_client: S3 client instance

    Returns:
        List of extracted price product items
    """
    try:
        if not s3_client:
            raise Exception("S3 client not available")

        # Check if file exists in S3
        if not s3_client.url_exists(file_url):
            raise Exception(f"File not found in S3: {file_url}")

        # Download file data from S3
        logger.info(f"Downloading file from S3: {file_url}")
        file_data = s3_client.get_object(file_url)

        # Log file size and first few bytes for debugging
        logger.info(f"Downloaded file size: {len(file_data)} bytes")
        logger.info(f"File header (first 20 bytes): {file_data[:20].hex()}")

        # Check file header to determine compression type
        file_header = file_data[:4]

        if file_header.startswith(b"\x1f\x8b"):  # GZ file header
            # Decompress GZ data
            with gzip.GzipFile(fileobj=io.BytesIO(file_data), mode="rb") as gz_file:
                xml_content = gz_file.read().decode("utf-8")
        elif file_header.startswith(b"PK"):  # ZIP file header
            # Decompress ZIP data
            with zipfile.ZipFile(io.BytesIO(file_data), "r") as zip_file:
                # Get the first XML file from the ZIP
                xml_files = [f for f in zip_file.namelist() if f.endswith(".xml")]
                if not xml_files:
                    raise Exception("No XML file found in ZIP archive")

                # Read the first XML file
                xml_content = zip_file.read(xml_files[0]).decode("utf-8")
                logger.info(f"Extracted XML file '{xml_files[0]}' from ZIP archive")
        else:
            # Try to read as plain XML
            try:
                xml_content = file_data.decode("utf-8")
                logger.info("File appears to be uncompressed XML")
            except UnicodeDecodeError:
                raise Exception(
                    f"Unsupported file format. File header: {file_header[:10].hex()}"
                )

        # Parse XML
        root = etree.fromstring(xml_content.encode("utf-8"))

        # Extract basic info from root
        chain_id = (
            root.find("ChainId").text if root.find("ChainId") is not None else "unknown"
        )
        sub_chain_id = (
            root.find("SubChainId").text
            if root.find("SubChainId") is not None
            else "unknown"
        )
        store_id = (
            root.find("StoreId").text if root.find("StoreId") is not None else "unknown"
        )
        bikoret_no = (
            root.find("BikoretNo").text
            if root.find("BikoretNo") is not None
            else "unknown"
        )

        # Find all items
        items = root.findall(".//Item")
        extracted_items = []

        for item in items:
            try:
                # Extract item data
                price_update_date_str = (
                    item.find("PriceUpdateDate").text
                    if item.find("PriceUpdateDate") is not None
                    else None
                )
                price_update_date = (
                    datetime.fromisoformat(price_update_date_str)
                    if price_update_date_str
                    else datetime.now()
                )

                extracted_item = ExtractedPriceProductItem(
                    file_id=file_id,  # Use actual file ID from event
                    chain_id=chain_id,
                    sub_chain_id=sub_chain_id,
                    store_id=store_id,
                    bikoret_no=bikoret_no,
                    price_update_date=price_update_date,
                    item_code=item.find("ItemCode").text
                    if item.find("ItemCode") is not None
                    and item.find("ItemCode").text is not None
                    else "",
                    item_type=item.find("ItemType").text
                    if item.find("ItemType") is not None
                    and item.find("ItemType").text is not None
                    else "",
                    item_name=item.find("ItemNm").text
                    if item.find("ItemNm") is not None
                    and item.find("ItemNm").text is not None
                    else "",
                    manufacturer_name=item.find("ManufacturerName").text
                    if item.find("ManufacturerName") is not None
                    and item.find("ManufacturerName").text is not None
                    else "",
                    manufacture_country=item.find("ManufactureCountry").text
                    if item.find("ManufactureCountry") is not None
                    and item.find("ManufactureCountry").text is not None
                    else "",
                    manufacturer_item_description=item.find(
                        "ManufacturerItemDescription"
                    ).text
                    if item.find("ManufacturerItemDescription") is not None
                    and item.find("ManufacturerItemDescription").text is not None
                    else "",
                    unit_qty=item.find("UnitQty").text
                    if item.find("UnitQty") is not None
                    and item.find("UnitQty").text is not None
                    else "",
                    quantity=float(item.find("Quantity").text)
                    if item.find("Quantity") is not None
                    else 0.0,
                    unit_of_measure=item.find("UnitOfMeasure").text
                    if item.find("UnitOfMeasure") is not None
                    and item.find("UnitOfMeasure").text is not None
                    else "",
                    is_weighted=item.find("bIsWeighted").text == "1"
                    if item.find("bIsWeighted") is not None
                    else False,
                    qty_in_package=float(item.find("QtyInPackage").text)
                    if item.find("QtyInPackage") is not None
                    else 0.0,
                    item_price=float(item.find("ItemPrice").text)
                    if item.find("ItemPrice") is not None
                    else 0.0,
                    unit_of_measure_price=float(item.find("UnitOfMeasurePrice").text)
                    if item.find("UnitOfMeasurePrice") is not None
                    else 0.0,
                    allow_discount=item.find("AllowDiscount").text == "1"
                    if item.find("AllowDiscount") is not None
                    else False,
                    item_status=item.find("ItemStatus").text
                    if item.find("ItemStatus") is not None
                    and item.find("ItemStatus").text is not None
                    else "",
                    extracted_at=datetime.now(),
                )
                if filter_items(extracted_item):
                    extracted_items.append(extracted_item)

            except Exception as e:
                logger.warning(f"Failed to extract item: {e}")
                continue

        logger.info(
            f"Successfully extracted {len(extracted_items)} items from S3 file {file_url}"
        )
        return extracted_items

    except Exception as e:
        logger.error(f"Error processing S3 file {file_url}: {e}")
        raise


class ExtractedPriceProductItem(BaseModel):
    """Model for extracted price product items from XML files."""

    # Source file metadata
    file_id: str = Field(..., description="Source file ID (placeholder for POC)")

    # Chain/Store context
    chain_id: str = Field(..., description="Chain identifier")
    sub_chain_id: str = Field(..., description="Sub-chain identifier")
    store_id: str = Field(..., description="Store identifier")
    bikoret_no: str = Field(..., description="Bikoret number")

    # Item details
    price_update_date: datetime = Field(..., description="Price update date and time")
    item_code: str = Field(..., description="Item code")
    item_type: str = Field(..., description="Item type")
    item_name: str = Field(..., description="Item name (Hebrew)")
    manufacturer_name: str = Field(..., description="Manufacturer name")
    manufacture_country: str = Field(..., description="Manufacture country code")
    manufacturer_item_description: str = Field(
        ..., description="Manufacturer item description"
    )
    unit_qty: str = Field(..., description="Unit quantity")
    quantity: float = Field(..., description="Quantity value")
    unit_of_measure: str = Field(..., description="Unit of measure")
    is_weighted: bool = Field(..., description="Whether item is weighted")
    qty_in_package: float = Field(..., description="Quantity in package")
    item_price: float = Field(..., description="Item price")
    unit_of_measure_price: float = Field(..., description="Unit of measure price")
    allow_discount: bool = Field(..., description="Whether discount is allowed")
    item_status: str = Field(..., description="Item status")

    # Processing metadata
    extracted_at: datetime = Field(..., description="Timestamp when item was extracted")
