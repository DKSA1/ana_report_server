import json
import time

from datetime import datetime, timedelta

import emoji as emoji
from sqlalchemy import create_engine, select, and_, update, delete
from sqlalchemy.dialects.mysql import insert

import pipeflow
from models.models import ebay_custom_report_task, ebay_category, ebay_product_report_result, ana_user_msg
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
                    ]
                }
            },
            # "aggs": {
            #     "sold_total": {
            #         "sum": {
            #             "field": "sold_total"
            #         }
            #     },
            #     "sum_sold_last_7": {
            #         "sum": {
            #             "field": "sold_last_7"
            #         }
            #     },
            #     "sum_sold_last_3": {
            #         "sum": {
            #             "field": "sold_last_3"
            #         }
            #     },
            #     "sum_gmv_last_7": {
            #         "sum": {
            #             "field": "gmv_last_7"
            #         }
            #     },
            #     "sum_gmv_last_3": {
            #         "sum": {
            #             "field": "gmv_last_3"
            #         }
            #     },
            #     "sum_sold_last_1": {
            #         "sum": {
            #             "field": "sold_last_1"
            #         }
            #     },
            #     "sum_gmv_last_1": {
            #         "sum": {
            #             "field": "gmv_last_1"
            #         }
            #     }
            # },
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
            # "gen_time",
            "sold_last_1",
            "sold_last_3",
            "sold_last_7",
            "sold_last_1_pop",
            "sold_last_3_pop",
            "sold_last_7_pop",
            "gmv_last_1",
            "gmv_last_3",
            "gmv_last_7",
            "gmv_last_1_pop",
            "gmv_last_3_pop",
            "gmv_last_7_pop",
            "visit_last_1",
            "visit_last_3",
            "visit_last_7",
            "cvr_last_1",
            "cvr_last_3",
            "cvr_last_7"
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
                if element['field'] == 'store_location':
                    if element['value'] == "CN":
                        element_list.append(
                            {
                                "terms": {
                                    "store_location": ["CN", "HK"]
                                }
                            }
                        )
                    elif element['value'] != "other":
                        element_list.append(
                            {
                                "term": {
                                    "store_location": element['value']
                                }
                            }
                        )

                    else:
                        not_list.append(
                            {
                                "terms": {
                                    "store_location": ["GB", "US", "DE", "AU", "CN", "HK"]
                                }
                            }
                        )

                # 发货地判断
                if element['field'] == 'item_location':
                    if element['value'] == '0':
                        # print(params['item_location'])
                        element_list.extend([{
                            "script": {
                                "script": "doc['item_location_country'].value != doc['store_location'].value"
                                # "script": "doc['item_location_country'].value == " + site.upper()
                            }
                        }])
                    elif element['value'] == '2':
                        element_list.extend([{
                            "script": {
                                # "script": "doc['item_location_country'].value == doc['store_location'].value"
                                "script": "doc['item_location_country'].value == " + "'" + task_params[
                                    'site'].upper() + "'"
                            }
                        }])
                    # TODO:改国内:CN
                    elif element['value'] == '1':
                        element_list.append({
                            "term": {
                                "item_location_country": "CN"
                            }
                        })  # HERE

                # 品类过滤
                # TODO:
                if element['field'] == 'category_id':
                    cid_list = element['value'].split('|')
                    element_list.append({"term": {'category_id': {"value": cid_list[1]}}})
                    # element_list.append({"term": {'category_id': {"value": element['value']}}})

                # 基础条件: 商家,品牌,品类
                if element['field'] == 'seller' or element['field'] == 'brand':
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


# async def redis_get_index():
#     redis = await aioredis.create_redis_pool(
#         address=REDIS_URL, password=REDIS_PASSWORD)
#
#     if PRODUCTION_ENV:
#         value = await redis.hgetall('ebay:product:batch_date', encoding='utf-8')
#     else:
#         value = await redis.hgetall('test:product:batch_date', encoding='utf-8')
#     if len(value) > 1:
#         key_list = []
#         for key, value in value.items():
#             if value == '1':
#                 key_list.append(datetime.strptime(key, '%Y-%m-%d'))
#         key_time = sorted(key_list)[-1]
#         key_time = datetime.strftime(key_time, '%Y-%m-%d')
#     elif len(value) == 1:
#         key_time = [x for x in value.keys()][0]
#         key_time = datetime.strftime(key_time, '%Y-%m-%d')
#     else:
#         logger.info("Can't get the es_index name")
#         key_time = '2020-04-07'
#     index_name = "ebay_product_" + key_time
#     return index_name


# engine = create_engine(
#     # pool_pre_ping=SQLALCHEMY_POOL_PRE_PING,
#     echo=SQLALCHEMY_ECHO,
#     # pool_size=SQLALCHEMY_POOL_SIZE,
#     # max_overflow=SQLALCHEMY_POOL_MAX_OVERFLOW,
#     pool_recycle=SQLALCHEMY_POOL_RECYCLE,
#     autocommit=True,
#     user=DB_USER_NAME, db=DB_DATABASE_NAME,
#     host=DB_SEVER_ADDR, port=DB_SEVER_PORT, password=DB_USER_PW,
#     maxsize=10)


engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=SQLALCHEMY_POOL_PRE_PING,
    echo=SQLALCHEMY_ECHO,
    pool_size=SQLALCHEMY_POOL_SIZE,
    max_overflow=SQLALCHEMY_POOL_MAX_OVERFLOW,
    pool_recycle=SQLALCHEMY_POOL_RECYCLE,
)
# logger.info(SQLALCHEMY_DATABASE_URI)


async def ebay_handle(group, task):
    hy_task = ANATask(task)
    task_log = [hy_task.task_type, hy_task.task_data]
    # logger.info("connecting")
    task = hy_task.task_data
    time_now = (datetime.now() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    with engine.connect() as conn:


        del_body = delete(ebay_product_report_result).where(
                ebay_product_report_result.c.task_id == task['task_id'],
        )

        conn.execute(del_body)

        try:
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
            # logger.info(index_result)
            # 报告商品结果列表
            the_es_result = index_result['hits']['hits']
            name_ids = []
            # 构造品类IDS
            for item in the_es_result:
                # logger.info(item)
                for category_id in item['_source']['leaf_category_id']:
                    name_ids.append(category_id)
            # 查出category_path
            select_category_name = select([
                ebay_category.c.category_name,
                ebay_category.c.category_id,
                ebay_category.c.category_id_path,
                ebay_category.c.category_name_path
            ]).where(
                and_(
                    ebay_category.c.category_id.in_(name_ids),
                    ebay_category.c.site == task['site']
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
                        # logger.info(low_id)
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
                "sum_sold_last_1": 0,
                "sum_gmv_last_3": 0,
                "sum_gmv_last_7": 0,
                "sum_gmv_last_1": 0
            }
            for item in the_es_result:
                # 构造商品dict
                sum_data['sold_total'] += item['_source']['sold_total']
                sum_data['sum_sold_last_3'] += item['_source']['sold_last_3']
                sum_data['sum_sold_last_7'] += item['_source']['sold_last_7']
                sum_data['sum_sold_last_1'] += item['_source']['sold_last_1']
                sum_data['sum_gmv_last_3'] += item['_source']['gmv_last_3']
                sum_data['sum_gmv_last_7'] += item['_source']['gmv_last_7']
                sum_data['sum_gmv_last_1'] += item['_source']['gmv_last_1']
                result_info = {
                    "task_id": task['task_id'],
                    "item_id": item['_source']['item_id'],
                    "img": item['_source']['img'],
                    "title": emoji.demojize(item['_source']['title']),
                    "site": item['_source']['site'],
                    "brand": item['_source']['brand'],
                    # 需要构造
                    "category_path": str(item['_source']['category_path']),
                    "store_location": item['_source']['store_location'],
                    "item_location": item['_source']['item_location'],
                    "item_location_country": item['_source']['item_location_country'],
                    "seller": item['_source']['seller'],
                    "price": item['_source']['price'],
                    "gmv_last_3_pop": item['_source']['gmv_last_3_pop'],
                    "gmv_last_3": item['_source']['gmv_last_3'],
                    "gmv_last_1": item['_source']['gmv_last_1'],
                    "gmv_last_7": item['_source']['gmv_last_7'],
                    "sold_last_7": item['_source']['sold_last_7'],
                    "sold_last_1": item['_source']['sold_last_1'],
                    "sold_last_3": item['_source']['sold_last_3'],
                    "visit": item['_source']['visit_last_1'],
                    "cvr": item['_source']['sold_last_1'] / item['_source']['visit_last_1'] if item['_source'][
                                                                                                   'visit_last_1'] != 0 else 0,
                    "date": (datetime.now()).strftime('%Y-%m-%d %H:%M:%S'),
                    "update_time": time_now
                }
                # logger.info(result_info)

                # 插入商品信息

                ins = insert(ebay_product_report_result)
                insert_stmt = ins.values(result_info)
                on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update(
                    task_id=insert_stmt.inserted.task_id,
                    item_id=insert_stmt.inserted.item_id,
                    img=insert_stmt.inserted.img,
                    title=insert_stmt.inserted.title,
                    site=insert_stmt.inserted.site,
                    brand=insert_stmt.inserted.brand,
                    seller=insert_stmt.inserted.seller,
                    price=insert_stmt.inserted.price,
                    category_path=insert_stmt.inserted.category_path,
                    store_location=insert_stmt.inserted.store_location,
                    item_location=insert_stmt.inserted.item_location,
                    item_location_country=insert_stmt.inserted.item_location_country,
                    gmv_last_3_pop=insert_stmt.inserted.gmv_last_3_pop,
                    gmv_last_3=insert_stmt.inserted.gmv_last_3,
                    gmv_last_1=insert_stmt.inserted.gmv_last_1,
                    gmv_last_7=insert_stmt.inserted.gmv_last_7,
                    sold_last_7=insert_stmt.inserted.sold_last_7,
                    sold_last_1=insert_stmt.inserted.sold_last_1,
                    sold_last_3=insert_stmt.inserted.sold_last_3,
                    visit=insert_stmt.inserted.visit,
                    cvr=insert_stmt.inserted.cvr,
                    date=insert_stmt.inserted.date,
                )
                result = conn.execute(on_duplicate_key_stmt)
                # logger.info(result)
                get_result_count += 1

            # 更新任务状态
            logger.info(sum_data)
            ins = update(ebay_custom_report_task)
            ins = ins.values({
                "status": 1,
                "update_time": time_now,
                "get_result_count": get_result_count,
                "product_total": get_result_count,
                "sold_total": sum_data['sold_total'],
                "sum_sold_last_3": sum_data['sum_sold_last_3'],
                "sum_sold_last_7": sum_data['sum_sold_last_7'],
                "sum_sold_last_1": sum_data['sum_sold_last_1'],
                "sum_gmv_last_3": round(sum_data['sum_gmv_last_3'], 2),
                "sum_gmv_last_7": round(sum_data['sum_gmv_last_7'], 2),
                "sum_gmv_last_1": round(sum_data['sum_gmv_last_1'], 2)
            }).where(
                ebay_custom_report_task.c.task_id == task['task_id']
            )
            result = conn.execute(ins)
            # logger.info(result)
            # 添加消息通知
            ins_msg = insert(ana_user_msg)
            insert_stmt_msg = ins_msg.values(
                {
                    "user_id": task['user_id'],
                    "msg_id": str(task['user_id']) + str(int(time.time())),
                    "msg_content": "您的Ebay自定义报告" + task['report_name'] + "于" +
                                   time_now + "生成成功,请及时查看!",
                    "create_at": time_now,
                    "status": 0
                }
            )
            result_msg = conn.execute(insert_stmt_msg)
        except Exception as e:
            logger.info(e)
            # 更新任务状态
            ins = update(ebay_custom_report_task)
            ins = ins.values({
                "status": 2,
                "update_time": time_now,
                # "get_result_count": get_result_count,
                # "product_total": get_result_count,
                # "sold_total": sum_data['sold_total'],
                # "sum_sold_last_3": sum_data['sold_last_3'],
                # "sum_sold_last_7": sum_data['sold_last_7'],
                # "sum_sold_last_1": sum_data['sold_last_1'],
                # "sum_gmv_last_3": round(sum_data['gmv_last_3'], 2),
                # "sum_gmv_last_7": round(sum_data['gmv_last_7'], 2),
                # "sum_gmv_last_1": round(sum_data['gmv_last_1'], 2)
            }).where(
                ebay_custom_report_task.c.task_id == task['task_id']
            )
            result = conn.execute(ins)
            # logger.info(result)
            # 添加消息通知
            ins_msg = insert(ana_user_msg)
            insert_stmt_msg = ins_msg.values(
                {
                    "user_id": task['user_id'],
                    "msg_id": str(task['user_id']) + str(int(time.time())),
                    "msg_content": "您的Ebay自定义报告" + task['report_name'] + "于" +
                                   time_now + "生成失败,请重新编辑条件或联系网站管理员!",
                    "create_at": time_now,
                    "status": 0
                }
            )


# def run():
#     input_end = NsqInputEndpoint(TOPIC_NAME, 'ebay_analysis', WORKER_NUMBER, **INPUT_NSQ_CONF)
#     logger.info('连接nsq成功,topic_name = {}, nsq_address={}'.format(TOPIC_NAME, INPUT_NSQ_CONF))
#     server = pipeflow.Server()
#     logger.info("pipeflow开始工作")
#     group = server.add_group('main', WORKER_NUMBER)
#     logger.info("抓取任务")
#     group.set_handle(ebay_handle)
#     logger.info("处理任务")
#     group.add_input_endpoint('input', input_end)
#
#     server.add_routine_worker(ebay_maintain_task, interval=5, immediately=True)
#     server.run()


# if __name__ == '__main__':
#     run()
