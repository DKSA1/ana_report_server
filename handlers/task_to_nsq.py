import asyncio
from contextlib import closing
from datetime import datetime, timedelta
from util.log import logger
from config import *
from models.models import AmazonTask, WishTask, WalmartTask
from util.task_protocol import pub_to_nsq


class TaskSaveToNsqScheduler:

    def __init__(self, db_session_mk):
        self.db_session_mk = db_session_mk

    async def schedule(self, server):
        while True:
            with closing(self.db_session_mk(autocommit=False)) as db_session:

                tasks = db_session.query(AmazonTask.task_id, AmazonTask.site, AmazonTask.index_name,
                                         AmazonTask.save_result_numb, AmazonTask.context, AmazonTask.user_id,
                                         AmazonTask.order_by, AmazonTask.order, AmazonTask.type, AmazonTask.report_name) \
                    .filter(AmazonTask.status == 0).all()

                if tasks:
                    for task in tasks:
                        task_info = {
                            "task_id": task.task_id,
                            "type": task.type,
                            "site": task.site,
                            "condition": str(task.context),
                            "result_count": task.save_result_numb,
                            "order_by": task.order_by,
                            "order": task.order,
                            "index_name": task.index_name,
                            "user_id": task.user_id,
                            "report_name": task.report_name
                        }

                        nsq_topic = AMAZON_REPORT_TASK_TOPIC
                        nsq_msg = {
                            "task": "amazon_report_product",
                            "data": task_info
                        }
                        task_status = await pub_to_nsq(NSQ_NSQD_HTTP_ADDR, nsq_topic, nsq_msg)

                        if task_status != 200:
                            logger.info(f"{task.task_id} save to nsq failed")
                            continue
                        else:
                            time_now = (datetime.now() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
                            ret = db_session.query(AmazonTask) \
                                .filter(AmazonTask.task_id == task.task_id) \
                                .update({AmazonTask.status: 1, AmazonTask.update_time: time_now,
                                         AmazonTask.report_chart: "报告任务正在执行,请耐心等待~!"},
                                        synchronize_session=False)
                            try:
                                db_session.commit()
                            except:
                                db_session.rollback()

            with closing(self.db_session_mk(autocommit=False)) as db_session:

                wish_tasks = db_session.query(WishTask.task_id, WishTask.index_name,
                                         WishTask.save_result_numb, WishTask.context, WishTask.user_id,
                                         WishTask.order_by, WishTask.order, WishTask.type, WishTask.report_name) \
                    .filter(WishTask.status == 0).all()

                if wish_tasks:
                    for task in wish_tasks:
                        task_info = {
                            "task_id": task.task_id,
                            "type": task.type,
                            "condition": str(task.context),
                            "result_count": task.save_result_numb,
                            "order_by": task.order_by,
                            "order": task.order,
                            "index_name": task.index_name,
                            "user_id": task.user_id,
                            "report_name": task.report_name
                        }

                        nsq_topic = WISH_REPORT_TASK_TOPIC
                        nsq_msg = {
                            "task": "wish_report_product",
                            "data": task_info
                        }
                        task_status = await pub_to_nsq(NSQ_NSQD_HTTP_ADDR, nsq_topic, nsq_msg)

                        if task_status != 200:
                            logger.info(f"{task.task_id} save to nsq failed")
                            continue
                        else:
                            time_now = (datetime.now() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
                            ret = db_session.query(AmazonTask) \
                                .filter(WishTask.task_id == task.task_id) \
                                .update({WishTask.status: 1, WishTask.update_time: time_now,
                                         WishTask.report_chart: "报告任务正在执行,请耐心等待~!"},
                                        synchronize_session=False)
                            try:
                                db_session.commit()
                            except:
                                db_session.rollback()

            with closing(self.db_session_mk(autocommit=False)) as db_session:

                wish_tasks = db_session.query(WalmartTask.task_id, WalmartTask.index_name,
                                         WalmartTask.save_result_numb, WalmartTask.context, WalmartTask.user_id,
                                         WalmartTask.order_by, WalmartTask.order, WalmartTask.type, WalmartTask.report_name) \
                    .filter(WalmartTask.status == 0).all()

                if wish_tasks:
                    for task in wish_tasks:
                        task_info = {
                            "task_id": task.task_id,
                            "type": task.type,
                            "condition": str(task.context),
                            "result_count": task.save_result_numb,
                            "order_by": task.order_by,
                            "order": task.order,
                            "index_name": task.index_name,
                            "user_id": task.user_id,
                            "report_name": task.report_name
                        }

                        nsq_topic = WALMART_REPORT_TASK_TOPIC
                        nsq_msg = {
                            "task": "walmart_report_product",
                            "data": task_info
                        }
                        task_status = await pub_to_nsq(NSQ_NSQD_HTTP_ADDR, nsq_topic, nsq_msg)

                        if task_status != 200:
                            logger.info(f"{task.task_id} save to nsq failed")
                            continue
                        else:
                            time_now = (datetime.now() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
                            ret = db_session.query(AmazonTask) \
                                .filter(WalmartTask.task_id == task.task_id) \
                                .update({WalmartTask.status: 1, WalmartTask.update_time: time_now,
                                         WalmartTask.report_chart: "报告任务正在执行,请耐心等待~!"},
                                        synchronize_session=False)
                            try:
                                db_session.commit()
                            except:
                                db_session.rollback()

            logger.info("no task status=0, resting...")
            await asyncio.sleep(15)