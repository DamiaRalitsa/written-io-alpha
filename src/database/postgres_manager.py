"""
PostgreSQL Database Connection Manager for Written AI Chatbot
Python equivalent of the Go connection.go file
"""

import os
import time
import threading
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from dataclasses import dataclass

import psycopg2
from psycopg2 import pool, extras
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from loguru import logger
from config.settings import settings


@dataclass
class DatabaseConfig:
    """Database configuration data class"""
    host: str
    port: int
    user: str
    password: str
    database: str
    max_pool: int = 20
    min_pool: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600  # 1 hour


class DatabaseConnectionError(Exception):
    """Custom exception for database connection errors"""
    pass


class DatabaseManager:
    """
    PostgreSQL Database Manager with connection pooling
    Python equivalent of Go's DatabaseManager interface
    """
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine: Optional[Engine] = None
        self.connection_pool: Optional[pool.ThreadedConnectionPool] = None
        self._lock = threading.Lock()
        self._initialized = False
        
    def get_connection_string(self) -> str:
        """Build PostgreSQL connection string"""
        return (
            f"postgresql://{self.config.user}:{self.config.password}@"
            f"{self.config.host}:{self.config.port}/{self.config.database}"
        )
    
    def connect(self) -> Engine:
        """
        Initialize database connection with SQLAlchemy engine
        Returns the SQLAlchemy engine for ORM operations
        """
        if self.engine is not None:
            return self.engine
            
        with self._lock:
            if self.engine is not None:
                return self.engine
                
            try:
                connection_string = self.get_connection_string()
                logger.info(f"postgres: Initializing connection to {self.config.host}:{self.config.port}")
                
                # Create SQLAlchemy engine with connection pooling
                self.engine = create_engine(
                    connection_string,
                    poolclass=QueuePool,
                    pool_size=self.config.min_pool,
                    max_overflow=self.config.max_overflow,
                    pool_timeout=self.config.pool_timeout,
                    pool_recycle=self.config.pool_recycle,
                    pool_pre_ping=True,  # Validate connections before use
                    echo=False  # Set to True for SQL debugging
                )
                
                # Test the connection
                with self.engine.connect() as conn:
                    result = conn.execute(text("SELECT 1"))
                    logger.info("postgres: Connection test successful")
                
                self._init_raw_connection_pool()
                self._initialized = True
                
                logger.info("postgres: PostgreSQL initialized successfully")
                return self.engine
                
            except Exception as e:
                logger.error(f"postgres: Failed to connect to PostgreSQL: {str(e)}")
                raise DatabaseConnectionError(f"Failed to connect to database: {str(e)}")
    
    def _init_raw_connection_pool(self):
        """Initialize raw psycopg2 connection pool for non-ORM operations"""
        try:
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=self.config.min_pool,
                maxconn=self.config.max_pool,
                host=self.config.host,
                port=self.config.port,
                user=self.config.user,
                password=self.config.password,
                database=self.config.database,
                cursor_factory=extras.RealDictCursor  # Return results as dictionaries
            )
            logger.info("postgres: Raw connection pool initialized")
        except Exception as e:
            logger.error(f"postgres: Failed to initialize connection pool: {str(e)}")
            raise DatabaseConnectionError(f"Failed to initialize connection pool: {str(e)}")
    
    def get_engine(self) -> Engine:
        """Get SQLAlchemy engine (for ORM operations)"""
        if not self._initialized or self.engine is None:
            raise DatabaseConnectionError("Database connection is not initialized")
        return self.engine
    
    @contextmanager
    def get_connection(self):
        """
        Get a raw database connection from the pool
        Use this for direct SQL operations outside of SQLAlchemy ORM
        """
        if self.connection_pool is None:
            raise DatabaseConnectionError("Connection pool is not initialized")
        
        connection = None
        try:
            connection = self.connection_pool.getconn()
            if connection is None:
                raise DatabaseConnectionError("Failed to get connection from pool")
            
            # Log connection stats if too many connections are open
            if hasattr(self.connection_pool, '_used') and len(self.connection_pool._used) > 15:
                logger.warning(f"postgres: High connection usage: {len(self.connection_pool._used)} connections")
            
            yield connection
            
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"postgres: Database operation failed: {str(e)}")
            raise
        finally:
            if connection:
                self.connection_pool.putconn(connection)
    
    def execute_query(self, query: str, params: Optional[tuple] = None, fetch_one: bool = False) -> Optional[List[Dict[str, Any]]]:
        """
        Execute a SELECT query and return results
        Python equivalent of the DatabaseHandlerFunc for SELECT operations
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute(query, params)
                    
                    if fetch_one:
                        result = cursor.fetchone()
                        return dict(result) if result else None
                    else:
                        results = cursor.fetchall()
                        return [dict(row) for row in results] if results else []
                        
                except Exception as e:
                    logger.error(f"postgres: Query execution failed: {str(e)}")
                    raise
    
    def execute_command(self, query: str, params: Optional[tuple] = None) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE command
        Python equivalent of the DatabaseHandlerFunc for EXEC operations
        Returns the number of affected rows
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute(query, params)
                    affected_rows = cursor.rowcount
                    conn.commit()
                    
                    if affected_rows == 0:
                        logger.warning("postgres: No rows affected by the query")
                    
                    return affected_rows
                    
                except Exception as e:
                    conn.rollback()
                    logger.error(f"postgres: Command execution failed: {str(e)}")
                    raise
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """Execute a query with multiple parameter sets"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.executemany(query, params_list)
                    affected_rows = cursor.rowcount
                    conn.commit()
                    return affected_rows
                except Exception as e:
                    conn.rollback()
                    logger.error(f"postgres: Batch execution failed: {str(e)}")
                    raise
    
    def test_connection(self) -> bool:
        """Test if the database connection is working"""
        try:
            result = self.execute_query("SELECT 1 as test", fetch_one=True)
            return result is not None and result.get('test') == 1
        except Exception as e:
            logger.error(f"postgres: Connection test failed: {str(e)}")
            return False
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        if self.connection_pool is None:
            return {"status": "not_initialized"}
        
        # Note: psycopg2 pool doesn't expose detailed stats like Go's sqlx
        # This is a basic implementation
        stats = {
            "status": "initialized",
            "min_connections": self.config.min_pool,
            "max_connections": self.config.max_pool,
        }
        
        if hasattr(self.connection_pool, '_used'):
            stats["active_connections"] = len(self.connection_pool._used)
        
        return stats
    
    def close(self):
        """Close all database connections"""
        try:
            if self.connection_pool:
                self.connection_pool.closeall()
                logger.info("postgres: Connection pool closed")
            
            if self.engine:
                self.engine.dispose()
                logger.info("postgres: SQLAlchemy engine disposed")
                
            self._initialized = False
            
        except Exception as e:
            logger.error(f"postgres: Error closing database connections: {str(e)}")


# Singleton pattern for global database instance
class DatabaseSingleton:
    """Singleton database manager instance"""
    _instance: Optional[DatabaseManager] = None
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls) -> DatabaseManager:
        """Get or create the singleton database manager instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    # Parse database configuration from settings
                    if settings.database_url.startswith('postgresql://'):
                        # Parse from URL
                        import urllib.parse as urlparse
                        parsed = urlparse.urlparse(settings.database_url)
                        
                        config = DatabaseConfig(
                            host=parsed.hostname or 'localhost',
                            port=parsed.port or 5432,
                            user=parsed.username or 'postgres',
                            password=parsed.password or '',
                            database=parsed.path.lstrip('/') or 'postgres'
                        )
                    else:
                        # Use individual settings (fallback)
                        config = DatabaseConfig(
                            host=getattr(settings, 'postgres_host', 'localhost'),
                            port=getattr(settings, 'postgres_port', 5432),
                            user=getattr(settings, 'postgres_user', 'postgres'),
                            password=getattr(settings, 'postgres_password', ''),
                            database=getattr(settings, 'postgres_db', 'postgres')
                        )
                    
                    cls._instance = DatabaseManager(config)
                    cls._instance.connect()
        
        return cls._instance
    
    @classmethod
    def close_instance(cls):
        """Close the singleton instance"""
        if cls._instance:
            cls._instance.close()
            cls._instance = None


# Global database manager instance
def get_database_manager() -> DatabaseManager:
    """Get the global database manager instance"""
    return DatabaseSingleton.get_instance()


# Convenience functions (equivalent to your Go functions)
def init_connection() -> DatabaseManager:
    """Initialize database connection (equivalent to Go's InitConnection)"""
    return get_database_manager()


def get_db_connection():
    """Get database connection (equivalent to Go's GetDB)"""
    return get_database_manager().get_connection()


def get_db_engine() -> Engine:
    """Get SQLAlchemy engine for ORM operations"""
    return get_database_manager().get_engine()


def close_database():
    """Close database connections"""
    DatabaseSingleton.close_instance()


# Database handler function type (equivalent to Go's DatabaseHandlerFunc)
def create_database_handler():
    """
    Create a database handler function
    Equivalent to Go's CreateDatabaseHandler method
    """
    db_manager = get_database_manager()
    
    def handler(query: str, params: Optional[tuple] = None, is_exec: bool = False, fetch_one: bool = False):
        """Database handler function"""
        if is_exec:
            return db_manager.execute_command(query, params)
        else:
            return db_manager.execute_query(query, params, fetch_one)
    
    return handler
