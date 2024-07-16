from testboto import s3, BUCKET

#@pytest.fixture(scope="session", autouse=True)
def pytest_sessionfinish(session, exitstatus):
    response = s3.list_objects_v2(Bucket=BUCKET)
    if 'Contents' in response:
        for object in response['Contents']:
            s3.delete_object(Bucket=BUCKET, Key=object['Key'])

    response = s3.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    if BUCKET in buckets:
        s3.delete_bucket(Bucket = BUCKET)