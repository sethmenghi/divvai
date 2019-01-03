#!/bin/bash

user_log=$(aws --endpoint-url=http://0.0.0.0:4572 s3 mb s3://$UPLOAD_BUCKET)
echo $user_log

pip install psycopg2

flask db init
flask db migrate
flask db upgrade

exec "$@"

