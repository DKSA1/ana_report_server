from datetime import datetime, timedelta
from models.models import AmazonTaskResult, AmazonTask, AnaUserMsg
from config import *
import time
from util.log import logger
from util.task_protocol import ANATask

from aioelasticsearch import Elasticsearch
from contextlib import closing
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
engine = create_engine(SQLALCHEMY_DATABASE_URI,
                       echo=SQLALCHEMY_ECHO,
                       pool_size=SQLALCHEMY_POOL_SIZE,
                       max_overflow=SQLALCHEMY_POOL_MAX_OVERFLOW,
                       pool_recycle=SQLALCHEMY_POOL_RECYCLE,
                       )
db_session_mk = sessionmaker(bind=engine)

WORKER_NUMBER = 1


class AmazonBody:
    def __init__(self):
        self.search_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "bool": {
                                "should": [

                                ]
                            }
                        }
                    ]
                }
            },
            "aggs": {
                "sold_total_7": {
                    "sum": {
                        "field": "sold_last_7"
                    }
                },
                "gmv_total_7": {
                    "sum": {
                        "field": "gmv_last_7"
                    }
                },
            },
            "size": 50,
            "sort": [
                {
                    "date": {
                        "order": "desc"
                    }
                }
            ]
        }
        self.element_data = [
            "sold_last_7",
            "gmv_last_7",
            "sold_last_30",
            "gmv_last_30",
            "price",
            "review_score",
            "review_number"
        ]
        self.element_e = [
            "brand",
            "merchant_name",
            "delivery",
            "category_id"
        ]
        self.element_symbol = {
            ">": "gt",
            "<": "lt",
            "≥": "gte",
            "≤": "lte"
        }

    def create_search(self, task_params):

        # 排序条件
        if task_params['order_by'] and task_params['order']:
            self.search_body['sort'][0] = {
                task_params['order_by']: {
                    "order": task_params['order']
                }
            }

        # 结果数限制
        self.search_body['size'] = task_params['result_count'] if task_params['result_count'] else 50

        # 过滤site
        self.search_body['query']['bool']['must'].append({"term":{"site":{"value":task_params['site']}}})

        for group in eval(task_params['condition']):
            element_list = []
            not_list = []
            for element in group:
                # # 七天销量判断
                # if element['field'] == 'sold_last_7' and element['field'] != '=':
                #     element_list.append(
                #         {"range": {"sold_last_7": {self.element_symbol[element['field']]: element['value']}}}
                #     )
                # # 七天销售额判断
                # if element['field'] == 'gmv_last_7' and element['field'] != '=':
                #     element_list.append(
                #         {"range": {"gmv_last_7": {self.element_symbol[element['field']]: element['value']}}}
                #     )
                # # 30天销量判断
                # if element['field'] == 'sold_last_30' and element['field'] != '=':
                #     element_list.append(
                #         {"range": {"sold_last_30": {self.element_symbol[element['field']]: element['value']}}}
                #     )
                # # 30天销售额判断
                # if element['field'] == 'gmv_last_30' and element['field'] != '=':
                #     element_list.append(
                #         {"range": {"gmv_last_30": {self.element_symbol[element['field']]: element['value']}}}
                #     )
                # # 单价判断
                # if element['field'] == 'price' and element['field'] != '=':
                #     element_list.append(
                #         {"range": {"price": {self.element_symbol[element['field']]: element['value']}}}
                #     )
                # # 评分判断
                # if element['field'] == 'review_score' and element['field'] != '=':
                #     element_list.append(
                #         {"range": {"review_score": {self.element_symbol[element['field']]: element['value']}}}
                #     )
                # # 评论数判断
                # if element['field'] == 'review_number' and element['field'] != '=':
                #     element_list.append(
                #         {"range": {"review_number": {self.element_symbol[element['field']]: element['value']}}}
                #     )

                # 基础条件: 商家,品牌,品类
                if element['field'] in self.element_e:
                    element_list.append({"term": {element['field']: {"value": element['value']}}})

                # 数据条件
                if element['field'] in self.element_data:
                    if element['operator'] == '=':
                        element_list.append({"term": {element['field']: {"value": element['value']}}})
                    else:
                        element_list.append({
                            "range": {
                                element['field']: {
                                    self.element_symbol[element['operator']]: element['value']
                                }
                            }
                        })

                # 关键词搜索
                if element['field'] == "keyword":
                    self.search_body['query']['bool']['must'].append({
                        "multi_match": {"query": element['value'], "fuzziness": "AUTO",
                                        "minimum_should_match": "2<70%"}})

            if not_list:
                self.search_body['query']['bool']['must'][0]['bool']['should'].append({
                    "bool": {
                        "must": element_list,
                        "must_not": not_list
                    }
                })
            else:
                self.search_body['query']['bool']['must'][0]['bool']['should'].append({
                    "bool": {
                        "must": element_list
                    }
                })

        return self.search_body


async def amazon_handle(group, task):
    logger.info("amazon report task start")
    hy_task = ANATask(task)
    task_log = [hy_task.task_type, hy_task.task_data]

    task = hy_task.task_data

    es = AmazonBody()
    search_body = es.create_search(task)
    try:
        es_connection = Elasticsearch(hosts=AMAZON_ELASTICSEARCH_URL, timeout=ELASTIC_TIMEOUT)
        index_result = await es_connection.search(
                index=task['index_name'],
                body=search_body,
                size=task['result_count'])
    except Exception as e:
        with closing(db_session_mk(autocommit=True)) as db_session:
            time_now = (datetime.now() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
            ret = db_session.query(AmazonTask) \
                .filter(AmazonTask.task_id == task['task_id']) \
                .update({AmazonTask.status: 3,
                         AmazonTask.update_time: time_now,
                         AmazonTask.report_chart: "查询失败请检查条件是否正确,若条件无误请重新保存任务或联系客服"},
                        synchronize_session=False)
            try:
                db_session.commit()
            except:
                db_session.rollback()
    get_result_count = 0
    with closing(db_session_mk(autocommit=True)) as db_session:
        if index_result['hits']['hits']:
            for result_value in index_result['hits']['hits']:
                #  插入商品信息
                t = AmazonTaskResult()
                t.task_id = task['task_id']
                t.asin = result_value['_source']["asin"]
                t.img = result_value['_source']["img"]
                t.title = result_value['_source']["title"]
                t.site = result_value['_source']["site"]
                t.brand = result_value['_source']["brand"]
                t.merchant_name = result_value['_source']["merchant_name"]
                t.price = result_value['_source']["price"]
                t.top_category_rank = result_value['_source']["top_category_rank"]
                t.sold_last_7 = result_value['_source']["sold_last_7"]
                t.gmv_last_7 = round(result_value['_source']["gmv_last_7"], 2)
                t.sold_last_30 = result_value['_source']["sold_last_30"]
                t.gmv_last_30 = round(result_value['_source']["gmv_last_30"], 2)
                t.review_score = result_value['_source']["review_score"]

                db_session.add(t)
                get_result_count += 1

            time_now = (datetime.now() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
            ret = db_session.query(AmazonTask) \
                .filter(AmazonTask.task_id == task['task_id']) \
                .update({AmazonTask.status: 2,
                         AmazonTask.update_time: time_now,
                         AmazonTask.product_total: index_result['hits']['total']['value'],
                         AmazonTask.sold_total_7: index_result['aggregations']['sold_total_7']['value'],
                         AmazonTask.gmv_total_7: round(index_result['aggregations']['gmv_total_7']['value'], 2),
                         AmazonTask.report_chart: f"查询到{index_result['hits']['total']['value']}条满足条件的商品数据",
                         AmazonTask.get_result_count: get_result_count},
                        synchronize_session=False)

            logger.info("*************************Amazon 报告消息正在写入*************************")
            m = AnaUserMsg()
            m.user_id = task["user_id"]
            m.msg_id = str(task['user_id']) + str(int(time.time())),
            m.msg_content = "您的Amazon自定义报告《" + task['report_name'] + "》于" + str(time_now) + "完成,请及时查看报告结果",
            m.create_at = time_now
            m.status = 0
            db_session.add(m)
            logger.info("*************************Amazon 报告消息写入成功*************************")

            try:
                db_session.commit()
            except:
                db_session.rollback()

        else:
            time_now = (datetime.now() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
            ret = db_session.query(AmazonTask) \
                .filter(AmazonTask.task_id == task['task_id']) \
                .update({AmazonTask.status: 3,
                         AmazonTask.update_time: time_now,
                         AmazonTask.report_chart: "未查询到满足条件的商品,请检查设置条件是否正确"},
                        synchronize_session=False)
            logger.info("*************************Amazon 报告消息正在写入*************************")
            m = AnaUserMsg()
            m.user_id = task["user_id"]
            m.msg_id = str(task['user_id']) + str(int(time.time())),
            m.msg_content = "您的Amazon自定义报告《" + task['report_name'] + "》于" + str(time_now) + "完成,请及时查看报告结果",
            m.create_at = time_now
            m.status = 0
            db_session.add(m)
            logger.info("*************************Amazon 报告消息写入成功*************************")
            try:
                db_session.commit()
            except:
                db_session.rollback()

    logger.info("amazon report task over")

# async def run():
#
#     with closing(db_session_mk(autocommit=True)) as db_session:
#         tasks = db_session.query(AmazonTask.task_id, AmazonTask.site, AmazonTask.index_name,
#                                  AmazonTask.save_result_numb, AmazonTask.context,
#                                  AmazonTask.order_by, AmazonTask.order, AmazonTask.type) \
#             .filter(AmazonTask.status == 0).all()
#
#     if tasks:
#         for task in tasks:
#             task_info = {
#                 "task_id": task.task_id,
#                 "type": task.type,
#                 "site": task.site,
#                 "condition": str(task.context),
#                 "result_count": task.save_result_numb,
#                 "order_by": task.order_by,
#                 "order": task.order,
#                 "index_name": task.index_name
#             }
#
#             nsq_msg = {
#                 "task": "amazon_report_product",
#                 "data": task_info
#             }
#
#         _ = await amazon_handle(None, task=nsq_msg)
#
#
#
#
#
# if __name__ == '__main__':
#
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(run())
