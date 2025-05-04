import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock
from src import db
from tests import app

from src.models import (
    SubscriptionPlan,
    SubscriptionStatus,
    User,
    UserSubscription
)


@pytest.fixture
def mock_db_session():
    session = MagicMock()
    db.session = session

    query_mock = MagicMock()
    session.query.return_value = query_mock
    query_mock.filter_by.return_value = query_mock
    query_mock.filter.return_value = query_mock
    query_mock.order_by.return_value = query_mock
    query_mock.first.return_value = None
    query_mock.all.return_value = []

    session.query_mock = query_mock

    return session


from src.routes import (
    subscribe_user,
    get_active_subscriptions_user,
    get_subscription_history_user,
    upgrade_subscription,
    cancel_subscription,
)


def create_mock_plan(id=1, name="Basic", duration_days=30):
    return SubscriptionPlan(id=id, name=name, duration_days=duration_days)


def create_mock_user(id=1):
    return User(id=id)


def create_mock_subscription(id=1, user_id=1, plan_id=1, end_date=None, status=SubscriptionStatus.ACTIVE, created_at=None, start_date=None):
    if end_date is None:
        end_date = datetime.utcnow() + timedelta(days=30)
    if start_date is None:
        start_date = datetime.utcnow()

    return UserSubscription(id=id, user_id=user_id, plan_id=plan_id, end_date=end_date, status=status, created_at=created_at, start_date=start_date)


def test_subscribe_user_success(app, mock_db_session):
    with app.app_context():
        user = create_mock_user()
        plan = create_mock_plan()
        mock_db_session.get.return_value = plan

        result, status_code = subscribe_user(user, plan.id)
        assert status_code == 201
        assert "Subscribed to Basic" in result.json["message"]
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()


def test_subscribe_user_plan_not_found(app, mock_db_session):
    with app.app_context():
        user = create_mock_user()
        mock_db_session.get.return_value = None

        result, status_code = subscribe_user(user, 1)
        assert status_code == 404
        assert "Subscription plan not found" in result.json["message"]
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()


def test_subscribe_user_already_subscribed(app, mock_db_session):
    with app.app_context():
        user = create_mock_user()
        plan = create_mock_plan()
        existing_subscription = create_mock_subscription(user_id=user.id, status=SubscriptionStatus.ACTIVE, created_at=datetime(2024, 1, 1))
        mock_db_session.get.return_value = plan
        mock_db_session.query_mock.filter_by.return_value.first.return_value = existing_subscription

        result, status_code = subscribe_user(user, plan.id)
        assert status_code == 400
        assert "User already has an active subscription" in result.json["message"]
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()


def test_get_active_subscriptions_success(app, mock_db_session):
    with app.app_context():
        user = create_mock_user()
        now = datetime.utcnow()
        plan = create_mock_plan()
        active_subscription = create_mock_subscription(user_id=user.id, end_date=now + timedelta(days=1), status=SubscriptionStatus.ACTIVE, created_at=datetime(2024, 1, 1))
        active_subscription.plan = plan

        mock_db_session.query_mock.filter.return_value.first.return_value = active_subscription
        result, status_code = get_active_subscriptions_user(user.id)
        assert status_code == 200
        assert result.json["plan_name"] == plan.name
        assert result.json["start_date"] == active_subscription.start_date.strftime('%a, %d %b %Y %H:%M:%S GMT')
        assert result.json["end_date"] == active_subscription.end_date.strftime('%a, %d %b %Y %H:%M:%S GMT')


def test_get_active_subscriptions_no_subscription(app, mock_db_session):
    with app.app_context():
        mock_db_session.query.filter.return_value.first.return_value = None

        result, status_code = get_active_subscriptions_user(1)
        assert status_code == 404
        assert "No active subscription found" in result.json["message"]


def test_get_subscription_history_success(app, mock_db_session):
    with app.app_context():
        user = create_mock_user()
        now = datetime.utcnow()
        subscription1 = create_mock_subscription(user_id=user.id, status=SubscriptionStatus.ACTIVE, created_at=datetime(2024, 1, 1), end_date=now + timedelta(days=1))
        subscription1.plan = create_mock_plan()
        subscription2 = create_mock_subscription(user_id=user.id, status=SubscriptionStatus.CANCELLED, created_at=datetime(2024, 2, 1), end_date=now - timedelta(days=1))
        subscription2.plan = create_mock_plan()
        mock_db_session.query_mock.all.return_value = [subscription1, subscription2]
        result, status_code = get_subscription_history_user(user.id)
        assert status_code == 200
        assert len(result.json) == 2
        assert result.json[0]["plan_name"] == "Basic"
        assert result.json[0]["status"] == "Active"
        assert result.json[1]["status"] == "Inactive"
        assert result.json[0]["created_at"] == subscription1.created_at.strftime('%a, %d %b %Y %H:%M:%S GMT')
        assert result.json[1]["created_at"] == subscription2.created_at.strftime('%a, %d %b %Y %H:%M:%S GMT')


def test_get_subscription_history_empty(app, mock_db_session):
    with app.app_context():
        mock_db_session.query.filter_by.return_value.order_by.return_value.all.return_value = []
        result, status_code = get_subscription_history_user(1)
        assert status_code == 200
        assert result.json == []


def test_upgrade_subscription_success(app, mock_db_session):
    with app.app_context():
        user = create_mock_user()
        old_plan = create_mock_plan(id=1, name="Basic", duration_days=30)
        new_plan = create_mock_plan(id=2, name="Pro", duration_days=90)
        active_subscription = create_mock_subscription(user_id=user.id, plan_id=old_plan.id, status=SubscriptionStatus.ACTIVE)
        active_subscription.plan = old_plan

        mock_db_session.get.side_effect = [new_plan, new_plan]
        mock_db_session.query_mock.filter_by.return_value.first.return_value = active_subscription

        result, status_code = upgrade_subscription(user, new_plan.id)
        assert status_code == 200
        assert "Upgraded to Pro" in result.json["message"]
        assert active_subscription.status == SubscriptionStatus.CANCELLED
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()


def test_upgrade_subscription_new_plan_not_found(app, mock_db_session):
    with app.app_context():
        user = create_mock_user()
        mock_db_session.get.return_value = None

        result, status_code = upgrade_subscription(user, 2)
        assert status_code == 404
        assert "New subscription plan not found" in result.json["message"]
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()


def test_upgrade_subscription_no_active_subscription(app, mock_db_session):
    with app.app_context():
        user = create_mock_user()
        new_plan = create_mock_plan()
        mock_db_session.get.return_value = new_plan
        mock_db_session.query_mock.filter_by.return_value.first.return_value = None

        result, status_code = upgrade_subscription(user, new_plan.id)
        assert status_code == 400
        assert "No active subscription to upgrade" in result.json["message"]
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()


def test_cancel_subscription_success(app, mock_db_session):

    with app.app_context():
        user = create_mock_user()
        active_subscription = create_mock_subscription(user_id=user.id, status=SubscriptionStatus.ACTIVE)
        mock_db_session.query_mock.filter_by.return_value.first.return_value = active_subscription

        result, status_code = cancel_subscription(user)
        assert status_code == 200
        assert "Subscription cancelled" in result.json["message"]
        assert active_subscription.status == SubscriptionStatus.CANCELLED
        mock_db_session.commit.assert_called_once()


def test_cancel_subscription_no_active_subscription(app, mock_db_session):
    with app.app_context():
        user = create_mock_user()
        mock_db_session.query_mock.filter_by.return_value.first.return_value = None

        result, status_code = cancel_subscription(user)
        assert status_code == 400
        assert "No active subscription to cancel" in result.json["message"]
        mock_db_session.commit.assert_not_called()
