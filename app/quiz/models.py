from dataclasses import dataclass

from sqlalchemy import Column, Integer, UniqueConstraint, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref

from app.store.database.sqlalchemy_base import db


@dataclass
class Theme:
    id: int
    title: str


@dataclass
class Question:
    id: int
    title: str
    theme_id: int
    answers: list["Answer"]


@dataclass
class Answer:
    title: str
    is_correct: bool


class ThemeModel(db):
    __tablename__ = "themes"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False, unique=True)
    questions = relationship('QuestionModel', cascade='all,delete', backref='theme_model')
    # __table_args__ = (
    #     UniqueConstraint('title', name='theme_title_uc'),
    # )


class QuestionModel(db):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False, unique=True)
    theme_id = Column(
        Integer,
        ForeignKey("themes.id", ondelete='CASCADE'),
        nullable=False
    )
    answers = relationship('AnswerModel', cascade='all,delete', backref='question_model')
    #theme = relationship('ThemeModel', backref=backref('questions', passive_deletes=True))
    # __table_args__ = (
    #     UniqueConstraint('title', name='question_title_uc'),
    # )


class AnswerModel(db):
    __tablename__ = "answers"

    title = Column(String, primary_key=True)
    is_correct = Column(Boolean, nullable=False)
    question_id = Column(
        Integer,
        ForeignKey("questions.id", ondelete='CASCADE'),
        nullable=False
    )
    #question = relationship('QuestionModel', backref=backref('answers', passive_deletes=True))
