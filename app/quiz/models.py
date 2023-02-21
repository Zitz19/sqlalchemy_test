from dataclasses import dataclass

from sqlalchemy import Column, Integer, UniqueConstraint, String, ForeignKey, Boolean, Sequence
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
    title = Column(String, unique=True, nullable=False)


class QuestionModel(db):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True, nullable=False)
    theme_id = Column(
        Integer,
        ForeignKey("themes.id", ondelete='CASCADE'),
        nullable = False
    )
    answers = relationship('AnswerModel', backref='question_model')



class AnswerModel(db):
    __tablename__ = "answers"

    id = Column(Integer, Sequence('answers_id_seq'), primary_key=True)
    title = Column(String, unique=True, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    question_id = Column(
        Integer,
        ForeignKey("questions.id", ondelete='CASCADE'),
        nullable=False
    )
