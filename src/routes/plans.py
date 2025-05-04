from flask import jsonify, request
from src.models import SubscriptionPlan
from src import auth, db


def get_all_plans():
    plans = SubscriptionPlan.query.all()
    return [
        {'id': plan.id, 'name': plan.name, 'price': plan.price, 'description': plan.description, 'duration_days': plan.duration_days}
        for plan in plans
    ]


def create_plan():
    if auth.current_user().username != 'admin':
        return jsonify({'message': 'Admin access required'}), 403

    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    duration_days = data.get('duration_days')

    if not name or price is None or duration_days is None:
        return jsonify({'message': 'Name, price, and duration_days are required'}), 400

    if SubscriptionPlan.query.filter_by(name=name).first():
        return jsonify({'message': 'Subscription plan name already exists'}), 409

    new_plan = SubscriptionPlan(name=name, price=price, duration_days=duration_days)
    db.session.add(new_plan)
    db.session.commit()

    return jsonify(new_plan), 201

