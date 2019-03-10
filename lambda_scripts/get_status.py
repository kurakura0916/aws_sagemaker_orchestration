import os
import boto3


def lambda_handler(event, _context):

    sagemaker_client = boto3.client("sagemaker", region_name="ap-northeast-1")

    stage = event["stage"]

    if stage == "Training":
        # トレーニングジョブ名を取得
        name = event["name"]
        training_details = describe_training_job(name, sagemaker_client)
        status = training_details["TrainingJobStatus"]

        # トレーニングジョブの状態
        if status == "Completed":
            s3_output_path = training_details["OutputDataConfig"]["S3OutputPath"]
            model_data_url = os.path.join(s3_output_path, name, "output/model.tar.gz")
            event["message"] = 'Training job "{}" complete. Model data uploaded to "{}"'.format(name, model_data_url)
            event["model_data_url"] = model_data_url
        elif status == "Failed":
            failure_reason = training_details['FailureReason']
            event['message'] = 'Training job failed. {}'.format(failure_reason)

    elif stage == "Deployment":
        # エンドポイントの名前
        name = event["endpoint"]
        endpoint_details = describe_endpoint(name, sagemaker_client)
        status = endpoint_details["EndpointStatus"]

        # エンドポイントの状態
        if status == "InService":
            event["message"] = 'Deployment completed for endpoint "{}".'.format(name)
        elif status == "Failed":
            failure_reason = endpoint_details['FailureReason']
            event["message"] = 'Deployment failed for endpoint "{}". {}'.format(name, failure_reason)
        elif status == 'RollingBack':
            event[
                'message'] = 'Deployment failed for endpoint "{}", rolling back to previously deployed version.'.format(
                name)
    event["status"] = status
    return event


def describe_training_job(training_job_name, client):
    try:
        response = client.describe_training_job(
            TrainingJobName=training_job_name
        )
    except Exception as e:
        print(e)
        print('Unable to describe training job.')
        raise (e)
    return response


def describe_endpoint(endpoint_name, client):
    try:
        response = client.describe_endpoint(
            EndpointName=endpoint_name
        )
    except Exception as e:
        print(e)
        print('Unable to describe endpoint.')
        raise (e)
    return response
