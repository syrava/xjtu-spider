# -*- coding: utf-8 -*-
import urllib.request
from bs4 import BeautifulSoup
import pandas as pd
from openpyxl.workbook import Workbook
from openpyxl import load_workbook
from urllib.parse import urljoin

def main():
    flag1 = 30  # 初始化 flag1 为爬取页面的总页数-1
    name = "精品课程"  # 修改项
    use_suffix = False  # 是否在 start_url 中添加后缀的标志

    while flag1 > 25:
        # 构造链接
        begin_url = 'http://dean.xjtu.edu.cn/jxzy/jpkc'  # 修改项
        if use_suffix:
            start_url = begin_url + '/' + str(flag1) + '.htm'
        else:
            start_url = begin_url + '.htm'

        # 初始化 DataFrame
        df_all = pd.DataFrame(columns=['标题', '发布日期', '浏览次数', '正文内容'])

        # 访问起始页面并提取链接
        links_to_visit = extract_links(start_url)

        # 顺序访问链接并提取数据
        for link in links_to_visit:
            html = get_full_html(link)
            if html:
                title, release_date, view_count, body_text = extract_info(html, link)
                df_all = pd.concat([df_all, pd.DataFrame(
                    {'标题': [title], '发布日期': [release_date], '浏览次数': [view_count],
                     '正文内容': [body_text]})], ignore_index=True)

        # 读取已存在的 Excel 文件或新建一个
        try:
            wb = load_workbook(name + '.xlsx')
            ws = wb.active
            row_count = ws.max_row
        except FileNotFoundError:
            wb = Workbook()
            ws = wb.active
            row_count = 1

        # 将 DataFrame 中的数据逐行写入 Excel 文件中
        for index, row in df_all.iterrows():
            ws.cell(row=row_count + index, column=1, value=row['标题'])
            ws.cell(row=row_count + index, column=2, value=row['发布日期'])
            ws.cell(row=row_count + index, column=3, value=row['浏览次数'])
            ws.cell(row=row_count + index, column=4, value=row['正文内容'])

        # 保存 Excel 文件
        wb.save(name + '.xlsx')
        print("已保存" + str(flag1) + "页信息")

        # 更新 flag1 的值
        flag1 -= 1
        use_suffix = True  # 开始使用后缀

    print("所有信息已保存到" + name + ".xlsx 文件中。")


def extract_links(url):
    # 设置 User-Agent 头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0'
    }

    # 创建请求对象并发送请求
    request = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(request)

    # 读取响应内容
    html = response.read()

    # 使用 BeautifulSoup 解析页面内容
    soup = BeautifulSoup(html, 'html.parser')

    # 查找包含链接的 <ul> 标签
    ul_tag = soup.find('ul', class_='wow fadeInUp list')

    # 如果找到了 <ul> 标签
    if ul_tag:
        # 提取所有包含链接的 <a> 标签
        links = ul_tag.find_all('a', href=True)

        link_start_url = 'https://dean.xjtu.edu.cn/'  # 修改项 教务处网站对应的info开始地址

        # 提取链接的 href 属性值，并将其转换为完整链接存储在列表中
        extracted_links = [urljoin(link_start_url, link['href']) for link in links]
        return extracted_links
    else:
        print("未找到包含链接的 <ul> 标签")
        return []


def get_full_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0'
    }

    req = urllib.request.Request(url, headers=headers)
    try:
        response = urllib.request.urlopen(req)
        full_html = response.read()
        return full_html
    except Exception as e:
        print(f"发生异常: {e}")
        return None


def extract_info(html_content, link):
    # 创建 BeautifulSoup 对象
    soup = BeautifulSoup(html_content, 'html.parser')

    # 查找包含标题和信息的 div 标签
    title_div = soup.find('div', class_='art-tit cont-tit')

    # 查找包含正文的 div 标签
    body_div = soup.find('div', class_='v_news_content')

    # 初始化变量
    body_text = ""

    # 初始化变量
    title = "未找到标题"
    release_date = "未找到发布日期"

    # 提取标题
    if title_div:
        title = title_div.find('h3').get_text(strip=True)

    # 查找包含信息的 p 标签
    info_p = title_div.find('p')

    # 从 p 标签中提取发布日期
    if info_p:
        spans = info_p.find_all('span')
        release_date = spans[1].get_text(strip=True).split(":")[1].strip()

    # 获取浏览次数
    clickid = link.split('/')[-1].split('.')[0]  # XJTU网站info链接的最后一个数字
    owner = "1968706210"  # 修改项
    start_view_url='https://dean.xjtu.edu.cn/system/resource/code/news/click/dynclicks.jsp?' # 修改项
    view_url = f'{start_view_url}clickid={clickid}&owner={owner}&clicktype=wbnews'
    try:
        # 直接获取<body>标签内的文本，去除多余的空白字符
        view_count = get_full_html(view_url)
    except Exception as e:
        print(f"获取浏览次数失败: {e}")
        view_count = "未知"

    if body_div:
        paragraphs = body_div.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            body_text += text + "\n"  # 每段之间换行分隔

    body_text = body_text.strip()
    return title, release_date, view_count, body_text


if __name__ == "__main__":
    # 调用函数
    main()
    print("爬取完毕！")
