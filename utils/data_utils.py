# -*- coding: utf-8 -*- #
# @Time : 2022/10/4 20:36
import csv


class DataLoader(object):
    def __init__(self):
        pass

    def load_txt_data(self, fp):
        data = []
        with open(fp, "r", encoding="utf-8") as fd:
            all_lines = fd.readlines()
            for word in all_lines:
                data.append(word.strip("\n"))
        return data

    def load_faq_docs(self, fp):
        # 加载FAQ问答对数据
        id_2_question = dict()
        id_2_qa = dict()
        with open(fp, "r", encoding="utf-8") as fd:
            reader = csv.reader(fd)
            next(reader)
            for line in reader:
                if not line:
                    continue
                idx, question, answer = line
                id_2_question[int(idx)] = question
                id_2_qa[int(idx)] = [question, answer]
        return id_2_question, id_2_qa
