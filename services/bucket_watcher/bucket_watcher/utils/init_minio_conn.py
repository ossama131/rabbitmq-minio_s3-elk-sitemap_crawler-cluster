import os

import minio
from minio.notificationconfig import (NotificationConfig, SuffixFilterRule,
                                      QueueConfig)

#MINIO variables
minio_endpoint = os.environ.get('MINIO_ENDPOINT')
minio_access_key = os.environ.get('MINIO_ACCESS_KEY')
minio_secret_key = os.environ.get('MINIO_SECRET_KEY')
minio_bucket_name = os.environ.get('MINIO_BUCKET_NAME')
minio_suffix_filter = os.environ.get('SUFFIX_FILTER')
minio_bucket_queue_arn = os.environ.get('BUCKET_QUEUE_ARN')

#Assert all variables are there
try:
    assert minio_endpoint and minio_access_key and minio_secret_key and minio_bucket_name \
        and minio_suffix_filter and minio_bucket_queue_arn, 'Minio variables missing!'
except AssertionError as e:
    raise RuntimeError(e)

#Establish connection to minio
try:
    minio_client = minio.Minio(
        endpoint=minio_endpoint,
        access_key=minio_access_key,
        secret_key=minio_secret_key,
        secure=False
    )
except Exception as e:
    raise RuntimeError(e)

#Minio Notification config object 
config = NotificationConfig(
    queue_config_list=[
        QueueConfig(
            minio_bucket_queue_arn,
            ["s3:ObjectCreated:*"],
            config_id="1",
            suffix_filter_rule=SuffixFilterRule(minio_suffix_filter),
        ),
    ],
)


#Check if bucket exists, else create new one with notification config
bucket_exists = minio_client.bucket_exists(minio_bucket_name)
if not bucket_exists:
    try:
        minio_client.make_bucket(minio_bucket_name)
        minio_client.set_bucket_notification(minio_bucket_name, config)
    except Exception as e:
        raise RuntimeError(e)

mc = minio_client
