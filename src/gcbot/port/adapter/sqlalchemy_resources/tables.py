from enum import StrEnum, auto
from uuid import uuid4
import sqlalchemy as sa


metadata = sa.MetaData()


class EntityType(StrEnum):
    WORKOUT = auto()
    MAILING = auto()
    SUPPORT_VOICE = auto()


users_table = sa.Table(
    'users',
    metadata,
    sa.Column('user_id', sa.BigInteger, primary_key=True, nullable=False),
    sa.Column('email', sa.String, unique=True, nullable=False),
    sa.Column('norma_kcal', sa.DECIMAL(20, 0), nullable=True),
)


groups_table = sa.Table(
    "groups",
    metadata,
    sa.Column('oid', sa.BigInteger, primary_key=True, autoincrement=True, nullable=False),
    sa.Column('email', sa.String, unique=False),
    sa.Column('group_id', sa.Integer, nullable=False),
)


like_workouts_table = sa.Table(
   'like_workouts',
    metadata,
    sa.Column('like_id', sa.UUID, default=uuid4, primary_key=True, nullable=False),
    sa.Column('workout_id', sa.ForeignKey('workouts.workout_id', ondelete="CASCADE"), nullable=False),
    sa.Column('user_id', sa.ForeignKey('users.user_id'), nullable=False),
)


workouts_table = sa.Table(
    'workouts',
    metadata,
    sa.Column('workout_id', sa.UUID, primary_key=True, nullable=False),
    sa.Column('entity_type', sa.String(30), nullable=False),
    sa.Column('category_id', sa.ForeignKey('categories.category_id', ondelete="CASCADE"), nullable=False),
    sa.Column('text', sa.String(5000), nullable=False),
    sa.Column('created_at', sa.DateTime, nullable=False),
)


medias_table = sa.Table(
    'medias',
    metadata,
    sa.Column('media_id', sa.UUID, primary_key=True, default=uuid4, nullable=False),
    sa.Column('entity_id', sa.UUID, nullable=False),
    sa.Column('entity_type', sa.String(20), nullable=False),
    sa.Column('file_id', sa.String(200), nullable=False),
    sa.Column('file_unique_id', sa.String(100), nullable=False),
    sa.Column('message_id', sa.Integer, nullable=False),
    sa.Column('content_type', sa.String, nullable=False)
)


categories_table = sa.Table(
    'categories',
    metadata,
    sa.Column('category_id', sa.UUID, primary_key=True, default=uuid4, nullable=False),
    sa.Column('name', sa.String(30), nullable=False),
)


recipes_table = sa.Table(
    'recipes',
    metadata,
    sa.Column('recipe_id', sa.BigInteger, primary_key=True, nullable=False),
    sa.Column('name', sa.String, nullable=False),
    sa.Column('text', sa.String, nullable=False),
    sa.Column('file_id', sa.String, nullable=False),
    sa.Column('amount_kcal', sa.DECIMAL(20, 0), nullable=False),
    sa.Column('type_meal', sa.Integer, nullable=False),
)


ingredients_table = sa.Table(
    'ingredients',
    metadata,
    sa.Column('oid', sa.BigInteger, primary_key=True, autoincrement=True, nullable=False),
    sa.Column('recipe_id', sa.ForeignKey('recipes.recipe_id', ondelete="CASCADE"), nullable=False),
    sa.Column('name', sa.String(500), nullable=False),
    sa.Column('value', sa.DECIMAL(20, 0), nullable=False),
    sa.Column('unit', sa.String, nullable=False),
)


messages_table = sa.Table(
    'messages',
    metadata,
    sa.Column('oid', sa.BigInteger, primary_key=True, autoincrement=True, nullable=False),
    sa.Column('sender_id', sa.BigInteger, nullable=False),
    sa.Column('recipient_id', sa.BigInteger, nullable=False),
    sa.Column('text', sa.String(4000), nullable=False),
    sa.Column('sent_to', sa.DateTime, nullable=False),
    sa.Column('message_id', sa.BigInteger, nullable=True),
)


mailing_table = sa.Table(
    "mailings",
    metadata,
    sa.Column('mailing_id', sa.UUID, primary_key=True, nullable=False),
    sa.Column('text', sa.String(4000), nullable=False),
    sa.Column('name', sa.String(128), nullable=True),
    sa.Column('type_recipient', sa.Integer, nullable=False),
    sa.Column('status', sa.String(20), nullable=False),
)