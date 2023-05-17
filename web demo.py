from flask import Flask, redirect, render_template, request, jsonify
import random
import csv
import json
import os
from lemmatize import lemmatize

app = Flask(__name__, static_folder = './static')

def load_json(file_path):
    assert file_path.split('.')[-1] == 'json'
    with open(file_path,'r') as file:
        data = json.load(file)
    return data

def save_json(save_path,data):
    assert save_path.split('.')[-1] == 'json'
    with open(save_path, 'w', encoding='utf-8') as file:
        json.dump(data, file)
    file.close()

all_stories = load_json('./preprocess/all_stories.json')
all_titles = load_json('./preprocess/all_titles.json')
all_section_counter = load_json('./preprocess/all_section_counter.json')
triples = load_json('./preprocess/triples_1.json')

def pick_a_paragraph():
    rand_section = random.choice(all_section_counter)
    story_id = int(rand_section.split('_')[0])
    section_id = int(rand_section.split('_')[1])
    title = all_titles[story_id]
    return load_json('./preprocess/data_updated/' + title + '.json')[str(section_id)]

@app.route('/new_paragraph', methods=["GET"])
def get_paragraph():
    if request.method == 'GET':
        story_title = str(request.args.get('title'))
        story_id = str(request.args.get('s_id'))
        para_id = str(request.args.get('id'))
        username = str(request.args.get('username'))
        print(story_title, para_id)
        ###########!!!!!!!!##########
        u_dict = load_json('./user_data/' + username + '.json')
        if (u_dict['labeled_flag'] == 1):
            if story_title in all_titles:
                all_stories[story_title][int(para_id)-1]["label_time"] += 1
            #check if the story is completely labeled
                if all_stories[story_title][int(para_id)-1]["label_time"] > 2:
                    all_section_counter.remove(str(story_id) + '_' + str(para_id))
        
        #pick a new paragraph
        u_dict['para_dict'] = pick_a_paragraph()
        u_dict['labeled_flag'] = 0
        save_json('./user_data/' + username + '.json', u_dict)
        return json.dumps(u_dict['para_dict'])

@app.route('/')
def load():
    return render_template("index.html")

@app.route('/search', methods=["GET"])
def search_form():
    if request.method == 'GET':
        word = request.args.get('word')
        username = str(request.args.get('username'))
        u_dict = load_json('./user_data/' + username + '.json')
        u_dict['word'] = word.replace('"','').replace("'",'').replace('.','').replace(',','').lower()
        print("before:", u_dict['word'])
        #----lemmanization----#
        u_dict['word'] = lemmatize(u_dict['word'])
        print("after:", u_dict['word'])
        u_dict['retrieval'] = triples[u_dict['word']]
        save_json('./user_data/' + username + '.json', u_dict)
        return json.dumps(u_dict['retrieval'])

@app.route('/submit', methods=["GET"])
def submit_qa():
    if request.method == 'GET':
        question = str(request.args.get('question'))
        answer = str(request.args.get('answer'))
        concept = int(str(request.args.get('concept')))
        word_id = str(request.args.get('word_id'))
        title = str(request.args.get('title'))
        section = int(str(request.args.get('section')))
        username = str(request.args.get('username'))
        
        u_dict = load_json('./user_data/' + username + '.json')
        retireved_triplets = u_dict['retrieval']['triples']
        triple = retireved_triplets[concept]
        sub = triple[0]
        rel = triple[1]
        obj = triple[2]
        weight = triple[3]
        #header = ['section_id', 'concept(sub)', 'relation', 'obj', 'question', 'answer']
        ######remember to remove 'test'######
        if not os.path.isdir('./QA dataset'):
            os.makedirs("./QA dataset")
        if not os.path.isdir('./QA dataset/' + username):
            os.makedirs('./QA dataset/' + username)  
        if not os.path.isfile("./QA dataset/" + username + '/' + title + "-QAC_test.csv"):
            f =  open("./QA dataset/" + username + '/' + title + "-QAC_test.csv", 'w', encoding='utf8', newline='')
            f.close()
        with open("./QA dataset/" + username + '/' + title + "-QAC_test.csv", 'w', encoding='utf8', newline='') as f:
            writer = csv.writer(f)
            r = [section, word_id, sub, rel, obj, question, answer]
            writer.writerow(r)
        u_dict['labeled_flag'] = 1
        save_json('./user_data/' + username + '.json', u_dict)
        return "done"

@app.route('/init', methods=["GET"])
def init():
    if request.method == 'GET':
        username = str(request.args.get('username'))
        if not os.path.isdir('./user_data'):
            os.makedirs("./user_data")
        if not os.path.isfile('./user_data/' + username + '.json'):
            f = open('./user_data/' + username + '.json', 'w', encoding='utf8')
            f.close()
        with open('./user_data/' + username + '.json', 'w', encoding='utf8') as f:
            u_dict = {}
            u_dict['labeled_flag'] = 0
            u_dict['word'] = ''
            u_dict['retrieval'] = {}
            u_dict['para_dict'] = {}
            save_json('./user_data/' + username + '.json', u_dict)
        return "done"

if __name__ == '__main__':     
    app.run(debug = True, host = "0.0.0.0")