#!/bin/bash -ex

SCRIPT_DIR=$(cd $(dirname $0); pwd)

export SCRIPT_DIR=$SCRIPT_DIR
export MSYS_NO_PATHCONV=1

# For use the specified credentials in enviroment variable
export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:=''}
export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:=''}
export AWS_SESSION_TOKEN=${AWS_SESSION_TOKEN:=''}
export AWS_DEFAULT_REGION=us-west-2 # SES don't support ap-northeast-1
export AWS_DEFAULT_OUTPUT=json

docker-compose up -d aws-cdk
docker-compose exec aws-cdk pip install -r /opt/awscdk/requirements.txt
docker-compose exec aws-cdk /bin/bash