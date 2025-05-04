from src.database import db
from sqlalchemy import text
import time


def analyze_query_performance(query, params=None):
    """Analyze and optimize query performance"""
    if params is None:
        params = {}

    # Explain query plan
    explain_query = f"EXPLAIN QUERY PLAN {query}"
    plan = db.session.execute(text(explain_query), params).fetchall()

    # Execute and time the query
    start_time = time.time()
    result = db.session.execute(text(query), params).fetchall()
    execution_time = time.time() - start_time

    return {
        'query_plan': plan,
        'execution_time': execution_time,
        'result_count': len(result)
    }


def create_index_if_not_exists(columns, table_name):
    """Helper to create composite indexes"""
    index_name = f"idx_{table_name}_{'_'.join(columns)}"

    check_query = text(f"""
    SELECT name FROM sqlite_master 
    WHERE type='index' AND name=:index_name
    """)

    exists = db.session.execute(check_query, {'index_name': index_name}).fetchone()

    if not exists:
        columns_str = ', '.join(columns)
        create_query = text(f"""
        CREATE INDEX {index_name} ON {table_name} ({columns_str})
        """)
        db.session.execute(create_query)
        db.session.commit()
        return True

    return False

