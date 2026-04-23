import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER", "testuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "testpass")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5433"))
DB_NAME = os.getenv("DB_NAME", "my_app_db")

pool = None

async def connect_to_db():
    global pool
    pool = await asyncpg.create_pool(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST,
        port=DB_PORT
    )

async def close_db():
    global pool
    if pool:
        await pool.close()

async def get_search_results(filters=None):
    if filters is None:
        filters = {}

    tag_ids = filters.get("tag_ids")
    search = filters.get("search")

    query = """
        SELECT
            ki.*, 
            primary_t.name AS tag_name,
            COALESCE(array_remove(array_agg(DISTINCT t.name), NULL), '{}') AS tag_names
        FROM KnowledgeItems ki
        LEFT JOIN tags primary_t ON ki.tags_id = primary_t.id
        LEFT JOIN ItemTags it ON it.knowledge_item_id = ki.id
        LEFT JOIN tags t ON t.id = it.tags_id
    """
    conditions = []
    values = []

    if tag_ids:
        # Filter items that have ALL the specified tag IDs
        tag_ids_list = tag_ids
        conditions.append(f"""
            (
                SELECT COUNT(DISTINCT it_filter.tags_id)
                FROM ItemTags it_filter
                WHERE it_filter.knowledge_item_id = ki.id
                  AND it_filter.tags_id = ANY(${len(values) + 1})
            ) = {len(tag_ids_list)}
        """
        )
        values.append(tag_ids_list)

    if search:
        conditions.append(f"(ki.title ILIKE ${len(values) + 1} OR ki.content ILIKE ${len(values) + 1})")
        values.append(f"%{search}%")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " GROUP BY ki.id, primary_t.name ORDER BY ki.created_at DESC"

    async with pool.acquire() as connection:
        rows = await connection.fetch(query, *values)
        return [dict(row) for row in rows]
