import aiohttp_session
from aiohttp.web import HTTPForbidden, HTTPUnauthorized
from aiohttp_apispec import request_schema, response_schema
from aiohttp_session import new_session

from app.admin.schemes import AdminSchema
from app.web.app import View
from app.web.utils import json_response


class AdminLoginView(View):
    @request_schema(AdminSchema)
    @response_schema(AdminSchema, 200)
    async def post(self):
        data = self.data
        email = data['email']
        password = data['password']
        admin = await self.request.app.store.admins.get_by_email(email)
        if admin is None:
            raise HTTPForbidden
        if admin.is_password_valid(password):
            session = await aiohttp_session.new_session(request=self.request)
            session['admin'] = {'id': admin.id, 'email': admin.email}
            # session['admin']['id'] = admin.id
            # session['admin']['email'] = admin.email
            return json_response(data={'id': admin.id, 'email': admin.email})
        else:
            raise HTTPForbidden


class AdminCurrentView(View):
    @response_schema(AdminSchema, 200)
    async def get(self):
        session = await aiohttp_session.get_session(self.request)
        if not session:
            raise HTTPUnauthorized
        admin = await self.request.app.store.admins.get_by_email(session['admin']['email'])
        return json_response(data={'id': admin.id, 'email': admin.email})
