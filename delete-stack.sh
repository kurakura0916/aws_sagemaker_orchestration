#!/bin/bash

aws cloudformation delete-stack \
    --stack-name sagemaker-orchestration \
    --profile your_profile
