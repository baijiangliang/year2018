# coding: utf8
import os
from typing import Dict, List, Tuple, Any

import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
from PIL import Image, ImageFont, ImageDraw
from matplotlib import font_manager

import const
from repository import Repos
import util

file_dir = os.path.dirname(os.path.realpath(__file__))
font_file_normal = os.path.join(file_dir, 'static/SourceHanSansSC/SourceHanSansSC-Normal.otf')
font_file_medium = os.path.join(file_dir, 'static/SourceHanSansSC/SourceHanSansSC-Medium.otf')

# Set font family for matplotlib
font_name = 'Source Han Sans SC'
font_entry = font_manager.FontEntry(fname=font_file_normal, name=font_name)
font_manager.fontManager.ttflist.extend([font_entry])
matplotlib.rcParams['font.family'] = font_name

# TODO speed up?
font_normal_24 = ImageFont.truetype(font_file_normal, size=24)
font_medium_30 = ImageFont.truetype(font_file_medium, size=30)

default_size = (720, 1280)
default_colors = {
    0: '#ebedf0',
    1: '#c6e48b',
    2: '#7bc96f',
    3: '#239a3b',
    4: '#196127',
}


class Reporter:
    def __init__(self, ctx: util.DotDict):
        self.ctx = ctx
        self.repos = Repos(ctx)

    def draw_cover(self):
        img = Image.new('RGB', default_size, 'white')
        self.add_header(img)

    def add_header(self, img: Image):
        text = '{name} 的 {year} 年度编程报告'.format(name=self.ctx.name, year=self.ctx.year)
        draw = ImageDraw.Draw(img)
        pos = (get_center_align_x(img, text, font_medium_30)[0], 20)
        draw.text(pos, text, fill='black', font=font_medium_30)

    def get_commit_graph(self) -> Image:
        commits = self.repos.get_commit_weight_by_day()
        days = list(range(1, const.MAX_YEAR_DAY))
        if const.MAX_YEAR_DAY in commits:
            days.append(const.MAX_YEAR_DAY)
        col_size = 19
        row_size = const.MAX_YEAR_DAY // col_size + 1
        rect_size = 26
        gap_size = 4
        img_width = col_size * (rect_size + gap_size) - gap_size
        img_height = row_size * (rect_size + gap_size) - gap_size
        img = Image.new('RGB', (img_width, img_height), 'white')
        draw = ImageDraw.Draw(img)
        for i, day in enumerate(days):
            row = i // col_size
            col = i % col_size
            left = col * (rect_size + gap_size)
            up = row * (rect_size + gap_size)
            right = left + rect_size
            down = up + rect_size
            commit_level = get_commit_level(commits.get(day, 0))
            color = default_colors[commit_level]
            draw.rectangle([left, down, right, up], fill=color, outline=color)
        return img


def get_center_align_x(img: Image, text: str, font: Any) -> Tuple[int, int]:
    draw = ImageDraw.Draw(img)
    text_w, text_h = draw.textsize(text, font=font)
    return (img.size[0] - text_w) // 2, (img.size[1] - text_h) // 2


# def latest_commit(repos: Repos):
#     commit = repos.get_latest_commit()
#     commit_time = util.timestamp_to_datetime(commit.timestamp)
#     msg = '你最晚的一次提交发生在 {month} 月 {day} 日 {hour} 时 {minute} 分'.format(
#         month=commit_time.month, day=commit_time.day, hour=commit_time.hour,
#         minute=commit_time.minute)
#     print(msg)
#     pic = Image.new('RGB', default_size, 'white')
#     add_header(pic, repos.ctx)
#     pic_draw = ImageDraw.Draw(pic)
#     pic_draw.text((200, 50), msg, font=font_normal_24, fill='black')
#     os.chdir(repos.ctx.run_dir)
#     pic.save('output/latest.png', 'PNG')
#
#
# def commit_distribution(repos):
#     res = repos.get_commit_times_by_hour()
#     stat = sorted(res.items(), key=lambda x: x[0])
#     hours, commits = [x[0] for x in stat], [x[1] for x in stat]
#     plt.figure(1, figsize=(5, 3.5))
#     plt.bar(hours, commits, width=0.6, color='skyblue', edgecolor='black')
#     plt.title('Commit times by hour')
#     plt.xticks(hours)
#     plt.yticks(range(0, max(commits) + 10, 10))
#     # plt.show()
#     bar_pic_name = 'output/commit_by_hour.png'
#     plt.savefig(bar_pic_name, fmt='png')
#     bar_pic = Image.open(bar_pic_name)
#     pic = Image.new('RGB', default_size, 'white')
#     draw = ImageDraw.Draw(pic)
#     add_header(pic, repos.ctx)
#     pic.paste(bar_pic, (100, 300))
#     stat.sort(key=lambda x: x[1], reverse=True)
#     most_hour = stat[0][0]
#     text = '你最常提交代码的时间是 {begin}:00 - {end}:00'.format(begin=most_hour, end=most_hour + 1)
#     draw.text((200, 100), text, fill='black', font=font_normal_24)
#     pic.save('output/distribution.png', 'PNG')
#
#
# def add_header(img: Image, ctx: util.DotDict):
#     width, height = img.size
#     text = '{name} 的 {year} 年度编程报告'.format(name=ctx.name, year=ctx.year)
#     draw = ImageDraw.Draw(img)
#     text_w, text_h = draw.textsize(text, font=font_medium_30)
#     pos = ((width - text_w) // 2, 20)
#     draw.text(pos, text, fill='black', font=font_medium_30)
#
#
# def merge_relations(repos: Repos):
#     merges = repos.get_merge_stat()
#     # TODO
#     user_name = repos.ctx.emails[0].split('@')[0].split('.')[0]
#     edges = []
#     weights = []
#     for name, stat in merges.items():
#         weight = sum(stat.values())
#         weights.append(weight)
#         edges.append([user_name, name, weight])
#     edges.sort(key=lambda x: x[-1], reverse=True)
#     print(edges)
#     best_partner = edges[0][1]
#     weights = util.rescale_to_interval(weights, 0.5, 5)
#     for i, edge in enumerate(edges):
#         edge[-1] = weights[i]
#     graph = nx.Graph()
#     graph.add_weighted_edges_from(edges)
#     plt.figure(1, figsize=(5, 4))
#     nx.draw(graph, with_labels=True, width=weights, node_size=1000, node_color='lightskyblue',
#             edge_color='skyblue', font_size=10)
#     merge_pic_name = 'output/merges.png'
#     res = plt.savefig(merge_pic_name, fmt='png')
#     import pdb;
#     pdb.set_trace()
#     text1 = '{year} 年与你合作最多的小伙伴是 {name}'.format(year=repos.ctx.year, name=best_partner)
#     text2 = '你们互相 review 代码高达 {times} 次'.format(times=sum(merges[best_partner].values()))
#     merge_pic = Image.open(merge_pic_name)
#     pic = Image.new('RGB', default_size, 'white')
#     draw = ImageDraw.Draw(pic)
#     add_header(pic, repos.ctx)
#     pic.paste(merge_pic, (100, 300))
#     draw.text((100, 100), text1, fill='black', font=font_normal_24)
#     draw.text((100, 150), text2, fill='black', font=font_normal_24)
#
#     os.chdir(repos.ctx.run_dir)
#     pic.save('output/merge_relations.png', fmt='png')
#
#
# def lang_stat(repos: Repos):
#     res = repos.get_language_stat()
#     if not res:
#         return
#     favorite = max(res.keys(), key=lambda x: res[x]['weight'])
#     pic = Image.new('RGB', default_size, 'white')
#     pic_draw = ImageDraw.Draw(pic)
#     text1 = '你最常使用的编程语言是 {lang}'.format(lang=favorite)
#     text2 = '{year} 年你一共使用 {lang} 提交代码 {commit} 次，添加代码 {insert} 行，删减代码 {delete} 行。'.format(
#         year=repos.ctx.year, lang=favorite, commit=res[favorite]['commits'],
#         insert=res[favorite]['insert'], delete=res[favorite]['delete'])
#     pic_draw.text((120, 80), text1, font=font_normal_24, fill='black')
#     pic_draw.text((120, 100), text2, font=font_normal_24, fill='black')
#     os.chdir(repos.ctx.run_dir)
#     pic.save('output/lang_stat.png', 'PNG')


def get_commit_level(weight: int) -> int:
    if weight <= 0:
        return 0
    elif 0 < weight < 48:
        return 1
    elif 48 <= weight < 128:
        return 2
    elif 128 <= weight < 512:
        return 3
    else:
        return 4
