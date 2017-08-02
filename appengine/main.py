from flask import Flask, request
import boto3
import config
import uuid
import json
import gochariots

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.files.get('file')
        body = data.read()

        seed = uuid.uuid1().int >> 64
        gochariots.setHost(config.GOCHARIOTS_HOST)
        content = {'action': 'post', 'host': request.remote_addr, 'filename': data.filename, 'size': len(body)}
        r1 = gochariots.Record(seed)
        r1.add('img-recog', json.dumps(content))
        gochariots.post(r1)

        content = {'action': 'upload', 'bucket': config.S3_BUCKET}
        r2 = gochariots.Record(seed)
        r2.add('img-recog', json.dumps(content))
        r2.setHash(gochariots.getHash(r1)[0])

        s3 = boto3.resource('s3', aws_access_key_id=config.AWS_KEY_ID, aws_secret_access_key=config.AWS_ACCESS_LEY, region_name=config.AWS_REGION)
        s3.Bucket(config.S3_BUCKET).put_object(Key=str(seed) + '/hash', Body=str(gochariots.getHash(r2)[0]).encode())
        print(seed, gochariots.getHash(r2)[0])
        s3.Bucket(config.S3_BUCKET).put_object(Key=str(seed) + '/' + data.filename, Body=body)

        gochariots.post(r2)

        return 'uploaded to S3'
    return 'POST image file to /'


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int('8080'),
        debug=True
    )
