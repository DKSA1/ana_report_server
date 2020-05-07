import os

ENV_TYPE = os.environ.get('ENV_TYPE', '')

PRODUCTION_ENV = True if ENV_TYPE == 'PRODUCTION' else False


DB_USER_NAME = "root" if PRODUCTION_ENV else "wind"
DB_USER_PW = "@ie0bzy3!dlpq*d7" if PRODUCTION_ENV else "!Syy950507"
DB_SEVER_ADDR = "10.0.1.7" if PRODUCTION_ENV else "47.102.220.1"
DB_SEVER_PORT = 4000 if PRODUCTION_ENV else 3306
DB_DATABASE_NAME = "bigdata"

SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{name:s}:{pw:s}@{addr:s}:{port}/{db:s}".format(
    name=DB_USER_NAME,
    pw=DB_USER_PW,
    addr=DB_SEVER_ADDR,
    db=DB_DATABASE_NAME,
    port=DB_SEVER_PORT
    )

SQLALCHEMY_POOL_PRE_PING = True
SQLALCHEMY_ECHO = False  # if PRODUCTION_ENV else True
SQLALCHEMY_POOL_SIZE = 0
SQLALCHEMY_POOL_MAX_OVERFLOW = -1
SQLALCHEMY_POOL_RECYCLE = 120

ELASTIC_TIMEOUT = 60
# 下面为 eBay大数据对应的 es配置参数
EBAY_ELASTIC_HOST = "10.0.1.3" if PRODUCTION_ENV else "es-fx731b5q.public.tencentelasticsearch.com"
EBAY_ELASTIC_PORT = 9200 if PRODUCTION_ENV else 9200
EBAY_ELASTIC_INDEX = "" if PRODUCTION_ENV else ""
EBAY_ELASTIC_DOC_TYPE = "" if PRODUCTION_ENV else ""
EBAY_ELASTIC_VALUES = "" if PRODUCTION_ENV else ""
EBAY_ELASTIC_USE_SSL = True
EBAY_ELASTIC_USERNAME = "elastic" if PRODUCTION_ENV else "elastic"
EBAY_ELASTIC_PASSWORD = "$EStest.813" if PRODUCTION_ENV else "$EStest.813"
EBAY_ELASTICSEARCH_URL = [{'host': EBAY_ELASTIC_HOST, 'port': EBAY_ELASTIC_PORT, 'user_ssl': EBAY_ELASTIC_USE_SSL,
                      'http_auth': (EBAY_ELASTIC_USERNAME, EBAY_ELASTIC_PASSWORD)}] \
    if PRODUCTION_ENV else "https://elastic:$EStest.813@es-fx731b5q.public.tencentelasticsearch.com:9200/"


# 下面为 Amazon大数据对应的 es配置参数
AMAZON_ELASTIC_HOST = "10.0.1.3" if PRODUCTION_ENV else "es-fx731b5q.public.tencentelasticsearch.com"
AMAZON_ELASTIC_PORT = 9200 if PRODUCTION_ENV else 9200
AMAZON_ELASTIC_INDEX = "" if PRODUCTION_ENV else ""
AMAZON_ELASTIC_DOC_TYPE = "" if PRODUCTION_ENV else ""
AMAZON_ELASTIC_VALUES = "" if PRODUCTION_ENV else ""
AMAZON_ELASTIC_USE_SSL = True
AMAZON_ELASTIC_USERNAME = "elastic" if PRODUCTION_ENV else "elastic"
AMAZON_ELASTIC_PASSWORD = "$EStest.813" if PRODUCTION_ENV else "$EStest.813"
AMAZON_ELASTICSEARCH_URL = [{'host': AMAZON_ELASTIC_HOST, 'port': AMAZON_ELASTIC_PORT,
                             'user_ssl': AMAZON_ELASTIC_USE_SSL,
                      'http_auth': (AMAZON_ELASTIC_USERNAME, AMAZON_ELASTIC_PASSWORD)}] \
    if PRODUCTION_ENV else "https://elastic:$EStest.813@es-fx731b5q.public.tencentelasticsearch.com:9200/"


JWT_SECRET = "sercet"

REDIS_HOST = "10.0.1.33" if PRODUCTION_ENV else "45.35.226.130"
REDIS_PORT = 6379 if PRODUCTION_ENV else 13111
REDIS_DB_NUMBER = 0
REDIS_PASSWORD = "$redis.813" if PRODUCTION_ENV else "c18d1ba0f01f15b2168297663a85abf5"
REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_NUMBER}'

NSQ_LOOKUPD_HTTP_ADDR = 'bd-nsqlookupd:4161' if PRODUCTION_ENV else '47.112.96.218:4161'
NSQ_NSQD_TCP_ADDR = 'bd-nsqd:4150' if PRODUCTION_ENV else '47.112.96.218:4150'
NSQ_NSQD_HTTP_ADDR = 'bd-nsqd:4151' if PRODUCTION_ENV else '47.112.96.218:4151'

INPUT_NSQ_CONF = {
    'lookupd_http_addresses': [NSQ_LOOKUPD_HTTP_ADDR]
}
OUTPUT_NSQ_CONF = {
    'nsqd_tcp_addresses': NSQ_NSQD_TCP_ADDR
}

EBAY_REPORT_TASK_TOPIC = "ebay_analysis_report.product"
SHOPEE_REPORT_TASK_TOPIC = "shopee_analysis_report.product"

AMAZON_REPORT_TASK_TOPIC = "amazon_analysis_report.product"