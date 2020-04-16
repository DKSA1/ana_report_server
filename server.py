import json
import pipeflow
from utils.log import logger
from pipeflow import HTTPOutputEndpoint, HTTPInputEndpoint, NsqInputEndpoint
from config import (
    HTTP_SYNC_ORDER_CONF,
    HTTP_RETURN_ORDER_CONF,
    HTTP_PUSH_DATA_CONF,
    NSQ_LOOKUPD_HTTP_ADDR,
)
from handlers import *

MAX_WORKERS = 4


def run():
    logger.info("start coupang api...")

    push_data_output = HTTPOutputEndpoint(**HTTP_PUSH_DATA_CONF)
    server = pipeflow.Server()
    """
    # by_time 抓单
    sync_order_input = HTTPInputEndpoint(**HTTP_SYNC_ORDER_CONF)
    og = server.add_group('sync_order:by_time', MAX_WORKERS)
    og.add_input_endpoint('input', sync_order_input)
    og.add_output_endpoint('push_data', push_data_output)
    og.set_handle(sync_order_handle)

    # returns_order 抓取coupang退款订单信息
    returns_order_input = HTTPInputEndpoint(**HTTP_RETURN_ORDER_CONF)
    og = server.add_group('returns_order:by_time', MAX_WORKERS)
    og.add_input_endpoint('input', returns_order_input)
    og.add_output_endpoint('push_data', push_data_output)
    og.set_handle(return_order_handle)

    """

    # by_time 抓单 nsq
    sync_order_input = NsqInputEndpoint(topic='coupang_sync_order_by_time',
                                        channel='channel_x',
                                        lookupd_http_addresses=[
                                            'http://{}'.format(NSQ_LOOKUPD_HTTP_ADDR)])  # nsq读消息的地址
    og = server.add_group('sync_order:by_time', MAX_WORKERS)
    og.set_handle(sync_order_handle)
    og.add_input_endpoint('coupang_sync_order_by_time', sync_order_input)
    og.add_output_endpoint('push_data', push_data_output)

    # by_time 抓取退款订单 nsq
    return_order_input = NsqInputEndpoint(topic='coupang_returns_order_by_time',
                                        channel='channel_x',
                                        lookupd_http_addresses=[
                                            'http://{}'.format(NSQ_LOOKUPD_HTTP_ADDR)])  # nsq读消息的地址
    ro = server.add_group('returns_order:by_time', MAX_WORKERS)
    ro.set_handle(return_order_handle)
    ro.add_input_endpoint('coupang_returns_order_by_time', return_order_input)
    ro.add_output_endpoint('push_data', push_data_output)

    server.run()


if __name__ == '__main__':
    run()
