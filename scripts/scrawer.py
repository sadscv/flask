import requests
import json
from bs4 import BeautifulSoup
import pandas as pd
import urllib3
import time

# 忽略SSL警告（如有必要）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 创建Session对象
session = requests.Session()
session.verify = False  # 如遇SSL错误，可设置为False

# 设置请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
}

# 请求的URL
post_url = 'https://sepawa.com/congress/wp-admin/admin-ajax.php'

# 初始化数据列表
exhibitors_list = []

# 获取初始页面，提取 'security' 和 'query' 参数
initial_url = 'https://sepawa.com/congress/en/visitors/exhibitor-list/'
response = session.get(initial_url, headers=headers)
if response.status_code == 200:
    # 解析初始页面
    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup)

    # 提取 'security' 参数
    security_input = soup.find('input', {'id': 'divi_filter_security'})
    if security_input:
        security_value = security_input['value']
    else:
        print("未找到 'security' 参数")
        exit()

    # 提取 'query' 参数
    scripts = soup.find_all('script')
    query_value = None
    for script in scripts:
        if 'var divi_filter_default_query' in script.text:
            script_text = script.string
            start_index = script_text.find('var divi_filter_default_query =') + len('var divi_filter_default_query =')
            end_index = script_text.find(';', start_index)
            query_str = script_text[start_index:end_index].strip()
            query_value = query_str
            break
    if not query_value:
        print("未找到 'query' 参数")
        exit()
else:
    print("无法访问初始页面")
    exit()

# 构造POST请求的数据
data = {
    'action': 'divi_filter_loadmore_ajax_handler',
    'security': security_value,
    'query': query_value,
    'page': 1,
    'layoutid': '10263',
    'posttype': 'aussteller',
    'noresults': 'none',
    'sortorder': '{"company_name_clause":"ASC","booth_clause":"ASC"}',
    'sortasc': 'ASC',
    'gridstyle': 'grid',
    'columnscount': '1',
    'resultcount': 'off',
    'countposition': 'right',
    'postnumber': '50',
    'loadmoretext': 'Load More',
    'link_wholegrid': 'on',
    'link_wholegrid_external': 'off',
    'link_wholegrid_external_acf': 'none',
    'is_loadmore': 'on',
    'has_map': 'off',
    'map_all_posts': 'off',
    'map_selector': '',
    'marker_layout': 'none',
    'result_count_single_text': 'Showing the single result',
    'result_count_all_text': 'Showing all %d results',
    'result_count_pagination_text': 'Showing %d-%d of %d results',
}

# 开始分页请求
page = 1
while True:
    data['page'] = page
    print(f"正在请求第 {page} 页数据...")
    response = session.post(post_url, data=data, headers=headers)
    if response.status_code == 200:
        result = response.json()
        if not result.get('html'):
            print("没有更多数据了。")
            break
        html_content = result['html']

        # 解析返回的HTML内容
        soup = BeautifulSoup(html_content, 'html.parser')
        exhibitors = soup.find_all('div', class_='et_pb_ajax_pagination_post')
        for exhibitor in exhibitors:
            # 提取公司名称和介绍
            name_tag = exhibitor.find('h2', class_='entry-title')
            description_tag = exhibitor.find('div', class_='post-content')

            name = name_tag.get_text(strip=True) if name_tag else "N/A"
            description = description_tag.get_text(strip=True) if description_tag else "N/A"

            exhibitors_list.append({
                'Company Name': name,
                'Description': description
            })
        page += 1
        time.sleep(1)  # 延时1秒，避免请求过于频繁
    else:
        print(f"请求失败，状态码：{response.status_code}")
        break

# 将数据保存到Excel文件
df = pd.DataFrame(exhibitors_list)
print(df)
df.to_excel('Exhibitors_List.xlsx', index=False)
print("数据已成功保存到 Exhibitors_List.xlsx")




