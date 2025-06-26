"""
ETL Execution Manager
File: etl/etl_runner.py
"""

from typing import Dict, Any, List
import logging
from datetime import datetime
from pathlib import Path
import sys
import os

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import configuration manager
from etl.etl_config import ETLConfig

class ETLRunner:
    """Orchestrate and run multiple ETL processes"""
    
    def __init__(self, config_path: str = None):
        self.config_manager = ETLConfig(config_path)
        self.logger = self._setup_logging()
        self.results = {}
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for ETL runner"""
        logger = logging.getLogger("ETLRunner")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # Ensure logs directory exists
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            # File handler
            log_file = log_dir / f"etl_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            file_handler = logging.FileHandler(log_file)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(file_formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def run_property_etl(self) -> Dict[str, Any]:
        """Run property data ETL"""
        self.logger.info("Starting Property ETL")
        
        try:
            from etl.property_etl import PropertyETL
            
            config = self.config_manager.get_config('property_etl')
            etl = PropertyETL(config)
            result = etl.run()
            
            self.results['property_etl'] = result
            return result
            
        except Exception as e:
            self.logger.error(f"Property ETL failed: {e}")
            error_result = {
                'success': False,
                'error': str(e),
                'records_processed': 0,
                'records_loaded': 0
            }
            self.results['property_etl'] = error_result
            return error_result
    
    def run_amenity_etl(self) -> Dict[str, Any]:
        """Run amenity data ETL"""
        self.logger.info("Starting Amenity ETL")
        
        try:
            from etl.amenity_etl import AmenityETL
            
            config = self.config_manager.get_config('amenity_etl')
            etl = AmenityETL(config)
            result = etl.run()
            
            self.results['amenity_etl'] = result
            return result
            
        except Exception as e:
            self.logger.error(f"Amenity ETL failed: {e}")
            error_result = {
                'success': False,
                'error': str(e),
                'records_processed': 0,
                'records_loaded': 0
            }
            self.results['amenity_etl'] = error_result
            return error_result
    
    def run_boundary_etl(self) -> Dict[str, Any]:
        """Run boundary data ETL"""
        self.logger.info("Starting Boundary ETL")
        
        try:
            from etl.boundary_etl import BoundaryETL
            
            config = self.config_manager.get_config('boundary_etl')
            etl = BoundaryETL(config)
            result = etl.run()
            
            self.results['boundary_etl'] = result
            return result
            
        except Exception as e:
            self.logger.error(f"Boundary ETL failed: {e}")
            error_result = {
                'success': False,
                'error': str(e),
                'records_processed': 0,
                'records_loaded': 0
            }
            self.results['boundary_etl'] = error_result
            return error_result
    
    def run_all_etl(self) -> Dict[str, Any]:
        """Run all configured ETL processes"""
        self.logger.info("Starting complete ETL pipeline")
        
        etl_processes = [
            ('property_etl', self.run_property_etl),
            ('amenity_etl', self.run_amenity_etl),
            ('boundary_etl', self.run_boundary_etl),
        ]
        
        for process_name, process_func in etl_processes:
            try:
                self.logger.info(f"Running {process_name}")
                result = process_func()
                
                if result.get('errors') or not result.get('success', True):
                    self.logger.warning(f"{process_name} completed with errors")
                else:
                    self.logger.info(f"{process_name} completed successfully")
                    
            except Exception as e:
                self.logger.error(f"{process_name} failed: {e}")
                self.results[process_name] = {
                    'success': False,
                    'error': str(e),
                    'records_processed': 0,
                    'records_loaded': 0
                }
        
        return self.results
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all ETL runs"""
        summary = {
            'total_processes': len(self.results),
            'successful': 0,
            'failed': 0,
            'total_records_processed': 0,
            'total_records_loaded': 0
        }
        
        for process_name, result in self.results.items():
            if result.get('errors') or not result.get('success', True):
                summary['failed'] += 1
            else:
                summary['successful'] += 1
            
            summary['total_records_processed'] += result.get('records_processed', 0)
            summary['total_records_loaded'] += result.get('records_loaded', 0)
        
        return summary
