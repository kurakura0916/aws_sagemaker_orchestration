import os
import boto3

EXECUTION_ROLE = os.environ['EXECUTION_ROLE']


def lambda_handler(event, _context):
    sagemaker_client = boto3.client("sagemaker", region_name="ap-northeast-1")
    model_params = create_parameter(event)
    print('Creating model resource from training artifact...')
    # モデルの作成
    create_model(model_params, sagemaker_client)
    print('Creating endpoint configuration...')
    # エンドポイントの設定の作成
    create_endpoint_config(event, sagemaker_client)
    print('Checking if model endpoint already exists...')
    endpoint_name = event["endpoint"]
    config_name = event["name"]
    # エンドポイントの存在を確認
    if check_endpoint_exists(endpoint_name, sagemaker_client):
        update_endpoint(endpoint_name, config_name, sagemaker_client)
    else:
        print('There is no existing endpoint for this model. Creating new model endpoint...')
        create_endpoint(endpoint_name, config_name, sagemaker_client)

    event['stage'] = 'Deployment'
    event['status'] = 'Creating'
    event['message'] = 'Started deploying model "{}" to endpoint "{}"'.format(config_name, endpoint_name)
    return event


def create_model(model_params, client):
    try:
        client.create_model(**model_params)
    except Exception as e:
        print(e)
        print('Unable to create model.')
        raise(e)


def create_parameter(event):
    return {
        "ExecutionRoleArn": EXECUTION_ROLE,
        "ModelName": event["name"],
        "PrimaryContainer": {
            "Image": event["container"],
            "ModelDataUrl": event["model_data_url"]
        }
    }


def create_endpoint_config(event, client):
    client.create_endpoint_config(
        EndpointConfigName=event["name"],
        ProductionVariants=[
            {
                'VariantName': 'hoge',
                'ModelName': event["name"],
                'InitialInstanceCount': 1,
                'InstanceType': 'ml.m4.xlarge'
            }
        ]
    )


def check_endpoint_exists(endpoint_name, client):
    try:
        client.describe_endpoint(
            EndpointName=endpoint_name
        )
        return True
    except Exception as e:
        return False


def update_endpoint(endpoint_name, config_name, client):
    try:
        client.update_endpoint(
            EndpointName=endpoint_name,
            EndpointConfigName=config_name
        )
    except Exception as e:
        print(e)
        print('Unable to update endpoint.')
        raise(e)


def create_endpoint(endpoint_name, config_name, client):
    try:
        client.create_endpoint(
            EndpointName=endpoint_name,
            EndpointConfigName=config_name
        )
    except Exception as e:
        print(e)
        print('Unable to create endpoint.')
        raise(e)
