import os
import pandas as pd
import json

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

all_section_counter = load_json('./all_section_counter_original.json')

for i in range (46):
    all_section_counter.append(str(i)+ '_' + '0')
    
save_json('./all_section_counter_original.json', all_section_counter)