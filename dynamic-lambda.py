import boto3
from botocore.client import Config
import StringIO
import zipfile
import mimetypes

s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))

static_bucket= s3.Bucket('static.skinnerslane.com')
dynamic_bucket = s3.Bucket('dynamic.skinnerslane.com')

dynamic_zip = StringIO.StringIO()
dynamic_bucket.download_fileobj('dynamicBuild.zip', dynamic_zip)

with zipfile.ZipFile(dynamic_zip) as myzip:
    for nm in myzip.namelist():
        obj = myzip.open(nm)
        static_bucket.upload_fileobj(obj, nm,
            ExtraArgs={'ContentType': 'NoneType'})
        static_bucket.Object(nm).Acl().put(ACL='public-read')
