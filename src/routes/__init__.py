from flask import jsonify

from src.routes.authen import register, login
from src import app, auth

from .subscriptions import (
    subscribe_user,
    get_active_subscriptions_user,
    get_subscription_history_user,
    upgrade_subscription,
    cancel_subscription,
)
from .plans import create_plan, get_all_plans
from .optimized_subscriptions import get_active_subscriptions_optimized_user, get_subscription_history_optimized_user


@app.route('/plans', methods=['GET'])
@auth.login_required
def list_plans():
    plans = get_all_plans()
    return jsonify(plans)


@app.route('/plans', methods=['POST'])
@auth.login_required
def create_plan():
    plan = create_plan()
    return plan


@app.route('/register', methods=['POST'])
def register_user():
    user_info = register()
    return jsonify(user_info)


@app.route('/login', methods=['POST'])
def login():
    token = login()
    return jsonify(token)


@app.route('/subscribe/<int:plan_id>', methods=['POST'])
@auth.login_required
def subscribe(plan_id):
    user = auth.current_user()
    if not plan_id:
        return jsonify({'message': 'plan_id is required'}), 400
    return subscribe_user(user, plan_id)


@app.route('/subscriptions/active', methods=['GET'])
@auth.login_required
def get_active_subscriptions():
    user = auth.current_user()
    return get_active_subscriptions_user(user.id)


@app.route('/subscriptions/history', methods=['GET'])
@auth.login_required
def get_subscription_history():
    user = auth.current_user()
    return get_subscription_history(user.id)


@app.route('/subscriptions/upgrade/<int:plan_id>', methods=['POST'])
@auth.login_required
def upgrade(new_plan_id):
    user = auth.current_user()
    return upgrade_subscription(user, new_plan_id)


@app.route('/subscriptions/cancel', methods=['POST'])
@auth.login_required
def cancel():
    user = auth.current_user()
    return cancel_subscription(user)


@app.route('/subscriptions/history/optimized', methods=['GET'])
@auth.login_required
def get_subscription_history_optimized():
    user = auth.current_user()
    return get_subscription_history_optimized_user(user.id)


@app.route('/subscriptions/active/optimized', methods=['GET'])
@auth.login_required
def get_active_subscriptions_optimized():
    user = auth.current_user()
    return get_active_subscriptions_optimized_user(user.id)
