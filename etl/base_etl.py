"""
Base ETL Framework
File: etl/base_etl.py
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import logging
import pandas as pd
import geopandas as gpd
from datetime import datetime
import os
from pathlib import Path

class BaseETL(ABC):
    """Abstract base class for all ETL operations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        self.metadata = {
            'start_time': None,
            'end_time': None,
            'records_processed': 0,
            'records_loaded': 0,
            'errors': []
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for ETL operations"""
        logger = logging.getLogger(f"ETL_{self.__class__.__name__}")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    @abstractmethod
    def extract(self) -> Any:
        """Extract data from source"""
        pass
    
    @abstractmethod
    def transform(self, data: Any) -> Any:
        """Transform extracted data"""
        pass
    
    @abstractmethod
    def load(self, data: Any) -> bool:
        """Load transformed data to destination"""
        pass
    
    def run(self) -> Dict[str, Any]:
        """Execute complete ETL pipeline"""
        self.metadata['start_time'] = datetime.now()
        self.logger.info(f"Starting ETL process: {self.__class__.__name__}")
        
        try:
            # Extract
            self.logger.info("Starting extraction phase")
            raw_data = self.extract()
            
            # Transform
            self.logger.info("Starting transformation phase")
            transformed_data = self.transform(raw_data)
            self.metadata['records_processed'] = len(transformed_data) if hasattr(transformed_data, '__len__') else 0
            
            # Load
            self.logger.info("Starting load phase")
            success = self.load(transformed_data)
            
            if success:
                self.metadata['records_loaded'] = self.metadata['records_processed']
                self.metadata['success'] = True
                self.logger.info("ETL process completed successfully")
            else:
                self.metadata['success'] = False
                self.logger.error("ETL process failed during load phase")
                
        except Exception as e:
            self.logger.error(f"ETL process failed: {str(e)}")
            self.metadata['errors'].append(str(e))
            self.metadata['success'] = False
        
        finally:
            self.metadata['end_time'] = datetime.now()
            self.metadata['duration'] = (
                self.metadata['end_time'] - self.metadata['start_time']
            ).total_seconds()
        
        return self.metadata
