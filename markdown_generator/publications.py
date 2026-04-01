# 用于AcademicPages的出版物markdown生成器
# 
# 接收包含元数据的出版物TSV/CSV文件，并将其转换为可用于[academicpages.github.io](academicpages.github.io)的格式。
# 可以通过命令提示符使用`python3 publications.py [filename]`来调用。

# 数据格式
# 
# 文件需要在顶部包含以下列作为标题：
# pub_date, title, venue, excerpt, citation, url_slug, paper_url, slides_url
# - `excerpt`、`paper_url`和slides_url可以为空，但其他字段必须有值。
# - `pub_date`必须格式化为YYYY-MM-DD。
# - `url_slug`将是.md文件的描述性部分和论文页面permalink URL的一部分。
#    .md文件将是`YYYY-MM-DD-[url_slug].md`，permalink将是`https://[yourdomain]/publications/YYYY-MM-DD-[url_slug]`
import csv
import os
import sys

# 指示发生错误的标志
EXIT_ERROR = 0

# CSV/TSV文件的预期布局
HEADER_LEGACY  = ['pub_date', 'title', 'venue', 'excerpt', 'citation', 'url_slug', 'paper_url', 'slides_url']
HEADER_UPDATED = ['pub_date', 'title', 'venue', 'excerpt', 'citation', 'url_slug', 'paper_url', 'slides_url', 'category']

# YAML对如何接受有效字符串非常挑剔，所以我们将单引号和双引号（以及和号）
# 替换为它们的HTML编码等价物。这使它们在原始格式中看起来不太可读，但它们被很好地解析和渲染。
HTML_ESCAPE_TABLE = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;"
    }

# 这是繁重工作完成的地方。这循环遍历TSV数据框中的所有行，然后开始
# 连接一个大字符串（```md```），其中包含每种类型的markdown。它首先做YAML元数据，然后
# 做单个页面的描述。
def create_md(lines: list, layout: list):
    for item in lines:
        # 解析文件名信息
        md_filename = f"{item[layout.index('pub_date')]}-{item[layout.index('url_slug')]}.md"
        html_filename = str(item[layout.index('pub_date')]) + "-" + item[layout.index('url_slug')]
        
        # 解析YAML变量
        md = f"---\ntitle: \"{item[layout.index('title')]}\"\n"
        md += "collection: publications"
        if len(layout) == len(HEADER_UPDATED):
            md += f"\ncategory: {item[layout.index('category')]}"
        else:
            md += "\ncategory: manuscripts"
        md += f"\npermalink: /publication/{html_filename}"
        if len(str(item[layout.index('excerpt')])) > 5:
            md += f"\nexcerpt: '{html_escape(item[layout.index('excerpt')])}'"
        md += f"\ndate: {item[layout.index('pub_date')]}"
        md += f"\nvenue: '{html_escape(item[layout.index('venue')])}'"
        if len(str(item[layout.index('paper_url')])) > 5:
            md += f"\npaperurl: '{item[layout.index('paper_url')]}'"
        md += f"\ncitation: '{html_escape(item[layout.index('citation')])}'"
        md += "\n---"
        
        # 单个页面的Markdown描述
        if len(str(item[layout.index('paper_url')])) > 5:
            md += f"\n<a href='{item[layout.index('paper_url')}'>Download paper here</a>\n"
        if len(str(item[layout.index('excerpt')])) > 5:
            md += f"\n{html_escape(item[layout.index('excerpt')])}\n"
        md += f"\nRecommended citation: {item[layout.index('citation')]}"
        
        # 写入文件
        md_filename = os.path.join("../_publications/", os.path.basename(md_filename))
        with open(md_filename, 'w') as f:
            f.write(md)

def html_escape(text):
    """在文本中生成实体。"""
    return "".join(HTML_ESCAPE_TABLE.get(c,c) for c in text)

def read(filename: str) -> tuple[list, list]:
    '''读取文件的内容，检查标题并返回解析的行以及文件类型。'''

    # 读取文件的内容
    lines = []
    with open(filename, 'r') as file:
        delimiter = ',' if filename.endswith('.csv') else '\t'
        reader = csv.reader(file, delimiter=delimiter)
        for row in reader:
            lines.append(row)

    # 验证文件格式是否合理
    if len(lines) <= 1:
        print(f'文件中的行数不足以处理，找到 {len(lines)} 行', file=sys.stderr)
        sys.exit(EXIT_ERROR)

    # 验证标题，检查后删除
    layout = HEADER_UPDATED
    if HEADER_LEGACY == lines[0]:
        layout = HEADER_LEGACY
    elif HEADER_UPDATED != lines[0]:
        print(lines[0])
        print('文件的标题与预期格式不匹配', file=sys.stderr)
        sys.exit(EXIT_ERROR)
    lines = lines[1:]
    
    # 返回行和格式
    return lines, layout

if __name__ == '__main__':
    # 确保提供了文件名
    if len(sys.argv) != 2:
        print('用法：python3 publications.py [filename]', file=sys.stderr)
        sys.exit(EXIT_ERROR)

    # 确保文件名是TSV或CSV
    filename = sys.argv[1]
    if not (filename.endswith('.csv') or filename.endswith('.tsv')):
        print(f'期望TSV或CSV文件，得到 {filename}', file=sys.stderr)
        sys.exit(EXIT_ERROR)    

    # 读取并处理行
    lines, layout = read(filename)
    create_md(lines, layout)
