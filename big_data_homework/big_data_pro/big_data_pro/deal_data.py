# -*- coding: utf-8 -*-
# @Author  : LouJingshuo
# @E-mail  : 3480339804@qq.com
# @Time    : 2023/11/18 20:31
# @Function: Infringement must be investigated, please indicate the source of reproduction!

import json
import settings
import matplotlib.pyplot as plt
import pandas as pd
from redis import StrictRedis
from wordcloud import WordCloud


def analyse_data():
    """借助pandas完成统计分析"""

    # 初始化数据库连接
    redis = StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
    # 初始化DataFrame
    key_list = [key.decode('utf-8') for key in redis.keys('*')]
    columns = ['名称', '评分', '作者', '标签', '评论']  # 书的属性作为列索引值
    df = pd.DataFrame(index=range(len(key_list)), columns=columns)

    # 将数据库的数据转移到DataFrame中
    for i in range(len(key_list)):
        book_info = [key_list[i]] + list(json.loads(redis.get(key_list[i])).values())[0]
        for j in range(5):
            if j == 1:
                if book_info[j] != '':
                    # import re
                    # score = re.findall(r"[-+]?\d*\.\d+|\d+", book_info[j])  #  通过这段程序,发现得到的数据中含有空字符串.
                    # print(score)
                    df[columns[j]][i] = float(book_info[j])  # 这里拿到的字符串比较特殊,类似于''3.6'',不能直接拿float转成浮点数.
                else:
                    df[columns[j]][i] = 0
                continue
            df[columns[j]][i] = book_info[j]

    # 给出分析结果
    df = df.loc[df['评分'] > 5]  # 筛选出评分高于5的书,生成新的DataFrame
    df.sort_values('评分', inplace=True, ascending=False)  # 降序排序
    df.index = range(df.shape[0])  # 更新索引

    df_score = df['评分']  # 切出只含有评分的DataFrame
    print('统计分析书评分结果: 最大值{} 最小值{} 均值{} 中位数{} 标准差{} 样本数{}\n'.format(
        df_score.max(), df_score.min(), df_score.mean(), df_score.median(), df_score.std(), df_score.count()
    ))

    for i in range(10):
        print('推荐书名:{}, 作者:{}, 评分:{}, 分类标签:{}\n一些书评:{}\n '.format(
            df.loc[i, '名称'], df.loc[i, '作者'], df.loc[i, '评分'], ', '.join(df.loc[i, '标签']), df.loc[i, '评论']
        ))

    return df


def visual_data(df):
    """借助matpoltlib完成数据可视化"""

    # 准备可视化数据
    score_list = []  # 数据一: 书评分
    label_list = []
    for i in range(5, 10):
        df_tmp = df.loc[(df['评分'] > i) & (df['评分'] <= i + 1)]
        book_num = df_tmp.shape[0]
        score_list.append(book_num)
        label_list.append(f'{i}.0-{i + 1}.0, 共{book_num}本')

    dic_tags = dict()  # 数据二: 书标签
    df_tags = df['标签']
    for tags_list in df_tags:
        for tag in tags_list:
            dic_tags[tag] = dic_tags.get(tag, 0) + 1

    # 新建画布
    plt.rcParams['font.sans-serif'] = 'SimHei'
    plt.rcParams['axes.unicode_minus'] = False
    p = plt.figure()

    p.add_subplot(1, 2, 1)  # 书评分展示
    plt.title('书评分占比饼状图')
    explode = [0.01 * i for i in range(1, 6)]
    plt.pie(score_list, labels=label_list, explode=explode)

    p.add_subplot(1, 2, 2)  # 书标签展示
    plt.title('书标签(字越大,这类书越多)')
    wc = WordCloud(font_path=r'others\Muyao.TTF', background_color='black', width=1080, height=900).fit_words(dic_tags)
    plt.imshow(wc)

    plt.show()


if __name__ == '__main__':
    visual_data(analyse_data())
