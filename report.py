# coding: utf8
import calendar
import csv
import os
from typing import List, Tuple, Any

import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
from PIL import Image, ImageFont, ImageDraw
from matplotlib import font_manager

import const
import util
from repository import Repos

file_dir = os.path.dirname(os.path.realpath(__file__))
font_file_normal = os.path.join(file_dir, 'static/SourceHanSansSC/SourceHanSansSC-Normal.otf')
font_file_regular = os.path.join(file_dir, 'static/SourceHanSansSC/SourceHanSansSC-Regular.otf')

# Set font family for matplotlib
font_name = 'Source Han Sans SC'
font_entry = font_manager.FontEntry(fname=font_file_normal, name=font_name)
font_manager.fontManager.ttflist.extend([font_entry])
matplotlib.rcParams['font.family'] = font_name

font_normal_18 = ImageFont.truetype(font_file_normal, size=18)
font_normal_20 = ImageFont.truetype(font_file_normal, size=20)
font_normal_26 = ImageFont.truetype(font_file_normal, size=26)
font_normal_28 = ImageFont.truetype(font_file_normal, size=28)
font_normal_30 = ImageFont.truetype(font_file_normal, size=30)
font_regular_30 = ImageFont.truetype(font_file_regular, size=30)
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
        self.output_dir = os.path.join(self.ctx.run_dir, 'output')
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)
        self.report_file = open(os.path.join(self.output_dir, 'report.csv'), 'w', encoding='utf8')
        self.report = csv.writer(self.report_file, lineterminator='\n')
        self.styles = (TextStyle('black', font_normal_26), TextStyle(colors[3], font_regular_36))
        self.styles1 = (TextStyle('black', font_normal_30), TextStyle('black', font_normal_30))

    def generate_report(self):
        self.write_stat()
        self.draw_cover()
        self.draw_short_summary()
        self.draw_most_common_repo()
        self.draw_language_stat()
        self.draw_merge_stat()
        self.draw_busiest_day()
        self.draw_latest_commit()
        self.draw_commit_distribution()
        self.draw_summary()

    def write_stat(self):
        email_name = util.get_name_from_email(self.ctx.emails[0])
        title = ['Annual programming report {0} of {1}'.format(self.ctx.year, email_name)]
        self.report.writerow(title)
        self.report.writerow('')

        self.report.writerow(['Summary'])
        summary = self.repos.get_commit_summary()
        names = ['projects', 'commits', 'merges', 'changes']
        for name in names[:3]:
            self.report.writerow([name, summary[name]])
        self.report.writerow([names[-1], summary['insert'] + summary['delete']])
        self.report.writerow('')

        self.report.writerow(['Coding stat by repo'])
        headers = ['name', 'language', 'commits', 'merges', 'insertions', 'deletions', 'changes']
        self.report.writerow(headers)
        for repo in self.repos.repos:
            repo_stat = repo.get_commit_summary()
            row = [
                repo.name, repo.language, repo_stat['commits'], repo_stat['merges'],
                repo_stat['insert'], repo_stat['delete'], repo_stat['insert'] + repo_stat['delete'],
            ]
            self.report.writerow(row)
        self.report.writerow('')

        self.report.writerow(['Coding stat by language'])
        lang_stat = self.repos.get_language_stat()
        headers = ['language', 'commits', 'insertions', 'deletions', 'changes']
        self.report.writerow(headers)
        sorted_lang = sorted(lang_stat.keys(), key=lambda x: lang_stat[x]['weight'], reverse=True)
        for lang in sorted_lang:
            stat = lang_stat[lang]
            row = [
                lang, stat['commits'], stat['insert'], stat['delete'],
                stat['insert'] + stat['delete'],
            ]
            self.report.writerow(row)
        self.report.writerow('')

        merge_stat = self.repos.get_merge_stat()
        self.report.writerow(['Merge stat by name'])
        headers = ['name', 'merge', 'merged_by', 'merges']
        self.report.writerow(headers)
        sorted_names = sorted(merge_stat,
                              key=lambda x: merge_stat[x]['merge'] + merge_stat[x]['merged_by'],
                              reverse=True)
        for name in sorted_names:
            stat = merge_stat[name]
            row = [
                name, stat['merge'], stat['merged_by'], stat['merge'] + stat['merged_by']
            ]
            self.report.writerow(row)
        self.report.writerow('')

        self.report_file.flush()

    def draw_cover(self):
        img = Image.new('RGBA', default_size, 'white')
        self.add_header(img)
        self.add_footer(img)
        calendar_graph = self.get_calendar_graph()
        pos_x, pos_y = (img.size[0] - calendar_graph.size[0]) // 2, 240
        img.paste(calendar_graph, (pos_x, pos_y))
        texts1 = ['你的编程秘密隐藏在上面这张日历图里']
        texts2 = ['答案即将揭晓']
        draw_center_with_y(img, 880, texts1, [], self.styles1)
        draw_center_with_y(img, 950, texts2, [], self.styles1)
        self.save_img(img, '1_cover', 'png')

    def draw_short_summary(self):
        img = Image.new('RGBA', default_size, 'white')
        self.add_header(img)
        self.add_footer(img)
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
        draw_center_with_y(img, 600, texts4, [], self.styles1)
        self.save_img(img, '2_short_summary', 'png')

    def draw_most_common_repo(self):
        img = Image.new('RGBA', default_size, 'white')
        self.add_header(img)
        self.add_footer(img)
        repo = self.repos.get_most_common_repo()
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
        draw_center_with_y(img, 240, texts1, bolds1, self.styles)
        draw_center_with_y(img, 300, texts2, bolds2, self.styles)
        draw_center_with_y(img, 360, texts3, bolds3, self.styles)
        draw_center_with_y(img, 600, texts4, [], self.styles1)
        draw_center_with_y(img, 670, texts5, [], self.styles1)
        self.save_img(img, '3_most_common_repo', 'png')

    def draw_language_stat(self):
        img = Image.new('RGBA', default_size, 'white')
        self.add_header(img)
        self.add_footer(img)
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
        percents = util.get_percents(weights)
        weighted = [(labels[i], percents[i]) for i in range(len(labels))]
        res = []
        other_percent = 0
        for item in weighted:
            if item[1] > 2:
                res.append(item)
            else:
                other_percent += item[1]
        if other_percent > 0:
            other_percent += 0.001
            res.append(('other', other_percent))
        labels, weights = [item[0] for item in res], [item[1] for item in res]
        plt.pie(weights, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.title('Programming languages by weight')
        fig_path = self.save_fig('language_pie', 'png')
        language_pie = Image.open(fig_path)
        img.paste(language_pie, (100, 360))
        language_cnt = len(list(p for p in percents if p > 5))
        if language_cnt == 1:
            text = '看来你是一个专一的程序员'
        else:
            text = '哪种语言是你的最爱呢'
        texts4 = [
            text
        ]
        draw_center_with_y(img, 840, texts4, [], self.styles1)
        self.save_img(img, '4_language_stat', 'png')

    def draw_merge_stat(self):
        img = Image.new('RGBA', default_size, 'white')
        self.add_header(img)
        self.add_footer(img)
        merges = self.repos.get_merge_stat()
        if not merges:
            print('Fail to generate merge stat!')
            return
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
        draw_center_with_y(img, 900, texts3, [], self.styles1)
        draw_center_with_y(img, 970, texts4, [], self.styles1)
        self.save_img(img, '5_merge_stat', 'png')

    def draw_busiest_day(self):
        img = Image.new('RGBA', default_size, 'white')
        self.add_header(img)
        self.add_footer(img)
        date, stat = self.repos.get_busiest_day()

        texts1 = [
            str(date.month),
            ' 月 ',
            str(date.day),
            ' 日是你过去一年写代码最多的一天'
        ]
        bolds1 = [0, 2]
        texts2 = [
            '这一天你一共提交了 ',
            str(len(stat['commits'])),
            ' 次更新'
        ]
        bolds2 = [1]
        texts3 = [
            '增加代码 ',
            str(stat['insert']),
            ' 行，删减代码 ',
            str(stat['delete']),
            ' 行'
        ]
        bolds3 = [1, 3]
        texts4 = [
            '同时，这也是你被 PM 打断次数最少的一天'
        ]
        draw_center_with_y(img, 240, texts1, bolds1, self.styles)
        draw_center_with_y(img, 300, texts2, bolds2, self.styles)
        draw_center_with_y(img, 360, texts3, bolds3, self.styles)
        draw_center_with_y(img, 600, texts4, [], self.styles1)
        self.save_img(img, '6_busiest_day', 'png')

    def draw_latest_commit(self):
        img = Image.new('RGBA', default_size, 'white')
        self.add_header(img)
        self.add_footer(img)
        commit = self.repos.get_latest_commit()
        date = util.timestamp_to_datetime(commit.timestamp)
        texts1 = [
            '还记得 ',
            str(date.month),
            ' 月 ',
            str(date.day),
            ' 日这天吗'
        ]
        bolds1 = [1, 3]
        texts2 = [
            '在这一天的 ',
            str(date.hour),
            ' 时 ',
            str(date.minute),
            ' 分，你执行了去年最晚的一次提交'
        ]
        bolds2 = [1, 3]
        draw_center_with_y(img, 240, texts1, bolds1, self.styles)
        draw_center_with_y(img, 300, texts2, bolds2, self.styles)
        commit_img = self.get_commit_img(commit)
        img.paste(commit_img, (60, 400))
        texts3 = [
            '再忙，也要照顾好自己'
        ]
        draw_center_with_y(img, 800, texts3, [], self.styles1)
        self.save_img(img, '7_latest_commit', 'png')

    def draw_commit_distribution(self):
        img = Image.new('RGBA', default_size, 'white')
        self.add_header(img)
        self.add_footer(img)
        stat = self.repos.get_commit_times_by_hour()
        most_hour = max(stat.keys(), key=lambda x: stat[x])
        most_percent = max(util.get_percents(list(stat.values()), digits=1))
        texts1 = [
            '你提交代码最多的时间段是 ',
            '{0}:00 - {1}:00'.format(most_hour, most_hour + 1),
        ]
        bolds1 = [1]
        texts2 = [
            '你在这个时间段提交代码的次数占总数的 ',
            str(most_percent) + '%',
        ]
        bolds2 = [1]
        draw_center_with_y(img, 240, texts1, bolds1, self.styles)
        draw_center_with_y(img, 300, texts2, bolds2, self.styles)
        hours = sorted(stat.keys())
        commits = [stat[hour] for hour in hours]
        plt.figure(1, figsize=(5, 3.5))
        plt.bar(hours, commits, width=0.6, color=colors[2], edgecolor='black')
        plt.title('Commit times by hour')
        plt.xticks(hours)
        plt.yticks(range(0, max(commits) + 10, 10))
        fig_path = self.save_fig('commit_bar', 'png')
        commit_bar = Image.open(fig_path)
        img.paste(commit_bar, (100, 400))
        self.save_img(img, '8_commit_distribution', 'png')

    def draw_summary(self):
        img = Image.new('RGBA', default_size, 'white')
        self.add_header(img)
        self.add_footer(img)
        summary = self.repos.get_commit_summary()
        texts1 = [
            '{0} 年你的码力(编码战斗力)为 '.format(self.ctx.year),
            str(summary.coding_power),
        ]
        bolds1 = [1]
        texts2 = [
            '击败了全球 ',
            '99%',
            ' 的程序员'
        ]
        bolds2 = [1]
        texts3 = [
            '{0}，请继续加油'.format(self.ctx.year + 1),
        ]
        draw_center_with_y(img, 240, texts1, bolds1, self.styles)
        draw_center_with_y(img, 300, texts2, bolds2, self.styles)
        draw_center_with_y(img, 600, texts3, [], self.styles1)
        self.save_img(img, '9_summary', 'png')

    def get_commit_img(self, commit):
        img = Image.new('RGBA', (600, 300), 'black')
        date = util.timestamp_to_datetime(commit.timestamp)
        line1 = 'commit ' + util.encrypt_string(commit.id, self.ctx.encrypt)
        line2 = 'Author: ' + commit.author + ' <' + commit.email + '>'
        line3 = 'Date:  ' + date.strftime('%a %b %d %H:%M:%S %Y %z')
        line4 = '    ' + util.encrypt_string(commit.subject, self.ctx.encrypt)
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), line1, fill='yellow', font=font_normal_20)
        draw.text((10, 40), line2, fill='white', font=font_normal_20)
        draw.text((10, 70), line3, fill='white', font=font_normal_20)
        draw.text((10, 120), line4, fill='white', font=font_normal_20)
        return img

    def add_header(self, img: Image):
        text = '{name} 的 {year} 年度编程报告'.format(name=self.ctx.name, year=self.ctx.year)
        draw = ImageDraw.Draw(img)
        text_w, text_h = draw.textsize(text, font=font_regular_32)
        pos_x, pos_y = (img.size[0] - text_w) // 2, 20
        draw.text((pos_x, pos_y), text, fill='black', font=font_regular_32)

    @staticmethod
    def add_footer(img: Image):
        text = const.REPO_URL
        draw = ImageDraw.Draw(img)
        text_w, text_h = draw.textsize(text, font_normal_18)
        pos_x, pos_y = default_size[0] - text_w - 20, default_size[1] - text_h - 20
        draw.text((pos_x, pos_y), text, fill='black', font=font_normal_18)

    def save_img(self, img: Image, name, fmt: str) -> str:
        full_name = name + '.' + fmt.lower()
        img_path = os.path.join(self.output_dir, full_name)
        img.save(img_path, fmt.upper())
        return img_path

    def save_fig(self, name, fmt: str) -> str:
        full_name = name + '.' + fmt.lower()
        fig_path = os.path.join(self.output_dir, full_name)
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
