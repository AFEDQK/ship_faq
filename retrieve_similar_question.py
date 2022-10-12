# -*- coding: utf-8 -*- #
# @Time : 2022/10/5 15:36
import csv

from utils.bm25_utils import BM25
from utils.data_utils import DataLoader
from utils.retriever import EntityRetriever, VectorRetriever

data_loader = DataLoader()

_, id_2_qa = data_loader.load_faq_docs("data/qa_pair.csv")
entity_retrieve = EntityRetriever()
vector_retrieve = VectorRetriever()

all_questions = [item[0] for item in id_2_qa.values()]


def get_entity_retrieval(query):
    return entity_retrieve.search_similar_question(query)


def get_vector_retrieval(query, docs):
    all_vectors = vector_retrieve.map_question_vector(docs)
    annoy_index = vector_retrieve.build_annoy_vector_package(all_vectors)
    return vector_retrieve.search_similar_vector(query, annoy_index)


def bm25_match(docs, sent, topk):
    matched_result = []
    bm25 = BM25(docs)
    result = bm25.simall(sent)
    result.sort(key=lambda x: x[1], reverse=True)
    for sim_question, score in result[:topk]:
        matched_result.append((sent, sim_question, round(score, 4)))
    return matched_result


def merge_retrieve_result(query, entity_similar_ids, vector_similar_ids, topk=5):
    similar_questions = []
    for idx, score in entity_similar_ids:
        question, answer = id_2_qa[idx]
        similar_questions.append(question)
    for idx, score in vector_similar_ids:
        question, answer = id_2_qa[idx]
        if question in similar_questions:
            continue
        similar_questions.append(question)
    matched_res = bm25_match(similar_questions, query, topk)
    return matched_res


def write_to_csv(save_fp, result):
    with open(save_fp, "w", encoding="utf-8", newline="") as fd:
        writer = csv.writer(fd)
        writer.writerow(["query", "similar_question", "score"])
        writer.writerows(result)


def main():
    query_lst = ["何谓船舶的排水量裕度其原因是什么", "船舶的固定压载是指什么？",
                 "什么叫船舶的续航力和自持力？与航速有何关系？", "舷侧纵桁的作用是什么？舷侧纵横与强肋骨、普通肋骨的连接方式是什么？",
                 "试述船体静水总纵弯曲的产生。", "油船船底结构的特点是什么？"]
    result = []
    for query in query_lst:
        print(query, "\n", "~~~~~~~~~~~")
        # entity_similar_ids = get_entity_retrieval(query)
        matched_res = bm25_match(all_questions, query, 20)
        bm25_recall_result = [item[1] for item in matched_res]
        vector_similar_ids = get_vector_retrieval(query, bm25_recall_result)

        # matched_res = merge_retrieve_result(query, entity_similar_ids, vector_similar_ids)
        sorted_res = sorted(vector_similar_ids, key=lambda x: x[-1], reverse=True)
        result.extend(sorted_res)
    save_fp = "result/ship_similar_faq_bm25_2.csv"
    write_to_csv(save_fp, result)


if __name__ == '__main__':
    main()
