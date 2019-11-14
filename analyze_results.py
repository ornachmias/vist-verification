import sys
import pandas
import numpy as np
from pandas import DataFrame
import matplotlib.pyplot as plt

import configurations

if len(sys.argv) != 2:
    sys.exit("Invalid input. Usage should be: python3 analyze_result.py <result_file_path>")

result_file_path = sys.argv[1]
df = pandas.read_csv(result_file_path, parse_dates=["AcceptTime", "SubmitTime"])

# Global Parameters
questions_range = range(0, configurations.number_of_questions + 2)
images_range = range(0, 5)
obvious_sequence = [1, 2, 3, 4, 5]


def check_duplicate_seq(df_row):
    question_ids = []
    duplicate_question = []
    for i in questions_range:
        question_id = get_question_id(i, df_row)
        if question_id in question_ids:
            duplicate_question.append(i)
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
    question_count = None
    for i in questions_range:
        if get_question_id(i, df_row) == "test":
            question_count = i
            break

    if question_count is None:
        print("Unable to find test question Id for AssignmentId=" + df_row["AssignmentId"])
        return False

    images = get_images(question_count, df_row)
    if np.array_equal(images, obvious_sequence) or np.array_equal(images[::-1], obvious_sequence):
        return True

    return False


def get_question_id(question_count, df_row):
    col_name = "question_" + str(question_count)
    return df_row[col_name]


def get_images(question_count, df_row):
    col_prefix = "question_" + str(question_count) + "_image_"
    cols = []
    for i in images_range:
        cols.append(col_prefix + str(i))

    return df_row[cols].values


def build_results(valid_hits, original_df):
    new_df = DataFrame(columns=['AssignmentId', 'QuestionId', 'Image0', 'Image1', 'Image2', 'Image3', 'Image4'])
    for index, row in original_df.iterrows():
        assignment_id = row['AssignmentId']
        if assignment_id not in valid_hits:
            continue

        for q in range(0, 5):
            question_id = get_question_id(q, row)
            image_ids = get_images(q, row)
            new_row = {"AssignmentId": assignment_id,
                       "QuestionId": question_id,
                       'Image0': image_ids[0],
                       'Image1': image_ids[1],
                       'Image2': image_ids[2],
                       'Image3': image_ids[3],
                       'Image4': image_ids[4]}
            new_df = new_df.append(new_row, ignore_index=True)

    return new_df





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
unique_order = valid_df.drop_duplicates().groupby("QuestionId").size().reset_index(name='unique_counts')
graph_df = pandas.merge(question_count, unique_order, how="inner", on="QuestionId")
graph_df.set_index("QuestionId",drop=True,inplace=True)
graph_df.plot(kind='bar')
plt.show()

