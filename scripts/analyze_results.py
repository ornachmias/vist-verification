import math
import sys
import pandas
import numpy as np
from pandas import DataFrame
import matplotlib.pyplot as plt
import re
from matplotlib import gridspec

import configurations


def get_question_numbers(columns):
    questions = []
    for col in columns:
        m = re.search("question_(\d+)", col)
        if m:
            count = m.group(1)
            if count not in questions:
                questions.append(count)

    return questions


def check_duplicate_seq(df_row):
    question_ids = []
    duplicate_question = []
    for q in questions_range:
        question_id = get_question_id(q, df_row)
        if question_id in question_ids:
            duplicate_question.append(q)
            duplicate_question.append(question_ids.index(question_id))
            break
        else:
            question_ids.append(question_id)

    first_seq = get_images(duplicate_question[0], df_row)
    second_seq = get_images(duplicate_question[1], df_row)

    if np.array_equal(first_seq, second_seq):
        return True

    return False


def check_obvious_seq(df_row):
    question = None
    for i in questions_range:
        if get_question_id(i, df_row) == configurations.test_sequence["id"]:
            question = i
            break

    if question is None:
        print("Unable to find test question Id for AssignmentId=" + df_row["AssignmentId"])
        return False

    images = get_images(question, df_row)
    clean_test_sequence = configurations.test_sequence["image_ids"]
    desired_array = [str(int(numeric_string)) for numeric_string in clean_test_sequence]

    if np.array_equal(images, clean_test_sequence) or np.array_equal(images[::-1], clean_test_sequence):
        return True

    if np.array_equal(images, desired_array) or np.array_equal(images[::-1], desired_array):
        return True

    return False


def get_question_id(question_number, df_row):
    col_name = "question_" + question_number
    return df_row[col_name]


def get_images(question_number, df_row):
    col_prefix = "question_" + str(question_number) + "_image_"
    cols = []
    for i in images_range:
        cols.append(col_prefix + i)

    return df_row[cols].values


def build_results(valid_hits, original_df):
    new_df = DataFrame(columns=['AssignmentId', 'QuestionId', 'Image0', 'Image1', 'Image2', 'Image3', 'Image4'])
    for _, r in original_df.iterrows():
        assignment_id = r['AssignmentId']
        if assignment_id not in valid_hits:
            continue

        for q in questions_range:
            question_id = get_question_id(q, r)
            if str(question_id) == "nan":
                continue
            image_ids = get_images(q, r)
            new_row = {"AssignmentId": assignment_id,
                       "QuestionId": str(question_id),
                       'Image0': str(image_ids[0]),
                       'Image1': str(image_ids[1]),
                       'Image2': str(image_ids[2]),
                       'Image3': str(image_ids[3]),
                       'Image4': str(image_ids[4])}
            new_df = new_df.append(new_row, ignore_index=True)

    return new_df


def cluster_score(x):
    max_cluster = np.max(x)
    return np.divide(x, max_cluster)


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

print("Number of valid submissions:", len(valid))
print("Number of invalid submissions:", total_submit - len(valid))

if len(dup_invalid) != 0:
    print("HIT Ids that have failed to answer the duplicate sequence correctly:")
    for i in dup_invalid:
        print(i)

if len(test_invalid) != 0:
    print("HIT Ids that have failed to answer the obvious sequence correctly:")
    for i in test_invalid:
        print(i)

failed_both = set(dup_invalid).intersection(set(test_invalid))
if len(failed_both) != 0:
    print("HIT Ids that have failed to answer the obvious sequence and the duplicate sequence correctly:")
    for i in failed_both:
        print(i)

valid_df = build_results(valid, df).sort_values(by=["QuestionId"])
question_count = valid_df.groupby("QuestionId").size().reset_index(name='total_counts')
unique_order = valid_df[["QuestionId", "Image0", "Image1", "Image2", "Image3", "Image4"]].drop_duplicates().groupby(["QuestionId"]).size().reset_index(name='unique_counts')

print("Stories with less than " + str(configurations.max_story_submit) + " responses:")
missing_questions = []
for _, row in question_count.iterrows():
    q = row[0]
    c = row[1]

    if c < configurations.max_story_submit:
        missing_questions.append(q)

print(missing_questions)