# the latest Python
FROM python:latest

# install the latest nodejs & npm
RUN apt update \
    && apt install -y nodejs \
       npm \
    && apt clean

# install the latest AWS CDK
RUN npm install -g aws-cdk \
    && pip3 install --upgrade aws-cdk.core

# install the latest AWSCLI
RUN pip3 install awscli --upgrade

RUN mkdir -p /opt/awscdk
WORKDIR /opt/awscdk