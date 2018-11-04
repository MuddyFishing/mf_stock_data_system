#!/bin/sh

DOCKER_TAG=muddyfishing/mf_stock_data_system:v0.1

echo " docker build -f Dockerfile -t ${DOCKER_TAG} ."
docker build -f Dockerfile -t ${DOCKER_TAG} .
echo "#################################################################"
echo " docker push ${DOCKER_TAG} "