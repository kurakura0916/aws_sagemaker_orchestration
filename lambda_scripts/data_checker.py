import os
import logging
import boto3
from datetime import datetime, timedelta, timezone

# データ確認用のバケット
BUCKET = "sample-bucket"
# 存在を確認するファイル名
FILE_NAME = "iris.csv"
# エンドポイント名
ENDPOINT_NAME = "multiclass"

# loggerの作成
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


def lambda_handler(event, _context):
    LOGGER.info(event)

    s3_client = boto3.client("s3")

    # 指定された日付の前日の日付を取得
    one_days_before = add_days(event["DATE"], -1)

    # 前日分の訓練データが存在するのか確認
    status = check_data(s3_client, one_days_before)

    if status is not True:
        print('No new data uploaded since last training run.')
        print('Skipping training until next scheduled training run.')
        return {
            "no_new_data": True
        }
    s3_input_path, s3_output_path, s3_valid_path = generate_s3_path(one_days_before)
    return {
        "time": one_days_before,
        "s3_input_path": s3_input_path,
        "s3_output_path": s3_output_path,
        "s3_valid_path": s3_valid_path,
        "no_new_data": False,
        "endpoint": ENDPOINT_NAME
    }


def check_data(s3_client, date):

    prefix = "input-data-training"
    response = s3_client.list_objects(
        Bucket=BUCKET,
        Prefix=prefix
    )
    print(response)
    assumed_keys = [f'input-data-training/{date}/multiclass/{FILE_NAME}']
    try:
        keys = [content['Key'] for content in response['Contents']]
        print("keys:", keys)
        status = set(assumed_keys).issubset(keys)
    except KeyError:
        status = False

    return status


def generate_s3_path(date):

    train_set_prefix = os.path.join('input-data-training', date, 'multiclass')
    output_set_prefix = os.path.join("output-model", date, "multiclass")
    validation_set_prefix = os.path.join("input-data-validation", date, "multiclass")

    s3_input_path = os.path.join('s3://', BUCKET, train_set_prefix, '')
    s3_output_path = os.path.join('s3://', BUCKET, output_set_prefix, '')
    s3_valid_path = os.path.join('s3://', BUCKET, validation_set_prefix, '')

    return s3_input_path, s3_output_path, s3_valid_path


def datetime_to_str(date: datetime) -> str:
    year = str(date.year)
    month = str("{0:02d}".format(date.month))
    day = str("{0:02d}".format(date.day))
    str_date = '{0}-{1}-{2}'.format(year, month, day)

    return str_date


def str_to_datetime(str_date: str) -> datetime:

    return datetime.strptime(str_date, '%Y-%m-%d')


def add_days(str_dt: str, days: int) -> str:
    datetime_dt = str_to_datetime(str_dt)
    n_days_after = datetime_dt + timedelta(days=days)
    str_n_days_after = datetime_to_str(n_days_after)

    return str_n_days_after
