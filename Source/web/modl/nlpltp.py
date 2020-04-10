# -*- coding: utf-8 -*-
import os
import time
from pyltp import SentenceSplitter
from pyltp import Segmentor
from pyltp import Postagger
#from pyltp import Parser
#from pyltp import SementicRoleLabeller
from pyltp import NamedEntityRecognizer
    
    
LTP_DATA_DIR = '../../data/ltp_model'  # ltp模型目录的路径
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词模型路径，模型名称为`cws.model`
print(cws_model_path)
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')  # 命名实体识别模型路径，模型名称为`ner.model`
#par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')  # 依存句法分析模型路径，模型名称为`parser.model`
#srl_model_path = os.path.join(LTP_DATA_DIR, 'pisrl_win.model')  # 语义角色标注模型
user_dict_seg = os.path.join(LTP_DATA_DIR, 'user_seg.txt')
user_dict_pos = os.path.join(LTP_DATA_DIR, 'user_pos.txt')

#省缩略词
PROVINCE_NAME = ['京', '沪', '津', '渝', '黑', '吉', '辽', '蒙','冀','新','甘','青','陕','宁','豫','晋','皖','鄂','湘','苏','川','黔','滇','桂','藏','浙','赣','粤','闽','台','琼','港','澳']
#NOUN_TYPE={'n':'一般名词','nh':'人名','ni':'机构名','ns':'地名','nt':'时间','ws':'外文名词'}
NOUN_LIST=['nh','ni','ns','ws','nt','nz']

class NlpLtp():
    def __init__(self):
        print('Load pyplt models...')
        start = time.time()
        self.segmentor = Segmentor()  # 初始化实例
        self.segmentor.load_with_lexicon(cws_model_path, user_dict_seg)  # 加载模型
        self.postagger=Postagger()
        self.postagger.load_with_lexicon(pos_model_path, user_dict_pos)
         
        #self.parser = Parser() # 初始化实例
        #self.parser.load(par_model_path)  # 加载模型
        #self.labeller = SementicRoleLabeller() # 初始化实例
        #self.labeller.load(srl_model_path)  # 加载模型
        self.recognizer = NamedEntityRecognizer() # 初始化实例
        self.recognizer.load(ner_model_path)
        self.nerdict = dict()
        elapsed = time.time() - start
        print('Load pyplt models finished in ', elapsed)
        
    # 释放模型
    def __del__(self):
        print('Release pyplt models...')
        self.segmentor.release()
        self.postagger.release()
        self.recognizer.release()
        #self.parser.release()
        #self.labeller.release()
        print('Release pyplt models finished.')
        
    def sentence(self, content):
        return SentenceSplitter.split(content)

    def segment(self, text):
        return self.segmentor.segment(text) 

    def postag(self, wordlist):
        return self.postagger.postag(wordlist)

    #def parse(self, wordlist, postags):
    #    return self.parser.parse(wordlist, postags)

    #def role_label(self, wordlist, postags, arcs):
    #    return self.labeller.label(wordlist, postags, arcs)
    def get_keywords(self, txt):
        words = pltobj.segment( txt )
        postags = pltobj.postag( words )
        ners = pltobj.ner( words, postags )
        keywords = list()
        for k, val in ners.items():
            keywords.append(k)
        return keywords
            
    def add_entity(self, word, tag):
        if word in self.nerdict:
            count = self.nerdict[word][1]
        else:
            count = 0
        self.nerdict[word] = [tag, count+1]

    #命名实体结果如下，ltp命名实体类型为：人名（Nh），地名（NS），机构名（Ni）；
    #ltp采用BIESO标注体系。
    #B表示实体开始词，I表示实体中间词，E表示实体结束词，S表示单独成实体，O表示不构成实体。
    def ner(self, wordlist, postags):
        ners = self.recognizer.recognize(wordlist, postags)
        for i in range(0,len(ners)):
            #print( wordlist[i], postags[i], ners[i] )
            if postags[i] in NOUN_LIST:
                word = wordlist[i].strip()
                if len(word)>1:
                    self.add_entity(word, postags[i])

            if ners[i]=='S-Ns' or ners[i]=='S-Nh' or ners[i]=='S-Ni':
                word = wordlist[i].strip()
                if len(word)>1 or word in PROVINCE_NAME: #实体名长度大于1，保存词性
                    self.add_entity(word, postags[i])
        return self.nerdict
    
    def clean_ner(self):
        self.nerdict = dict()

    def get_ner(self):
        return self.nerdict

pltobj = NlpLtp()

