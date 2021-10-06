# -*- coding: UTF-8 -*-

import re
import requests

from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz

post_text = input('查询内容：')
search_text = post_text[:27]
print('\n字数限制，将搜索文本：', search_text)


def search(keyword):
    url = 'http://www.baidu.com/s?wd=site%3A(tieba.baidu.com)%20'
    target = url + keyword + '&rn=20'
    print('搜索链接为：', target, end=' | ')
    search_html = requests.get(target).text
    soup = BeautifulSoup(search_html, features='html.parser')
    tag_list = soup.find_all(name='div', attrs={'class': 'result c-container new-pmd'})  # 找到所有搜索结果部分
    print('查找到%s条结果' % len(tag_list))
    return tag_list


def check_result(tag_list):
    post_list = []
    for tag in tag_list:
        text_match_list = re.findall(r'<em>(.+?)</em>', str(tag))  # 粗略匹配重合内容
        text_match = ''.join(text_match_list)
        print('搜索到 %s | （粗测）重复率：%.2f%%' % (text_match, len(text_match) / len(search_text) * 100), end=' | ')
        if (len(text_match) / len(search_text)) >= 0.5:  # 粗略筛选
            baidu_link = re.findall(r'href="(.+?)" target', str(tag))[0]  # 匹配链接内容
            long_link = requests.get(baidu_link).url
            if long_link.find('mo') is not -1:
                tid = re.findall(r'tid=(.+?)&pid', str(long_link))[0]
                short_link = 'https://tieba.baidu.com/p/' + tid
            else:
                short_link = long_link
            print(short_link)
            post_list.append(short_link)
        else:
            print('已忽略')
    post_list = list(set(post_list))
    print(post_list)
    return post_list


def check_fulltext(post_list):
    tag_list = []
    result_list = []
    for url in post_list:
        post_html = requests.get(url)
        soup = BeautifulSoup(post_html.text, features='html.parser')
        tag_list = soup.find_all(name='div', attrs={'class': 'd_post_content j_d_post_content clearfix'})  # 找到帖子正文部分
        print('从%s获取的结果：' % url, tag_list)
        statue = 0
        repetition = []
        for tag in tag_list:
            raw_text = re.findall(r' {12}(.+?)<', str(tag))
            if len(raw_text) is 0:
                print('寻找内容失败')
                continue
            print('检测 %s' % raw_text[0], end=' | ')
            repetition_rate = fuzz.ratio(post_text, raw_text[0])
            if repetition_rate < 50:
                print('无关内容')
                continue
            repetition.append(repetition_rate)
            print(repetition_rate, '%')
            statue = 1
        if statue == 1:
            title = re.findall(r'【(.+?)】', soup.title.text)[0]
            result_text = '【%s】 %s 帖子内重复率为%s' % (title, url, str(max(repetition))+'%')
            result_list.append(result_text)
    return result_list


def main():
    a = search(search_text)
    b = check_result(a)
    c = check_fulltext(b)
    print('查重报告')
    for i in c:
        print(i)


main()