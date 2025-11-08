from typing import Optional
import asyncpg
from asyncpg import Pool, Connection

from pr_agent.config.settings import settings
from pr_agent.utils.logger import get_logger

logger = get_logger(__name__)

# Global connection pool
_pool: Optional[Pool] = None


async def get_pool() -> Pool:
    """Get or create the database connection pool.
    
    Returns:
        Database connection pool
        
    Raises:
        RuntimeError: If DATABASE_URL is not configured
    """
    global _pool
    
    if _pool is None:
        database_url = settings.database_url
        if not database_url:
            raise RuntimeError(
                "DATABASE_URL environment variable is not set. "
                "Please configure your PostgreSQL connection string."
            )
        
        logger.info(
            "Creating database connection pool",
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow
        )
        
        _pool = await asyncpg.create_pool(
            database_url,
            min_size=1,
            max_size=settings.db_pool_size,
            max_queries=50000,
            max_inactive_connection_lifetime=300.0,
            command_timeout=60.0
        )
        
        logger.info("Database connection pool created successfully")
    
    return _pool


async def close_pool() -> None:
    """Close the database connection pool."""
    global _pool
    
    if _pool:
        logger.info("Closing database connection pool")
        await _pool.close()
        _pool = None
        logger.info("Database connection pool closed")


async def get_connection() -> Connection:
    """Get a connection from the pool.
    
    Returns:
        Database connection
    """
    pool = await get_pool()
    return await pool.acquire()


async def release_connection(conn: Connection) -> None:
    """Release a connection back to the pool.
    
    Args:
        conn: Database connection to release
    """
    pool = await get_pool()
    await pool.release(conn)


async def execute_query(query: str, *args) -> list:
    """Execute a query and return results.
    
    Args:
        query: SQL query string
        *args: Query parameters
        
    Returns:
        List of result rows
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch(query, *args)


async def execute_command(command: str, *args) -> str:
    """Execute a command (INSERT, UPDATE, DELETE) and return result.
    
    Args:
        command: SQL command string
        *args: Command parameters
        
    Returns:
        Result (e.g., inserted ID)
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.fetchval(command, *args)
        return result

