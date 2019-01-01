# coding: utf8
import os
from typing import Dict, List, Tuple, Any

import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
from PIL import Image, ImageFont, ImageDraw
from matplotlib import font_manager
import calendar

import const
from repository import Repos
import util

file_dir = os.path.dirname(os.path.realpath(__file__))
font_file_normal = os.path.join(file_dir, 'static/SourceHanSansSC/SourceHanSansSC-Normal.otf')
font_file_regular = os.path.join(file_dir, 'static/SourceHanSansSC/SourceHanSansSC-Regular.otf')

# Set font family for matplotlib
font_name = 'Source Han Sans SC'
font_entry = font_manager.FontEntry(fname=font_file_normal, name=font_name)
font_manager.fontManager.ttflist.extend([font_entry])
matplotlib.rcParams['font.family'] = font_name

font_normal_16 = ImageFont.truetype(font_file_normal, size=16)
font_normal_26 = ImageFont.truetype(font_file_normal, size=26)
font_normal_28 = ImageFont.truetype(font_file_normal, size=28)
font_normal_30 = ImageFont.truetype(font_file_normal, size=30)
font_regular_32 = ImageFont.truetype(font_file_regular, size=32)
font_regular_36 = ImageFont.truetype(font_file_regular, size=36)

default_size = (720, 1280)
colors = {
    0: '#ebedf0',
    1: '#c6e48b',
    2: '#7bc96f',
    3: '#239a3b',
    4: '#196127',
}


class TextStyle:
    def __init__(self, color: str, font: Any):
        self.color = color
        self.font = font


class Reporter:
    def __init__(self, ctx: util.DotDict):
        self.ctx = ctx
        self.repos = Repos(ctx)
        self.styles = (TextStyle('black', font_normal_26), TextStyle(colors[3], font_regular_36))

    def generate_report(self):
        self.draw_cover()
        self.draw_short_summary()
        self.draw_most_common_repo()
        self.draw_language_stat()
        self.draw_merge_stat()

    def draw_cover(self):
        img = Image.new('RGBA', default_size, 'white')
        self.add_header(img)
        add_footer(img)
        calendar_graph = self.get_calendar_graph()
        pos_x, pos_y = (img.size[0] - calendar_graph.size[0]) // 2, 260
        img.paste(calendar_graph, (pos_x, pos_y))
        texts1 = ['你的编程秘密隐藏在上面这张日历图里']
        texts2 = ['答案即将揭晓']
        draw_center_with_y(img, 880, texts1, [], self.styles)
        draw_center_with_y(img, 920, texts2, [], self.styles)
        self.save_img(img, '1_cover', 'png')

    def draw_short_summary(self):
        img = Image.new('RGBA', default_size, 'white')
        self.add_header(img)
        add_footer(img)
        summary = self.repos.get_commit_summary()
        texts1 = ['{0} 年你一共参与了 '.format(self.ctx.year), str(summary.projects), ' 个项目']
        bolds1 = [1]
        texts2 = ['提交更新 ', str(summary.commits), ' 次']
        bolds2 = [1]
        texts3 = ['修改代码 ', str(summary.insert + summary.delete), ' 行']
        bolds3 = [1]
        texts4 = ['看到这些数字，你是否充满了成就感呢']
        draw_center_with_y(img, 200, texts1, bolds1, self.styles)
        draw_center_with_y(img, 260, texts2, bolds2, self.styles)
        draw_center_with_y(img, 320, texts3, bolds3, self.styles)
        draw_center_with_y(img, 500, texts4, [], self.styles)
        self.save_img(img, '2_short_summary', 'png')

    def draw_most_common_repo(self):
        img = Image.new('RGBA', default_size, 'white')
        self.add_header(img)
        add_footer(img)
        repo = self.repos.get_most_common_repo()
        # TODO encrypt
        texts1 = [
            '{0} 年你最常去的地方是 '.format(self.ctx.year),
            repo.name,
        ]
        bolds1 = [1]
        summary = repo.get_commit_summary()
        texts2 = [
            '你在这个项目上进行了 ',
            str(summary.commits),
            ' 次提交，',
            str(summary.merges),
            ' 次合并']
        bolds2 = [1, 3]
        texts3 = [
            '共计修改了 ',
            str(summary.insert + summary.delete),
            ' 行代码'
        ]
        bolds3 = [1]
        texts4 = ['在这里，你挥洒了最多的汗水']
        texts5 = ['和泪水']
        draw_center_with_y(img, 200, texts1, bolds1, self.styles)
        draw_center_with_y(img, 260, texts2, bolds2, self.styles)
        draw_center_with_y(img, 320, texts3, bolds3, self.styles)
        draw_center_with_y(img, 500, texts4, [], self.styles)
        draw_center_with_y(img, 540, texts5, [], self.styles)
        self.save_img(img, '3_most_common_repo', 'png')

    def draw_language_stat(self):
        img = Image.new('RGBA', default_size, 'white')
        self.add_header(img)
        add_footer(img)
        lang_stat = self.repos.get_language_stat()
        favor = max(lang_stat.keys(), key=lambda x: lang_stat[x]['weight'])
        texts1 = [
            '{0} 年你最常用的编程语言是 '.format(self.ctx.year),
            favor,
        ]
        bolds1 = [1]
        texts2 = [
            '这一年你一共使用 ',
            favor,
            ' 提交代码 ',
            str(lang_stat[favor]['commits']),
            ' 次',
        ]
        bolds2 = [1, 3]
        texts3 = [
            '增加代码 ',
            str(lang_stat[favor]['insert']),
            ' 行，删减代码 ',
            str(lang_stat[favor]['delete']),
            ' 行'
        ]
        bolds3 = [1, 3]
        draw_center_with_y(img, 180, texts1, bolds1, self.styles)
        draw_center_with_y(img, 240, texts2, bolds2, self.styles)
        draw_center_with_y(img, 300, texts3, bolds3, self.styles)

        plt.figure(1, figsize=(5, 5))
        labels = list(lang_stat.keys())
        weights = [lang_stat[key]['weight'] for key in labels]
        plt.pie(weights, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.title('Programming languages by weight')
        fig_path = self.save_fig('language_pie', 'png')
        language_pie = Image.open(fig_path)
        img.paste(language_pie, (100, 360))
        percents = util.get_percents(weights)
        language_cnt = len(list(p for p in percents if p > 5))
        if language_cnt == 1:
            text = '看来你是一个专一的程序员'
        else:
            text = '哪种语言是你的最爱呢'
        texts4 = [
            text
        ]
        draw_center_with_y(img, 800, texts4, [], self.styles)
        self.save_img(img, '4_language_stat', 'png')

    def draw_merge_stat(self):
        img = Image.new('RGBA', default_size, 'white')
        self.add_header(img)
        add_footer(img)
        merges = self.repos.get_merge_stat()
        user_name = util.get_name_from_email(self.ctx.emails[0])
        edges = []
        weights = []
        for name, stat in merges.items():
            weight = stat.get('merge', 0) + stat.get('merged_by', 0)
            weights.append(weight)
            edges.append([user_name, name, weight])
        edges.sort(key=lambda x: x[-1], reverse=True)
        best_partner = edges[0][1]
        most_merge = merges[best_partner].get('merge', 0) + merges[best_partner].get('merged_by', 0)
        texts1 = [
            '{0} 年与你合作最多的小伙伴是 '.format(self.ctx.year),
            merges[best_partner]['readable_name'],
        ]
        bolds1 = [1]
        texts2 = [
            '你们互相 review 代码高达 ',
            str(most_merge),
            ' 次'
        ]
        bolds2 = [1]
        draw_center_with_y(img, 180, texts1, bolds1, self.styles)
        draw_center_with_y(img, 240, texts2, bolds2, self.styles)

        weights = util.rescale_to_interval(weights, 0.5, 5)
        for i, edge in enumerate(edges):
            edge[-1] = weights[i]
        graph = nx.Graph()
        graph.add_weighted_edges_from(edges)
        plt.figure(1, figsize=(6, 5))
        nx.draw(graph, with_labels=True, width=weights, node_size=1000, node_color=colors[1],
                edge_color=colors[2], font_size=10)
        fig_path = self.save_fig('merge_relations', 'png')
        merge_graph = Image.open(fig_path)
        img.paste(merge_graph, (100, 360))
        texts3 = [
            '过去一年与你有过交集的那些人'
        ]
        texts4 = [
            '他们现在在哪里呢'
        ]
        draw_center_with_y(img, 900, texts3, [], self.styles)
        draw_center_with_y(img, 940, texts4, [], self.styles)
        self.save_img(img, '5_merge_stat', 'png')

    def add_header(self, img: Image):
        text = '{name} 的 {year} 年度编程报告'.format(name=self.ctx.name, year=self.ctx.year)
        draw = ImageDraw.Draw(img)
        pos_x, pos_y = get_center_align(img, text, font_regular_32)[0], 20
        draw.text((pos_x, pos_y), text, fill='black', font=font_regular_32)

    def save_img(self, img: Image, name, fmt: str):
        output_dir = os.path.join(self.ctx.run_dir, 'output')
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        full_name = name + '.' + fmt.lower()
        img_path = os.path.join(output_dir, full_name)
        img.save(img_path, fmt.upper())

    def save_fig(self, name, fmt: str) -> str:
        output_dir = os.path.join(self.ctx.run_dir, 'output')
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        full_name = name + '.' + fmt.lower()
        fig_path = os.path.join(output_dir, full_name)
        plt.savefig(fig_path, fmt=fmt)
        plt.clf()
        return fig_path

    def get_background(self, img_name: str, transparency: float) -> Image:
        img_path = os.path.join(self.ctx.run_dir, 'static/images', img_name)
        img = Image.open(img_path)
        img_w, img_h = img.size
        # Cut and resize to default size
        cut_h = default_size[1] if img_h > default_size[1] else img_h
        cut_w = cut_h * default_size[0] // default_size[1]
        left, upper = (img_w - cut_w) // 2, (img_h - cut_h) // 2
        right, lower = left + cut_w, upper + cut_h
        img = img.crop((left, upper, right, lower))
        img = img.resize(default_size, resample=Image.ANTIALIAS)
        # Add transparency
        img = img.convert('RGBA')
        img_blender = Image.new('RGBA', img.size, (0, 0, 0, 0))
        img = Image.blend(img_blender, img, transparency)
        return img

    def get_calendar_graph(self) -> Image:
        commits = self.repos.get_commit_weight_by_day()
        days = list(range(1, const.MAX_YEAR_DAY))
        if calendar.isleap(self.ctx.year):
            days.append(const.MAX_YEAR_DAY)
        col_size = 19
        row_size = const.MAX_YEAR_DAY // col_size + 1
        rect_size = 26
        gap_size = 4
        img_width = col_size * (rect_size + gap_size) - gap_size
        img_height = row_size * (rect_size + gap_size) - gap_size
        img = Image.new('RGBA', (img_width, img_height), 'white')
        draw = ImageDraw.Draw(img)
        for i, day in enumerate(days):
            row, col = i // col_size, i % col_size
            left, upper = col * (rect_size + gap_size), row * (rect_size + gap_size)
            right, lower = left + rect_size, upper + rect_size
            commit_level = get_commit_level(commits.get(day, 0))
            color = colors[commit_level]
            draw.rectangle([left, lower, right, upper], fill=color, outline=color)
        return img


def get_center_align(img: Image, text: str, font: Any) -> Tuple[int, int]:
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

def draw_with_bold(img: Image, pos: Tuple[int, int], texts: List[str], bolds: List[int],
                   styles: Tuple[TextStyle, TextStyle]):
    draw = ImageDraw.Draw(img)
    _, normal_h = draw.textsize(texts[0], styles[0].font)
    _, bold_h = draw.textsize(texts[0], styles[1].font)
    pos_x, pos_y = pos
    bold_y = pos_y
    if bold_h > normal_h:
        bold_y = pos_y - (bold_h - normal_h) // 2 - 1
    for i, text in enumerate(texts):
        if i in bolds:
            draw.text((pos_x, bold_y), text, styles[1].color, styles[1].font)
            pos_x += draw.textsize(text, styles[1].font)[0]
        else:
            draw.text((pos_x, pos_y), text, styles[0].color, styles[0].font)
            pos_x += draw.textsize(text, styles[0].font)[0]


def draw_center_with_y(img: Image, pos_y: int, texts: List[str], bolds: List[int],
                       styles: Tuple[TextStyle, TextStyle]):
    draw = ImageDraw.Draw(img)
    total_w = 0
    for i, text in enumerate(texts):
        if i in bolds:
            total_w += draw.textsize(text, styles[1].font)[0]
        else:
            total_w += draw.textsize(text, styles[0].font)[0]
    pos_x = (img.size[0] - total_w) // 2
    draw_with_bold(img, (pos_x, pos_y), texts, bolds, styles)


def add_footer(img: Image):
    text = 'https://github.com/baijiangliang/year2018'
    draw = ImageDraw.Draw(img)
    text_w, text_h = draw.textsize(text, font_normal_16)
    pos_x, pos_y = default_size[0] - text_w - 20, default_size[1] - text_h - 20
    draw.text((pos_x, pos_y), text, fill='black', font=font_normal_16)


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
