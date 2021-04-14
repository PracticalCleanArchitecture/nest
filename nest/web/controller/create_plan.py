# -*- coding: utf8 -*-
from datetime import datetime
from typing import Set, Union

from flask import request
from webargs import fields

from nest.app.use_case.create_plan import CreatePlanUseCase, InvalidRepeatTypeError, IParams
from nest.web.authentication_plugin import AuthenticationPlugin, IParams as AuthenticationParams
from nest.web.handle_response import wrap_response
from nest.web.parser import parser
from nest.web.presenter.plan import PlanPresenter


class HTTPParams(AuthenticationParams, IParams):
    def __init__(self):
        args = {
            'repeat_type': fields.Str(allow_none=True),
            'task_id': fields.Int(required=True),
            'trigger_time': fields.DateTime('%Y-%m-%d %H:%M:%S', required=True),
            'visible_hours': fields.List(fields.Int, allow_none=True),
            'visible_wdays': fields.List(fields.Int, allow_none=True),
        }
        parsed_args = parser.parse(args, request)
        self.repeat_type = parsed_args.get('repeat_type')
        self.task_id = parsed_args['task_id']
        self.trigger_time = parsed_args['trigger_time']
        self.visible_hours = set(parsed_args.get('visible_hours') or [])
        self.visible_wdays = set(parsed_args.get('visible_wdays') or [])
        args = {
            'certificate_id': fields.Str(required=True),
            'user_id': fields.Int(required=True),
        }
        parsed_args = parser.parse(args, request, location='cookies')
        self.certificate_id = parsed_args['certificate_id']
        self.user_id = parsed_args['user_id']

    def get_certificate_id(self):
        return self.certificate_id

    def get_repeat_type(self) -> Union[None, str]:
        return self.repeat_type

    def get_task_id(self) -> int:
        return self.task_id

    def get_trigger_time(self) -> datetime:
        return self.trigger_time

    def get_user_id(self):
        return self.user_id

    def get_visible_hours(self) -> Union[None, Set[int]]:
        return self.visible_hours

    def get_visible_wdays(self) -> Union[None, Set[int]]:
        return self.visible_wdays


@wrap_response
def create_plan(certificate_repository, repository_factory):
    params = HTTPParams()
    authentication_plugin = AuthenticationPlugin(
        certificate_repository=certificate_repository,
        params=params
    )
    use_case = CreatePlanUseCase(
        authentication_plugin=authentication_plugin,
        params=params,
        plan_repository=repository_factory.plan(),
    )
    try:
        plan = use_case.run()
        presenter = PlanPresenter(plan=plan)
        return presenter.format(), 201
    except InvalidRepeatTypeError as e:
        return {
            'message': '不支持的重复类型：{}'.format(e.repeat_type)
        }, 422
