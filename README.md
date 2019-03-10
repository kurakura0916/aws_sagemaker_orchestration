## 開発環境

### 開発環境ライブラリー

```
$ python --version
Python 3.6.3

# venv
$ python -m venv env

# activate
. env/bin/activate

(env) $ docker build -t dev-sagemaker-orchestration-image .

(env) $ pip install `docker run dev-sagemaker-orchestration-image pip freeze`

```

## 環境構築

### cloudformationによるAWS StepFunctionsの環境構築

```
./create-stack.sh
```

- いらなくなったformationの削除

```
./delete-stack.sh
```

## ジョブの送信

### StepFunctionsのジョブ実行

```
DATE=YYYY-MM-DD # トレーニングの開始日

aws stepfunctions start-execution \
--state-machine-arn arn:aws:states:ap-northeast-1:123123:stateMachine:dev-SageMaker-orchestration \ 
--name your_job_name \
--input "{\"DATE\": \"${DATE}\"}" \
--profile your_profile_name
```
