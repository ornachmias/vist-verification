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

question = ExternalQuestion(configurations.api_url, frame_height=600)
new_hit = mturk.create_hit(
    Title='Answer a simple question',
    Description='Help research a topic',
    Keywords='question, answer, research',
    Reward='0.05',
    MaxAssignments=1,
    LifetimeInSeconds=172800,
    AssignmentDurationInSeconds=600,
    AutoApprovalDelayInSeconds=14400,
    Question=question.get_as_xml(),
)

print ("HITID = " + new_hit['HIT']['HITId'])