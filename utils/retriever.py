# -*- coding: utf-8 -*- #
# @Time : 2022/10/5 14:36
import logging
from collections import defaultdict

import jieba
import numpy as np
from bert4keras.snippets import sequence_padding

from utils.data_utils import DataLoader
from utils.simcse_model import SimcseModel
from annoy import AnnoyIndex

jieba.setLogLevel(log_level=logging.INFO)
jieba.load_userdict("data/ship_terms.txt")

vector_dim = 312
ann = AnnoyIndex(vector_dim, "angular")
n_trees = 512
maxlen = 64


class EntityRetriever(object):
    def __init__(self):
        self.data_loader = DataLoader()
        self.stopwords = self.data_loader.load_txt_data("cn_stopwords.txt")
        self.ship_terms = self.data_loader.load_txt_data("data/ship_terms.txt")
        self.id_2_question, _ = self.data_loader.load_faq_docs("data/qa_pair.csv")
        self.entity_2_doc_id = self.construct_inverted_list()

    def split_filter_stopwords(self, sentence):
        # 分词并去停用词
        cutted_question = jieba.lcut(sentence)
        removed_res = [word for word in cutted_question if word not in self.stopwords]
        return removed_res

    def construct_inverted_list(self):
        # 根据FAQ库构建倒排表
        entity_2_doc_id = defaultdict(list)
        for idx, question in self.id_2_question.items():
            removed_stopwords_res = self.split_filter_stopwords(question)
            for each_word in removed_stopwords_res:
                if each_word in self.ship_terms and idx not in entity_2_doc_id[each_word]:
                    entity_2_doc_id[each_word].append(idx)
        return entity_2_doc_id

    def search_similar_question(self, query):
        # 实体检索
        searched_result = []
        similar_ids = []
        query_word_lst = self.split_filter_stopwords(query)
        for word in query_word_lst:
            if word not in self.entity_2_doc_id:
                continue
            similar_question_ids = self.entity_2_doc_id[word]
            for q_id in similar_question_ids:
                if q_id in similar_ids:
                    continue
                # print(query, "~~~", self.id_2_question[q_id])
                # 保证不同检索器返回的格式一致，而这里实体检索没有score，所以默认设为0
                searched_result.append((q_id, 0))
                similar_ids.append(q_id)
        return searched_result


class VectorRetriever(object):
    def __init__(self):
        self.simcse = SimcseModel()
        self.data_loader = DataLoader()
        self.model = self.simcse.model
        self.tokenizer = self.simcse.tokenizer
        self.id_2_question, _ = self.data_loader.load_faq_docs("data/qa_pair.csv")

    def convert_to_ids(self, sentence):
        # 将文本转化为token ids

        token_ids = self.tokenizer.encode(sentence, maxlen=maxlen)[0]
        all_token_ids = sequence_padding([token_ids], length=maxlen)
        return all_token_ids

    def build_annoy_vector_package(self, all_vectors):
        # 构建annoy向量库
        for q_idx, q_vec in all_vectors.items():
            ann.add_item(q_idx, q_vec)
        ann.build(n_trees)
        return ann

    def l2_normalize(self, vecs):
        """标准化
        """
        norms = (vecs ** 2).sum(keepdims=True) ** 0.5
        return vecs / np.clip(norms, 1e-8, np.inf)

    def get_sentence_vector(self, sentence):
        token_ids = self.convert_to_ids(sentence)
        vec = self.model.predict([token_ids, np.zeros_like(token_ids)])[0]
        normalized_vec = self.l2_normalize(vec)
        return normalized_vec

    def map_question_vector(self, docs=None):
        # 构建问答对id到问题向量的映射
        all_vectors = dict()
        if not docs:
            # for idx, question in self.id_2_question.items():
            #     all_vectors[int(idx)] = self.get_sentence_vector(question)
            raise Exception("No documents!")
        else:
            for idx, doc in enumerate(docs):
                print(idx, doc)
                all_vectors[int(idx)] = self.get_sentence_vector(doc)
        return all_vectors

    def search_similar_vector(self, query, annoy_index, recall_nums=5):
        # 检索相似问题句
        similar_result = []
        norm_sent_vec = self.get_sentence_vector(query)
        # 检索相似的向量
        result = annoy_index.get_nns_by_vector(norm_sent_vec, recall_nums, search_k=-1, include_distances=True)
        for idx, score in zip(result[0], result[1]):
            # question, answer = self.id_2_question[idx]
            # print("origin_sentence:%s" % sentence)
            # print("question:%s *** answer:%s *** score:%s \n" % (question, answer, score))
            similar_result.append((idx, score))
        return similar_result
