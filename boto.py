import boto3
import json
import io
import pathlib
import uuid
import mimetypes

def generate_name(file):
    ext = pathlib.Path(file.filename).suffix
    key = str(uuid.uuid4())+ext
    return key
    
def upload_file(file, s3_client, bucket):
    file_uuid = generate_name(file)
    filebytes = io.BytesIO(file.file.read())
    try:
        response = s3_client.put_object(Body=filebytes, Bucket=bucket, Key=file_uuid, ContentType='text/html')
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return {"file_bytes" : filebytes, "new_image_uuid" : file_uuid}
        else:
            raise Exception(f"Failed to retrieve file. Response = {response}")
    except Exception as e:
        print(e)

def update_file(oldfile_uuid, newFile, s3_client, bucket):
    filebytes = io.BytesIO(newFile.file.read())
    new_key = generate_name(newFile)
    try:
        response = s3_client.put_object(Body=filebytes, Bucket=bucket, Key=new_key, ContentType='text/html')
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            delete_response = delete_file(oldfile_uuid, s3_client, bucket)
            if delete_response["ResponseMetadata"]["HTTPStatusCode"] == 204:
                return {"new_image_uuid" : new_key}
            else:
                raise Exception(f"Failed to delete file during update. Response = {delete_response}")
        else:
            raise Exception(f"Failed to retrieve file. Response = {response}")
    except Exception as e:
        print(e)

def delete_file(file_uuid, s3_client, bucket):
    try:
        response = s3_client.delete_object(Bucket = bucket, Key = file_uuid)
        return response
    except Exception as e:
        print(e)

def get_file(filename, s3_client, bucket):
    try:
        response = s3_client.get_object(Bucket=bucket, Key=filename)
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return response["Body"].read()
        else:
            raise Exception(f"Failed to retrieve file. Response = {response}")
    except Exception as e:
        print(e)
