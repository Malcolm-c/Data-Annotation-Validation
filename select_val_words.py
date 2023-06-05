import csv 
import os
import json
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from random import shuffle
from scipy.linalg import norm

def save_json(save_path,data):
    assert save_path.split('.')[-1] == 'json'
    with open(save_path, 'w', encoding='utf-8') as file:
        json.dump(data,file)
    file.close()
 
def load_json(file_path):
    assert file_path.split('.')[-1] == 'json'
    with open(file_path,'r') as file:
        data = json.load(file)
    return data

all_titles = load_json('./preprocess/all_titles.json')

def read_test_file(username, filepath):
    test_annotation_res = {}
    test_words = {}
    for i, j, k in os.walk(filepath):
        for c, n in enumerate(k):
            story_title = n[0: len(n)-13]
            test_annotation_res[story_title] = []
            with open(filepath + n, 'r', encoding='utf8', newline='') as f:
                csv_reader = csv.reader(f)
                for row in csv_reader:
                    if row[0] != "section_id":
                        row_dict = {}
                        row_dict['section_id'] = row[0]
                        row_dict['word_id'] = row[1]
                        row_dict['concept'] = row[2]
                        row_dict['relation'] = row[3]
                        row_dict['obj'] = row[4]
                        row_dict['question'] = row[5]
                        row_dict['answer'] = row[6]
                        test_words[str(c) + '_' + row[0] + '_' + row[1]] = {"word": row[2], "sim": 0}
                        test_annotation_res[story_title].append(row_dict)
    return test_annotation_res, test_words

def tfidf_similarity(s1, s2):
    # 转化为TF矩阵
    cv = TfidfVectorizer(tokenizer=lambda s: s.split())
    corpus = [s1, s2]
    vectors = cv.fit_transform(corpus).toarray()
    # 计算TF系数
    return np.dot(vectors[0], vectors[1]) / (norm(vectors[0]) * norm(vectors[1]))

triples = load_json('./preprocess/triples.json')

def rank_top_words(test_annotation_res, test_words):
    key_list = list(test_words.keys())
    avg_sim = []
    for i in range (len(key_list)):
        avg_sim.append(0)
    for i in range (len(key_list) -1):
        for j in range(i + 1, len(key_list)):
            avg_sim[j] += tfidf_similarity(test_words[key_list[i]]["word"], test_words[key_list[j]]["word"])
            avg_sim[i] += tfidf_similarity(test_words[key_list[i]]["word"], test_words[key_list[j]]["word"])
            #print(test_words[key_list[i]]["word"], test_words[key_list[j]]["word"], avg_sim[j])
    #print(avg_sim)
    for i in range (len(key_list)):
        avg_sim[i] /= len(key_list) - 1
        test_words[key_list[i]]["sim"] = avg_sim[i]
    #print(test_words)
    sorted_words = sorted(test_words.items(), key=lambda d: d[1]['sim'], reverse = False)

    #Isabelles words are all unique, can be shuffled
    shuffle(sorted_words)
    word_list = []
    ann_words = load_json('./annalise-word-list.json')
    all_section_counter = []
    annotated_words = {}
    cnt = 0
    i = -1
    while cnt < 50:
        i += 1
        story_id = sorted_words[i][0].split('_')[0]
        section_id = sorted_words[i][0].split('_')[1]
        word_id = sorted_words[i][0].split('_')[2]
        word = sorted_words[i][1]["word"]
        if(word in word_list or len(triples[word.lower()]["triples"]) < 3 or word in ann_words):
            continue
        else:
            if story_id + '_' + section_id not in all_section_counter:
                all_section_counter.append(story_id + '_' + section_id)
            
            story_title = all_titles[int(story_id)]
            for row_dict in test_annotation_res[story_title]:
                if (row_dict["section_id"] == section_id) and (row_dict["word_id"] == word_id):
                    if (story_id + '_' + section_id not in annotated_words):
                        annotated_words[story_id + '_' + section_id] = []
                    annotated_words[story_id + '_' + section_id].append(row_dict)
            word_list.append(word)
            cnt += 1
    save_json("./isabelle-word-list.json", word_list)
    #save_json("./annalise-word-list.json", word_list)
    return all_section_counter, annotated_words

test_annotation_res, test_words = read_test_file("isabelle", './annotation data/isabelle/test/')

all_section_counter, annotated_words = rank_top_words(test_annotation_res, test_words)

save_json("./isabelle-all_section_counter.json", all_section_counter)
save_json("./isabelle-annotated_words.json", annotated_words)

