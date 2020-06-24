from datetime import datetime, timedelta
from models.models import WalmartTask, WalmartTaskResult, AnaUserMsg, AnaUserPermission
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


class WalmartBody:
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
            "review_score",
            "review_number"
        ]
        self.element_e = [
            "merchant_name",
            "category_id",
            "brand"
        ]
        self.element_symbol = {
            ">": "gt",
            "<": "lt",
            "≥": "gte",
            "≤": "lte"
        }

    def create_search(self, task_params):
        category_name = None
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
                    if element.get('name'):  # 如果是 类目搜索 获取
                        category_name = element.get('name')
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

        return self.search_body, category_name


async def walmart_handle(group, task):
    logger.info("walmart report task start")
    hy_task = ANATask(task)
    index_result = None
    task = hy_task.task_data

    es = WalmartBody()

    try:
        search_body, category_name = es.create_search(task)
        # 获取用户 数据过滤信息 对请求 数据进行过滤
        with closing(db_session_mk(autocommit=True)) as db_session:
            permission_info = db_session.query(AnaUserPermission.is_bailun, AnaUserPermission.walmart_permission,
                                               AnaUserPermission.baned_seller, AnaUserPermission.baned_brand) \
                .filter(AnaUserPermission.user_id == task["user_id"]).first()
            if permission_info:
                if permission_info.is_bailun == "4k":
                    pass
                else:
                    category_list = eval(permission_info.walmart_permission).get("all")
                    if category_list:
                        search_body['query']['bool']['filter'].append({"terms": {"category_id": category_list}})
                    seller_list = eval(permission_info.baned_seller).get("walmart")
                    if seller_list:
                        search_body['query']['bool']['must_not'].append({"terms": {"shop_name": seller_list}})
                    brand_list = eval(permission_info.baned_brand).get("walmart")
                    if brand_list:
                        search_body['query']['bool']['must_not'].append({"terms": {"brand": brand_list}})

        es_connection = Elasticsearch(hosts=AMAZON_ELASTICSEARCH_URL, timeout=ELASTIC_TIMEOUT)
        index_result = await es_connection.search(
                index=task['index_name'],
                body=search_body,
                size=task['result_count'])
    except Exception as e:
        logger.error(f"{e}, **** Search failed ****")
        with closing(db_session_mk(autocommit=False)) as db_session:
            time_now = (datetime.now() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
            ret = db_session.query(WalmartTask) \
                .filter(WalmartTask.task_id == task['task_id']) \
                .update({WalmartTask.status: 3,
                         WalmartTask.update_time: time_now,
                         WalmartTask.report_chart: "查询失败请检查条件是否正确,若条件无误请重新保存任务或联系客服"},
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
    if index_result['hits']['hits']:
        with closing(db_session_mk(autocommit=False)) as db_session:
            for result_value in index_result['hits']['hits']:
                #  插入商品信息
                t = WalmartTaskResult()
                t.task_id = task['task_id']
                t.item_id = result_value['_source']["item_id"]
                t.img = result_value['_source']["img"]
                t.title = emoji.demojize(result_value['_source']["title"])
                t.brand = str(result_value['_source']["brand"])
                t.merchant_name = emoji.demojize(result_value['_source']["merchant_name"])
                t.price = result_value['_source']["price"]
                t.sold_last_1 = result_value['_source']["sold_last_1"]
                t.gmv_last_1 = result_value['_source']["gmv_last_1"]
                t.sold_last_7 = result_value['_source']["sold_last_7"]
                t.gmv_last_7 = round(result_value['_source']["gmv_last_7"], 2)
                t.sold_last_30 = result_value['_source']["sold_last_30"]
                t.gmv_last_30 = round(result_value['_source']["gmv_last_30"], 2)
                t.review_score = result_value['_source']["review_score"]
                t.review_number = result_value['_source']["review_number"]
                path_list = []
                if category_name:
                    for keyword in result_value['_source']["category_path"]:
                        if category_name in keyword:
                            for name in keyword.split('->'):
                                path_list.append(name)
                else:
                    if result_value['_source']["category_path"]:
                        for name in result_value['_source']["category_path"][0].split('->'):
                            path_list.append(name)
                t.category_path = str(path_list)

                db_session.add(t)
                get_result_count += 1
                sum_sold_total_7 += result_value['_source']["sold_last_7"]
                sum_gmv_total_7 += result_value['_source']["gmv_last_7"]
                sum_sold_total_1 += result_value['_source']["sold_last_1"]
                sum_gmv_total_1 += result_value['_source']["gmv_last_1"]
            try:
                db_session.commit()
            except Exception as e:
                logger.info(e)
                db_session.rollback()
        with closing(db_session_mk(autocommit=False)) as db_session:
            time_now = (datetime.now() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
            ret = db_session.query(WalmartTask) \
                .filter(WalmartTask.task_id == task['task_id']) \
                .update({WalmartTask.status: 2,
                         WalmartTask.update_time: time_now,
                         WalmartTask.product_total: get_result_count,
                         WalmartTask.sold_total_7: sum_sold_total_7,
                         WalmartTask.gmv_total_7: round(sum_gmv_total_7, 2),
                         WalmartTask.report_chart: f"查询到{index_result['hits']['total']['value']}条满足条件的商品数据",
                         WalmartTask.get_result_count: get_result_count},
                        synchronize_session=False)
            try:
                db_session.commit()
            except Exception as e:
                logger.info(e)
                db_session.rollback()

        with closing(db_session_mk(autocommit=False)) as db_session:
            m = AnaUserMsg()
            m.user_id = task["user_id"]
            m.msg_id = str(task['user_id']) + str(int(time.time())),
            m.msg_content = "您的Walmart自定义报告《" + task['report_name'] + "》于" + str(time_now) + "完成,请及时查看报告结果",
            m.create_at = time_now
            m.status = 0
            db_session.add(m)
            logger.info("*************************Walmart 报告消息写入成功*************************")

            try:
                db_session.commit()
            except Exception as e:
                logger.info(e)
                db_session.rollback()

    else:
        with closing(db_session_mk(autocommit=False)) as db_session:
            time_now = (datetime.now() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
            ret = db_session.query(WalmartTask) \
                .filter(WalmartTask.task_id == task['task_id']) \
                .update({WalmartTask.status: 3,
                         WalmartTask.update_time: time_now,
                         WalmartTask.report_chart: "未查询到满足条件的商品,请检查设置条件是否正确"},
                        synchronize_session=False)

            m = AnaUserMsg()
            m.user_id = task["user_id"]
            m.msg_id = str(task['user_id']) + str(int(time.time())),
            m.msg_content = "您的Walmart自定义报告《" + task['report_name'] + "》于" + str(time_now) + "完成,请及时查看报告结果",
            m.create_at = time_now
            m.status = 0
            db_session.add(m)
            logger.info("*************************Walmart 报告消息写入成功*************************")
            try:
                db_session.commit()
            except Exception as e:
                logger.info(e)
                db_session.rollback()

    logger.info("Walmart report task over")

