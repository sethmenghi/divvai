#!/bin/bash

user_log=$(aws --endpoint-url=http://localstack:4572 s3 mb s3://$UPLOAD_BUCKET)
echo $user_log

init=$(python manage.py db init)
migrate=$(python manage.py db migrate)
upgrade=$(python manage.py db upgrade)
echo $init
echo $migrate
echo $upgrade

exec "$@"
