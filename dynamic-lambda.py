import boto3
from botocore.client import Config
import StringIO
import zipfile
import mimetypes


def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:eu-west-2:528774710936:deployDynamicTopic')

    location = {
        "bucketName": 'dynamic.skinnerslane.com',
        "objectKey": 'dynamicBuild.zip'
    }
    try:
        job = event.get("CodePipeline.job")

        if job:
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"] == "MyAppBuild":
                    location = artifact["location"]["s3Location"]

        print "Building Dynamic Website from " + str(location)

        s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))

        static_bucket= s3.Bucket('static.skinnerslane.com')
        dynamic_bucket = s3.Bucket(location["bucketName"])

        dynamic_zip = StringIO.StringIO()
        dynamic_bucket.download_fileobj(location["objectKey"], dynamic_zip)

        with zipfile.ZipFile(dynamic_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                static_bucket.upload_fileobj(obj, nm,
                    ExtraArgs={'ContentType': 'NoneType'})
                static_bucket.Object(nm).Acl().put(ACL='public-read')

        return "Job Done!"
        topic.publish(Subject="Dynamic Website Deployed", Message="Dynamic Website Deployed Successfully!")
        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId = job["id"])
    except:
        topic.publish(Subject="Dynamic Website Deployed Failed", Message="Dynamic Website Was Not Deployed Successfully!")
        raise
