import logging
import os
import boto3
import copy
from time import strftime, gmtime

TARGET = os.environ["TARGET"]
BASE_JOB_NAME = f"dev-sagemaker-{TARGET}"
NUM_CLASS = os.environ["NUM_CLASS"]
IMAGE_ARN = f"123123.dkr.ecr.ap-northeast-1.amazonaws.com" \
               f"/sagemaker-repo:latest"

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


def lambda_handler(event, _context):
    LOGGER.info(event)
    sagemaker_client = boto3.client("sagemaker", region_name="ap-northeast-1")

    base_training_conf = create_training_conf(event)
    training_conf = generate_name_with_timestamp(base_training_conf, "training_job_name")
    training_params = create_parameter(training_conf)
    create_training_job(training_params, sagemaker_client)
    event["name"] = training_conf["training_job_name"]
    event["container"] = training_conf["image_arn"]
    event["stage"] = "Training"
    event["status"] = "InProgress"
    event['message'] = 'Starting training job "{}"'.format(training_conf["training_job_name"])
    return event


def create_training_job(params, client):
    try:
        response = client.create_training_job(**params)
        LOGGER.info(response)
    except Exception as e:

        LOGGER.info('Unable to create training job.')
        raise (e)


def generate_name_with_timestamp(conf: dict, key: str):
    conf = copy.deepcopy(conf)
    name = conf[key] + "-" + strftime("%Y-%m-%d-%H-%M-%S", gmtime())
    conf[key] = name
    return conf


def create_training_conf(event):
    input_data_path = event["s3_input_path"]
    valid_data_path = event["s3_valid_path"]
    output_data_path = event["s3_output_path"]

    return {
        "training_job_name": BASE_JOB_NAME,
        "target": TARGET,
        "num_class": NUM_CLASS,
        "image_arn": IMAGE_ARN,
        "input_data_path": input_data_path,
        "valid_data_path": valid_data_path,
        "output_data_path": output_data_path
    }


def create_parameter(conf):

    params = {
        "TrainingJobName": conf["training_job_name"],
        "HyperParameters": {
            "objective": conf["target"],
            "num_class": conf["num_class"],
            "max_leaf_nodes": "5"
        },
        "AlgorithmSpecification": {
            "TrainingImage": conf["image_arn"],
            "TrainingInputMode": "File"
        },
        "RoleArn": "arn:aws:iam::123123:role/dev-sagemaker",
        "InputDataConfig": [
            {
                "ChannelName": "training",
                "DataSource": {
                    "S3DataSource": {
                        "S3DataType": "S3Prefix",
                        "S3Uri": conf["input_data_path"]
                    }
                }
            },
            {
                "ChannelName": "validation",
                "DataSource": {
                    "S3DataSource": {
                        "S3DataType": "S3Prefix",
                        "S3Uri": conf["valid_data_path"]
                    }
                }
            }
        ],
        "OutputDataConfig": {
            "S3OutputPath": conf["output_data_path"]
        },
        "ResourceConfig": {
            "InstanceType": "ml.m4.xlarge",
            "InstanceCount": 1,
            "VolumeSizeInGB": 10
        },
        "StoppingCondition": {
            "MaxRuntimeInSeconds": 1800
        }
    }
    return params
