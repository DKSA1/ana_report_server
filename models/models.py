from sqlalchemy import Table, Column, PrimaryKeyConstraint, Integer, String, TIMESTAMP, \
    Boolean, TEXT, DECIMAL, SMALLINT, Float, Date, DateTime
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.declarative import declarative_base
from models import metadata

Base = declarative_base()

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

ana_user_msg = Table(
    'ana_user_msg', metadata,
    Column('user_id', String(32), nullable=False, default=''),
    Column('msg_id', String(256), nullable=False, default=''),
    Column('msg_content', String(256), nullable=False, default=''),
    Column('create_at', DateTime, nullable=False),
    Column('status', TINYINT, nullable=False, default=0),
    PrimaryKeyConstraint('user_id', 'msg_id', name='pk')
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
    Column('sum_sold_last_3', Integer, nullable=False),
    Column('sum_sold_last_7', Integer, nullable=False),
    Column('sum_sold_last_1', Integer, nullable=False),
    Column('sum_gmv_last_3', DECIMAL(10, 2), nullable=False),
    Column('sum_gmv_last_7', DECIMAL(10, 2), nullable=False),
    Column('sum_gmv_last_1', DECIMAL(10, 2), nullable=False),
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
    Column('seller', String(64), nullable=False, default=''),
    Column('price', DECIMAL(10, 2), nullable=False, default=''),
    Column('category_path', String(512), nullable=False, default=''),
    # Column('leaf_category_id', String(128), nullable=False, default=''),
    # Column('leaf_category_name', String(256), nullable=False, default=''),
    Column('store_location', String(64), nullable=False, default=''),
    Column('item_location', String(64), nullable=False, default=''),
    Column('item_location_country', String(8), nullable=False, default=''),
    Column('gmv_last_3_pop', Float, nullable=False, default=0),
    Column('gmv_last_3', DECIMAL(10, 2), nullable=False, default=0),
    Column('gmv_last_1', DECIMAL(10, 2), nullable=False, default=0),
    Column('gmv_last_7', DECIMAL(10, 2), nullable=False, default=0),
    Column('sold_last_1', Integer, nullable=False, default=0),
    Column('sold_last_3', Integer, nullable=False, default=0),
    Column('sold_last_7', Integer, nullable=False, default=0),
    Column('visit', Integer, nullable=False, default=0),
    Column('cvr', Float, nullable=False, default=0),
    Column('date', DateTime, nullable=False),
    Column('update_time', DateTime, nullable=False),
)

shopee_custom_report_task = Table(
    'shopee_custom_report_task', metadata,
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
    Column('sum_sold_last_3', Integer, nullable=False),
    Column('sum_sold_last_7', Integer, nullable=False),
    Column('sum_sold_last_30', Integer, nullable=False),
    Column('sum_gmv_last_3', DECIMAL(10, 2), nullable=False),
    Column('sum_gmv_last_7', DECIMAL(10, 2), nullable=False),
    Column('sum_gmv_last_30', DECIMAL(10, 2), nullable=False),
    Column('sold_total', Integer, nullable=False),
    Column('status', TINYINT, nullable=False)
)

shopee_product_report_result = Table(
    'shopee_product_report_result', metadata,
    Column('pid', String(32), nullable=False, default=''),
    Column('task_id', String(32), nullable=False, default=''),
    Column('img', String(256), nullable=False, default=''),
    Column('title', String(512), nullable=False, default=''),
    Column('site', String(32), nullable=False, default=''),
    Column('merchant_name', String(64), nullable=False, default=''),
    Column('shop_name', String(64), nullable=False, default=''),
    Column('category_path', TEXT, nullable=False, default=''),
    # Column('leaf_category_id', String(128), nullable=False, default=''),
    # Column('leaf_category_name', String(256), nullable=False, default=''),
    Column('shop_location', String(64), nullable=False, default=''),
    Column('price', DECIMAL(10, 2), nullable=False, default=0),
    Column('gmv_last_3', DECIMAL(10, 2), nullable=False, default=0),
    Column('gmv_last_7', DECIMAL(10, 2), nullable=False, default=0),
    Column('sold_last_7', Integer, nullable=False, default=0),
    Column('sold_last_3', Integer, nullable=False, default=0),
    Column('sold_total', Integer, nullable=False, default=0),
    Column('review_score', Float, nullable=False, default=0),
    Column('date', DateTime, nullable=False),
    Column('update_time', DateTime, nullable=False),
)

shopee_category = Table(
    'shopee_category', metadata,
    Column('category_id', String(64), nullable=False, default=''),
    Column('category_name', String(128), nullable=False, default=''),
    Column('level', TINYINT),
    Column('is_leaf', TINYINT),
    Column('parent_id', String(32), nullable=False, default=''),
    Column('site', String(8), nullable=False, default=''),
    Column('category_id_path', String(128), nullable=False, default=''),
    Column('category_name_path', String(523), nullable=False, default=''),
    Column('update_time', DateTime, nullable=False),
    PrimaryKeyConstraint('category_id_path', 'site', name='pk')
)


class AmazonTask(Base):
    __tablename__ = 'amazon_custom_report_task'
    __table_args__ = (
        PrimaryKeyConstraint('task_id', 'user_id', name='PK_id'),
    )
    task_id = Column(Integer)
    user_id = Column(String(32), nullable=False)
    report_name = Column(String(128), nullable=False, default=0)
    site = Column(String(8))
    create_time = Column(TIMESTAMP, nullable=True)
    update_time = Column(TIMESTAMP, nullable=True)
    report_chart = Column(String(128), nullable=True)
    # 0=待执行， 1=执行中，2=成功，3=失败
    status = Column(Integer, nullable=False, default=0)
    save_result_numb = Column(Integer, nullable=True)
    context = Column(TEXT, nullable=False, default='')
    order_by = Column(String(32))
    order = Column(String(4))
    methods = Column(String(512))
    product_total = Column(Integer, default=0)
    sold_total_7 = Column(Integer, default=0)
    gmv_total_7 = Column(DECIMAL(12, 2), default=0)
    sold_total_30 = Column(Integer, default=0)
    gmv_total_30 = Column(DECIMAL(12, 2), default=0)
    type = Column(String(32))
    index_name = Column(String(32))
    get_result_count = Column(Integer)


class AmazonTaskResult(Base):
    __tablename__ = 'amazon_product_report_result'
    __table_args__ = (
        PrimaryKeyConstraint('id', 'asin', name='PK_id'),
    )
    id = Column(Integer, autoincrement=True)
    task_id = Column(Integer, nullable=False)
    asin = Column(String(16), nullable=False)
    img = Column(String(256), default='')
    title = Column(String(512), nullable=False, default='')
    category_path = Column(String(512), nullable=False, default='')
    site = Column(String(32), nullable=False)
    brand = Column(String(64), nullable=True)
    merchant_name = Column(String(128), nullable=True)
    price = Column(DECIMAL(8, 2), nullable=True, default=0)
    top_category_rank = Column(Integer, nullable=True)
    sold_last_7 = Column(Integer, nullable=False, default=0)
    gmv_last_7 = Column(DECIMAL(12, 2))
    sold_last_30 = Column(Integer)
    gmv_last_30 = Column(DECIMAL(12, 2), default=0)
    review_score = Column(DECIMAL(8, 2), default=0)
    sold_last_1 = Column(Integer, nullable=False, default=0)
    review_number = Column(Integer, nullable=False, default=0)
    top_category_name = Column(String(64), nullable=False)
    delivery = Column(String(16), nullable=False)
    gmv_last_1 = Column(DECIMAL(12, 2))


class AnaUserMsg(Base):
    __tablename__ = 'ana_user_msg'
    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'msg_id', name='PK_id'),
    )
    user_id = Column(String(32), nullable=False)
    msg_id = Column(String(32), default='')
    msg_content = Column(String(255), nullable=False, default='')
    create_at = Column(TIMESTAMP, nullable=False)
    status = Column(Integer, nullable=True)


class WishTask(Base):
    __tablename__ = 'wish_custom_report_task'
    __table_args__ = (
        PrimaryKeyConstraint('task_id', 'user_id', name='PK_id'),
    )
    task_id = Column(Integer)
    user_id = Column(String(32), nullable=False)
    report_name = Column(String(128), nullable=False, default=0)
    create_time = Column(TIMESTAMP, nullable=True)
    update_time = Column(TIMESTAMP, nullable=True)
    report_chart = Column(String(128), nullable=True)
    # 0=待执行， 1=执行中，2=成功，3=失败
    status = Column(Integer, nullable=False, default=0)
    save_result_numb = Column(Integer, nullable=True)
    context = Column(TEXT, nullable=False, default='')
    order_by = Column(String(32))
    order = Column(String(4))
    methods = Column(String(512))
    product_total = Column(Integer, default=0)
    sold_total_1 = Column(Integer, default=0)
    gmv_total_1 = Column(DECIMAL(12, 2), default=0)
    sold_total_7 = Column(Integer, default=0)
    gmv_total_7 = Column(DECIMAL(12, 2), default=0)
    type = Column(String(32))
    index_name = Column(String(32))
    get_result_count = Column(Integer)


class WishTaskResult(Base):
    __tablename__ = 'wish_product_report_result'
    __table_args__ = (
        PrimaryKeyConstraint('id', 'task_id', name='PK_id'),
    )
    id = Column(Integer, autoincrement=True)
    task_id = Column(Integer, nullable=False)
    pid = Column(String(32), nullable=False)
    img = Column(String(256), default='')
    title = Column(String(512), nullable=False, default='')
    shop_name = Column(String(64), nullable=True)
    price = Column(DECIMAL(8, 2), nullable=True, default=0)
    sold_last_1 = Column(Integer, nullable=False, default=0)
    gmv_last_1 = Column(DECIMAL(12, 2))
    sold_last_7 = Column(Integer, nullable=False, default=0)
    gmv_last_7 = Column(DECIMAL(12, 2))
    sold_last_3 = Column(Integer, nullable=False, default=0)
    gmv_last_3 = Column(DECIMAL(12, 2))
    total_bought = Column(Integer, nullable=False)
    total_wishlist = Column(Integer, nullable=False)
    review_score = Column(DECIMAL(8, 2), default=0)
    category_path = Column(String(256), default='')
    is_hwc = Column(Integer, nullable=False, default=0)
    is_pb = Column(Integer, nullable=False, default=0)
    is_verified = Column(Integer, nullable=False, default=0)


ana_user_permission = Table(
    'ana_user_permission', metadata,
    Column('user_id', String(32), nullable=False, default=""),
    Column('is_bailun', String(10), nullable=False, default=""),
    Column('ebay_permission', TEXT, nullable=False, default=""),
    Column('amazon_permission', TEXT, nullable=False, default=""),
    Column('shopee_permission', TEXT, nullable=False, default=""),
    Column('wish_permission', TEXT, nullable=False, default=""),
    Column('baned_seller', TEXT, nullable=False, default=""),
    Column('baned_brand', TEXT, nullable=False, default=""),
    Column('walmart_permission', TEXT, nullable=False, default=""),
    Column('update_time', DateTime, nullable=False),
    # Column('report_count', Integer, nullable=False),
    # Column('report_count_update', DateTime, nullable=False),
    PrimaryKeyConstraint('user_id', name='pk')
)


class AnaUserPermission(Base):
    __tablename__ = 'ana_user_permission'
    __table_args__ = (
        PrimaryKeyConstraint('user_id', name='PK_id'),
    )
    user_id = Column(String(32), nullable=False)
    is_bailun = Column(String(10), default='')
    ebay_permission = Column(TEXT, nullable=False, default='')
    amazon_permission = Column(TEXT, nullable=False, default='')
    shopee_permission = Column(TEXT, nullable=False, default='')
    wish_permission = Column(TEXT, nullable=False, default='')
    walmart_permission = Column(TEXT, nullable=False, default='')
    baned_seller = Column(TEXT, nullable=False, default="")
    baned_brand = Column(TEXT, nullable=False, default="")
    update_time = Column(TIMESTAMP, nullable=False, default=0)


class AmazonCategory(Base):
    __tablename__ = 'amazon_category'
    __table_args__ = (
        PrimaryKeyConstraint('site', 'category_id_path', name='PK_id'),
    )
    category_id = Column(String(32), nullable=False, default='')
    category_name = Column(String(128), nullable=False, default='')
    level = Column(Integer, nullable=False, default=0)
    is_leaf = Column(Integer, nullable=False, default=0)
    parent_id = Column(String(32), nullable=False, default='')
    site = Column(String(8), nullable=False, default='')
    category_id_path = Column(String(128), nullable=False, default='')
    category_name_path = Column(String(512), nullable=False, default='')
    hy_create_time = Column(TIMESTAMP, nullable=False, default=0)
    update_time = Column(TIMESTAMP, nullable=False, default=0)