from sqlalchemy import select
from sqlalchemy.engine import ChunkedIteratorResult

from app.base.base_accessor import BaseAccessor
from app.quiz.models import (
    Answer,
    Question,
    Theme, ThemeModel, AnswerModel, QuestionModel,
)


class QuizAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> Theme:
        # query = insert(ThemeModel).values(title=title)
        async with self.app.database.session.begin() as session:
            # await session.execute(query)
            session.add(ThemeModel(
                title=title
            ))
            await session.commit()
            res: ChunkedIteratorResult = await session.execute(
                select(ThemeModel).where(ThemeModel.title == title)
            )
            raw_res = res.scalars().all()
            await session.commit()
            # await session.commit()
        return Theme(
            id=raw_res[0].id,
            title=raw_res[0].title
        )

    async def get_theme_by_title(self, title: str) -> Theme | None:
        query = select(ThemeModel).where(ThemeModel.title == title)
        async with self.app.database.session.begin() as session:
            res: ChunkedIteratorResult = await session.execute(query)
            raw_res = res.scalars().all()
            await session.commit()
        if len(raw_res) == 0:
            return None
        else:
            return Theme(
                id=raw_res[0].id,
                title=raw_res[0].title
            )

    async def get_theme_by_id(self, id_: int) -> Theme | None:
        query = select(ThemeModel).where(ThemeModel.id == id_)
        async with self.app.database.session.begin() as session:
            res: ChunkedIteratorResult = await session.execute(query)
            raw_res = res.scalars().all()
            await session.commit()
        if len(raw_res) == 0:
            return None
        else:
            return Theme(
                id=raw_res[0].id,
                title=raw_res[0].title
            )

    async def list_themes(self) -> list[Theme]:
        themes = []
        query = select(ThemeModel)
        async with self.app.database.session.begin() as session:
            res: ChunkedIteratorResult = await session.execute(query)
            raw_res = res.scalars().all()
            await session.commit()
        for raw_theme in raw_res:
            themes += [Theme(raw_theme.id, raw_theme.title)]
        return themes

    async def create_answers(
            self, question_id: int, answers: list[Answer]
    ) -> list[Answer]:
        for answer in answers:
            # query = insert(AnswerModel).values(
            #    is_correct=answer.is_correct,
            #    title=answer.title,
            #    question_id=question_id
            # )
            async with self.app.database.session.begin() as session:
                # await session.execute(query)
                session.add(AnswerModel(
                    is_correct=answer.is_correct,
                    title=answer.title,
                    question_id=question_id
                ))
                await session.commit()
        return answers

    async def create_question(
        self, title: str, theme_id: int, answers: list[Answer]
    ) -> Question:
        async with self.app.database.session.begin() as session:
            # await session.execute(query)
            session.add(QuestionModel(
                title=title,
                theme_id=theme_id
            ))
            await session.commit()
            res: ChunkedIteratorResult = await session.execute(
                select(QuestionModel).where(QuestionModel.title == title)
            )
            raw_res = res.scalars().all()
            await session.commit()
        raw_answers = await self.create_answers(raw_res[0].id, answers)
        return Question(
            id=raw_res[0].id,
            theme_id=theme_id,
            title=title,
            answers=raw_answers
        )

    async def get_question_by_title(self, title: str) -> Question | None:
        query = select(QuestionModel).where(QuestionModel.title == title)
        async with self.app.database.session.begin() as session:
            res: ChunkedIteratorResult = await session.execute(query)
            raw_res_q = res.scalars().all()
            await session.commit()
        if len(raw_res_q) == 0:
            return None
        else:
            query = select(AnswerModel). \
                where(AnswerModel.question_id == raw_res_q[0].id)
            res: ChunkedIteratorResult = await session.execute(query)
            raw_res_a = res.scalars().all()
            await session.commit()
            question = Question(
                id=raw_res_q[0].id,
                title=raw_res_q[0].title,
                theme_id=raw_res_q[0].theme_id,
                answers=[Answer(title=x.title, is_correct=x.is_correct)
                         for x in raw_res_a]
            )
            return question

    async def list_questions(self, theme_id: int | None = None) -> list[Question]:
        if not theme_id:
            query = select(QuestionModel)
        else:
            query = select(QuestionModel).where(QuestionModel.theme_id == int(theme_id))
        questions = []
        async with self.app.database.session.begin() as session:
            res: ChunkedIteratorResult = await session.execute(query)
            raw_res_q = res.scalars().all()
            await session.commit()
        for raw_q in raw_res_q:
            raw_answers = []
            query = select(AnswerModel).where(AnswerModel.question_id == raw_q.id)
            async with self.app.database.session.begin() as session:
                res: ChunkedIteratorResult = await session.execute(query)
                raw_res_a = res.scalars().all()
                await session.commit()
            for raw_a in raw_res_a:
                raw_answers += [Answer(
                    title=raw_a.title,
                    is_correct=raw_a.is_correct
                )]
            questions += [Question(
                id=raw_q.id,
                title=raw_q.title,
                theme_id=raw_q.theme_id,
                answers=raw_answers
            )]
        return questions
