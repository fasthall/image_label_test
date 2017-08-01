from flask import Flask, request
import boto3
import config

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.files.get('file')
        s3 = boto3.resource('s3', aws_access_key_id=config.AWS_KEY_ID, aws_secret_access_key=config.AWS_ACCESS_LEY, region_name=config.AWS_REGION)
        s3.Bucket(config.S3_BUCKET).put_object(Key=data.filename, Body=data.read())
        return data.read()
    return 'hello'


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int('8080'),
        debug=True
    )
