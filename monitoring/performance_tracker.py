"""
Performance Tracking for Spatial Queries
File: src/spatial_search_engine/monitoring/performance_tracker.py
"""

import time
import logging
from functools import wraps
from typing import Dict, Any, Callable
import json
from ..database.connection import db

class PerformanceTracker:
    """Track and analyze query performance"""
    
    def __init__(self):
        self.query_stats = {
            'total_queries': 0,
            'avg_response_time': 0,
            'slow_queries': [],
            'query_types': {}
        }
        self.logger = logging.getLogger(__name__)
    
    def track_query(self, query_type: str):
        """Decorator to track query performance"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    # Update statistics
                    self._update_stats(query_type, execution_time, True, len(result) if hasattr(result, '__len__') else 0)
                    
                    # Log slow queries
                    if execution_time > 2.0:  # 2 seconds threshold
                        self._log_slow_query(query_type, execution_time, args, kwargs)
                    
                    # Store in database
                    self._store_performance_data(query_type, execution_time, len(result) if hasattr(result, '__len__') else 0)
                    
                    return result
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    self._update_stats(query_type, execution_time, False, 0)
                    raise
                    
            return wrapper
        return decorator
    
    def _update_stats(self, query_type: str, execution_time: float, success: bool, result_count: int):
        """Update performance statistics"""
        self.query_stats['total_queries'] += 1
        
        # Update average response time
        current_avg = self.query_stats['avg_response_time']
        total_queries = self.query_stats['total_queries']
        self.query_stats['avg_response_time'] = (
            (current_avg * (total_queries - 1) + execution_time) / total_queries
        )
        
        # Update query type stats
        if query_type not in self.query_stats['query_types']:
            self.query_stats['query_types'][query_type] = {
                'count': 0,
                'avg_time': 0,
                'success_rate': 0,
                'total_results': 0
            }
        
        type_stats = self.query_stats['query_types'][query_type]
        type_stats['count'] += 1
        type_stats['avg_time'] = (
            (type_stats['avg_time'] * (type_stats['count'] - 1) + execution_time) 
            / type_stats['count']
        )
        type_stats['total_results'] += result_count
        
        # Update success rate
        if success:
            type_stats['success_rate'] = (
                (type_stats['success_rate'] * (type_stats['count'] - 1) + 1) 
                / type_stats['count']
            )
    
    def _store_performance_data(self, query_type: str, execution_time: float, result_count: int):
        """Store performance data in database"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                insert_query = """
                    INSERT INTO analytics.query_performance 
                    (query_type, execution_time_ms, result_count, created_at)
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                """
                
                cursor.execute(insert_query, [
                    query_type,
                    int(execution_time * 1000),  # Convert to milliseconds
                    result_count
                ])
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to store performance data: {e}")

# Global performance tracker instance
performance_tracker = PerformanceTracker()
