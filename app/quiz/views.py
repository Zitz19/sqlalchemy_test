import aiohttp_session
from aiohttp.web_exceptions import HTTPUnauthorized, HTTPForbidden, HTTPConflict, HTTPBadRequest, HTTPNotFound
from aiohttp_apispec import querystring_schema, request_schema, response_schema

from app.quiz.models import Answer
from app.quiz.schemes import (
    ListQuestionSchema,
    QuestionSchema,
    ThemeIdSchema,
    ThemeListSchema,
    ThemeSchema,
)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class ThemeAddView(AuthRequiredMixin, View):
    @request_schema(ThemeSchema)
    @response_schema(ThemeSchema)
    async def post(self):
        session = await aiohttp_session.get_session(self.request)
        if not session:
            raise HTTPUnauthorized
        user = await self.store.admins.get_by_email(session['admin']['email'])
        if not user or session['admin']['email'] != user.email:
            raise HTTPForbidden
        else:
            title = self.data['title']
            theme = await self.store.quizzes.get_theme_by_title(title)
            if theme:
                raise HTTPConflict
            else:
                theme = await self.store.quizzes.create_theme(title=title)
                return json_response(data=ThemeSchema().dump(theme))


class ThemeListView(AuthRequiredMixin, View):
    @response_schema(ThemeListSchema)
    async def get(self):
        session = await aiohttp_session.get_session(self.request)
        if not session:
            raise HTTPUnauthorized
        user = await self.store.admins.get_by_email(session['admin']['email'])
        if not user or session['admin']['email'] != user.email:
            raise HTTPForbidden
        else:
            themes = await self.store.quizzes.list_themes()
            raw_themes = [ThemeSchema().dump(theme) for theme in themes]
            return json_response(data={'themes': raw_themes})


class QuestionAddView(AuthRequiredMixin, View):
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema)
    async def post(self):
        session = await aiohttp_session.get_session(self.request)
        if not session:
            raise HTTPUnauthorized
        user = await self.store.admins.get_by_email(session['admin']['email'])
        if not user or session['admin']['email'] != user.email:
            raise HTTPForbidden
        else:
            title = self.data['title']
            theme_id = self.data['theme_id']
            answers = self.data['answers']
            only_answer: bool = False
            for answer in answers:
                if answer['is_correct']:
                    if only_answer:
                        raise HTTPBadRequest
                    only_answer = True
            if not only_answer:
                raise HTTPBadRequest
            if len(answers) == 1:
                raise HTTPBadRequest
            if not await self.store.quizzes.get_theme_by_id(theme_id):
                raise HTTPNotFound
            if await self.store.quizzes.get_question_by_title(title):
                raise HTTPConflict
            raw_answers = [Answer(
                title=x['title'],
                is_correct=x['is_correct']
            ) for x in answers]
            question = await self.store.quizzes.create_question(title, theme_id, raw_answers)
            return json_response(data=({'id': question.id} | self.data))


class QuestionListView(AuthRequiredMixin, View):
    @querystring_schema(ThemeIdSchema)
    @response_schema(ListQuestionSchema)
    async def get(self):
        session = await aiohttp_session.get_session(self.request)
        if not session:
            raise HTTPUnauthorized
        user = await self.store.admins.get_by_email(session['admin']['email'])
        if not user or session['admin']['email'] != user.email:
            raise HTTPForbidden
        else:
            theme_id = self.request.query.get('theme_id')
            questions = await self.store.quizzes.list_questions(theme_id)
            raw_questions = [QuestionSchema().dump(question) for question in questions]
            return json_response(data={'questions': raw_questions})
