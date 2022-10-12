# -*- coding: utf-8 -*- #
# @Time : 2022/10/11 19:01
import re
from collections import defaultdict


def load_data(fp):
    data = []
    with open(fp, "r", encoding="utf-8") as fd:
        all_lines = fd.readlines()
        for line in all_lines:
            data.append(line.strip("\n"))
    return data


type_2_flag = {"length": ["船长", "宽", "型宽", "总长", "船宽", "长", "两柱间长", "满载吃水",
                          "全长", "高", "垂线间长", "结构吃水", "总型长", "@长", "型长", "最大吃水",
                          "水面以上最大高度", "总高", "首尾间长", "最大下潜深度", "深", "吃水深度", "挖泥深度",
                          "总宽", "干舷高度", "作业水深", "水线间长", "船舶总长"
                          ],
               "volume": ["重", "载重", "满载排水量", "载重吨", "排水量", "总吨", "净吨", "总载重", "满载载重吨",
                          "总吨位", "满载负荷", "货舱容积", "净吨位", "满载总重", "总载重量", "设计载重", "设计载重", "重量"],
               "area": ["甲板面积", "干散货甲板面积", "主甲板面积"],
               "date": ["试航", "下水", "试航时间"],
               "people": ["人员", "定员", "最大舱容", "载客", "载员", "舱容", "可搭载", "船员", "设计客位", "可乘员",
                          "时速", "乘客", "可载客", "可载船员", "核定船员", "载客量", "客位", "船舶定员"],
               "speed": ["速度", "设计船速", "运行航速", "试航速度", "平均航速", "@航速", "满载航速", "船舶速度", "最低航速", "船速"]}


def transfer_templates(templates):
    label_2_templates = defaultdict(list)
    for each_temp in templates:
        label, template = each_temp.split(":")
        label_2_templates[label].append(template)
    return label_2_templates


def transfer_regulars(regulars):
    entity_2_substitution = defaultdict(list)
    for each_regulars in regulars:
        entity, replaced_text = each_regulars.split(";")
        words = replaced_text.split("/")
        entity_2_substitution[entity].extend(words)
    return entity_2_substitution


def process_ship_name(ship_name):
    # 变换船名
    # 船名形式为：艾莱尼(ELENI)
    splited_ship_names = []
    if "(" in ship_name:
        p1 = re.compile(r'[(](.*?)[)]', re.S)  # 最小匹配
        sub_name = re.findall(p1, ship_name)
        main_name = re.sub(p1, "", ship_name)
        splited_ship_names.extend([sub_name[0], main_name])
    # 形式为：GREATSHIP RACHNA
    elif " " in ship_name:
        n1, n2 = ship_name.split(" ")
        splited_ship_names.extend([n1, n2])
        if n1.isalpha() and n2.isalpha():
            new_name = n1[0] + n2[0]
            splited_ship_names.append(new_name)
    # 形式为：韦斯顿·澳大利亚
    elif "·" in ship_name:
        n1, n2 = ship_name.split("·")
        splited_ship_names.extend((n1, n2 + "的" + n1))
    else:
        return ship_name
    return splited_ship_names


def get_template_label(rel, tail):
    # 获取模板句的标签
    temp_type = ""
    for label, signal_words in type_2_flag.items():
        if rel in signal_words:
            temp_type = label
            break
        if label == "length":
            if "米" in tail or "M" in tail or "m" in tail or "公尺" in tail:
                temp_type = label
                break
        elif label == "volume":
            if "吨" in tail or "立方米" in tail or "t" in tail:
                temp_type = label
                break
        elif label == "speed":
            if "节" in tail or "海里" in tail:
                temp_type = label
                break
        elif label == "people":
            if "人" in tail:
                temp_type = label
                break
    if not temp_type:
        return None
    return temp_type


def build_diff_questions(triples, label_2_templates, entity_2_substitution):
    # 构建不同形式的问句
    all_questions = []
    for each_triple in triples:
        head, rel, tail = each_triple.split("||")
        # TODO:对head进行变形
        if rel in entity_2_substitution:
            replace_text = entity_2_substitution[rel]
            for text in replace_text:
                question = "%s%s？" % (head, text)
                print(question)
                all_questions.append(question)
        temp_type = get_template_label(rel, tail)
        if temp_type:
            templates = label_2_templates[temp_type]
        else:
            templates = label_2_templates["common"]
        # templates.extend(label_2_templates["place"])
        # templates.extend(label_2_templates["special"])
        for each_temp in templates:
            question = each_temp.replace("[Subject]", head).replace("[Predicate]", rel).replace("[Object]", tail)
            # print(question)
            all_questions.append(question)
    print("构建问题的数量:", len(all_questions))


def main():
    fp = "../data/ship_triples.txt"
    triples = load_data(fp)
    tmp_fp = "question_templates.txt"
    templates = load_data(tmp_fp)
    regx_fp = "replacement_regular.txt"
    regulars = load_data(regx_fp)
    label_2_templates = transfer_templates(templates)
    entity_2_substitution = transfer_regulars(regulars)
    build_diff_questions(triples, label_2_templates, entity_2_substitution)


if __name__ == '__main__':
    main()
