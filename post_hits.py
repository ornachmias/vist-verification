import boto3
from boto.mturk.question import ExternalQuestion
import configurations

region_name = 'us-east-1'

mturk = boto3.client(
    'mturk',
    endpoint_url='https://mturk-requester.us-east-1.amazonaws.com',
    region_name='us-east-1',
    aws_access_key_id=configurations.aws_access_key_id,
    aws_secret_access_key=configurations.aws_secret_access_key,
)

balance = mturk.get_account_balance()
print("Available balance: " + balance["AvailableBalance"])

question = ExternalQuestion(configurations.api_url, frame_height=0)
new_hit = mturk.create_hit(
    Title='Image Sequences Ordering',
    Description='Order image sequences to tell a story.',
    Keywords='question, answer, research, images, sequences',
    Reward='0.12',
    MaxAssignments=60,
    LifetimeInSeconds=4320000,
    AssignmentDurationInSeconds=600,
    AutoApprovalDelayInSeconds=604800,
    Question=question.get_as_xml(),
)

print("HITID = " + new_hit['HIT']['HITId'])
