import re
import math
import numpy as np
import pandas as pd
from numpy import dot
from numpy.linalg import norm
from markupsafe import Markup

#import nltk
#from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
#from nltk.stem import PorterStemmer
#from nltk.stem import WordNetLemmatizer
#from nltk.corpus import wordnet
#from nltk.stem.snowball import SnowballStemmer
#from nltk.stem.lancaster import LancasterStemmer


    
def getDocuText(text, searchQuery):
        queryTerms = word_tokenize(str(searchQuery.strip()).strip())
        resultData = ""
        originalData = text
        for word in originalData:
            prunedWord = word.strip()
            if prunedWord in queryTerms:
                resultData = resultData + '<span style="background:yellow;">' + word + '</span> '
            else:
                resultData = resultData + word + ' '
        return resultData

def work(query):
    data = np.array(pd.read_csv('data.csv'))
    data = np.delete(data, 0, 1)
# print(data[:,15])
# 0 link
# 1 title
# 2 Giá
# 3 Diện tích
# 4 Quận/Huyện
# 5 Phường/Xã
# 6 Chiều dài
# 7 Chiều rộng
# 8 Hướng
# 9 Mặt tiền
# 10 Hẻm
# 11 Tầng
# 12 Giấy tờ
# 13 Phòng ngủ
# 14 Phòng tắm
# 15 Truy vấn
# truy van chinh xac
# for i in range(len(data)):
#     if dk 2 3 4 5 6 7 8 9 10 11 12 13 14:
#         data = np.delete(data, i, 0)
#         i-=1
    
    

    words = {}

    for i in range(len(data)):
        data[i][15] = re.split(' |; |, |\?|\*|\n|\(|\)|\. |\.|\'|\"|\“|\”|\:',(data[i][15]).replace('\xa0', ' ').lower())
        data[i][15] = list(filter(''.__ne__, data[i][15]))
        for x in data[i][15]:
            if x in words:
                words[x] = np.append(words[x], i)
            else:
                words[x] = np.array([i])
    # print(data[0])

    tf = np.array([[x.count(y) / len(x) for y in x] for x in data[:, 15]])
    idf = np.array([
        math.log10(float(len(data)) / float(len(set(x)))) + 1
        for x in words.values()
    ])
    exqs = re.split('\' |\" | \'| \"|\'|\"|\“|\”', query)
    exqs = [exqs[(i+1)*2-1] for i in range(int(query.count('"')/2))]
    # print(exqs)
    qs = re.split(' |; |, |\?|\*|\n|\(|\)|\. |\' |\" | \'| \"|\'|\"|\“|\”|\.|\:',
              query)
    # exqs = list(set(exqs).symmetric_difference(qs))
    # exqs = list(filter(''.__ne__, exqs))
    
    for i in range(len(exqs)):
        exqs[i] = re.split(' |; |, |\?|\*|\n|\(|\)|\. |\' |\" | \'| \"|\'|\"|\“|\”|\.|\:',exqs[i])
    
    qss = np.array(list(list(set(qs)) & words.keys()))
    out = []
    link = []
    score = []
    detail = []
    
    if qss.size:
        qtf = np.array([qs.count(y) / len(qs) for y in qss])

        qtfidf = np.array(
            [qtf[i] * idf[list(words).index(qss[i])] for i in range(len(qss))])

        qd = []
        for x in qss:
            qd.append(list(words[x]))
        qd = np.array(list(set(sum(qd, []))))

        qdtfidf = []
        for x in qd:
            qdtfidf.append([
                tf[x][(data[x][15]).index(qss[i])] if qss[i] in data[x][15] else 0 *
                idf[list(words).index(qss[i])] for i in range(len(qss))
            ])
        
        result = []
        for i in range(len(qd)):
            cos_sin = dot(qtfidf, qdtfidf[i]) / (norm(qtfidf) * norm(qdtfidf[i]))
            a = np.array(data[qd[i]][15])
            for j in range(len(exqs)):
                # print(set(exqs[j]).intersection(data[qd[i]][15]),exqs[j])
                # print( len(set(exqs[j]).intersection(data[qd[i]][15])) , len(exqs[j]))
                if len(set(exqs[j]).intersection(data[qd[i]][15])) == len(exqs[j]):
                    i_int = 0
                    b=[]
                    # print(qd[i])
                    for k in range(len(exqs[j])):
                        b.append(np.where(a==exqs[j][k])[0])
                
                    for k in range(len(b[0])):
                        for l in range(len(b)-1):
                            if b[0][k]+l+1 in b[l+1]:
                                i_int += 1
                    if i_int == len(exqs[j])-1:
                        cos_sin += 1
                    else:
                        cos_sin += 0.7
                else:
                    cos_sin += (len(set(exqs[j]).intersection(data[qd[i]][15]))/len(exqs[j]) ) * 0.5
            result.append((cos_sin, data[qd[i]][1], data[qd[i]][0], data[qd[i]][15]))
        
        result.sort(reverse=True)
        
        for i in range(len(result)):
            out.append(result[i][1]) 
            link.append(result[i][2])
            score.append(result[i][0])
            info = Markup(str(getDocuText(result[i][3], query)))
            #detail.append(result[i][3])
            detail.append(info)
        return out, link, score, detail