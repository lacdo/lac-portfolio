import boto3
from botocore.client import Config
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic =sns.Topic('arn:aws:sns:us-east-1:528774710936:deployeSkinnerTopic')

    location = {
        "bucketName": 'build.skinnerslane.com',
        "objectKey": 'buildSkinnerslane.zip'
    }

    try:
        job = event.get("CodePipeline.job")

        if job:
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"] == "MyAppBuild":
                    location = artifact["location"]["s3Location"]

        print "Building Skinner's Lane from " + str(location)

        s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))

        skinnerslane_bucket= s3.Bucket('skinnerslane.com')
        build_bucket = s3.Bucket(location["bucketName"])

        build_zip = StringIO.StringIO()
        build_bucket.download_fileobj(location["objectKey"], build_zip)

        with zipfile.ZipFile(build_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                skinnerslane_bucket.upload_fileobj(obj, nm,
                    ExtraArgs={'ContentType': 'None-Type'})
                skinnerslane_bucket.Object(nm).Acl().put(ACL='public-read')

        print "Job done!"
        topic.publish(Subject="Deployment Completed", Message="Skinner's Lane deployed suscessfully!")
        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId=job["id"])
    except:
        topic.publish(Subject="Deployment Failed", Message="Skinner's Lane was not deployed successfully!")
        raise

    return 'Hello from Lambda'
