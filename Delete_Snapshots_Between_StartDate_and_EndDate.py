import boto3
import datetime
import os

START_DATE = os.getenv('START_DATE', '01-01-2018')
END_DATE = os.getenv('END_DATE', '31-12-2019')
AWS_ACCOUNT_NUMBER = os.getenv('AWS_ACCOUNT_NUMBER', '462070801659')
AWS_REGION = os.getenv('AWS_REGION', 'us-gov-west-1')
DRY_RUN = os.getenv('NO_RUN', 'True')


def lambda_handler(event, context):
    client = boto3.client('ec2', region_name=AWS_REGION)
    paginator = client.get_paginator('describe_snapshots')

    for page in paginator.paginate(OwnerIds=[AWS_ACCOUNT_NUMBER]):
        for snapshot in page['Snapshots']:
            start_time = snapshot['StartTime']
            snapshot_time = start_time.replace(tzinfo=None)

            try:
                start = datetime.datetime.strptime(START_DATE, "%d-%m-%Y").replace(tzinfo=None)
                end = datetime.datetime.strptime(END_DATE, "%d-%m-%Y").replace(tzinfo=None)
                snapshot_id = snapshot['SnapshotId']
                if start <= snapshot_time <= end:
                    print("🚨Snapshot with id: {} - Created Date: {} - will be DELETED❗️".format(snapshot_id, start_time))

                    if DRY_RUN != 'True':
                        print("✅Snapshot with id : {} is DELETED successfully.💡".format(snapshot_id))
                        client.delete_snapshot(SnapshotId=snapshot_id)
            except Exception as e:
                print(str(e))
                if 'InvalidSnapshot.InUse' in str(e):
                    print("❗Skipping this snapshot")
                    continue


if __name__ == "__main__":
    lambda_handler(None, None)
