# -*- coding: utf-8 -*- #
# @Time : 2022/10/2 15:21
import csv
import re


def load_terms(fp):
    fmt_data = []
    with open(fp, "r", encoding="utf-8") as fd:
        all_lines = fd.readlines()
        for each_line in all_lines:
            if not each_line:
                continue
            item = each_line.strip("\n")
            term_explanation = re.sub(r"[^a-z](.*)[$a-z]", "", item)
            prefix_text = re.match(r"[^a-z](.*)[$a-z]", item).group()
            idx_lst = re.findall("\d{2}[.]\d{3}", prefix_text)
            term = re.findall(r"[\u4e00-\u9fa5]+", prefix_text)
            term_en = re.sub(r"(.*)[$\u4e00-\u9fa5]", "", prefix_text)
            print(idx_lst, term, term_en, term_explanation)
            fmt_data.append((idx_lst[0], term[0], term_en, term_explanation))
    return fmt_data


def write_to_csv(save_fp, fmt_data):
    with open(save_fp, "w", encoding="utf-8", newline="") as fd:
        writer = csv.writer(fd)
        writer.writerow(["id", "term", "term_en", "explanation"])
        writer.writerows(fmt_data)


def write_to_txt(save_fp, fmt_data):
    with open(save_fp, "w", encoding="utf-8") as fd:
        for d in fmt_data:
            fd.write(d[1])
            fd.write("\n")


if __name__ == '__main__':
    fp = "../data/船舶总体性能结构.txt"
    res = load_terms(fp)
    save_fp = "../data/terms_of_ship_performance.csv"
    write_to_csv(save_fp, res)
    save_txt_fp = "../data/ship_terms.txt"
    write_to_txt(save_txt_fp, res)
