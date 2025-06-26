#!/usr/bin/env python3
"""
Database Setup Script
File: scripts/setup_database.py
"""

import sys
import os
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


from database.connection import DatabaseManager
import argparse
import logging

def create_database(config):
    """Create database if it doesn't exist"""
    # Connect to postgres database to create our database
    conn = psycopg2.connect(
        host=config.host,
        port=config.port,
        user=config.user,
        password=config.password,
        database='postgres'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", [config.database])
    if not cursor.fetchone():
        cursor.execute(f"CREATE DATABASE {config.database}")
        print(f"Created database: {config.database}")
    else:
        print(f"Database {config.database} already exists")
    
    cursor.close()
    conn.close()

def main():
    parser = argparse.ArgumentParser(description='Setup spatial search database')
    parser.add_argument('--init-sql', default='database/setup/init_database.sql',
                       help='Path to initialization SQL file')
    parser.add_argument('--create-db', action='store_true',
                       help='Create database if it doesn\'t exist')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        db_manager = DatabaseManager()
        
        if args.create_db:
            create_database(db_manager.config)
        
        # Initialize database schema
        if Path(args.init_sql).exists():
            print("Running:", args.init_sql)
            db_manager.initialize_database(args.init_sql)
            logger.info("Database initialization completed successfully")
        else:
            logger.error(f"Initialization SQL file not found: {args.init_sql}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
