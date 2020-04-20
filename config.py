import os

ENV_TYPE = os.environ.get('ENV_TYPE', '')
# print(ENV_TYPE)
PRODUCTION_ENV = True if ENV_TYPE == 'PRODUCTION' else False

# DB_USER_NAME = "root" if PRODUCTION_ENV else "linkcool"
# DB_USER_PW = "@ie0bzy3!dlpq*d7" if PRODUCTION_ENV else "forconnect"
# DB_SEVER_ADDR = "10.0.1.7" if PRODUCTION_ENV else "119.145.69.74"
# DB_SEVER_PORT = 4000 if PRODUCTION_ENV else 43021
# DB_DATABASE_NAME = "bigdata"


# DB_USER_NAME = "root" if PRODUCTION_ENV else "linkcool"
# DB_USER_PW = "@ie0bzy3!dlpq*d7" if PRODUCTION_ENV else "forconnect"
# DB_SEVER_ADDR = "134.175.210.192" if PRODUCTION_ENV else "119.145.69.74"
# DB_SEVER_PORT = 4000 if PRODUCTION_ENV else 43021
# DB_DATABASE_NAME = "bigdata"

# DB_USER_NAME = "wind" if PRODUCTION_ENV else "linkcool"
# DB_USER_PW = "!Syy950507" if PRODUCTION_ENV else "forconnect"
# DB_SEVER_ADDR = "47.112.96.218" if PRODUCTION_ENV else "119.145.69.74"
# DB_SEVER_PORT = 3306 if PRODUCTION_ENV else 43021
# DB_DATABASE_NAME = "bigdata"


#
# DB_USER_NAME = "linkcool" if PRODUCTION_ENV else "root"
# DB_USER_PW = "forconnect" if PRODUCTION_ENV else "@ie0bzy3!dlpq*d7"
# DB_SEVER_ADDR = "119.145.69.74" if PRODUCTION_ENV else "134.175.210.192"
# DB_SEVER_PORT = 43021 if PRODUCTION_ENV else 4000
# DB_DATABASE_NAME = "bigdata"


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

ELASTIC_HOST = "10.0.1.3" if PRODUCTION_ENV else "es-fx731b5q.public.tencentelasticsearch.com"
ELASTIC_PORT = 9200 if PRODUCTION_ENV else 9200
ELASTIC_INDEX = "" if PRODUCTION_ENV else ""
ELASTIC_DOC_TYPE = "" if PRODUCTION_ENV else ""
ELASTIC_VALUES = "" if PRODUCTION_ENV else ""
ELASTIC_USE_SSL = True
ELASTIC_TIMEOUT = 60
ELASTIC_USERNAME = "elastic" if PRODUCTION_ENV else "elastic"
ELASTIC_PASSWORD = "$EStest.813" if PRODUCTION_ENV else "$EStest.813"
# ELASTICSEARCH_URL = \
#     f'http://{ELASTIC_USERNAME}:{ELASTIC_PASSWORD}@{ELASTIC_HOST}:{ELASTIC_PORT}' \
#         if PRODUCTION_ENV else "http://47.102.220.1:9200"
# ELASTICSEARCH_URL = f'https://{ELASTIC_USERNAME}:{ELASTIC_PASSWORD}@{ELASTIC_HOST}:{ELASTIC_PORT}' \
#         if PRODUCTION_ENV else "https://elastic:$EStest.813@es-fx731b5q.public.tencentelasticsearch.com:9200/"
# ELASTICSEARCH_URL = f"https://elastic:$EStest.813@es-fx731b5q.public.tencentelasticsearch.com:9200/"
# ELASTIC_VALUES = {'index': "ebay", 'doc_type': "ebay_product"}
ELASTICSEARCH_URL = [{'host': ELASTIC_HOST, 'port': ELASTIC_PORT, 'user_ssl': ELASTIC_USE_SSL,
                      'http_auth': (ELASTIC_USERNAME, ELASTIC_PASSWORD)}] \
    if PRODUCTION_ENV else "https://elastic:$EStest.813@es-fx731b5q.public.tencentelasticsearch.com:9200/"

JWT_SECRET = "sercet"

REDIS_HOST = "10.0.1.33" if PRODUCTION_ENV else "45.35.226.130"
REDIS_PORT = 6379 if PRODUCTION_ENV else 13111
REDIS_DB_NUMBER = 0
REDIS_PASSWORD = "$redis.813" if PRODUCTION_ENV else "c18d1ba0f01f15b2168297663a85abf5"
REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_NUMBER}'

# NSQ_LOOKUPD_HTTP_ADDR = 'bd-nsqlookupd:4161' if PRODUCTION_ENV else '134.73.133.2:25761'
# NSQ_NSQD_TCP_ADDR = 'bd-nsqd:4150' if PRODUCTION_ENV else '134.73.133.2:25750'
# NSQ_NSQD_HTTP_ADDR = 'bd-nsqd:4151' if PRODUCTION_ENV else '134.73.133.2:25751'

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

AMAZON_REPORT_TASK_TOPIC = "amazon_analysis_report.product"