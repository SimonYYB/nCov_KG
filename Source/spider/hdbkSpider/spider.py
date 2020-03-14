# -*- coding: utf-8 -*-
import requests
from os.path import basename, isdir
from os import mkdir
from bs4 import BeautifulSoup


class Spider:
    def __init__(self, word, list_polysemy_word=[],  **args):
        self.url = r'http://www.baike.com/wiki/'
        self.word = word
        self.content = {
            'nr': "",
            'information':{}
        }  # nr 基本介绍， information 基本信息
        self.list_polysemy_word = list_polysemy_word
        if args.get("headers", None):
            self.headers = args.get("headers")
        else:
            self.headers = {
                "User-Agent": "Mozilla/5.0(WindowsNT10.0;Win64;x64;rv:73.0)Gecko/20100101Firefox/73.0"
            }

    def run_spider(self):
        self.parse()

    def get_soup(self, url, word):
        try:
            rq = requests.get(url+word, headers=self.headers)
            rq.encoding = rq.apparent_encoding
            soup = BeautifulSoup(rq.text, "lxml")
            return soup
        except:
            return None

    def parse(self):
        soup = self.get_soup(self.url, self.word)

        if soup == None:
            return
        else:
            qy = soup.select("#polysemyAll>li")
            if qy:
                list_qy = [i.text for i in qy]
                soup = self.qy_parse(list_qy)

            for p in soup.select('#anchor>p'):
                self.content['nr'] = self.content.get('nr') + p.text

            for td_key, td_value in zip(soup.select('#datamodule td strong'), soup.select('#datamodule td span')):
                key = td_key.text[:len(td_key.text)-1]
                value = td_value.text
                self.content['information'][key] = value

    def qy_parse(self, list_qy):
        list_polysemy_word = self.list_polysemy_word  # 关键字匹配
        res = list_qy[0]
        for qy in list_qy:
            for word in list_polysemy_word:
                try:
                    qy.index(word)
                    res = qy
                except:
                    pass

        new_word = self.word+'['+res+']'

        return self.get_soup(self.url, new_word)

    def show_content(self):
        if self.content['nr'] == '':
            return ''
        ans = "实体名：" + self.word + "\n\n"+"内容："+self.content['nr']+"\n\n"
        for key, value in self.content['information'].items():
            ans = ans+key + "：" + value + "\n"
        return ans



class CtrlV:
    def __init__(self, word_filename, output_path="./"):
        self.word_filename = word_filename
        if not isdir(output_path):
            mkdir(output_path)
        self.output_path = output_path

    def get_list_word(self):
        with open(self.word_filename, "r", encoding="utf-8") as fp:
            return fp.read().split("\n")

    def ctrl_v(self):
        list_word = self.get_list_word()

        for word in list_word:
            spider = Spider(word, ['医学', '症状'])
            spider.run_spider()
            content = spider.show_content()

            if not spider.show_content():
                print("实体"+spider.word+"：没有爬取到内容")
                continue
            with open(self.output_path+'/'+word+".txt", 'w', encoding="utf-8") as fp:
                fp.write(content)
            print("实体"+spider.word+"：爬取成功")

    def run(self):
        self.ctrl_v()


if __name__ == '__main__':
    a = CtrlV("userdict.txt", "./select")
    a.run()

