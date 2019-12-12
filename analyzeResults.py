import math
import os
import pickle
import re

import pandas
from pandas import DataFrame
import matplotlib.pyplot as plt
from matplotlib import gridspec

import numpy as np
import configurations


# noinspection DuplicatedCode
class AnalyzeResults(object):
    def __init__(self, data_root, data_loader, vist_dataset):
        self._data_root = data_root
        self._data_loader = data_loader
        self._vist_dataset = vist_dataset
        self._results_path = os.path.join(data_root, "results")
        self._result_file_ext = ".csv"
        self.images_range = ["0", "1", "2", "3", "4"]
        self._cluster_score_threshold = 0.5

    def get_results_ids(self):
        result_files = [f for f in os.listdir(self._results_path)
                        if os.path.isfile(os.path.join(self._results_path, f)) and f.endswith(self._result_file_ext)]

        result_files = [f[:-len(self._result_file_ext)] for f in result_files]
        return result_files

    def _get_graphs_dir_path(self, result_id, graph_type):
        return os.path.join(self._results_path, result_id, graph_type)

    def _save_graph(self, result_id, graph_type, fig, fig_name):
        dir = self._get_graphs_dir_path(result_id, graph_type)
        if not os.path.exists(dir):
            os.makedirs(dir)

        path = os.path.join(dir, fig_name + ".png")
        fig.savefig(path)
        return path

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

    def _generate_hist(self, valid_df, result_id):
        pickle_path = os.path.join(self._get_graphs_dir_path(result_id, "hist"), "hist.pickle")

        if os.path.exists(pickle_path):
            with open(pickle_path, 'rb') as handle:
                return pickle.load(handle)

        unique_order_hist = valid_df[["QuestionId", "Image0", "Image1", "Image2", "Image3", "Image4"]]
        unique_order_hist = unique_order_hist.groupby(unique_order_hist.columns.tolist(), as_index=False).size()

        histogram_values = {}
        for index in unique_order_hist.index:
            question_id = index[0]
            if question_id not in histogram_values:
                histogram_values[question_id] = {"values": [], "labels": []}

            histogram_values[question_id]["values"].append(unique_order_hist[index])
            histogram_values[question_id]["labels"].append(index[1:])

        data_keys = list(histogram_values.keys())
        plt.tight_layout()
        for k in data_keys:
            fig = plt.figure()
            v = np.asarray(histogram_values[k]["values"])
            v_i = np.argsort(np.multiply(-1, v))
            v = v[v_i]
            custer_scores = self._cluster_score(v)
            clusters_colors = np.asarray(['b'] * len(v))
            clusters_colors[custer_scores >= self._cluster_score_threshold] = 'r'
            plt.bar(np.arange(len(v)), v, align='center', color=clusters_colors)
            plt.xticks(np.arange(len(v)), np.arange(len(v)))
            plt.title("Story Id: " + str(k))
            if "test" in k or "obv" in k:
                plt.ylim(0, 80)
            else:
                plt.ylim(0, 10)

            histogram_values[k]["fig_path"] = self._save_graph(result_id, "hist", fig, k)

        with open(pickle_path, 'wb') as handle:
            pickle.dump(histogram_values, handle, protocol=pickle.HIGHEST_PROTOCOL)

        return histogram_values

    def _generate_general_graph(self, valid_df, result_id):
        question_count = valid_df.groupby("QuestionId").size().reset_index(name='total_counts')
        unique_order = valid_df[
            ["QuestionId", "Image0", "Image1", "Image2", "Image3", "Image4"]].drop_duplicates().groupby(
            ["QuestionId"]).size().reset_index(name='unique_counts')

        graph_df = pandas.merge(question_count, unique_order, how="inner", on="QuestionId")
        obvious_seq_ids = [d["id"] for d in configurations.obvious_sequences]
        test_questions = graph_df.loc[graph_df['QuestionId'].isin(obvious_seq_ids)]

        obvious_seq_ids.append(configurations.test_sequence["id"])
        graph_df = graph_df[~graph_df['QuestionId'].isin(obvious_seq_ids)]

        plt.tight_layout()

        test_graph_path = None
        if test_questions.shape[0] != 0:
            plt.figure()
            test_plt = test_questions.plot(x='QuestionId', kind='bar', ax=plt.gca())
            test_graph_path = self._save_graph(result_id, "general", test_plt.figure, "test")

        batch_size = 10
        batches_count = len(graph_df) // batch_size + 1
        general_graph_paths = []
        for i in range(batches_count):
            plt.figure()
            if not graph_df[i * batch_size:(i + 1) * batch_size].empty:
                general_plt = graph_df[i * batch_size:(i + 1) * batch_size].plot(x='QuestionId', kind='bar', ax=plt.gca())
                general_graph_paths.append(self._save_graph(result_id, "general", general_plt.figure, "general_" + str(i)))
            else:
                print("Couldn't calculate general graph for batch {}".format(i))

        return test_graph_path, general_graph_paths

    def get_histogram(self, result_id, question_id):
        pickle_path = os.path.join(self._get_graphs_dir_path(result_id, "hist"), "hist.pickle")

        if os.path.exists(pickle_path):
            with open(pickle_path, 'rb') as handle:
                hists = pickle.load(handle)
        else:
            _, _, hists = self.analyze(result_id)

        return hists[question_id]

    def analyze(self, result_id):
        result_file_path = os.path.join(self._results_path, result_id) + self._result_file_ext
        print("Analyzing file={}".format(result_file_path))
        df = pandas.read_csv(result_file_path, parse_dates=["AcceptTime", "SubmitTime"], dtype=str)
        questions_range = self._get_question_numbers(df.columns)

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
        hists = self._generate_hist(valid_df, result_id)
        test_path, general_paths = self._generate_general_graph(valid_df, result_id)

        return test_path, general_paths, hists









