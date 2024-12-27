#!/usr/bin/env python3  
#coding: utf-8

#基于训练好的词向量模型进行聚类
#聚类采用Kmeans算法
import math
import jieba
import numpy as np
from gensim.models import Word2Vec
from sklearn.cluster import KMeans
from collections import defaultdict

#输入模型文件路径
#加载训练好的模型
def load_word2vec_model(path):
    model = Word2Vec.load(path)
    return model

def load_sentence(path):
    sentences = set()
    with open(path, encoding="utf8") as f:
        for line in f:
            sentence = line.strip()
            sentences.add(" ".join(jieba.cut(sentence)))
    print("获取句子数量：", len(sentences))
    return sentences

#将文本向量化
def sentences_to_vectors(sentences, model):
    vectors = []
    for sentence in sentences:
        words = sentence.split()  #sentence是分好词的，空格分开
        vector = np.zeros(model.vector_size)
        #所有词的向量相加求平均，作为句子向量
        for word in words:
            try:
                vector += model.wv[word]
            except KeyError:
                #部分词在训练中未出现，用全0向量代替
                vector += np.zeros(model.vector_size)
        vectors.append(vector / len(words))
    return np.array(vectors)

def main():
    model = load_word2vec_model("model.w2v") #加载词向量模型
    sentences = load_sentence("titles.txt")  #加载所有标题
    vectors = sentences_to_vectors(sentences, model)   #将所有标题向量化

    n_clusters = int(math.sqrt(len(sentences)))  #指定聚类数量
    print("指定聚类数量：", n_clusters)
    kmeans = KMeans(n_clusters)  #定义一个kmeans计算类
    kmeans.fit(vectors)          #进行聚类计算

    sentence_label_dict = defaultdict(list)
    for sentence, label in zip(sentences, kmeans.labels_):  #取出句子和标签
        sentence_label_dict[label].append(sentence)         #同标签的放到一起

    # 计算类内平均距离并排序
    intra_cluster_distances = []
    for i in range(n_clusters):
        cluster_center = kmeans.cluster_centers_[i]
        cluster_vectors = vectors[kmeans.labels_ == i]
        intra_cluster_distance = np.mean([np.linalg.norm(v - cluster_center) for v in cluster_vectors])
        intra_cluster_distances.append((i, intra_cluster_distance))
    sorted_intra_cluster_distances = sorted(intra_cluster_distances, key=lambda x: x[1])

    # 打印排序后的聚类信息
    for label, distance in sorted_intra_cluster_distances:
        print(f"Cluster {label} has an average intra-cluster distance of {distance:.4f}")
        print("Sentences in cluster:")
        for i, sentence in enumerate(sentence_label_dict[label]):
            if i < 10:  # 打印每个聚类中的前10个句子
                print(f" {sentence.replace(' ', '')}")
            else:
                break
        print()  # 换行
        print("---------")

if __name__ == "__main__":
    main()

