from setuptools import find_packages, setup

setup(
    name="products-watch",
    version="1.0.0",
    description="Products Watch System - Microservices for retail file processing",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.20.0",
        "aiokafka>=0.8.0",
        "pydantic>=2.0.0",
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.0",
        "python-dotenv>=1.0.0",
        "httpx>=0.24.0",
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.0.0",
    ],
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="microservices kafka retail file processing",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/products_watch_4/issues",
        "Source": "https://github.com/yourusername/products_watch_4",
    },
)
