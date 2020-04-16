from sqlalchemy import Table, Column, PrimaryKeyConstraint, Integer, String, TIMESTAMP, \
    Boolean, TEXT, DECIMAL, SMALLINT, Float, Date, DateTime
from sqlalchemy.dialects.mysql import TINYINT
from models import metadata

ebay_category = Table(
    'ebay_category', metadata,
    Column('category_id', String(64), nullable=False, default=''),
    Column('category_name', String(64), nullable=False, default=''),
    Column('level', TINYINT),
    Column('is_leaf', Boolean),
    Column('parent_id', String(64), nullable=False, default=''),
    Column('site', String(64), nullable=False, default=''),
    Column('category_id_path', String(64), nullable=False, default=''),
    Column('category_name_path', String(64), nullable=False, default=''),
    Column('update_time', DateTime, nullable=False),
    PrimaryKeyConstraint('category_id_path', 'site', name='pk')
)

ebay_product = Table(
    'ebay_product', metadata,
    Column('item_id', String(32), nullable=False, default=''),
    Column('site', String(8), nullable=False, default=''),
    Column('category_id', String(32), nullable=False, default=''),
    Column('img', String(128), nullable=False, default=''),
    Column('title', String(512), nullable=False, default=''),
    Column('brand', String(64), nullable=False, default=''),
    Column('item_location', String(64), nullable=False, default=''),
    Column('item_location_country', String(8), nullable=False, default=''),
    Column('seller', String(64), nullable=False, default=''),
    Column('store', String(64), nullable=False, default=''),
    Column('store_location', String(64), nullable=False, default=''),
    Column('marketplace', String(16), nullable=False, default=''),
    Column('popular', TINYINT, nullable=False, default=0),
    Column('price', DECIMAL(10, 2), nullable=False, default=0),
    Column('sold', Integer, nullable=False, default=0),
    Column('visit', Integer, nullable=False, default=0),
    Column('gen_time', DateTime, nullable=True),
    Column('data_update_time', DateTime, nullable=True),
    Column('update_time', DateTime, nullable=True),
    Column('description', TEXT, nullable=True),
    PrimaryKeyConstraint('item_id', 'site', name='pk')
)

ebay_product_history = Table(
    'ebay_product_history', metadata,
    Column('item_id', String(32), nullable=False, default=''),
    Column('site', String(8), nullable=False, default=''),
    Column('date', DateTime, nullable=False),
    # Column('brand', String(64), nullable=False, default=''),
    # Column('seller', String(64), nullable=False, default=''),
    # Column('category_id', String(32), nullable=False, default=''),
    Column('price', DECIMAL(10, 2), nullable=False, default=0),
    Column('sold_total', Integer, nullable=False, default=0),
    Column('sold_last_1', Integer, nullable=False, default=0),
    Column('sold_last_3', Integer, nullable=False, default=0),
    Column('sold_last_7', Integer, nullable=False, default=0),
    Column('sold_last_1_delta', Integer, nullable=False, default=0),
    Column('sold_last_3_delta', Integer, nullable=False, default=0),
    Column('sold_last_7_delta', Integer, nullable=False, default=0),
    Column('sold_last_1_pop', Float, nullable=False, default=0),
    Column('sold_last_3_pop', Float, nullable=False, default=0),
    Column('sold_last_7_pop', Float, nullable=False, default=0),
    Column('gmv_last_1', DECIMAL(10, 2), nullable=False, default=0),
    Column('gmv_last_3', DECIMAL(10, 2), nullable=False, default=0),
    Column('gmv_last_7', DECIMAL(10, 2), nullable=False, default=0),
    Column('gmv_last_1_delta', DECIMAL(10, 2), nullable=False, default=0),
    Column('gmv_last_3_delta', DECIMAL(10, 2), nullable=False, default=0),
    Column('gmv_last_7_delta', DECIMAL(10, 2), nullable=False, default=0),
    Column('gmv_last_1_pop', Float, nullable=False, default=0),
    Column('gmv_last_3_pop', Float, nullable=False, default=0),
    Column('gmv_last_7_pop', Float, nullable=False, default=0),
    Column('visit_total', Integer, nullable=False, default=0),
    Column('visit_last_1', Integer, nullable=False, default=0),
    Column('visit_last_3', Integer, nullable=False, default=0),
    Column('visit_last_7', Integer, nullable=False, default=0),
    Column('cvr_total', Float, nullable=False, default=0),
    Column('cvr_last_1', Float, nullable=False, default=0),
    Column('cvr_last_3', Float, nullable=False, default=0),
    Column('cvr_last_7', Float, nullable=False, default=0),
    PrimaryKeyConstraint('item_id', 'site', 'date', name='pk')
)

'''
ebay_category_history = Table(
    'ebay_category_history', metadata,
    Column('category_id', String(32), nullable=False, default=''),
    Column('site', String(8), nullable=False, default=''),
    Column('date', DateTime, nullable=False),
    Column('sold_last_1', Integer, nullable=False, default=0),
    Column('sold_last_3', Integer, nullable=False, default=0),
    Column('sold_last_7', Integer, nullable=False, default=0),
    Column('sold_last_1_pop', Float, nullable=False, default=0),
    Column('sold_last_3_pop', Float, nullable=False, default=0),
    Column('sold_last_7_pop', Float, nullable=False, default=0),
    Column('gmv_last_1', DECIMAL(10,2), nullable=False, default=0),
    Column('gmv_last_3', DECIMAL(10,2), nullable=False, default=0),
    Column('gmv_last_7', DECIMAL(10,2), nullable=False, default=0),
    Column('gmv_last_1_pop', Float, nullable=False, default=0),
    Column('gmv_last_3_pop', Float, nullable=False, default=0),
    Column('gmv_last_7_pop', Float, nullable=False, default=0),
    PrimaryKeyConstraint('category_id', 'site', 'date', name='pk')
)


ebay_brand_history = Table(
    'ebay_brand_history', metadata,
    Column('brand', String(64), nullable=False, default=''),
    Column('site', String(8), nullable=False, default=''),
    Column('date', DateTime, nullable=False),
    Column('sold_last_1', Integer, nullable=False, default=0),
    Column('sold_last_3', Integer, nullable=False, default=0),
    Column('sold_last_7', Integer, nullable=False, default=0),
    Column('sold_last_1_pop', Float, nullable=False, default=0),
    Column('sold_last_3_pop', Float, nullable=False, default=0),
    Column('sold_last_7_pop', Float, nullable=False, default=0),
    Column('gmv_last_1', DECIMAL(10,2), nullable=False, default=0),
    Column('gmv_last_3', DECIMAL(10,2), nullable=False, default=0),
    Column('gmv_last_7', DECIMAL(10,2), nullable=False, default=0),
    Column('gmv_last_1_pop', Float, nullable=False, default=0),
    Column('gmv_last_3_pop', Float, nullable=False, default=0),
    Column('gmv_last_7_pop', Float, nullable=False, default=0),
    PrimaryKeyConstraint('brand', 'site', 'date', name='pk')
)


ebay_seller_history = Table(
    'ebay_seller_history', metadata,
    Column('seller', String(64), nullable=False, default=''),
    Column('site', String(8), nullable=False, default=''),
    Column('date', DateTime, nullable=False),
    Column('sold_last_1', Integer, nullable=False, default=0),
    Column('sold_last_3', Integer, nullable=False, default=0),
    Column('sold_last_7', Integer, nullable=False, default=0),
    Column('sold_last_1_pop', Float, nullable=False, default=0),
    Column('sold_last_3_pop', Float, nullable=False, default=0),
    Column('sold_last_7_pop', Float, nullable=False, default=0),
    Column('gmv_last_1', DECIMAL(10,2), nullable=False, default=0),
    Column('gmv_last_3', DECIMAL(10,2), nullable=False, default=0),
    Column('gmv_last_7', DECIMAL(10,2), nullable=False, default=0),
    Column('gmv_last_1_pop', Float, nullable=False, default=0),
    Column('gmv_last_3_pop', Float, nullable=False, default=0),
    Column('gmv_last_7_pop', Float, nullable=False, default=0),
    PrimaryKeyConstraint('seller', 'site', 'date', name='pk')
)
'''

ebay_user = Table(
    'ebay_user', metadata,
    Column('id', String(32), nullable=False, default=''),
    Column('name', String(256), nullable=False, default=''),
    Column('account', String(256), nullable=False, default=''),
    Column('phone', String(13), nullable=False, default=''),
    Column('password', String(256), nullable=False, default=''),
    Column('create_at', DateTime, nullable=False),
    Column('update_at', DateTime, nullable=False),
    PrimaryKeyConstraint('id', name='pk')
)

ebay_custom_report_task = Table(
    'ebay_custom_report_task', metadata,
    Column('task_id', String(32), nullable=False, default=''),
    Column('user_id', String(32), nullable=False, default=''),
    Column('site', String(8), nullable=False, default=''),
    Column('report_name', String(256), nullable=False, default=''),
    Column('type', String(16), nullable=False, default=''),
    Column('index_name', String(32), nullable=False, default=''),
    Column('condition', TEXT),
    Column('start_at', DateTime, nullable=False),
    Column('end_at', DateTime, nullable=False),
    Column('result_count', Integer, nullable=False, default=0),
    Column('order_by', String(32), nullable=False, default=''),
    Column('order', String(5), nullable=False, default=''),
    Column('methods', String(512), nullable=False, default=''),
    Column('update_time', DateTime, nullable=False),
    Column('product_total', Integer, nullable=False),
    Column('get_result_count', Integer, nullable=False),
    Column('sold_total', Integer, nullable=False),
    Column('status', TINYINT, nullable=False)
)

# ebay_custom_report_list = Table(
#     'ebay_custom_report_list', metadata,
#     Column('task_id', String(32), nullable=False, default=''),
#     Column('user_id', String(32), nullable=False, default=''),
#     Column('report_id', String(32), nullable=False, default=''),
#     Column('update_time', DateTime, nullable=False),
# )

ebay_custom_product_report = Table(
    'ebay_custom_product_report', metadata,
    Column('task_id', String(32), nullable=False, default=''),
    # Column('report_id', String(32), nullable=False, default=''),
    Column('gmv_last_3_pop', Float, nullable=False, default=0),
    Column('gmv_last_3', DECIMAL(10, 2), nullable=False, default=0),
    Column('gmv', DECIMAL(10, 2), nullable=False, default=0),
    Column('sold', Integer, nullable=False, default=0),
    Column('update_time', DateTime, nullable=False),
)

ebay_product_report_result = Table(
    'ebay_product_report_result', metadata,
    Column('item_id', String(32), nullable=False, default=''),
    Column('task_id', String(32), nullable=False, default=''),
    Column('img', String(256), nullable=False, default=''),
    Column('title', String(512), nullable=False, default=''),
    Column('site', String(32), nullable=False, default=''),
    Column('brand', String(64), nullable=False, default=''),
    Column('category_path', String(512), nullable=False, default=''),
    # Column('leaf_category_id', String(128), nullable=False, default=''),
    # Column('leaf_category_name', String(256), nullable=False, default=''),
    Column('store_location', String(64), nullable=False, default=''),
    Column('gmv_last_3_pop', Float, nullable=False, default=0),
    Column('gmv_last_3', DECIMAL(10, 2), nullable=False, default=0),
    Column('gmv_last_1', DECIMAL(10, 2), nullable=False, default=0),
    Column('sold_last_1', Integer, nullable=False, default=0),
    Column('sold_last_3', Integer, nullable=False, default=0),
    Column('visit', Integer, nullable=False, default=0),
    Column('cvr', Float, nullable=False, default=0),
    Column('date', DateTime, nullable=False),
    Column('update_time', DateTime, nullable=False),
)
