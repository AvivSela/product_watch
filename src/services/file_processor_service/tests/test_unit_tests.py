"""
Unit tests for file_processor_service that can run without infrastructure.
"""

# Add the project root to the Python path
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from services.file_processor_service.file_processor import (
    ExtractedPriceProductItem,
    process_xml_file,
)


@pytest.mark.integration
class TestFileProcessorUnitTests:
    """Unit tests for file processor service that can run without infrastructure."""

    def test_extracted_price_product_item_creation(self):
        """Test that ExtractedPriceProductItem can be created correctly."""
        item = ExtractedPriceProductItem(
            file_id="test-file-id",
            chain_id="7290027600007",
            sub_chain_id="001",
            store_id="1",
            bikoret_no="12345",
            price_update_date=datetime.now(timezone.utc),
            item_code="123456789",
            item_type="1",
            item_name="Test Product",
            manufacturer_name="Test Manufacturer",
            manufacture_country="IL",
            manufacturer_item_description="Test Description",
            unit_qty="1",
            quantity=1.0,
            unit_of_measure="יחידה",
            is_weighted=False,
            qty_in_package=1.0,
            item_price=10.50,
            unit_of_measure_price=10.50,
            allow_discount=True,
            item_status="1",
            extracted_at=datetime.now(timezone.utc),
        )

        assert item.item_code == "123456789"
        assert item.item_name == "Test Product"
        assert item.item_price == 10.50
        assert item.chain_id == "7290027600007"
        assert item.store_id == "1"

    def test_process_xml_file_with_mock_s3(self):
        """Test XML file processing with mocked S3 client."""
        # Sample XML content
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<Root>
    <ChainId>7290027600007</ChainId>
    <SubChainId>001</SubChainId>
    <StoreId>1</StoreId>
    <BikoretNo>12345</BikoretNo>
    <Items>
        <Item>
            <ItemCode>123456789</ItemCode>
            <ItemType>1</ItemType>
            <ItemNm>Test Product 1</ItemNm>
            <ManufacturerName>Test Manufacturer</ManufacturerName>
            <ManufactureCountry>IL</ManufactureCountry>
            <ManufacturerItemDescription>Test Description</ManufacturerItemDescription>
            <UnitQty>1</UnitQty>
            <Quantity>1.0</Quantity>
            <UnitOfMeasure>יחידה</UnitOfMeasure>
            <bIsWeighted>0</bIsWeighted>
            <QtyInPackage>1.0</QtyInPackage>
            <ItemPrice>10.50</ItemPrice>
            <UnitOfMeasurePrice>10.50</UnitOfMeasurePrice>
            <AllowDiscount>1</AllowDiscount>
            <ItemStatus>1</ItemStatus>
            <PriceUpdateDate>2024-01-15T10:30:00</PriceUpdateDate>
        </Item>
        <Item>
            <ItemCode>987654321</ItemCode>
            <ItemType>1</ItemType>
            <ItemNm>Test Product 2</ItemNm>
            <ManufacturerName>Test Manufacturer 2</ManufacturerName>
            <ManufactureCountry>US</ManufactureCountry>
            <ManufacturerItemDescription>Test Description 2</ManufacturerItemDescription>
            <UnitQty>2</UnitQty>
            <Quantity>2.0</Quantity>
            <UnitOfMeasure>יחידה</UnitOfMeasure>
            <bIsWeighted>0</bIsWeighted>
            <QtyInPackage>2.0</QtyInPackage>
            <ItemPrice>25.99</ItemPrice>
            <UnitOfMeasurePrice>12.995</UnitOfMeasurePrice>
            <AllowDiscount>1</AllowDiscount>
            <ItemStatus>1</ItemStatus>
            <PriceUpdateDate>2024-01-15T11:00:00</PriceUpdateDate>
        </Item>
    </Items>
</Root>"""

        # Mock S3 client
        mock_s3_client = MagicMock()
        mock_s3_client.url_exists.return_value = True
        mock_s3_client.get_object.return_value = xml_content.encode("utf-8")

        # Test the process_xml_file function
        items = process_xml_file(
            file_url="s3://test-bucket/test-file.xml",
            file_id="test-file-id",
            s3_client=mock_s3_client,
        )

        # Verify results
        assert len(items) == 2

        # Check first item
        item1 = items[0]
        assert item1.item_code == "123456789"
        assert item1.item_name == "Test Product 1"
        assert item1.item_price == 10.50
        assert item1.manufacturer_name == "Test Manufacturer"
        assert item1.chain_id == "7290027600007"
        assert item1.store_id == "1"
        assert not item1.is_weighted
        assert item1.allow_discount

        # Check second item
        item2 = items[1]
        assert item2.item_code == "987654321"
        assert item2.item_name == "Test Product 2"
        assert item2.item_price == 25.99
        assert item2.manufacturer_name == "Test Manufacturer 2"
        assert item2.chain_id == "7290027600007"
        assert item2.store_id == "1"

    def test_process_xml_file_with_compressed_data(self):
        """Test XML file processing with compressed data."""
        import gzip

        # Sample XML content
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<Root>
    <ChainId>7290027600007</ChainId>
    <SubChainId>001</SubChainId>
    <StoreId>1</StoreId>
    <BikoretNo>12345</BikoretNo>
    <Items>
        <Item>
            <ItemCode>123456789</ItemCode>
            <ItemType>1</ItemType>
            <ItemNm>Test Product</ItemNm>
            <ManufacturerName>Test Manufacturer</ManufacturerName>
            <ManufactureCountry>IL</ManufactureCountry>
            <ManufacturerItemDescription>Test Description</ManufacturerItemDescription>
            <UnitQty>1</UnitQty>
            <Quantity>1.0</Quantity>
            <UnitOfMeasure>יחידה</UnitOfMeasure>
            <bIsWeighted>0</bIsWeighted>
            <QtyInPackage>1.0</QtyInPackage>
            <ItemPrice>10.50</ItemPrice>
            <UnitOfMeasurePrice>10.50</UnitOfMeasurePrice>
            <AllowDiscount>1</AllowDiscount>
            <ItemStatus>1</ItemStatus>
            <PriceUpdateDate>2024-01-15T10:30:00</PriceUpdateDate>
        </Item>
    </Items>
</Root>"""

        # Compress the XML content
        compressed_data = gzip.compress(xml_content.encode("utf-8"))

        # Mock S3 client
        mock_s3_client = MagicMock()
        mock_s3_client.url_exists.return_value = True
        mock_s3_client.get_object.return_value = compressed_data

        # Test the process_xml_file function
        items = process_xml_file(
            file_url="s3://test-bucket/test-file.xml.gz",
            file_id="test-file-id",
            s3_client=mock_s3_client,
        )

        # Verify results
        assert len(items) == 1
        item = items[0]
        assert item.item_code == "123456789"
        assert item.item_name == "Test Product"
        assert item.item_price == 10.50

    def test_process_xml_file_with_missing_file(self):
        """Test XML file processing when file doesn't exist."""
        # Mock S3 client that returns False for url_exists
        mock_s3_client = MagicMock()
        mock_s3_client.url_exists.return_value = False

        # Test the process_xml_file function
        with pytest.raises(Exception, match="File not found in S3"):
            process_xml_file(
                file_url="s3://test-bucket/nonexistent-file.xml",
                file_id="test-file-id",
                s3_client=mock_s3_client,
            )

    def test_process_xml_file_with_invalid_xml(self):
        """Test XML file processing with invalid XML."""
        # Mock S3 client
        mock_s3_client = MagicMock()
        mock_s3_client.url_exists.return_value = True
        mock_s3_client.get_object.return_value = b"Invalid XML content"

        # Test the process_xml_file function
        with pytest.raises(Exception):
            process_xml_file(
                file_url="s3://test-bucket/invalid-file.xml",
                file_id="test-file-id",
                s3_client=mock_s3_client,
            )

    def test_extracted_price_product_item_json_serialization(self):
        """Test that ExtractedPriceProductItem can be serialized to JSON."""
        item = ExtractedPriceProductItem(
            file_id="test-file-id",
            chain_id="7290027600007",
            sub_chain_id="001",
            store_id="1",
            bikoret_no="12345",
            price_update_date=datetime.now(timezone.utc),
            item_code="123456789",
            item_type="1",
            item_name="Test Product",
            manufacturer_name="Test Manufacturer",
            manufacture_country="IL",
            manufacturer_item_description="Test Description",
            unit_qty="1",
            quantity=1.0,
            unit_of_measure="יחידה",
            is_weighted=False,
            qty_in_package=1.0,
            item_price=10.50,
            unit_of_measure_price=10.50,
            allow_discount=True,
            item_status="1",
            extracted_at=datetime.now(timezone.utc),
        )

        # Test JSON serialization
        json_data = item.model_dump_json()
        assert isinstance(json_data, str)
        assert "123456789" in json_data
        assert "Test Product" in json_data
        assert "10.5" in json_data  # JSON serializes floats without trailing zeros

    def test_message_flow_simulation(self):
        """Test the complete message flow simulation."""
        # This test simulates the complete flow without requiring real services

        # Step 1: Simulate retail file creation
        retail_file_data = {
            "id": "test-retail-file-id",
            "chain_id": "7290027600007",
            "store_id": 1,
            "file_name": "test_price_file.xml.gz",
            "file_path": "s3://test-bucket/test_price_file.xml.gz",
            "file_size": 1024,
            "upload_date": datetime.now(timezone.utc).isoformat(),
            "is_processed": False,
        }

        # Step 2: Simulate Kafka message production (for documentation)
        # retail_file_message = {
        #     "event_type": "retail_file_created",
        #     "data": retail_file_data,
        # }

        # Step 3: Simulate message consumption and processing
        mock_s3_client = MagicMock()
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<Root>
    <ChainId>7290027600007</ChainId>
    <SubChainId>001</SubChainId>
    <StoreId>1</StoreId>
    <BikoretNo>12345</BikoretNo>
    <Items>
        <Item>
            <ItemCode>123456789</ItemCode>
            <ItemType>1</ItemType>
            <ItemNm>Test Product</ItemNm>
            <ManufacturerName>Test Manufacturer</ManufacturerName>
            <ManufactureCountry>IL</ManufactureCountry>
            <ManufacturerItemDescription>Test Description</ManufacturerItemDescription>
            <UnitQty>1</UnitQty>
            <Quantity>1.0</Quantity>
            <UnitOfMeasure>יחידה</UnitOfMeasure>
            <bIsWeighted>0</bIsWeighted>
            <QtyInPackage>1.0</QtyInPackage>
            <ItemPrice>10.50</ItemPrice>
            <UnitOfMeasurePrice>10.50</UnitOfMeasurePrice>
            <AllowDiscount>1</AllowDiscount>
            <ItemStatus>1</ItemStatus>
            <PriceUpdateDate>2024-01-15T10:30:00</PriceUpdateDate>
        </Item>
    </Items>
</Root>"""

        mock_s3_client.url_exists.return_value = True
        mock_s3_client.get_object.return_value = xml_content.encode("utf-8")

        # Process the file
        items = process_xml_file(
            file_url=retail_file_data["file_path"],
            file_id=retail_file_data["id"],
            s3_client=mock_s3_client,
        )

        # Step 4: Simulate processed items production
        processed_messages = []
        for item in items:
            processed_message = {
                "topic": "retail-product-updates",
                "key": item.item_code,
                "value": item.model_dump(),
            }
            processed_messages.append(processed_message)

        # Verify the complete flow
        assert len(processed_messages) == 1
        assert processed_messages[0]["key"] == "123456789"
        assert processed_messages[0]["value"]["item_name"] == "Test Product"
        assert processed_messages[0]["value"]["item_price"] == 10.50
        assert processed_messages[0]["value"]["file_id"] == "test-retail-file-id"

        print("✅ Complete message flow simulation test passed!")
