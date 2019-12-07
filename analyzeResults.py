import math
import os
import re

import pandas
from pandas import DataFrame
import matplotlib.pyplot as plt
from matplotlib import gridspec

import numpy as np
import configurations


class AnalyzeResults(object):
    def __init__(self, data_root, data_loader, vist_dataset):
        self._data_root = data_root
        self._data_loader = data_loader
        self._vist_dataset = vist_dataset
        self._results_dir = os.path.join(data_root, "results")
        self._result_file_ext = ".csv"
        self.images_range = ["0", "1", "2", "3", "4"]

    def get_results_ids(self):
        result_files = [f for f in os.listdir(self._results_dir)
                        if os.path.isfile(os.path.join(self._results_dir, f)) and f.endswith(self._result_file_ext)]

        result_files = [f[:-len(self._result_file_ext)] for f in result_files]
        return result_files

    def _get_question_numbers(self, columns):
        questions = []
        for col in columns:
            m = re.search("question_(\d+)", col)
            if m:
                count = m.group(1)
                if count not in questions:
                    questions.append(count)

        return questions

    def _check_duplicate_seq(self, questions_range, df_row):
        question_ids = []
        duplicate_question = []
        for q in questions_range:
            question_id = self._get_question_id(q, df_row)
            if question_id in question_ids:
                duplicate_question.append(q)
                duplicate_question.append(question_ids.index(question_id))
                break
            else:
                question_ids.append(question_id)

        first_seq = self._get_images(duplicate_question[0], df_row)
        second_seq = self._get_images(duplicate_question[1], df_row)

        if np.array_equal(first_seq, second_seq):
            return True

        return False

    def _check_obvious_seq(self, questions_range, df_row):
        question = None
        for i in questions_range:
            if self._get_question_id(i, df_row) == configurations.test_sequence["id"]:
                question = i
                break

        if question is None:
            print("Unable to find test question Id for AssignmentId=" + df_row["AssignmentId"])
            return False

        images = self._get_images(question, df_row)
        clean_test_sequence = configurations.test_sequence["image_ids"]

        if np.array_equal(images, clean_test_sequence) or np.array_equal(images[::-1], clean_test_sequence):
            return True

        return False

    def _get_question_id(self, question_number, df_row):
        col_name = "question_" + question_number
        return df_row[col_name]

    def _get_images(self, question_number, df_row):
        col_prefix = "question_" + str(question_number) + "_image_"
        cols = []
        for i in self.images_range:
            cols.append(col_prefix + i)

        return df_row[cols].values

    def _build_results(self, questions_range, valid_hits, original_df):
        new_df = DataFrame(columns=['AssignmentId', 'QuestionId', 'Image0', 'Image1', 'Image2', 'Image3', 'Image4'])
        for _, r in original_df.iterrows():
            assignment_id = r['AssignmentId']
            if assignment_id not in valid_hits:
                continue

            for q in questions_range:
                question_id = self._get_question_id(q, r)
                if str(question_id) == "nan":
                    continue
                image_ids = self._get_images(q, r)
                new_row = {"AssignmentId": assignment_id,
                           "QuestionId": str(question_id),
                           'Image0': str(image_ids[0]),
                           'Image1': str(image_ids[1]),
                           'Image2': str(image_ids[2]),
                           'Image3': str(image_ids[3]),
                           'Image4': str(image_ids[4])}
                new_df = new_df.append(new_row, ignore_index=True)

        return new_df

    def _cluster_score(self, x):
        max_cluster = np.max(x)
        return np.divide(x, max_cluster)

    def _get_graph_path(self, result_id, graph_type, number_of_results):
        return os.path.join(self._results_dir, "{}_{}_{}.png".format(result_id, graph_type, number_of_results))

    def _get_hist(self, valid_df):
        unique_order_hist = valid_df[["QuestionId", "Image0", "Image1", "Image2", "Image3", "Image4"]]
        unique_order_hist = unique_order_hist.groupby(unique_order_hist.columns.tolist(), as_index=False).size()

        histogram_values = {}
        for index in unique_order_hist.index:
            question_id = index[0]
            if question_id not in histogram_values:
                histogram_values[question_id] = []

            histogram_values[question_id].append(unique_order_hist[index])

        col_num = 5
        rows_num = math.ceil(len(histogram_values) / col_num)
        fig = plt.figure(0, figsize=(18, 18))
        gs = gridspec.GridSpec(rows_num, col_num)
        data_keys = list(histogram_values.keys())

        i = 0
        for r in range(rows_num):
            for c in range(col_num):
                if i >= len(data_keys):
                    break
                ax = fig.add_subplot(gs[r, c])
                v = histogram_values[data_keys[i]]
                custer_scores = self._cluster_score(v)
                clusters_colors = np.asarray(['b'] * len(v))
                clusters_colors[custer_scores >= 0.5] = 'r'
                ax.bar(np.arange(len(v)), v, align='center', alpha=0.5, color=clusters_colors)
                ax.title.set_text(str(data_keys[i]))
                i += 1

        return fig

    def _get_general_graph(self, valid_df):
        question_count = valid_df.groupby("QuestionId").size().reset_index(name='total_counts')
        unique_order = valid_df[
            ["QuestionId", "Image0", "Image1", "Image2", "Image3", "Image4"]].drop_duplicates().groupby(
            ["QuestionId"]).size().reset_index(name='unique_counts')

        graph_df = pandas.merge(question_count, unique_order, how="inner", on="QuestionId")
        obvious_seq_ids = [d["id"] for d in configurations.obvious_sequences]
        test_questions = graph_df.loc[graph_df['QuestionId'].isin(obvious_seq_ids)]

        obvious_seq_ids.append(configurations.test_sequence["id"])
        graph_df = graph_df[~graph_df['QuestionId'].isin(obvious_seq_ids)]

        result = np.array_split(graph_df, 3)
        figure_index = 1
        plt.figure(figure_index, dpi=200)

        test_plt = None
        if test_questions.shape[0] != 0:
            test_plt = test_questions.plot(x='QuestionId', kind='bar', ax=plt.gca())

        general_plt = []
        for i in result:
            figure_index += 1
            plt.figure(figure_index, dpi=200)
            general_plt.append(i.plot(x='QuestionId', kind='bar', ax=plt.gca()))

        return test_plt, general_plt

    def _write_graphs(self, result_id, total_submit, valid_df):
        hist_path = self._get_graph_path(result_id, "hist", total_submit)
        if not os.path.exists(hist_path):
            hist = self._get_hist(valid_df)
            hist.savefig(hist_path)

        test_path = self._get_graph_path(result_id, "test", total_submit)
        general1_path = self._get_graph_path(result_id, "general1", total_submit)
        general2_path = self._get_graph_path(result_id, "general2", total_submit)
        general3_path = self._get_graph_path(result_id, "general3", total_submit)
        if not os.path.exists(test_path) or not general1_path or not general2_path or not general3_path:
            test_plt, general_plt = self._get_general_graph(valid_df)

            if test_plt is not None:
                test_plt.figure.savefig(test_path)
            general_plt[0].figure.savefig(general1_path)
            general_plt[1].figure.savefig(general2_path)
            general_plt[2].figure.savefig(general3_path)

        return [hist_path, test_path, general1_path, general2_path, general3_path]

    def analyze(self, result_id):
        result_file_path = os.path.join(self._results_dir, result_id) + self._result_file_ext
        print("Analyzing file={}".format(result_file_path))
        df = pandas.read_csv(result_file_path, parse_dates=["AcceptTime", "SubmitTime"], dtype=str)
        questions_range = self._get_question_numbers(df.columns)
        total_submit = df.shape[0]

        dup_invalid = []
        test_invalid = []
        valid = []

        for index, row in df.iterrows():
            is_dup_valid = self._check_duplicate_seq(questions_range, row)
            is_test_valid = self._check_obvious_seq(questions_range, row)

            if not is_dup_valid:
                dup_invalid.append(row["AssignmentId"])

            if not is_test_valid:
                test_invalid.append(row["AssignmentId"])

            if is_test_valid and is_dup_valid:
                valid.append(row["AssignmentId"])

        valid_df = self._build_results(questions_range, valid, df).sort_values(by=["QuestionId"])
        graphs_paths = self._write_graphs(result_id, total_submit, valid_df)

        return valid_df, graphs_paths









