from datetime import datetime, timedelta
from models.models import WishTask, WishTaskResult, AnaUserMsg
from config import *
import time
import emoji as emoji
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


class WishBody:
    def __init__(self):
        self.search_body = {
            "track_total_hits": True,
            "query": {
                "bool": {
                    "filter": [],
                    "must": [
                                {
                                    "bool": {
                                        "should": [

                                        ]
                                    }
                                }
                            ],
                    "must_not": []
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
                "sold_total_1": {
                    "sum": {
                        "field": "sold_last_1"
                    }
                },
                "gmv_total_1": {
                    "sum": {
                        "field": "gmv_last_1"
                    }
                },
                "sum_total_bought": {
                    "sum": {
                        "field": "total_bought"
                    }
                }
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
            "sold_last_1",
            "gmv_last_1",
            "sold_last_7",
            "gmv_last_7",
            "sold_last_30",
            "gmv_last_30",
            "price",
            "total_bought",
            "review_score",
            "review_number"
        ]
        self.element_e = [
            "shop_name",
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

        for group in eval(task_params['condition']):
            element_list = []
            not_list = []
            for element in group:

                # 基础条件: 店铺,品类
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


async def wish_handle(group, task):
    logger.info("wish report task start")
    hy_task = ANATask(task)
    index_result = None
    task = hy_task.task_data

    es = WishBody()
    search_body = es.create_search(task)
    es_connection = Elasticsearch(hosts=AMAZON_ELASTICSEARCH_URL, timeout=ELASTIC_TIMEOUT)
    index_result = await es_connection.search(
        index=task['index_name'],
        body=search_body,
        size=task['result_count'])
    try:
        search_body = es.create_search(task)
        es_connection = Elasticsearch(hosts=AMAZON_ELASTICSEARCH_URL, timeout=ELASTIC_TIMEOUT)
        index_result = await es_connection.search(
                index=task['index_name'],
                body=search_body,
                size=task['result_count'])
    except Exception as e:
        logger.error(f"{e}, **** Search failed ****")
        with closing(db_session_mk(autocommit=True)) as db_session:
            time_now = (datetime.now() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
            ret = db_session.query(WishTask) \
                .filter(WishTask.task_id == task['task_id']) \
                .update({WishTask.status: 3,
                         WishTask.update_time: time_now,
                         WishTask.report_chart: "查询失败请检查条件是否正确,若条件无误请重新保存任务或联系客服"},
                        synchronize_session=False)
            try:
                db_session.commit()
            except:
                db_session.rollback()
    get_result_count = 0
    sum_sold_total_7 = 0
    sum_gmv_total_7 = 0
    sum_sold_total_1 = 0
    sum_gmv_total_1 = 0
    with closing(db_session_mk(autocommit=False)) as db_session:
        if index_result['hits']['hits']:
            for result_value in index_result['hits']['hits']:
                #  插入商品信息
                t = WishTaskResult()
                t.task_id = task['task_id']
                t.pid = result_value['_source']["pid"]
                t.img = f"https://contestimg.wish.com/api/webimage/{result_value['_source']['pid']}-0-large"
                t.title = emoji.demojize(result_value['_source']["title"])
                t.shop_name = emoji.demojize(result_value['_source']["shop_name"])
                t.price = result_value['_source']["price"]
                t.sold_last_1 = result_value['_source']["sold_last_1"]
                t.gmv_last_1 = result_value['_source']["gmv_last_1"]
                t.sold_last_7 = result_value['_source']["sold_last_7"]
                t.gmv_last_7 = round(result_value['_source']["gmv_last_7"], 2)
                t.sold_last_30 = result_value['_source']["sold_last_30"]
                t.gmv_last_30 = round(result_value['_source']["gmv_last_30"], 2)
                t.total_bought = result_value['_source']["total_bought"]
                t.total_wishlist = result_value['_source']["total_wishlist"]
                t.review_score = result_value['_source']["review_score"]

                db_session.add(t)
                get_result_count += 1
                sum_sold_total_7 += result_value['_source']["sold_last_7"]
                sum_gmv_total_7 += result_value['_source']["gmv_last_7"]
                sum_sold_total_1 += result_value['_source']["sold_last_1"]
                sum_gmv_total_1 += result_value['_source']["gmv_last_1"]

            time_now = (datetime.now() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
            ret = db_session.query(WishTask) \
                .filter(WishTask.task_id == task['task_id']) \
                .update({WishTask.status: 2,
                         WishTask.update_time: time_now,
                         WishTask.product_total: get_result_count,
                         WishTask.sold_total_7: sum_sold_total_7,
                         WishTask.gmv_total_7: round(sum_gmv_total_7, 2),
                         WishTask.sold_total_1: sum_sold_total_1,
                         WishTask.gmv_total_1: round(sum_gmv_total_1, 2),
                         WishTask.report_chart: f"查询到{index_result['hits']['total']['value']}条满足条件的商品数据",
                         WishTask.get_result_count: get_result_count},
                        synchronize_session=False)

            logger.info("*************************Wish 报告消息正在写入*************************")
            m = AnaUserMsg()
            m.user_id = task["user_id"]
            m.msg_id = str(task['user_id']) + str(int(time.time())),
            m.msg_content = "您的Wish自定义报告《" + task['report_name'] + "》于" + str(time_now) + "完成,请及时查看报告结果",
            m.create_at = time_now
            m.status = 0
            db_session.add(m)
            logger.info("*************************Wish 报告消息写入成功*************************")

            try:
                db_session.commit()
            except Exception as e:
                logger.info(e)
                db_session.rollback()

        else:
            time_now = (datetime.now() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
            ret = db_session.query(WishTask) \
                .filter(WishTask.task_id == task['task_id']) \
                .update({WishTask.status: 3,
                         WishTask.update_time: time_now,
                         WishTask.report_chart: "未查询到满足条件的商品,请检查设置条件是否正确"},
                        synchronize_session=False)
            logger.info("*************************Wish 报告消息正在写入*************************")
            m = AnaUserMsg()
            m.user_id = task["user_id"]
            m.msg_id = str(task['user_id']) + str(int(time.time())),
            m.msg_content = "您的Wish自定义报告《" + task['report_name'] + "》于" + str(time_now) + "完成,请及时查看报告结果",
            m.create_at = time_now
            m.status = 0
            db_session.add(m)
            logger.info("*************************Wish 报告消息写入成功*************************")
            try:
                db_session.commit()
            except Exception as e:
                logger.info(e)
                db_session.rollback()

    logger.info("wish report task over")

