import boto3
from botocore.client import Config
import StringIO
import zipfile

def lambda_handler(event, context):

    s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))

    skinnerslane_bucket= s3.Bucket('skinnerslane.com')
    build_bucket = s3.Bucket('build.skinnerslane.com')

    build_zip = StringIO.StringIO()
    build_bucket.download_fileobj('buildSkinnerslane.zip', build_zip)

    with zipfile.ZipFile(build_zip) as myzip:
        for nm in myzip.namelist():
            obj = myzip.open(nm)
            skinnerslane_bucket.upload_fileobj(obj, nm)
            skinnerslane_bucket.Object(nm).Acl().put(ACL='public-read')

    return 'Hello from Lambda'
