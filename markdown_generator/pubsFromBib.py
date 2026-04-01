#!/usr/bin/env python
# coding: utf-8

# # 用于academicpages的出版物markdown生成器
#
# 接收一组出版物的bibtex，并将其转换为可用于[academicpages.github.io](academicpages.github.io)的格式。
# 这是一个交互式Jupyter notebook（[更多信息请点击这里](http://jupyter-notebook-beginner-guide.readthedocs.io/en/latest/what_is_jupyter.html)）。
#
# 核心Python代码也在`pubsFromBibs.py`中。
# 从`markdown_generator`文件夹运行，在更新publist字典后，包含：
# * bib文件名
# * 基于你的bib文件偏好的特定venue键
# * 特定文件的任何特定前置文本
# * 集合名称（未来功能）
#
# TODO：使其能够与其他引用数据库一起工作，
# TODO：将其与现有的TSV解析解决方案合并


from pybtex.database.input import bibtex
import pybtex.database.input.bibtex
from time import strptime
import string
import html
import os
import re

# todo：整合不同的集合类型，而不是一个包罗万象的出版物，需要对模板进行其他更改
publist = {
    "proceeding": {
        "file": "proceedings.bib",
        "venuekey": "booktitle",
        "venue-pretext": "In the proceedings of ",
        "collection": {"name": "publications", "permalink": "/publication/"},
    },
    "journal": {
        "file": "pubs.bib",
        "venuekey": "journal",
        "venue-pretext": "",
        "collection": {"name": "publications", "permalink": "/publication/"},
    },
}

html_escape_table = {"&": "&amp;", '"': "&quot;", "'": "&apos;"}


def html_escape(text):
    """在文本中生成实体。"""
    return "".join(html_escape_table.get(c, c) for c in text)


for pubsource in publist:
    parser = bibtex.Parser()
    bibdata = parser.parse_file(publist[pubsource]["file"])

    # 循环遍历给定bibtex文件中的单个引用
    for bib_id in bibdata.entries:
        # 重置默认日期
        pub_year = "1900"
        pub_month = "01"
        pub_day = "01"

        b = bibdata.entries[bib_id].fields

        try:
            pub_year = f"{b['year']}"

            # todo：这个月份和日期的hack需要一些清理
            if "month" in b.keys():
                if len(b["month"]) < 3:
                    pub_month = "0" + b["month"]
                    pub_month = pub_month[-2:]
                elif b["month"] not in range(12):
                    tmnth = strptime(b["month"][:3], "%b").tm_mon
                    pub_month = "{:02d}".format(tmnth)
                else:
                    pub_month = str(b["month"])
            if "day" in b.keys():
                pub_day = str(b["day"])

            pub_date = pub_year + "-" + pub_month + "-" + pub_day

            # 根据需要去除{}（一些维护格式的bibtex条目）
            clean_title = (
                b["title"]
                .replace("{", "")
                .replace("}", "")
                .replace("\\", "")
                .replace(" ", "-")
            )

            url_slug = re.sub("\\[.*\\]|[^a-zA-Z0-9_-]", "", clean_title)
            url_slug = url_slug.replace("--", "-")

            md_filename = (str(pub_date) + "-" + url_slug + ".md").replace("--", "-")
            html_filename = (str(pub_date) + "-" + url_slug).replace("--", "-")

            # 从文本构建引用
            citation = ""

            # 引用作者 - todo - 为主要作者添加高亮？
            for author in bibdata.entries[bib_id].persons["author"]:
                citation = (
                    citation
                    + " "
                    + author.first_names[0]
                    + " "
                    + author.last_names[0]
                    + ", "
                )

            # 引用标题
            citation = (
                citation
                + '"'
                + html_escape(
                    b["title"].replace("{", "").replace("}", "").replace("\\", "")
                )
                + '."'
            )

            # 根据引用类型添加venue逻辑
            venue = publist[pubsource]["venue-pretext"] + b[
                publist[pubsource]["venuekey"]
            ].replace("{", "").replace("}", "").replace("\\", "")

            citation = citation + " " + html_escape(venue)
            citation = citation + ", " + pub_year + "."

            ## YAML变量
            md = (
                '---\ntitle: "'
                + html_escape(
                    b["title"].replace("{", "").replace("}", "").replace("\\", "")
                )
                + '"\n'
            )

            md += """collection: """ + publist[pubsource]["collection"]["name"]

            md += (
                """\npermalink: """
                + publist[pubsource]["collection"]["permalink"]
                + html_filename
            )

            note = False
            if "note" in b.keys():
                if len(str(b["note"])) > 5:
                    md += "\nexcerpt: '" + html_escape(b["note"]) + "'"
                    note = True

            md += "\ndate: " + str(pub_date)

            md += "\nvenue: '" + html_escape(venue) + "'"

            url = False
            if "url" in b.keys():
                if len(str(b["url"])) > 5:
                    md += "\npaperurl: '" + b["url"] + "'"
                    url = True

            md += "\ncitation: '" + html_escape(citation) + "'"

            md += "\n---"

            ## 单个页面的Markdown描述
            if note:
                md += "\n" + html_escape(b["note"]) + "\n"

            if url:
                md += "\n[Access paper here](" + b["url"] + '){:target="_blank"}\n'
            else:
                md += (
                    "\nUse [Google Scholar](https://scholar.google.com/scholar?q="
                    + html.escape(clean_title.replace("-", "+"))
                    + '){:target="_blank"} for full citation'
                )

            md_filename = os.path.basename(md_filename)

            with open("../_publications/" + md_filename, "w", encoding="utf-8") as f:
                f.write(md)
            print(
                f'成功解析 {bib_id}: "',
                b["title"][:60],
                "..." * (len(b["title"]) > 60),
                '"',
            )
        # 引用可能不存在某个字段
        except KeyError as e:
            print(
                f'警告缺少预期字段 {e} 来自条目 {bib_id}: "',
                b["title"][:30],
                "..." * (len(b["title"]) > 30),
                '"',
            )
            continue
