import boto3
from decimal import Decimal
import json
import urllib
import shutil
import os
import time
import gochariots
from google.cloud import datastore

def read_hash_from_s3(bucket, seed):
    path = '/tmp/' + str(seed)
    shutil.rmtree(path, ignore_errors=True)
    os.makedirs(path)
    s3 = boto3.client('s3')
    s3.download_file(bucket, str(seed) + '/hash', path + '/hash')
    with open(path + '/hash', 'r') as f:
        hash = f.readline()
    return hash

def lambda_handler(event, context):
    rekognition = boto3.client('rekognition')
    gochariots.setHost(os.environ['GOCHARIOTS_HOST'])

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    seed = int(key.split('/')[0])
    hash = int(read_hash_from_s3(bucket, seed))

    content = {'action': 'lambda', 's3_bucket': bucket, 's3_key': key}
    r1 = gochariots.Record(seed)
    r1.add('img-recog', json.dumps(content))
    r1.setHash(hash)
    gochariots.post(r1)

    start = time.time()
    response = rekognition.detect_labels(Image={"S3Object": {"Bucket": bucket, "Name": key}})
    d = {}
    for pair in response['Labels']:
        d[pair['Name']] = pair['Confidence']
    print(json.dumps(d))

    content = {'action': 'rekognition', 'elapsed_time': time.time() - start, 'labels': response}
    r2 = gochariots.Record(seed)
    r2.add('img-recog', json.dumps(content))
    r2.setHash(gochariots.getHash(r1)[0])
    gochariots.post(r2)

    client = datastore.Client.from_service_account_json('./cred.json')
    key = client.key('Labels')
    entity = datastore.Entity(key=key)
    entity['labels'] = json.dumps(d)
    entity['seed'] = str(seed)
    client.put(entity)

    r3 = gochariots.Record(seed)
    content = {'action': 'result', 'key': str(key)}
    r3.add('img-recog', json.dumps(content))
    r3.setHash(gochariots.getHash(r2)[0])
    gochariots.post(r3)
    
    return response
