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

2. **Access pgAdmin:**
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

## Management Commands

- **Stop services:** `docker-compose down`
- **View logs:** `docker-compose logs -f`
- **Restart services:** `docker-compose restart`
- **Remove volumes (WARNING: deletes all data):** `docker-compose down -v`

## Data Persistence

Database data is persisted in Docker volumes:
- `postgres_data`: PostgreSQL data files
- `pgadmin_data`: pgAdmin configuration and settings
