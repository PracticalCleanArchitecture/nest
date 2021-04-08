# -*- coding: utf8 -*-
from datetime import datetime
from typing import List

from pypika import Order, Query, Table, Tables

from nest.app.entity.plan import IPlanRepository, Plan
from nest.repository.db_operation import DatabaseOperationMixin


class DatabasePlanRepository(DatabaseOperationMixin, IPlanRepository):
    def __init__(self, connection):
        super(DatabasePlanRepository, self).__init__(connection)

    def add(self, plan: Plan):
        now = datetime.now()
        insert_id = self.insert_to_db({
            'repeat_type': plan.repeat_type,
            'task_id': plan.task_id,
            'trigger_time': plan.trigger_time,
            'ctime': now,
            'mtime': now,
        }, 't_plan')

        plan.id = insert_id

    def find_as_queue(self, *, page: int, per_page: int, user_id: int, max_trigger_time=None) -> List[Plan]:
        plan_table, task_table = Tables('t_plan', 't_task')
        query = Query\
            .from_(plan_table)\
            .left_join(task_table)\
            .on(plan_table.task_id == task_table.id)\
            .select(plan_table.star)\
            .where(task_table.user_id == user_id)\
            .orderby(plan_table.trigger_time, order=Order.asc)\
            .limit(per_page)\
            .offset((page - 1) * per_page)

        if isinstance(max_trigger_time, datetime):
            query = query.where(plan_table.trigger_time < max_trigger_time)

        print('sql', query.get_sql(quote_char=None))
        plans = []
        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query.get_sql(quote_char=None))
                plan_dicts = cursor.fetchall()

        for plan_dict in plan_dicts:
            plan = Plan()
            plan.id = plan_dict['id']
            plan.repeat_type = plan_dict['repeat_type']
            plan.task_id = plan_dict['task_id']
            plan.trigger_time = plan_dict['trigger_time']
            plans.append(plan)
        return plans

    def find_by_id(self, id_: int) -> Plan:
        plan_table = Table('t_plan')
        query = Query\
            .from_(plan_table)\
            .delete()\
            .where(plan_table.id == id_)
        sql = query.get_sql(quote_char=None)
        print('sql', sql)
        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                plan_dict = cursor.fetchone()
                if plan_dict is None:
                    return None
                plan = Plan()
                plan.id = plan_dict['id']
                plan.repeat_type = plan_dict['repeat_type']
                plan.task_id = plan_dict['task_id']
                plan.trigger_time = plan_dict['trigger_time']
                return plan

    def remove(self, id_: int):
        self.remove_from_db(id_, 't_plan')
