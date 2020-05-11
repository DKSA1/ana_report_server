import json
import time

from datetime import datetime, timedelta

import emoji as emoji
from sqlalchemy import create_engine, select, and_, update
from sqlalchemy.dialects.mysql import insert

import pipeflow
from models.models import shopee_custom_report_task, shopee_category, shopee_product_report_result, ana_user_msg
from pipeflow import NsqInputEndpoint
from config import *
from util.log import logger
from util.task_protocol import ANATask

from aioelasticsearch import Elasticsearch

WORKER_NUMBER = 1


# TOPIC_NAME = REPORT_TASK_TOPIC + '.product'


class ESBody:
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
                "sum_sold_total": {
                    "sum": {
                        "field": "sold_total"
                    }
                },
                "sum_sold_last_7": {
                    "sum": {
                        "field": "sold_last_7"
                    }
                },
                "sum_sold_last_3": {
                    "sum": {
                        "field": "sold_last_3"
                    }
                },
                "sum_gmv_last_7": {
                    "sum": {
                        "field": "gmv_last_7"
                    }
                },
                "sum_gmv_last_3": {
                    "sum": {
                        "field": "gmv_last_3"
                    }
                },
                "sum_sold_last_30": {
                    "sum": {
                        "field": "sold_last_30"
                    }
                },
                "sum_gmv_last_30": {
                    "sum": {
                        "field": "gmv_last_30"
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
            "sold_last_30",
            "gmv_last_30",
            "price",
            "sold_total",
            "review_score",
            "favorite",
            "review_number"
        ]
        self.element_symbol = {
            ">": "gt",
            "<": "lt",
            ">=": "gte",
            "<=": "lte"
        }

    def create_search(self, task_params):

        # 排序条件
        if task_params['order_by'] and task_params['order']:
            order_dict = {
                'sold': 'sold_last_1',
                'gmv': 'gmv_last_1',
                'visit': 'visit_last_1'
            }
            if task_params['order_by'] in order_dict:
                self.search_body['sort'][0] = {
                    order_dict[task_params['order_by']]: {
                        "order": task_params['order']
                    }
                }
            else:
                self.search_body['sort'][0] = {
                    task_params['order_by']: {
                        "order": task_params['order']
                    }
                }

        # 结果数限制
        self.search_body['size'] = task_params['result_count'] if task_params['result_count'] else 50

        # 过滤site
        self.search_body['query']['bool']['must'].append({"term": {"site": {"value": task_params['site']}}})

        for group in eval(task_params['condition']):
            #
            element_list = []
            not_list = []
            for element in group:
                # 上架时间判断
                # if element['field'] == 'min_gen_time':
                #     element_list.append(
                #         {"range": {"gen_time": {"gte": element['value'], "format": "yyyy-MM-dd"}}}
                #     )
                # if element['field'] == 'max_gen_time':
                #     element_list.append(
                #         {"range": {"gen_time": {"lte": element['value'], "format": "yyyy-MM-dd"}}}
                #     )
                if element['field'] == 'gen_time':
                    gen_time_list = element['value'].split("|")
                    element_list.append(
                        {
                            "range": {
                                "gen_time": {
                                    "gte": gen_time_list[0],
                                    "lte": gen_time_list[1],
                                    "format": "yyyy-MM-dd"
                                }
                            }
                        }
                    )

                # 注册地判断
                if element['field'] == 'shop_location':
                    if element['value'] == "0":
                        pass
                    elif element['value'] == "1":
                        element_list.append(
                            {
                                "term": {
                                    "shop_location": "Overseas"
                                }
                            }
                        )

                    elif element['value'] == "2":
                        not_list.append(
                            {
                                "term": {
                                    "shop_location": {
                                        "value": "Overseas"
                                    }
                                }
                            }
                        )


                # 品类过滤
                # TODO:
                if element['field'] == 'category':
                    cid_list = element['value'].split('|')
                    element_list.append({"term": {'category_id': {"value": cid_list[1]}}})
                    # element_list.append({"term": {'category_id': {"value": element['value']}}})

                # 基础条件: 商家,店铺
                if element['field'] == 'merchant_name' or element['field'] == 'shop_name':
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



engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=SQLALCHEMY_POOL_PRE_PING,
    echo=SQLALCHEMY_ECHO,
    pool_size=SQLALCHEMY_POOL_SIZE,
    max_overflow=SQLALCHEMY_POOL_MAX_OVERFLOW,
    pool_recycle=SQLALCHEMY_POOL_RECYCLE,
)




async def shopee_handle(group, task):
    hy_task = ANATask(task)
    task_log = [hy_task.task_type, hy_task.task_data]
    task = hy_task.task_data
    time_now = (datetime.now() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    with engine.connect() as conn:

        es = ESBody()
        # # 逐个任务完成查询es写入db
        search_body = es.create_search(task)
        logger.info("========================es请求体================================")
        logger.info(json.dumps(search_body))
        logger.info("========================es请求体================================")

        es_connection = Elasticsearch(hosts=EBAY_ELASTICSEARCH_URL, timeout=ELASTIC_TIMEOUT)

        index_result = await es_connection.search(
            index=task['index_name'],
            body=search_body,
            size=task['result_count'])
        # 报告商品结果列表
        the_es_result = index_result['hits']['hits']
        name_ids = []
        # 构造品类IDS
        for item in the_es_result:
            for category_id in item['_source']['leaf_category_id']:
                name_ids.append(category_id)
        # 查出category_path
        select_category_name = select([
            shopee_category.c.category_name,
            shopee_category.c.category_id,
            shopee_category.c.category_id_path,
            shopee_category.c.category_name_path
        ]).where(
            and_(
                shopee_category.c.category_id.in_(name_ids),
                shopee_category.c.site == task['site']
            ))
        cursor_name = conn.execute(select_category_name)
        records_name = cursor_name.fetchall()
        logger.info("=======补全category_path的id========")
        logger.info(name_ids)
        logger.info("===============")
        # 生成类目path
        for db_info in records_name:
            for category in the_es_result:
                for low_id in category['_source']['leaf_category_id']:
                    if low_id == db_info['category_id']:
                        name_list = db_info['category_name_path'].split(':')
                        id_list = db_info['category_id_path'].split(':')
                        complete_list = []
                        category['_source']['category_path'] = []
                        try:
                            for i in range(3):
                                complete_list.append({"name": name_list.pop(0), "id": id_list.pop(0)})
                            category['_source']['category_path'].append(complete_list)
                        except Exception as e:
                            logger.info(e)
                            category['_source']['category_path'].append(complete_list)

        # 逐个商品更新db
        get_result_count = 0
        for item in the_es_result:
            # 构造商品dict
            result_info = {
                "task_id": task['task_id'],
                "pid": item['_source']['pid'],
                "img": 'https://cf.shopee.com.my/file/' + item['_source']['img'],
                "title": emoji.demojize(item['_source']['title']),
                "site": item['_source']['site'],
                "merchant_name": item['_source']['merchant_name'],
                "shop_name": item['_source']['shop_name'],
                # 需要构造
                "category_path": str(item['_source']['category_path']),
                "shop_location": item['_source']['shop_location'],
                "price": item['_source']['price'],
                "gmv_last_3": item['_source']['gmv_last_3'],
                "gmv_last_7": item['_source']['gmv_last_7'],
                "sold_last_7": item['_source']['sold_last_7'],
                "sold_last_3": item['_source']['sold_last_3'],
                "sold_total": item['_source']['sold_total'],
                "review_score": item['_source']['review_score'],
                "date": (datetime.now()).strftime('%Y-%m-%d %H:%M:%S'),
                "update_time": time_now
            }

            # 插入商品信息
            try:
                ins = insert(shopee_product_report_result)
                insert_stmt = ins.values(result_info)
                on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update(
                    task_id=insert_stmt.inserted.task_id,
                    pid=insert_stmt.inserted.pid,
                    img=insert_stmt.inserted.img,
                    title=insert_stmt.inserted.title,
                    site=insert_stmt.inserted.site,
                    merchant_name=insert_stmt.inserted.merchant_name,
                    shop_name=insert_stmt.inserted.shop_name,
                    category_path=insert_stmt.inserted.category_path,
                    shop_location=insert_stmt.inserted.shop_location,
                    price=insert_stmt.inserted.price,
                    gmv_last_3=insert_stmt.inserted.gmv_last_3,
                    gmv_last_7=insert_stmt.inserted.gmv_last_7,
                    sold_last_7=insert_stmt.inserted.sold_last_7,
                    sold_last_3=insert_stmt.inserted.sold_last_3,
                    sold_total=insert_stmt.inserted.sold_total,
                    review_score=insert_stmt.inserted.review_score,
                    date=insert_stmt.inserted.date,
                )
                result = conn.execute(on_duplicate_key_stmt)
                get_result_count += 1

                # 更新任务状态
                ins = update(shopee_custom_report_task)
                ins = ins.values({
                    "status": 1,
                    "update_time": time_now,
                    "get_result_count": get_result_count,
                    "product_total": index_result['hits']['total']['value'],
                    "sold_total": index_result['aggregations']['sum_sold_total']['value'],
                    "sum_sold_last_3": index_result['aggregations']['sum_sold_last_3']['value'],
                    "sum_sold_last_7": index_result['aggregations']['sum_sold_last_7']['value'],
                    "sum_sold_last_30": index_result['aggregations']['sum_sold_last_30']['value'],
                    "sum_gmv_last_3": round(index_result['aggregations']['sum_gmv_last_3']['value'], 2),
                    "sum_gmv_last_7": round(index_result['aggregations']['sum_gmv_last_7']['value'], 2),
                    "sum_gmv_last_30": round(index_result['aggregations']['sum_gmv_last_30']['value'], 2)
                }).where(
                    shopee_custom_report_task.c.task_id == task['task_id']
                )
                result = conn.execute(ins)
            except Exception as e:
                logger.info(e)
                # 更新任务状态
                ins = update(shopee_custom_report_task)
                ins = ins.values({
                    "status": 2,
                    "update_time": time_now,
                    "get_result_count": get_result_count,
                    "product_total": index_result['hits']['total']['value'],
                    "sold_total": index_result['aggregations']['sum_sold_total']['value'],
                    "sum_sold_last_3": index_result['aggregations']['sum_sold_last_3']['value'],
                    "sum_sold_last_7": index_result['aggregations']['sum_sold_last_7']['value'],
                    "sum_sold_last_30": index_result['aggregations']['sum_sold_last_30']['value'],
                    "sum_gmv_last_3": index_result['aggregations']['sum_gmv_last_3']['value'],
                    "sum_gmv_last_7": index_result['aggregations']['sum_gmv_last_7']['value'],
                    "sum_gmv_last_30": index_result['aggregations']['sum_gmv_last_30']['value']
                }).where(
                    shopee_custom_report_task.c.task_id == task['task_id']
                )
                result = conn.execute(ins)

        # 查询DB,验证任务状态,发送消息通知
        select_task_status = select([shopee_custom_report_task.c.status]).where(
            shopee_custom_report_task.c.task_id == task['task_id']
        )
        cursor_status = conn.execute(select_task_status)
        records_status = cursor_status.fetchone()
        if records_status['status'] == 1:
            msg_conteng = "生成成功,请及时查看!"
        elif records_status['status'] == 2:
            msg_conteng = "生成失败,请重新编辑条件或联系网站管理员!"
        # 添加消息通知
        ins_msg = insert(ana_user_msg)
        insert_stmt_msg = ins_msg.values(
            {
                "user_id": task['user_id'],
                "msg_id": task['user_id'] + str(int(time.time())),
                "msg_content": "您的Shopee自定义报告" + task['report_name'] + "于" +
                               time_now + msg_conteng,
                "create_at": time_now,
                "status": 0
            }
        )

        result_msg = conn.execute(insert_stmt_msg)
