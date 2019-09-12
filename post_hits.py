import boto3
from boto.mturk.question import ExternalQuestion
import configurations

region_name = 'us-east-1'

mturk = boto3.client(
    'mturk',
    endpoint_url='https://mturk-requester-sandbox.us-east-1.amazonaws.com',
    region_name='us-east-1',
    aws_access_key_id=configurations.aws_access_key_id,
    aws_secret_access_key=configurations.aws_secret_access_key,
)

question = ExternalQuestion(configurations.api_url, frame_height=0)
new_hit = mturk.create_hit(
    Title='Image Sequences Ordering',
    Description='Order image sequences to tell a story.',
    Keywords='question, answer, research, images, sequences',
    Reward='0.05',
    MaxAssignments=50,
    LifetimeInSeconds=172800,
    AssignmentDurationInSeconds=600,
    AutoApprovalDelayInSeconds=14400,
    Question=question.get_as_xml(),
)

print ("HITID = " + new_hit['HIT']['HITId'])