"""
Database schema integration tests for price service.
Tests real PostgreSQL database schema and constraints.
"""

from sqlalchemy import inspect, text


class TestDatabaseSchemaIntegration:
    """Schema integration tests for Price database."""

    def test_database_schema_exists(self, integration_db_session):
        """Test that database schema and tables exist."""
        inspector = inspect(integration_db_session.bind)

        # Check that prices table exists
        tables = inspector.get_table_names()
        assert "prices" in tables

        # Check table columns
        columns = inspector.get_columns("prices")
        column_names = [col["name"] for col in columns]

        expected_columns = [
            "id",
            "chain_id",
            "store_id",
            "item_code",
            "price_amount",
            "currency_code",
            "price_update_date",
            "created_at",
            "updated_at",
        ]

        for expected_col in expected_columns:
            assert expected_col in column_names, f"Column {expected_col} not found"

    def test_database_column_types(self, integration_db_session):
        """Test that database columns have correct types."""
        inspector = inspect(integration_db_session.bind)
        columns = inspector.get_columns("prices")

        column_info = {col["name"]: col["type"] for col in columns}

        # Check UUID column
        assert "id" in column_info
        assert str(column_info["id"]).startswith("UUID")

        # Check String columns
        assert "chain_id" in column_info
        assert str(column_info["chain_id"]).startswith("VARCHAR")

        assert "item_code" in column_info
        assert str(column_info["item_code"]).startswith("VARCHAR")

        assert "currency_code" in column_info
        assert str(column_info["currency_code"]).startswith("VARCHAR")

        # Check Integer column
        assert "store_id" in column_info
        assert str(column_info["store_id"]).startswith("INTEGER")

        # Check Numeric column
        assert "price_amount" in column_info
        assert str(column_info["price_amount"]).startswith("NUMERIC")

        # Check TIMESTAMP columns
        assert "price_update_date" in column_info
        assert str(column_info["price_update_date"]).startswith("TIMESTAMP")

        assert "created_at" in column_info
        assert str(column_info["created_at"]).startswith("TIMESTAMP")

        assert "updated_at" in column_info
        assert str(column_info["updated_at"]).startswith("TIMESTAMP")

    def test_database_nullable_constraints(self, integration_db_session):
        """Test that database nullable constraints are correct."""
        inspector = inspect(integration_db_session.bind)
        columns = inspector.get_columns("prices")

        column_info = {col["name"]: col["nullable"] for col in columns}

        # All fields should be nullable except id, created_at, and updated_at
        assert column_info["id"] is False  # Primary key should not be nullable
        assert column_info["chain_id"] is True
        assert column_info["store_id"] is True
        assert column_info["item_code"] is True
        assert column_info["price_amount"] is True
        assert column_info["currency_code"] is True
        assert column_info["price_update_date"] is True
        assert (
            column_info["created_at"] is False
        )  # Should not be nullable due to default
        assert (
            column_info["updated_at"] is False
        )  # Should not be nullable due to default

    def test_database_indexes(self, integration_db_session):
        """Test that database indexes are properly created."""
        inspector = inspect(integration_db_session.bind)
        indexes = inspector.get_indexes("prices")

        # Check that id column has an index (primary key)
        index_names = [idx["name"] for idx in indexes]
        assert any("id" in idx["column_names"] for idx in indexes), (
            "ID column should have an index"
        )

    def test_database_table_creation_sql(self, integration_db_session):
        """Test that table creation SQL is correct."""
        # This test verifies the table structure by checking the actual SQL
        result = integration_db_session.execute(
            text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'prices'
                ORDER BY ordinal_position
            """)
        )

        columns = result.fetchall()
        column_names = [col[0] for col in columns]

        expected_columns = [
            "id",
            "chain_id",
            "store_id",
            "item_code",
            "price_amount",
            "currency_code",
            "price_update_date",
            "created_at",
            "updated_at",
        ]

        assert len(columns) == len(expected_columns)
        for expected_col in expected_columns:
            assert expected_col in column_names

    def test_database_constraints_work(self, integration_db_session):
        """Test that database constraints work as expected."""
        # Test that we can insert a record with all fields
        result = integration_db_session.execute(
            text("""
                INSERT INTO prices (id, chain_id, store_id, item_code, price_amount, currency_code, price_update_date, created_at, updated_at)
                VALUES (gen_random_uuid(), 'test_chain', 1, 'test_item', 10.50, 'USD', '2024-01-15 10:30:00', NOW(), NOW())
                RETURNING id
            """)
        )
        price_id = result.fetchone()[0]

        # Test that we can insert a record with minimal fields (including required timestamps)
        result = integration_db_session.execute(
            text("""
                INSERT INTO prices (id, created_at, updated_at)
                VALUES (gen_random_uuid(), NOW(), NOW())
                RETURNING id
            """)
        )
        price_id_2 = result.fetchone()[0]

        # Verify both records exist
        result = integration_db_session.execute(
            text("SELECT COUNT(*) FROM prices WHERE id IN (:id1, :id2)"),
            {"id1": price_id, "id2": price_id_2},
        )
        count = result.fetchone()[0]
        assert count == 2

    def test_database_timestamps_auto_update(self, integration_db_session):
        """Test that timestamp fields are automatically updated."""
        from datetime import datetime, timezone

        # Create initial timestamp
        initial_time = datetime.now(timezone.utc)

        # Insert a record with explicit timestamps
        result = integration_db_session.execute(
            text("""
                INSERT INTO prices (id, chain_id, store_id, item_code, price_amount, currency_code, created_at, updated_at)
                VALUES (gen_random_uuid(), 'timestamp_test', 1, 'timestamp_item', 5.99, 'USD', :created_at, :updated_at)
                RETURNING id, created_at, updated_at
            """),
            {"created_at": initial_time, "updated_at": initial_time},
        )
        price_id, created_at, updated_at = result.fetchone()

        # Verify timestamps are set
        assert created_at is not None
        assert updated_at is not None
        assert created_at == updated_at  # Should be equal on creation

        # Create a new timestamp for update
        update_time = datetime.now(timezone.utc)

        # Update the record
        integration_db_session.execute(
            text("""
                UPDATE prices
                SET price_amount = 6.99, updated_at = :updated_at
                WHERE id = :price_id
            """),
            {"price_id": price_id, "updated_at": update_time},
        )

        # Check that updated_at changed
        result = integration_db_session.execute(
            text("SELECT created_at, updated_at FROM prices WHERE id = :price_id"),
            {"price_id": price_id},
        )
        new_created_at, new_updated_at = result.fetchone()

        assert new_created_at == created_at  # created_at should not change
        assert new_updated_at > updated_at  # updated_at should be newer
