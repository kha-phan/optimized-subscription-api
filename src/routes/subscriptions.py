from flask import jsonify
from src import db
from src.models import SubscriptionPlan, UserSubscription, SubscriptionStatus
from datetime import datetime, timedelta


def subscribe_user(user, plan_id):
    plan = db.session.get(SubscriptionPlan, plan_id)
    if not plan:
        return jsonify({'message': 'Subscription plan not found'}), 404

    existing_subscription = db.session.query(UserSubscription).filter_by(user_id=user.id, status=SubscriptionStatus.ACTIVE).first()

    if existing_subscription:
        return jsonify({'message': 'User already has an active subscription. Cancel it first.'}), 400

    end_date = datetime.utcnow() + timedelta(days=plan.duration_days)
    new_subscription = UserSubscription(user_id=user.id, plan_id=plan.id, end_date=end_date)
    db.session.add(new_subscription)
    db.session.commit()

    return jsonify({'message': f'Subscribed to {plan.name} until {end_date}'}), 201


def get_active_subscriptions_user(user_id):
    active_subscription = db.session.query(UserSubscription).filter(
        UserSubscription.user_id == user_id,
        UserSubscription.status == 'active',
        UserSubscription.end_date > datetime.utcnow()
    ).first()

    if active_subscription:
        return jsonify({
            'plan_name': active_subscription.plan.name,
            'start_date': active_subscription.start_date,
            'end_date': active_subscription.end_date
        }), 200
    else:
        return jsonify({'message': 'No active subscription found'}), 404


def get_subscription_history_user(user_id):
    history = db.session.query(UserSubscription).filter_by(user_id=user_id).order_by(UserSubscription.start_date.desc()).all()

    return jsonify([{
        'plan_name': sub.plan.name,
        'start_date': sub.start_date,
        'end_date': sub.end_date,
        'status': 'Active' if sub.end_date > datetime.utcnow() else 'Inactive',
        'created_at': sub.created_at,
        'updated_at': sub.updated_at
    } for sub in history]), 200


def upgrade_subscription(user, new_plan_id):
    new_plan = db.session.get(SubscriptionPlan, new_plan_id)
    if not new_plan:
        return jsonify({'message': 'New subscription plan not found'}), 404

    active_subscription = db.session.query(UserSubscription).filter_by(user_id=user.id, status=SubscriptionStatus.ACTIVE).first()
    if not active_subscription:
        return jsonify({'message': 'No active subscription to upgrade'}), 400

    active_subscription.status = SubscriptionStatus.CANCELLED
    active_subscription.end_date = datetime.utcnow()
    end_date = datetime.utcnow() + timedelta(days=new_plan.duration_days)
    new_user_subscription = UserSubscription(user_id=user.id, plan_id=new_plan.id, end_date=end_date)
    db.session.add(new_user_subscription)
    db.session.commit()

    return jsonify({'message': f'Upgraded to {new_plan.name} until {end_date}'}), 200


def cancel_subscription(user):
    active_subscription = db.session.query(UserSubscription).filter_by(user_id=user.id, status=SubscriptionStatus.ACTIVE).first()
    if not active_subscription:
        return jsonify({'message': 'No active subscription to cancel'}), 400

    active_subscription.status = SubscriptionStatus.CANCELLED
    active_subscription.end_date = datetime.utcnow()
    db.session.commit()

    return jsonify({'message': 'Subscription cancelled'}), 200
