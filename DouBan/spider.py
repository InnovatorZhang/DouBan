import json
import os
from urllib.parse import urlencode
from config import *
import requests
from pyquery import PyQuery as pq


headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36'
}

def generate_index_url(tag,start,limit):
    data = {
        'type': 'movie',
        'tag': tag,
        'sort': 'recommend',
        'page_limit': limit,
        'page_start': start,
    }
    return START_URL + urlencode(data)

def generate_comment_url(movie_url,start,limit):
    data = {
        'start': start,
        'limit': limit,
        'sort': 'new_score',
        'status': 'P',
        'comment_only': 1
    }
    return movie_url + 'comments?' + urlencode(data)


def get_data(url):
    try:
        #ip被封的时候就换一个
        response = requests.get(url,headers=headers)
        # response = requests.get(url, headers=headers, proxies=get_proxy())
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError as e:
        print(e)

def get_proxy():
    return {
            'http':'socks5://127.0.0.1:1080',
            'https': 'socks5://127.0.0.1:1080',
        }

# 获取电影的地址
def parse_index(json_data):
    data = json.loads(json_data)
    if data and 'subjects' in data.keys():
        movies = data.get('subjects')
        for movie in movies:
            yield {
                "title": movie.get('title'),
                "rate": movie.get('rate'),
                "cover": movie.get('cover'),
                "url": movie.get('url'),
                "id": movie.get('id'),
                "is_new": movie.get('is_new'),
                "playable": movie.get('playable')
            }

def parse_comment(html):
    doc = pq(html)
    items = doc('#comments .comment-item').items()
    for item in items:
        yield {
            'avatar': item.find('.avatar a img').attr('src'),
            'comment': item.find('.comment p span').text(),
            'votes': item.find('.comment h3 .comment-vote .votes').text(),
            'rating': item.find('.comment h3 .comment-info .rating').attr('title'),
            'comment_time': item.find('.comment h3 .comment-info span.comment-time').attr('title')
        }

def save_comment(title,content):
    file_path = file_path = '{0}/movie_comment/'.format(os.getcwd())
    mkdir(file_path)
    file_name = file_path + title + '.txt'
    with open(file_name,'a',encoding='utf-8') as f:
        f.write(json.dumps(content,ensure_ascii=False) + '\n')


def mkdir(path):
    folder = os.path.exists(path)
    if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(path)  # makedirs 创建文件时如果路径不存在会创建这个路径


def main(start):
    try:
        url = generate_index_url(TAG,start,LIMIT)
        for item in parse_index(get_data(url)):
            url = item['url']
            title = item['title']
            print(item)
            for start in [i*20 for i in range(0,10)]:
                html = get_data(generate_comment_url(url,start,LIMIT))
                for item in parse_comment(html):
                    save_comment(title,item)
    except TypeError as e:
        print(e)


if __name__ == '__main__':
    for start in [i*20 for i in range(0,10)]:
        main(start)