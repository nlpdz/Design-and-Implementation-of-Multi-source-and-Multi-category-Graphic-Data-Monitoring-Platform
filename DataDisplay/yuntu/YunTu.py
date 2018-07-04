# -*- coding: UTF-8 -*-
from wordcloud import WordCloud
import jieba
import time
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from os import path

def wordcloudplot(txt):
    path = r'D:/vain/Special_thing_spider/wordcloud/hope.ttf'   # 字体文件地址
    alice_mask = np.array(Image.open('D:/vain/Special_thing_spider/wordcloud/broken.jpg'))  # 面具图片地址
    wordcloud = WordCloud(font_path=path,                              # 生成云图样式
                          background_color="white",                    # 背景颜色
                          margin=5, width=1800, height=800, mask=alice_mask, max_words=150, max_font_size=100,  # 词云最大词数，最大size等
                          random_state=42)
    wordcloud = wordcloud.generate(txt)     # 根据给定的文本生成词云
    wordcloud.to_file('D:/vain/Special_thing_spider/wordcloud/dora.png')  # 文件存储路径
    plt.ion()  # 交互操作模式打开,就可以用到后面的暂停关闭
    plt.imshow(wordcloud)
    plt.axis("off")  # 展示方式
    plt.show()  # 展示
    plt.pause(10)  # 暂停5s
    plt.close()  # 关闭当前显示的图像


def main():
    a = []
    d = path.dirname(__file__)
    text = open(path.join(d, 'data.txt'),encoding = 'UTF-8').read()  # 如果有问题，加上 encoding = 'UTF-8'
    #text = open(r'data.txt', 'r', encoding='utf-8').read()
    # print(f)
    words = list(jieba.cut(text))
    for word in words:
        if len(word) > 1:
            a.append(word)
    txt = r' '.join(a)
    print(txt)
    wordcloudplot(txt)


if __name__ == '__main__':
    main()





