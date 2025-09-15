# About
A comprehensive microservices architecture for processing retail product data, featuring automated file processing, price tracking, and store management. Built with FastAPI, PostgreSQL, Kafka, and Docker.
Key Features:
🏪 Store Management - Multi-chain store registration and management
📦 Product Catalog - Product information and metadata management
💰 Price Tracking - Real-time price monitoring and updates
📄 File Processing - Automated XML/CSV retail file processing with S3 integration
🔄 Event Streaming - Kafka-based asynchronous data processing
🐳 Containerized - Full Docker Compose setup with PostgreSQL, Kafka, MinIO, and pgAdmin

# Products Watch - Docker Setup

This project includes a Docker Compose setup with PostgreSQL database and pgAdmin for database management.

## Services

- **PostgreSQL**: Database server running on port 5432
- **pgAdmin**: Web-based PostgreSQL administration tool running on port 8080

## Quick Start

1. **Start the services:**
   ```bash
   docker-compose up -d
   ```

2. **Initialize the database:**
   ```bash
   # Option 1: Using centralized script (recommended)
   python scripts/init_database.py

   # Option 2: Initialize individual services
   python src/services/store_service/database.py
   python src/services/product_service/database.py
   python src/services/price_service/database.py
   python src/services/retail_file_service/database.py
   ```

3. **Access pgAdmin:**
   - Open your browser and go to `http://localhost:8080`
   - Login with the credentials from `docker.env`:
     - Email: `admin@example.com`
     - Password: `admin`

3. **Connect to PostgreSQL in pgAdmin:**
   - Right-click "Servers" → "Create" → "Server"
   - General tab: Name: `Products Watch DB`
   - Connection tab:
     - Host: `postgres` (container name)
     - Port: `5432`
     - Database: `products_watch`
     - Username: `postgres`
     - Password: `password`

## Configuration

Edit `docker.env` to customize:
- Database name, user, and password
- pgAdmin email and password

## Database Connection

From your application, connect to PostgreSQL using:
- Host: `localhost` (or `postgres` if connecting from another container)
- Port: `5432`
- Database: `products_watch`
- Username: `postgres`
- Password: `password`

## Database Initialization

The project includes a centralized database initialization script that creates all tables for all microservices:

### Features:
- ✅ **Centralized**: One script initializes all services
- ✅ **Connection Testing**: Verifies database connectivity before creating tables
- ✅ **Error Handling**: Provides clear error messages and status updates
- ✅ **Table Detection**: Shows which tables were created vs. already existing
- ✅ **Service Summary**: Lists all tables created for each service

### Usage:
```bash
# Initialize all database tables
python scripts/init_database.py
```

### Environment Variables:
- `DATABASE_URL`: PostgreSQL connection string (default: `postgresql://postgres:password@localhost:5432/products_watch`)

## Management Commands

- **Stop services:** `docker-compose down`
- **View logs:** `docker-compose logs -f`
- **Restart services:** `docker-compose restart`
- **Remove volumes (WARNING: deletes all data):** `docker-compose down -v`
- **Reinitialize database:** `python scripts/init_database.py`

## Data Persistence

Database data is persisted in Docker volumes:
- `postgres_data`: PostgreSQL data files
- `pgadmin_data`: pgAdmin configuration and settings
