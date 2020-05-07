import json
import pipeflow
from config import *
from util.log import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pipeflow import HTTPOutputEndpoint, HTTPInputEndpoint, NsqInputEndpoint
from handlers import *

WORKER_NUMBER = 4

engine = create_engine(SQLALCHEMY_DATABASE_URI,
                       echo=SQLALCHEMY_ECHO,
                       pool_size=SQLALCHEMY_POOL_SIZE,
                       max_overflow=SQLALCHEMY_POOL_MAX_OVERFLOW,
                       pool_recycle=SQLALCHEMY_POOL_RECYCLE,
                       )
db_session_mk = sessionmaker(bind=engine)


def run():
    server = pipeflow.Server()
    # ebay 报表任务处理
    ebay_end = NsqInputEndpoint(EBAY_REPORT_TASK_TOPIC, 'ebay_analysis', WORKER_NUMBER, **INPUT_NSQ_CONF)
    group = server.add_group('ebay_report', WORKER_NUMBER)
    group.set_handle(ebay_handle)
    group.add_input_endpoint('input', ebay_end)

    # shopee 报表处理
    shopee_end = NsqInputEndpoint(SHOPEE_REPORT_TASK_TOPIC, 'shopee_analysis', WORKER_NUMBER, **INPUT_NSQ_CONF)
    group = server.add_group('shopee_report', WORKER_NUMBER)
    group.set_handle(shopee_handle)
    group.add_input_endpoint('input', shopee_end)

    # 处理 Amazon报表任务
    amazon_input_end = NsqInputEndpoint(AMAZON_REPORT_TASK_TOPIC, 'amazon_analysis', WORKER_NUMBER, **INPUT_NSQ_CONF)
    amazon_report_group = server.add_group('amazon_report', WORKER_NUMBER)
    amazon_report_group.set_handle(amazon_handle)
    amazon_report_group.add_input_endpoint("input", amazon_input_end)

    # 处理 wish 报表任务
    wish_input_end = NsqInputEndpoint(WISH_REPORT_TASK_TOPIC, 'wish_analysis', WORKER_NUMBER, **INPUT_NSQ_CONF)
    wish_report_group = server.add_group('wish_report', WORKER_NUMBER)
    wish_report_group.set_handle(wish_handle)
    wish_report_group.add_input_endpoint("input", wish_input_end)

    # 把数据库任务 推到NSQ中
    task_save_to_nsq = TaskSaveToNsqScheduler(db_session_mk)
    server.add_worker(task_save_to_nsq.schedule)

    server.run()


if __name__ == '__main__':
    run()
