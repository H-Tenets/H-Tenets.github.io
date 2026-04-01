# coding: utf-8

# # 用于academicpages的演讲markdown生成器
#
# 接收包含元数据的演讲TSV文件，并将其转换为可用于[academicpages.github.io](academicpages.github.io)的格式。
# 这是一个交互式Jupyter notebook（[更多信息请点击这里](http://jupyter-notebook-beginner-guide.readthedocs.io/en/latest/what_is_jupyter.html)）。
# 核心Python代码也在`talks.py`中。在将`talks.tsv`替换为包含你的数据的文件后，从`markdown_generator`文件夹运行。
#
# TODO：使其能够与BibTex和其他数据库一起工作，而不是Stuart的非标准TSV格式和引用样式。

# In[1]:

import pandas as pd
import os


# ## 数据格式
#
# TSV需要在顶部包含以下列：title, type, url_slug, venue, date, location, talk_url, description，并带有标题行。
# 这些字段中有许多可以为空，但列必须在TSV中。
#
# - 不能为空的字段：`title`、`url_slug`、`date`。其他都可以为空。`type`默认为"Talk"
# - `date`必须格式化为YYYY-MM-DD。
# - `url_slug`将是.md文件的描述性部分和论文页面permalink URL的一部分。
#     - .md文件将是`YYYY-MM-DD-[url_slug].md`，permalink将是`https://[yourdomain]/talks/YYYY-MM-DD-[url_slug]`
#     - `url_slug`和`date`的组合必须是唯一的，因为它将是你文件名的基础
#


# ## 导入TSV
#
# Pandas通过read_csv函数使这变得很容易。我们使用的是TSV，所以我们将分隔符指定为制表符，即`\t`。
#
# 我发现将这种数据放入制表符分隔的值格式中很重要，因为这类数据中有很多逗号，逗号分隔的值可能会出错。
# 但是，你可以修改导入语句，因为pandas也有read_excel()、read_json()等。

# In[3]:

talks = pd.read_csv("talks.tsv", sep="\t", header=0)
talks


# ## 转义特殊字符
#
# YAML对如何接受有效字符串非常挑剔，所以我们将单引号和双引号（以及和号）替换为它们的HTML编码等价物。
# 这使它们在原始格式中看起来不太可读，但它们被很好地解析和渲染。

# In[4]:

html_escape_table = {"&": "&amp;", '"': "&quot;", "'": "&apos;"}


def html_escape(text):
    if type(text) is str:
        return "".join(html_escape_table.get(c, c) for c in text)
    else:
        return "False"


# ## 创建markdown文件
#
# 这是繁重工作完成的地方。这循环遍历TSV数据框中的所有行，然后开始连接一个大字符串（```md```），其中包含每种类型的markdown。
# 它首先做YAML元数据，然后做单个页面的描述。

# In[5]:

loc_dict = {}

for row, item in talks.iterrows():
    md_filename = str(item.date) + "-" + item.url_slug + ".md"
    html_filename = str(item.date) + "-" + item.url_slug
    year = item.date[:4]

    md = '---\ntitle: "' + item.title + '"\n'
    md += "collection: talks" + "\n"

    if len(str(item.type)) > 3:
        md += 'type: "' + item.type + '"\n'
    else:
        md += 'type: "Talk"\n'

    md += "permalink: /talks/" + html_filename + "\n"

    if len(str(item.venue)) > 3:
        md += 'venue: "' + item.venue + '"\n'

    if len(str(item.date)) > 3:
        md += "date: " + str(item.date) + "\n"

    if len(str(item.location)) > 3:
        md += 'location: "' + str(item.location) + '"\n'

    md += "---\n"

    if len(str(item.talk_url)) > 3:
        md += "\n[More information here](" + item.talk_url + ")\n"

    if len(str(item.description)) > 3:
        md += "\n" + html_escape(item.description) + "\n"

    md_filename = os.path.basename(md_filename)
    # print(md)

    with open("../_talks/" + md_filename, "w") as f:
        f.write(md)


# These files are in the talks directory, one directory below where we're working from.
