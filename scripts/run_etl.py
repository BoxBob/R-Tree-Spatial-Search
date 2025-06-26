#!/usr/bin/env python3
"""
ETL execution script for spatial search engine
"""

import sys
import os
from pathlib import Path

def setup_project_path():
    """Setup project path for imports based on actual structure"""
    # Get the script directory
    script_dir = Path(__file__).parent
    
    # Project root is parent of scripts directory
    project_root = script_dir.parent
    
    # Add project root to Python path (since modules are at root level)
    sys.path.insert(0, str(project_root))
    
    return project_root

def main():
    # Setup project path
    project_root = setup_project_path()
    
    try:
        # Import from etl directory at root level
        from etl.etl_runner import ETLRunner
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please ensure the ETL runner exists at: etl/etl_runner.py")
        print("Current project structure detected:")
        etl_path = project_root / 'etl'
        if etl_path.exists():
            print(f"✓ ETL directory exists at: {etl_path}")
            etl_runner_path = etl_path / 'etl_runner.py'
            if etl_runner_path.exists():
                print(f"✓ ETL runner exists at: {etl_runner_path}")
            else:
                print(f"✗ ETL runner missing at: {etl_runner_path}")
        else:
            print(f"✗ ETL directory missing at: {etl_path}")
        sys.exit(1)
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Run ETL processes')
    parser.add_argument('--config', help='Path to ETL configuration file')
    parser.add_argument('--process', choices=['property', 'amenity', 'boundary', 'all'], 
                       default='all', help='Which ETL process to run')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging level
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    try:
        # Initialize ETL runner
        runner = ETLRunner(args.config)
        
        # Run specified process
        if args.process == 'property':
            print("Running Property ETL...")
            result = runner.run_property_etl()
        elif args.process == 'amenity':
            print("Running Amenity ETL...")
            result = runner.run_amenity_etl()
        elif args.process == 'boundary':
            print("Running Boundary ETL...")
            result = runner.run_boundary_etl()
        elif args.process == 'all':
            print("Running All ETL Processes...")
            result = runner.run_all_etl()
        else:
            print(f"Process {args.process} not implemented yet")
            return
        
        # Print summary
        summary = runner.get_summary()
        print("\n" + "="*50)
        print("ETL EXECUTION SUMMARY")
        print("="*50)
        print(f"Total processes: {summary['total_processes']}")
        print(f"Successful: {summary['successful']}")
        print(f"Failed: {summary['failed']}")
        print(f"Records processed: {summary['total_records_processed']}")
        print(f"Records loaded: {summary['total_records_loaded']}")
        
        if summary['failed'] > 0:
            print("\nSome processes failed. Check logs for details.")
            sys.exit(1)
        else:
            print("\nAll processes completed successfully!")
            
    except Exception as e:
        print(f"ETL execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
