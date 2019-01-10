# Splitter
A web app for uploading an image of a receipt and calculating who owes what using AWS Rekognition.

### Development Next Steps:
[Trello Board](https://trello.com/b/sa1EM33j/splitter)

## Setup
Splitter can be setup locally or deployed with Docker

### Environment Variables
Use the [env-file.template](./docker/env-files/env-file.template) as a guide for the environment variables used in splitter.
- Create an environment file and edit the env_file in docker-compose-dev.yaml to point to that file (default is dev-env-file)

### Local
1. Edit the env-file you setup for your target postgres db or use a docker pg
- For the docker pg you can use `docker-compose -f docker/docker-compose-local.yaml up`

### Docker
1. Navigate to the base project directory
2. Build the docker image 
`docker build -f docker/Dockerfile -t splitter:latest .`
4. Run docker-compose with [docker-compose-dev.yaml](./docker/docker-compose-dev.yaml)
`docker-compose -f docker/docker-compose-dev.yaml up -d`
