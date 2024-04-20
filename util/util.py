import urllib.request
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import config


def extract_links(url):
    # 初始化配置
    headers = config.headers
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

        link_start_url = config.link_start_url  # 修改项 教务处网站对应的info开始地址

        # 提取链接的 href 属性值，并将其转换为完整链接存储在列表中
        extracted_links = [urljoin(link_start_url, link['href']) for link in links]
        return extracted_links
    else:
        print("未找到包含链接的 <ul> 标签")
        return []


def get_full_html(url):
    # 初始化配置
    headers = config.headers
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
    owner = config.owner  # 修改项
    start_view_url = 'https://dean.xjtu.edu.cn/system/resource/code/news/click/dynclicks.jsp?'  # 修改项
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
