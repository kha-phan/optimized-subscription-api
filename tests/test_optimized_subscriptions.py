import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from src import db
from tests import app

from src.models import (
    SubscriptionStatus,
    User,
    UserSubscription
)


@pytest.fixture
def mock_db_session():
    with patch.object(db, 'session', autospec=True) as mock_session:
        mock_execute = MagicMock()
        mock_session.execute.return_value = mock_execute
        mock_execute.fetchall.return_value = []

        yield mock_session


@pytest.fixture
def mock_auth_user():
    mock_user = User(id=1, username="testuser", password="pass", email="mock@gmail.com")
    with patch("src.routes.auth.current_user", return_value=mock_user), \
         patch("src.routes.auth.login_required", lambda f: f):
        yield mock_user


from src.routes import (
    get_active_subscriptions_optimized_user,
    get_subscription_history_optimized_user
)


def create_mock_subscription(id=1, user_id=1, plan_id=1, end_date=None, status=SubscriptionStatus.ACTIVE, created_at=None, start_date=None):
    if end_date is None:
        end_date = datetime.utcnow() + timedelta(days=30)
    if start_date is None:
        start_date = datetime.utcnow()
    return UserSubscription(id=id, user_id=user_id, plan_id=plan_id, end_date=end_date, status=status, created_at=created_at, start_date=start_date)


def test_get_active_subscriptions_optimized_success(app, mock_db_session):
    with app.app_context():
        user_id = 1
        expected_result = [
            {"id": 1, "name": "Basic", "price": 10, "duration_days": 30, "start_date": "2024-01-01T00:00:00", "end_date": "2024-01-31T00:00:00"},
            {"id": 2, "name": "Pro", "price": 20, "duration_days": 90, "start_date": "2024-02-01T00:00:00", "end_date": "2024-04-30T00:00:00"},
        ]
        mock_db_session.execute.return_value.fetchall.return_value = expected_result

        result = get_active_subscriptions_optimized_user(user_id)

        assert result.get_json() == expected_result
        mock_db_session.execute.assert_called_once()


def test_get_active_subscriptions_optimized_no_subscriptions(app, mock_db_session):
    with app.app_context():
        user_id = 1
        mock_db_session.execute.return_value.fetchall.return_value = []

        result = get_active_subscriptions_optimized_user(user_id)
        assert result.get_json() == []
        mock_db_session.execute.assert_called_once()


def test_get_subscription_history_optimized_success(app, mock_db_session):
    with app.app_context():
        user_id = 1
        expected_result = [
            {"id": 1, "name": "Pro", "price": 20, "duration_days": 90, "start_date": "2024-02-01T00:00:00", "end_date": "2024-04-30T00:00:00", "status": "active"},
            {"id": 2, "name": "Basic", "price": 10, "duration_days": 30, "start_date": "2024-01-01T00:00:00", "end_date": "2024-01-31T00:00:00", "status": "completed"},
        ]
        mock_db_session.execute.return_value.fetchall.return_value = expected_result

        result = get_subscription_history_optimized_user(user_id)

        assert result.get_json() == expected_result
        mock_db_session.execute.assert_called_once()


def test_get_subscription_history_optimized_no_subscriptions(app, mock_db_session):
    with app.app_context():
        user_id = 1
        mock_db_session.execute.return_value.fetchall.return_value = []

        result = get_subscription_history_optimized_user(user_id)
        assert result.get_json() == []
        mock_db_session.execute.assert_called_once()
