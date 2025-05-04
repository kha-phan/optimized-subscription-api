from flask import jsonify

from src import db
from sqlalchemy import text
from datetime import datetime


def get_active_subscriptions_optimized_user(user_id):
    """
    Optimized query for active subscriptions using:
    - Proper indexing (status, end_date, user_id)
    - Minimal column selection
    - Parameterized queries
    """
    sql = text("""
        SELECT us.id, sp.name, sp.price, sp.duration_days, us.start_date, us.end_date
        FROM user_subscriptions us
        JOIN subscription_plans sp ON us.plan_id = sp.id
        WHERE us.user_id = :user_id AND us.status = :active_status
        AND (us.end_date IS NULL OR us.end_date > :now)
    """)
    result = db.session.execute(sql, {"user_id": user_id, "active_status": "active", "now": datetime.utcnow()}).fetchall()
    subscriptions = [dict(row) for row in result]

    return jsonify(subscriptions)


def get_subscription_history_optimized_user(user_id):
    """
    Optimized query for active subscriptions using:
    - Proper indexing (status, end_date, user_id)
    - Minimal column selection
    - Parameterized queries
    """
    sql = text("""
        SELECT us.id, sp.name, sp.price, sp.duration_days, us.start_date, us.end_date, us.status
        FROM user_subscriptions us
        JOIN subscription_plans sp ON us.plan_id = sp.id
        WHERE us.user_id = :user_id
        ORDER BY us.start_date DESC
    """)
    result = db.session.execute(sql, {"user_id": user_id}).fetchall()
    history = [dict(row) for row in result]
    return jsonify(history)
