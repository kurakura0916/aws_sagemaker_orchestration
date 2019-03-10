---
# define include macro
{% macro include(file) %}{% include(file) %}{% endmacro %}

AWSTemplateFormatVersion: 2010-09-09
Description: Build SageMaker Orchestration environment
# =======set parameters======== #
Parameters:
  Runtime:
    Description: Language of scripts
    Type: String
    Default: python3.6
  NumClass:
    Description: Number of class
    Type: String
    Default: 3
  Target:
    Description: Targets
    Type: String
    Default: multiclass
  HookUrl:
    Description: hookurl of  slack
    Type: String
    Default: https://hooks.slack.com/services/hoge
  SlackChannel:
    Description: channel of  slack
    Type: String
    Default: aws_notify
  ExecutionRole:
    Description: sagemaker execution role
    Type: String
    Default: arn:aws:iam::123123:role/dev-sagemaker

Resources:
  # =======IAM======== #
  StepFunctionsRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service:
                - states.amazonaws.com
            Action:
              - sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/AWSLambdaFullAccess
      Path: "/service-role/"

  DataCheckerLambdaRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
        - Effect: Allow
          Principal:
            Service:
            - lambda.amazonaws.com
          Action:
          - sts:AssumeRole
      ManagedPolicyArns:
      - arn:aws:iam::aws:policy/AWSLambdaFullAccess
      - arn:aws:iam::aws:policy/AmazonSageMakerFullAccess
      Path: "/service-role/"

  # =======Step Functions======== #
  SageMakerStateMachine:
    Type: "AWS::StepFunctions::StateMachine"
    Properties:
      StateMachineName: "dev-SageMaker-orchestration"
      DefinitionString:
        !Sub
          - |-
            {{ include('./stepfunctions/state_machine.json')|indent(12) }}
          - DataCheckerArn: !GetAtt DataChecker.Arn
      RoleArn: !GetAtt StepFunctionsRole.Arn

  # =======Lambda======== #
  DataChecker:
    Type: AWS::Lambda::Function
    Properties:
      Code:
        ZipFile: !Sub |
          {{ include('./lambda_scripts/data_checker.py')|indent(10) }}
      Description: "SagaMaker orchestration data checker lambda"
      FunctionName: "DataChecker"
      Handler: index.lambda_handler
      MemorySize: 128
      Role: !GetAtt DataCheckerLambdaRole.Arn
      Runtime: !Ref Runtime
      Timeout: 15
  StartTrainingJob:
    Type: AWS::Lambda::Function
    Properties:
      Code:
        ZipFile: !Sub |
          {{ include('./lambda_scripts/start_training_job.py')|indent(10) }}
      Description: "SagaMaker orchestration start training job lambda"
      FunctionName: "StartTrainingJob"
      Handler: index.lambda_handler
      MemorySize: 128
      Role: !GetAtt DataCheckerLambdaRole.Arn
      Runtime: !Ref Runtime
      Timeout: 15
      Environment:
        Variables:
          TARGET: !Ref Target
          NUM_CLASS: !Ref NumClass

  NotifySlack:
    Type: AWS::Lambda::Function
    Properties:
      Code:
        ZipFile: !Sub |
          {{ include('./lambda_scripts/notify_slack.py')|indent(10) }}
      Description: "SagaMaker orchestration notify slack"
      FunctionName: "NotifySlack"
      Handler: index.lambda_handler
      MemorySize: 128
      Role: !GetAtt DataCheckerLambdaRole.Arn
      Runtime: !Ref Runtime
      Timeout: 15
      Environment:
        Variables:
          HOOK_URL: !Ref HookUrl
          CHANNEL: !Ref SlackChannel

  GetStatus:
    Type: AWS::Lambda::Function
    Properties:
      Code:
        ZipFile: !Sub |
          {{ include('./lambda_scripts/get_status.py')|indent(10) }}
      Description: "SagaMaker orchestration get status"
      FunctionName: "GetStatus"
      Handler: index.lambda_handler
      MemorySize: 128
      Role: !GetAtt DataCheckerLambdaRole.Arn
      Runtime: !Ref Runtime
      Timeout: 15

  DeployModel:
    Type: AWS::Lambda::Function
    Properties:
      Code:
        ZipFile: !Sub |
          {{ include('./lambda_scripts/deploy_model.py')|indent(10) }}
      Description: "SagaMaker orchestration deploy model"
      FunctionName: "DeployModel"
      Handler: index.lambda_handler
      MemorySize: 128
      Role: !GetAtt DataCheckerLambdaRole.Arn
      Runtime: !Ref Runtime
      Timeout: 15
      Environment:
        Variables:
           EXECUTION_ROLE: !Ref ExecutionRole

