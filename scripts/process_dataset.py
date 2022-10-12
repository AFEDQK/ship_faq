# -*- coding: utf-8 -*- #
# @Time : 2022/9/18 16:28
import csv

import xlrd


def load_ship_data(fp):
    ship_qa_dataset = []
    idx = 0
    with open(fp, "r", encoding="utf-8") as fd:
        reader = csv.reader(fd)
        _ = next(reader)
        for line in reader:
            if not line:
                continue
            question, answer = line
            answer_lst = answer.strip(" ").split("\n")
            idx = idx + 1
            pair_id = idx
            ship_qa_dataset.append((pair_id, question.strip(), "".join(answer_lst)))
    print(ship_qa_dataset)
    return ship_qa_dataset


def load_excel_data(fp):
    wb = xlrd.open_workbook(filename=fp)
    # 打开第一个sheet
    sh1 = wb.sheet_by_index(0)
    data = []
    for i in range(1, sh1.nrows):
        pair_id, question, answer = sh1.row_values(i)
        data.append((int(pair_id), question.strip(), answer))
    return data


def write_to_csv(save_fp, dataset):
    with open(save_fp, "w", encoding="utf-8", newline="") as fd:
        writer = csv.writer(fd)
        writer.writerow(["id", "question", "answer"])
        writer.writerows(dataset)


if __name__ == '__main__':
    fp = "../data/工作簿1.xlsx"
    dataset = load_excel_data(fp)
    # dataset = load_ship_data(fp)
    save_fp = "../data/qa_pair.csv"
    write_to_csv(save_fp, dataset)
