# -*- coding: utf-8 -*- #
# @Time : 2022/10/10 21:06
import json
from collections import defaultdict

predicate_2_num = defaultdict(int)


def load_cnshipnet(fp):
    all_triples = []

    with open(fp, "r", encoding="utf-8") as fd:
        all_data = json.load(fd)
        for each_data in all_data:
            text = each_data["text"]
            # print(f"text:{text}\n")
            relation_list = each_data["relation_list"]
            for each_relation in relation_list:
                subject = each_relation["subject"]
                obj = each_relation["object"]
                predicate = each_relation["predicate"]
                predicate_2_num[predicate] += 1
                triple = "%s||%s||%s" % (subject, predicate, obj)
                all_triples.append(triple)

    return all_triples



def write_to_txt(save_fp, result):
    with open(save_fp, "w", encoding="utf-8") as fd:
        for line in result:
            fd.write(line)
            fd.write("\n")


if __name__ == '__main__':
    fp = "../data/CNShipNet/"
    json_lst = ["train.json", "dev.json", "test.json"]
    result = []
    for each_file in json_lst:
        triples = load_cnshipnet(fp + each_file)
        result.extend(triples)
    print(predicate_2_num)
    save_fp = "../data/ship_triples.txt"
    # write_to_txt(save_fp, result)
