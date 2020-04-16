### MQ:
    nsq:
    address:
        http://134.73.133.2:25751
    example:
        curl -d "<message>" http://134.73.133.2:25751/pub?topic=name

                




### Ebay 自定义报告任务
任务:

    mq:
        nsq:
            topic:
                ebay_analysis_report.product
    数据:
        {
            "task": "ebay_report_product",
            "data: {
                "task_id": ...,
                "user_id": ...,
                "report_name": ...,
                "type": ...,
                "site": ...,
                "condition": ...,
                "index_name": ...,
                "start_at": ...,
                "update_time": ...,
                "result_count": ...,
                "order_by": ...,
                "order": ...,
                "methods": ...,
                "status": ...
            }   
        }
        