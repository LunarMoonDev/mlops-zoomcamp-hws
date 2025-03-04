### Requirements:
- Run `docker compose up` on `experiment-tracking` directory under `mlops-notebook`
- Create S3 bucket with the following command

```bash
export AWS_PROFILE=localstack
aws s3api create-bucket --bucket homework
```
- Run `docker compose up` on this directory to run `starter.py` in Docker


### How to validate
- simply run `aws s3 ls s3://homework/2023/05` to confirm the contents of the output bucket
