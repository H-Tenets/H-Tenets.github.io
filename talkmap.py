# 演讲位置的Leaflet集群地图
#
# 从_talks/目录运行，该目录包含所有演讲的.md文件。此脚本从每个.md文件中提取location YAML字段，
# 使用geopy/Nominatim进行地理定位，并使用getorg库输出独立集群地图的数据、HTML和JavaScript。
# 这在功能上与#talkmap Jupyter notebook相同。
import frontmatter
import glob
import getorg
from geopy import Nominatim
from geopy.exc import GeocoderTimedOut

# 设置默认超时时间，单位为秒
TIMEOUT = 5

# 收集Markdown文件
g = glob.glob("_talks/*.md")

# 准备进行地理定位
geocoder = Nominatim(user_agent="academicpages.github.io")
location_dict = {}
location = ""
permalink = ""
title = ""

# 执行地理定位
for file in g:
    # 读取文件
    data = frontmatter.load(file)
    data = data.to_dict()

    # 如果位置不存在，继续处理
    if "location" not in data:
        continue

    # 准备描述
    title = data["title"].strip()
    venue = data["venue"].strip()
    location = data["location"].strip()
    description = f"{title}<br />{venue}; {location}"

    # 对位置进行地理编码并报告状态
    try:
        location_dict[description] = geocoder.geocode(location, timeout=TIMEOUT)
        print(description, location_dict[description])
    except ValueError as ex:
        print(f"错误：地理编码失败，输入为 {location}，错误信息：{ex}")
    except GeocoderTimedOut as ex:
        print(f"错误：地理编码超时，输入为 {location}，错误信息：{ex}")
    except Exception as ex:
        print(f"处理输入 {location} 时发生未处理的异常，错误信息：{ex}")

# 保存地图
m = getorg.orgmap.create_map_obj()
getorg.orgmap.output_html_cluster_map(
    location_dict, folder_name="talkmap", hashed_usernames=False
)
