#!/bin/bash

eval $(aws ecr get-login --region ap-northeast-1 --no-include-email --profile your_profile)

echo "スタックを作成します"
# Lambdaの環境を構築する
python formation_config_creator.py
aws cloudformation create-stack \
    --stack-name sagemaker-orchestration \
    --template-body file://$PWD/cloudformation/cloudformation.yml \
    --capabilities CAPABILITY_IAM \
    --profile your_profile
