import boto3
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic =sns.Topic('arn:aws:sns:us-east-1:528774710936:deployeSkinnerTopic')

    try:
        s3 = boto3.resource('s3')

        skinnerslane_bucket= s3.Bucket('skinnerslane.com')
        build_bucket = s3.Bucket('build.skinnerslane.com')

        build_zip = StringIO.StringIO()
        build_bucket.download_fileobj('buildSkinnerslane.zip', build_zip)

        with zipfile.ZipFile(build_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                skinnerslane_bucket.upload_fileobj(obj, nm,
                    ExtraArgs={'ContentType': 'None-Type'})
                skinnerslane_bucket.Object(nm).Acl().put(ACL='public-read')

        print "Job done!"
        topic.publish(Subject="Deployment Completed", Message="Skinner's Lane deployed suscessfully!")
    except:
        topic.publish(Subject="Deployment Failed", Message="Skinner's Lane was not deployed successfully!")
        raise

    return 'Hello from Lambda'
