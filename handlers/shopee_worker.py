import json
import time

from datetime import datetime, timedelta

import emoji as emoji
from sqlalchemy import create_engine, select, and_, update, delete
from sqlalchemy.dialects.mysql import insert

import pipeflow
from models.models import shopee_custom_report_task, shopee_category, shopee_product_report_result, ana_user_msg, \
    ana_user_permission
from pipeflow import NsqInputEndpoint
from config import *
from util.log import logger
from util.task_protocol import ANATask

from aioelasticsearch import Elasticsearch

WORKER_NUMBER = 1


# TOPIC_NAME = REPORT_TASK_TOPIC + '.product'

# 权限过滤
async def get_permission_es_body(user_id, search_body, site):
    '''获取用户 数据过滤信息 对请求 数据进行过滤'''
    with engine.connect() as connection:
        try:
            select_permission = select([
                ana_user_permission.c.is_bailun,
                ana_user_permission.c.shopee_permission,
                ana_user_permission.c.baned_seller,
                ana_user_permission.c.baned_brand
            ]).where(
                and_(
                    ana_user_permission.c.user_id == user_id
                )
            )

            cursor = connection.execute(select_permission)
            record = cursor.fetchone()

        except Exception as e:
            logger.info(e)
            logger.info("DB error")
        if record:
            # if record['is_bailun'] == '4k':
            #     return search_body
            if record['shopee_permission']:
                shopee_permission = eval(record['shopee_permission'])
                if shopee_permission:
                    if site in shopee_permission:
                        search_body['query']['bool']['must'].append(
                            {"terms": {"category_id": [j for i in shopee_permission.values() for j in i]}})
                seller_list = eval(record['baned_seller'])['shopee'] if 'shopee' in eval(
                    record['baned_seller']) else None
                if seller_list:
                    search_body['query']['bool']['must_not'].append({"terms": {"seller": seller_list}})
                brand_list = eval(record['baned_brand'])['shopee'] if 'shopee' in eval(
                    record['baned_brand']) else None
                if brand_list:
                    search_body['query']['bool']['must_not'].append({"terms": {"brand": brand_list}})

        return search_body


class ESBody:
    def __init__(self):
        self.search_body = {
            "track_total_hits": True,
            "query": {
                "bool": {
                    "must": [
                        {
                            "bool": {
                                "should": [

                                ]
                            }
                        }
                    ],
                    "must_not":[]
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
            "≥": "gte",
            "≤": "lte"
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
                if element['field'] == 'category_id':
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
                    element_list.append({
                        "match": {
                            "title": {
                                "query": element['value'],
                                "minimum_should_match": "2<70%"
                            }
                        }
                    })

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
        del_body = delete(shopee_product_report_result).where(
            shopee_product_report_result.c.task_id == task['task_id'],
        )

        conn.execute(del_body)

        try:
            es = ESBody()
            # # 逐个任务完成查询es写入db
            search_body = es.create_search(task)
            search_body = await get_permission_es_body(task['user_id'], search_body, task['site'])

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
            sum_data = {
                "sold_total": 0,
                "sum_sold_last_3": 0,
                "sum_sold_last_7": 0,
                "sum_sold_last_30": 0,
                "sum_gmv_last_3": 0,
                "sum_gmv_last_7": 0,
                "sum_gmv_last_30": 0
            }
            for item in the_es_result:
                sum_data['sold_total'] += item['_source']['sold_total']
                sum_data['sum_sold_last_3'] += item['_source']['sold_last_3']
                sum_data['sum_sold_last_7'] += item['_source']['sold_last_7']
                sum_data['sum_sold_last_30'] += item['_source']['sold_last_30']
                sum_data['sum_gmv_last_3'] += item['_source']['gmv_last_3']
                sum_data['sum_gmv_last_7'] += item['_source']['gmv_last_7']
                sum_data['sum_gmv_last_30'] += item['_source']['gmv_last_30']

                # 构造商品dict
                result_info = {
                    "task_id": task['task_id'],
                    "pid": item['_source']['pid'],
                    "img": 'https://cf.shopee.com.my/file/' + item['_source']['img'],
                    "title": emoji.demojize(item['_source']['title']),
                    "site": item['_source']['site'],
                    "merchant_name": emoji.demojize(item['_source']['merchant_name']),
                    "shop_name": emoji.demojize(item['_source']['shop_name']),
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
                "product_total": get_result_count,
                "sold_total": sum_data['sold_total'],
                "sum_sold_last_3": sum_data['sum_sold_last_3'],
                "sum_sold_last_7": sum_data['sum_sold_last_7'],
                "sum_sold_last_30": sum_data['sum_sold_last_30'],
                "sum_gmv_last_3": round(sum_data['sum_gmv_last_3'], 2),
                "sum_gmv_last_7": round(sum_data['sum_gmv_last_7'], 2),
                "sum_gmv_last_30": round(sum_data['sum_gmv_last_30'], 2)
            }).where(
                shopee_custom_report_task.c.task_id == task['task_id']
            )
            result = conn.execute(ins)

            ins_msg = insert(ana_user_msg)
            insert_stmt_msg = ins_msg.values(
                {
                    "user_id": task['user_id'],
                    "msg_id": str(task['user_id']) + str(int(time.time())),
                    "msg_content": "您的Shopee自定义报告" + task['report_name'] + "于" +
                                   time_now + "生成成功",
                    "create_at": time_now,
                    "status": 0
                }
            )

            result_msg = conn.execute(insert_stmt_msg)
        except Exception as e:
            # 更新任务状态
            ins = update(shopee_custom_report_task)
            ins = ins.values({
                "status": 2,
                "update_time": time_now,
            }).where(
                shopee_custom_report_task.c.task_id == task['task_id']
            )
            result = conn.execute(ins)
            ins_msg = insert(ana_user_msg)
            insert_stmt_msg = ins_msg.values(
                {
                    "user_id": task['user_id'],
                    "msg_id": str(task['user_id']) + str(int(time.time())),
                    "msg_content": "您的Shopee自定义报告" + task['report_name'] + "于" +
                                   time_now + "生成失败",
                    "create_at": time_now,
                    "status": 0
                }
            )

            result_msg = conn.execute(insert_stmt_msg)
            logger.info(e)
