# -*- coding: utf-8 -*- #
# @Time : 2022/10/4 20:31
import math

import jieba

from utils.data_utils import DataLoader

data_loader = DataLoader()
stopwords = data_loader.load_txt_data("cn_stopwords.txt")


class BM25(object):

    def __init__(self, documents):
        self.docs, self.id_2_doc = self.match_similar_sentence(documents)
        self.D = len(self.docs)
        self.avgdl = sum([len(doc) + 0.0 for doc in self.docs]) / self.D
        self.docs = self.docs
        self.f = []  # 列表的每一个元素是一个dict，dict存储着一个文档中每个词的出现次数
        self.df = {}  # 存储每个词及出现了该词的文档数量
        self.idf = {}  # 存储每个词的idf值
        self.k1 = 1
        self.b = 0.5
        self.init()

    def init(self):
        for doc in self.docs:
            word_2_freq = {}
            for word in doc:
                word_2_freq[word] = word_2_freq.get(word, 0) + 1  # 存储每个文档中每个词的出现次数
            self.f.append(word_2_freq)
            for word in word_2_freq:
                self.df[word] = self.df.get(word, 0) + 1
        for k, v in self.df.items():
            self.idf[k] = math.log(self.D - v + 0.5) - math.log(v + 0.5)

    def split_and_remove_stopwords(self, sentence):
        """
        分词并去停用词
        Args:
            sentence:
        Returns:
        """
        cutted_question = jieba.lcut(sentence)
        removed_res = [word for word in cutted_question if word not in stopwords]
        return removed_res

    def sim(self, sent, index):
        score = 0
        for word in sent:
            if word not in self.f[index]:
                continue
            d = len(self.docs[index])
            score += (self.idf[word] * self.f[index][word] * (self.k1 + 1)
                      / (self.f[index][word] + self.k1 * (1 - self.b + self.b * d
                                                          / self.avgdl)))
        return score

    def simall(self, sent):
        scores = []
        sent_word_lst = self.split_and_remove_stopwords(sent)
        for idx, cand_sent in enumerate(self.docs):
            score = self.sim(sent_word_lst, idx)
            scores.append((self.id_2_doc[idx], round(score, 4)))
        return scores

    def match_similar_sentence(self, documents):
        docs_lst = []
        id_2_doc = dict()
        for idx, each_doc in enumerate(documents):
            id_2_doc[idx] = each_doc
            filtered_res = self.split_and_remove_stopwords(each_doc)
            docs_lst.append(filtered_res)
        return docs_lst, id_2_doc
