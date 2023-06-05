import csv 
import os
import json
import numpy as np

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

ann = load_json('./annalise-annotated_words.json')
isa = load_json('./isabelle-annotated_words.json')
triples = load_json('./preprocess/triples.json')
ann_words = []
for key in ann.keys():
    word_list = ann[key]
    for w_dict in word_list:
        word = w_dict['concept']
        if (word in ann_words):
            print(word + " already in ann")
        if len(triples[word.lower()]["triples"]) < 3:
            print(word + " has < 3 triples in ann")
        ann_words.append(word)

isa_words = []
for key in isa.keys():
    word_list = isa[key]
    for w_dict in word_list:
        word = w_dict['concept']
        if (word in isa_words):
            print(word + " already in isa")
        if (word in ann_words):
            print(word + " repeated in both")
        if len(triples[word.lower()]["triples"]) < 3:
            print(word + " has < 3 triples in isa")
        isa_words.append(word)


