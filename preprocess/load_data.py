import os
import pandas as pd
import json
filepath = './test/'

def load_json(file_path):
    assert file_path.split('.')[-1] == 'json'
    with open(file_path,'r') as file:
        data = json.load(file)
    return data
def save_json(save_path,data):
    assert save_path.split('.')[-1] == 'json'
    with open(save_path, 'w', encoding='utf-8') as file:
        json.dump(data,file)
    file.close()
 

all_stories = load_json("./all_stories1.json")
all_titles = []
all_section_counter = []
for i, j, k in os.walk(filepath):
    for c, n in enumerate(k):
        if '-story.csv' in n:
            story_title = n[:len(n)-10]
            story = pd.read_csv(filepath + n)
            for index, row in story.iterrows():
                if index == 0:
                    p_dict = {}
                    paragraph = row["text"]
                    p_dict["id"] = index
                    p_dict["text"] = paragraph
                    p_dict["label_time"] = 0
                    all_stories[story_title].append(p_dict)

save_json('./all_stories1.json', all_stories)




