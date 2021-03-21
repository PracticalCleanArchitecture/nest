# -*- coding: utf8 -*-
from typing import List

from nest.app.entity.plan import IPlanRepository, Plan
from nest.app.use_case.authentication_plugin import IAuthenticationPlugin
from nest.app.use_case.pop_plan import IParams, PopPlanUseCase


class MockAuthenticationPlugin(IAuthenticationPlugin):
    def authenticate(self):
        pass


class MockParams(IParams):
    def get_size(self) -> int:
        return 1

    def get_user_id(self) -> int:
        return 1234567890


class MockPlanRepository(IPlanRepository):
    def add(self, plan: Plan):
        pass

    def find_as_queue(self, *, page: int, per_page: int, user_id: int, max_trigger_time=None) -> List[Plan]:
        return [Plan()]

    def remove(self, id_: int):
        pass


def test_dequeue():
    use_case = PopPlanUseCase(
        authentication_plugin=MockAuthenticationPlugin(),
        params=MockParams(),
        plan_repository=MockPlanRepository()
    )
    plans = use_case.run()
    assert plans
    assert len(plans) == 1