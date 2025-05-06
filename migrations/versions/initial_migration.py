"""Initial migration

Revision ID: 0001
Revises: 
Create Date: 2023-10-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создание таблицы users
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('username', sa.String(255), unique=True, nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False)
    )

    # Создание таблицы learning_profiles
    op.create_table('learning_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('learning_style', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('cognitive_profile', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('preferences', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False)
    )

    # Создание таблицы concepts
    op.create_table('concepts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('domain', sa.String(100), nullable=False),
        sa.Column('difficulty', sa.Float, nullable=False),
        sa.Column('taxonomy_tags', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False)
    )

    # Создание таблицы concept_relationships
    op.create_table('concept_relationships',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('source_concept_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('concepts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('target_concept_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('concepts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('relationship_type', sa.String(50), nullable=False),
        sa.Column('strength', sa.Float, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.UniqueConstraint('source_concept_id', 'target_concept_id', 'relationship_type')
    )

    # Создание таблицы educational_content
    op.create_table('educational_content',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content_type', sa.String(50), nullable=False),
        sa.Column('body', sa.Text, nullable=False),
        sa.Column('difficulty', sa.Float, nullable=False),
        sa.Column('metadata', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False)
    )

    # Создание таблицы content_concept (связь многие-ко-многим)
    op.create_table('content_concept',
        sa.Column('content_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('educational_content.id', ondelete='CASCADE'), nullable=False),
        sa.Column('concept_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('concepts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('relevance', sa.Float, nullable=False, server_default='1.0'),
        sa.PrimaryKeyConstraint('content_id', 'concept_id')
    )

    # Создание таблицы adapted_content
    op.create_table('adapted_content',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('original_content_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('educational_content.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('body', sa.Text, nullable=False),
        sa.Column('difficulty', sa.Float, nullable=False),
        sa.Column('adaptation_params', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.UniqueConstraint('original_content_id', 'user_id')
    )

    # Создание таблицы assessments
    op.create_table('assessments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('assessment_type', sa.String(50), nullable=False),
        sa.Column('metadata', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True)
    )

    # Создание таблицы assessment_questions
    op.create_table('assessment_questions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('assessment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('assessments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('concept_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('concepts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('question_type', sa.String(50), nullable=False),
        sa.Column('content', postgresql.JSONB, nullable=False),
        sa.Column('difficulty', sa.Float, nullable=False),
        sa.Column('metadata', postgresql.JSONB, nullable=False, server_default='{}')
    )

    # Создание таблицы assessment_responses
    op.create_table('assessment_responses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('assessment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('assessments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('assessment_questions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('response', postgresql.JSONB, nullable=False),
        sa.Column('score', sa.Float, nullable=True),
        sa.Column('feedback', sa.Text, nullable=True),
        sa.Column('response_time_seconds', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False)
    )

    # Создание таблицы concept_mastery
    op.create_table('concept_mastery',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('concept_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('concepts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('mastery_level', sa.Float, nullable=False),
        sa.Column('confidence', sa.Float, nullable=False),
        sa.Column('last_assessed_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.UniqueConstraint('user_id', 'concept_id')
    )

    # Создание таблицы learning_interactions
    op.create_table('learning_interactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('interaction_type', sa.String(50), nullable=False),
        sa.Column('content', postgresql.JSONB, nullable=False),
        sa.Column('metadata', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False)
    )

    # Создание таблицы learning_sessions
    op.create_table('learning_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('session_type', sa.String(50), nullable=False),
        sa.Column('metadata', postgresql.JSONB, nullable=False, server_default='{}')
    )

    # Создание таблицы learning_plans
    op.create_table('learning_plans',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('plan_data', postgresql.JSONB, nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False)
    )

    # Создание индексов
    op.create_index('idx_learning_interactions_user_id', 'learning_interactions', ['user_id'])
    op.create_index('idx_learning_interactions_session_id', 'learning_interactions', ['session_id'])
    op.create_index('idx_learning_interactions_timestamp', 'learning_interactions', ['timestamp'])
    op.create_index('idx_concept_mastery_user_id', 'concept_mastery', ['user_id'])
    op.create_index('idx_concept_mastery_concept_id', 'concept_mastery', ['concept_id'])
    op.create_index('idx_assessment_responses_user_id', 'assessment_responses', ['user_id'])
    op.create_index('idx_assessment_responses_assessment_id', 'assessment_responses', ['assessment_id'])
    op.create_index('idx_educational_content_difficulty', 'educational_content', ['difficulty'])
    op.create_index('idx_concepts_domain', 'concepts', ['domain'])


def downgrade() -> None:
    # Удаление индексов
    op.drop_index('idx_concepts_domain')
    op.drop_index('idx_educational_content_difficulty')
    op.drop_index('idx_assessment_responses_assessment_id')
    op.drop_index('idx_assessment_responses_user_id')
    op.drop_index('idx_concept_mastery_concept_id')
    op.drop_index('idx_concept_mastery_user_id')
    op.drop_index('idx_learning_interactions_timestamp')
    op.drop_index('idx_learning_interactions_session_id')
    op.drop_index('idx_learning_interactions_user_id')

    # Удаление таблиц
    op.drop_table('learning_plans')
    op.drop_table('learning_sessions')
    op.drop_table('learning_interactions')
    op.drop_table('concept_mastery')
    op.drop_table('assessment_responses')
    op.drop_table('assessment_questions')
    op.drop_table('assessments')
    op.drop_table('adapted_content')
    op.drop_table('content_concept')
    op.drop_table('educational_content')
    op.drop_table('concept_relationships')
    op.drop_table('concepts')
    op.drop_table('learning_profiles')
    op.drop_table('users')
