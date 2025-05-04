from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    subscriptions = relationship("UserSubscription", back_populates="user")

    __table_args__ = (
        Index('idx_users_username', 'username'),
        Index('idx_users_email', 'email')
    )


class SubscriptionPlan(Base):
    __tablename__ = 'subscription_plans'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    price = Column(Integer, nullable=False)
    description = Column(String(200))
    duration_days = Column(Integer, nullable=False)
    subscriptions = relationship("UserSubscription", back_populates="plan")

    __table_args__ = (
        Index('idx_plans_name', 'name'),
    )


class SubscriptionStatus(enum.Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    CANCELLED = 'cancelled'


class UserSubscription(Base):
    __tablename__ = 'user_subscriptions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    plan_id = Column(Integer, ForeignKey('subscription_plans.id'), nullable=False)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="subscriptions")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")

    # Optimization: Index for efficient retrieval of active subscriptions for a user.
    # This index includes user_id (for filtering), status (for filtering active subscriptions),
    # and end_date (potentially for ordering or further filtering). When querying for active
    # subscriptions of a specific user, the database can quickly locate the relevant rows
    # using this combined index, avoiding a full table scan.

    __table_args__ = (
        Index('idx_user_subscriptions_user_id_status', 'user_id', 'status'),
        Index('idx_user_subscriptions_status_end_date', 'status', 'end_date')
    )
