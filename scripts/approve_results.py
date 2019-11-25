import sys

import boto3
import pandas

import configurations
from scripts.analyze_results import check_duplicate_seq, get_question_numbers, check_obvious_seq


def approve_assignments(mturk_client, assignment_ids):
    for assignment_id in assignment_ids:
        mturk_client.approve_assignment(AssignmentId=assignment_id, OverrideRejection=False)


def reject_assignments(mturk_client, assignment_ids, reason):
    for assignment_id in assignment_ids:
        mturk_client.reject_assignment(AssignmentId=assignment_id, RequesterFeedback=reason)


if len(sys.argv) != 2:
    sys.exit("Invalid input. Usage should be: python3 analyze_result.py <result_file_path>")

result_file_path = sys.argv[1]

# Since we are using number as mostly ids, it's better to parse everything as string
df = pandas.read_csv(result_file_path, parse_dates=["AcceptTime", "SubmitTime"], dtype=str)

# Global Parameters
questions_range = get_question_numbers(df.columns)
images_range = ["0", "1", "2", "3", "4"]

total_submit = df.shape[0]
print("Total HIT submissions:", total_submit)

dup_invalid = []
test_invalid = []
valid = []

for index, row in df.iterrows():
    is_dup_valid = check_duplicate_seq(row)
    is_test_valid = check_obvious_seq(row)

    if not is_dup_valid:
        dup_invalid.append(row["AssignmentId"])

    if not is_test_valid:
        test_invalid.append(row["AssignmentId"])

    if is_test_valid and is_dup_valid:
        valid.append(row["AssignmentId"])

mturk = boto3.client(
    'mturk',
    endpoint_url='https://mturk-requester.us-east-1.amazonaws.com',
    region_name='us-east-1',
    aws_access_key_id=configurations.aws_access_key_id,
    aws_secret_access_key=configurations.aws_secret_access_key,
)

approve_assignments(mturk, valid)
approve_assignments(mturk, dup_invalid)
reject_assignments(mturk, test_invalid, "Sorry, you've failed to answer the test sequence correctly. "
                                        "As warned, the HIT is rejected.")
