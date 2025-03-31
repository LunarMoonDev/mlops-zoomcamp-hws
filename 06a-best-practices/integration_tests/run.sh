#!/usr/bin/env bash

cd "$(dirname "$0")/.."

# to prepare for logs, make it nice
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# environment variables
export INPUT_FILE_PATTERN="s3://nyc-duration/in/{year:04d}-{month:02d}.parquet"
export OUTPUT_FILE_PATTERN="s3://nyc-duration/out/{year:04d}-{month:02d}.parquet"
export S3_ENDPOINT_URL='http://localhost:4566'

# run docker image by creating container
echo -e "${YELLOW}$(date '+%Y-%m-%d %H:%M:%S') - === Block 1: Creating Container ===${NC}"
docker compose -f integration_tests/docker-compose.yaml up -d
echo -e "\n\n"

# delay for container cus detached
echo -e "${BLUE}$(date '+%Y-%m-%d %H:%M:%S') - === Block 2: Delaying for 5 seconds ===${NC}"
sleep 5
echo -e "\n\n"

# create aws s3 bucket
echo -e "${BLUE}$(date '+%Y-%m-%d %H:%M:%S') - === Block 3: AWS S3 preparation ===${NC}"
export AWS_PROFILE=localstack
aws s3 mb s3://nyc-duration/

# push input data to s3 bucket
aws s3 cp integration_tests/data/2023-01.parquet s3://nyc-duration/in/
echo -e "\n\n"

# run the integration test
echo -e "${BLUE}$(date '+%Y-%m-%d %H:%M:%S') - === Block 4: Running the integration test ===${NC}"
python -m integration_tests.integration_test
ERROR_CODE=$?
echo -e "\n\n"

# cleanup
if [ ${ERROR_CODE} != 0 ]; then
    echo -e "${YELLOW}$(date '+%Y-%m-%d %H:%M:%S') - === Block 5: Cleaning up resources ===${NC}"
    docker compose -f integration_tests/docker-compose.yaml logs
    docker compose -f integration_tests/docker-compose.yaml down
    exit ${ERROR_CODE}
fi

# cleaning
echo -e "${BLUE}$(date '+%Y-%m-%d %H:%M:%S') - === Block 5: Cleaning ===${NC}"
docker compose -f integration_tests/docker-compose.yaml down
echo -e "\n\n"
