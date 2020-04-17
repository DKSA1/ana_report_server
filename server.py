import json
import pipeflow
from config import *
from util.log import logger
from pipeflow import HTTPOutputEndpoint, HTTPInputEndpoint, NsqInputEndpoint
from handlers import *

WORKER_NUMBER = 4


def run():
    input_end = NsqInputEndpoint(EBAY_REPORT_TASK_TOPIC, 'ebay_analysis', WORKER_NUMBER, **INPUT_NSQ_CONF)
    logger.info('连接nsq成功,topic_name = {}, nsq_address={}'.format(EBAY_REPORT_TASK_TOPIC, INPUT_NSQ_CONF))
    server = pipeflow.Server()
    logger.info("pipeflow开始工作")
    group = server.add_group('main', WORKER_NUMBER)
    logger.info("抓取ebay任务")
    group.set_handle(ebay_handle)
    logger.info("处理ebay任务")
    group.add_input_endpoint('input', input_end)

    server.add_routine_worker(ebay_maintain_task, interval=5, immediately=True)
    server.run()


if __name__ == '__main__':
    run()
