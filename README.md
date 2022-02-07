# aws-serverless-framework-video-preview

## Install serverless if not installed

```bash
npm install serverless
```

## COnfigure AWS for serverless

```bash
serverless config credentials \
    --provider aws \
    --key <access_key> \
    --secret <secret_key>
```

## Install serverless-python-requirement plugin

```bash
sls plugin install -n serverless-python-requirements
```

## Deploy code

```bash
sls deploy --stage dev
```