# year2018
Annual report for programmers.

## 使用
### 基础
```bash
$ git clone https://github.com/baijiangliang/year2018.git
$ cd /path-to-year2018/
$ python3 main.py
```
注意：必须使用 Python3。Python3 已经发布十年了，试一下吧，它很棒。如果你的电脑上没有 Python3，你可以在 [Anaconda](https://www.anaconda.com/download/) 或者 [Python 官方网站](https://www.python.org/downloads/) 下载安装。推荐使用 Anaconda Python，它已经包含了此项目依赖的所有 Python 包。

### 高级
- 你可以修改 conf.py 里的 ignore_directories 来设定你想要忽略的目录。

## 依赖

### 必须
- [Pillow](https://pillow.readthedocs.io)
- [Matplotlib](https://matplotlib.org/)
- [NetworkX](https://networkx.github.io/)

你可以安装 Anaconda Python，或者使用命令 `$ pip3 install Pillow matplotlib networkx` 安装以上 Python 包。

### 可选
- [Ruby](https://www.ruby-lang.org)
- Ruby gems: [github-linguist](https://github.com/github/linguist)

## 示例
- ![report](static/examples/report.png)
- ![merge_stat](static/examples/5_merge_stat.png)

## TODO
- Support Chinese in NetworkX
- Beautify
- Portability
- Configurability
