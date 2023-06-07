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

#all_titles = load_json('./preprocess/all_titles.json')
#all_section_counter = load_json('./preprocess/all_section_counter.json')
#triples = load_json('./preprocess/triples.json')
#anntation_history = load_json('./preprocess/annotation_history.json')

#rewrite: filtered all_section_counter, and have annotated_words(dict) already, use '0_0' format to find values(list format)
def pick_a_paragraph(section_id_list, username):
    if (username == "isabelle"):
        all_section_counter = load_json('./preprocess/annalise-all_section_counter.json')
        remain_sections = list(set(all_section_counter)-set(section_id_list))
        all_titles = load_json('./preprocess/all_titles.json')
        if remain_sections == []:
            return 0
        else:
            annotated_words = load_json('./preprocess/annalise-annotated_words.json')
            rand_section = random.choice(remain_sections)
            story_id = int(rand_section.split('_')[0])
            story_title = all_titles[story_id]
            section_id = int(rand_section.split('_')[1])
            words_info = annotated_words[str(story_id) + '_' + str(section_id)]
            text = load_json('./preprocess/data/' + story_title + '.json')[str(section_id-1)]
            res = {}
            res['text'] = text
            res['annotated_words'] = words_info
            return res
    elif (username == 'annalise'):
        all_section_counter = load_json('./preprocess/isabelle-all_section_counter.json')
        remain_sections = list(set(all_section_counter)-set(section_id_list))
        all_titles = load_json('./preprocess/all_titles.json')
        if remain_sections == []:
            return 0
        else:
            annotated_words = load_json('./preprocess/isabelle-annotated_words.json')
            rand_section = random.choice(remain_sections)
            story_id = int(rand_section.split('_')[0])
            story_title = all_titles[story_id]
            section_id = int(rand_section.split('_')[1])
            words_info = annotated_words[str(story_id) + '_' + str(section_id)]
            text = load_json('./preprocess/data/' + story_title + '.json')[str(section_id-1)]
            res = {}
            res['text'] = text
            res['annotated_words'] = words_info
            return res
    else:
        all_section_counter = load_json('./preprocess/annalise-all_section_counter.json')
        remain_sections = list(set(all_section_counter)-set(section_id_list))
        all_titles = load_json('./preprocess/all_titles.json')
        if remain_sections == []:
            return 0
        else:
            annotated_words = load_json('./preprocess/annalise-annotated_words.json')
            rand_section = random.choice(remain_sections)
            story_id = int(rand_section.split('_')[0])
            story_title = all_titles[story_id]
            section_id = int(rand_section.split('_')[1])
            words_info = annotated_words[str(story_id) + '_' + str(section_id)]
            print(words_info)
            print(story_title)
            text = load_json('./preprocess/data/' + story_title + '.json')[str(section_id-1)]
            res = {}
            res['text'] = text
            res['annotated_words'] = words_info
            return res


@app.route('/new_paragraph', methods=["GET"])
def get_paragraph():
    if request.method == 'GET':
        story_title = str(request.args.get('title'))
        story_id = str(request.args.get('s_id'))
        para_id = str(request.args.get('id'))
        username = str(request.args.get('username')).lower()
        print(story_title, para_id)
        ###########!!!!!!!!##########
        u_dict = load_json('./user_data/' + username + '.json')
        anntation_history = load_json('./preprocess/annotation_history.json')
        all_titles = load_json('./preprocess/all_titles.json')
        if (u_dict['word_label_num'] > 0):
            return "Haven't finished!"
        #pick a new paragraph
        new_para_res = pick_a_paragraph(u_dict['section_id'], username)
        if new_para_res == 0:
            return "No more New Paragraphs"
        else:
            u_dict['word_label_num'] = len(new_para_res['annotated_words'])
            u_dict['para_dict'] = new_para_res
            save_json('./user_data/' + username + '.json', u_dict)
            save_json('./preprocess/annotation_history.json', anntation_history)
            return json.dumps(u_dict['para_dict'])

@app.route('/')
def load():
    return render_template("index.html")

@app.route('/search', methods=["GET"])
def search_form():
    if request.method == 'GET':
        word = request.args.get('word')
        username = str(request.args.get('username')).lower()
        u_dict = load_json('./user_data/' + username + '.json')
        triples = load_json('./preprocess/triples.json')
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
        question1 = str(request.args.get('question1'))
        answer1_for_question1 = str(request.args.get('answer1_for_question1'))
        answer2_for_question1 = str(request.args.get('answer2_for_question1'))
        question2 = str(request.args.get('question2'))
        answer_for_question2 = str(request.args.get('answer_for_question2'))
        c1 = str(request.args.get('c1'))
        c2 = str(request.args.get('c2'))
        c3 = str(request.args.get('c3'))
        r1 = str(request.args.get('r1'))
        r2 = str(request.args.get('r2'))
        r3 = str(request.args.get('r3'))
        o1 = str(request.args.get('o1'))
        o2 = str(request.args.get('o2'))
        o3 = str(request.args.get('o3'))
        word_id = str(request.args.get('word_id'))
        title = str(request.args.get('title'))
        section = int(str(request.args.get('section')))
        username = str(request.args.get('username')).lower()
        
        u_dict = load_json('./user_data/' + username + '.json')
        if not os.path.isdir('./QA validate'):
            os.makedirs("./QA validate")
        if not os.path.isdir('./QA validate/' + username):
            os.makedirs('./QA validate/' + username)  
        if not os.path.isfile("./QA validate/" + username + '/' + title + ".csv"):
            f =  open("./QA validate/" + username + '/' + title + ".csv", 'w', encoding='utf8', newline='')
            header = ['section_id', 'word_id', 'concept(sub)1', 'relation1', 'obj1', 'concept(sub)2', 'relation2', 'obj2', 'concept(sub)3', 'relation3', 'obj3', 'question1', 'answer1_for_question1', 'answer2_for_question1', 'question2', 'answer_for_question2']
            writer = csv.writer(f)
            writer.writerow(header)
            f.close()
        with open("./QA validate/" + username + '/' + title + ".csv", 'a', encoding='utf8', newline='') as f:
            writer = csv.writer(f)
            r = [section + 1, word_id, c1, r1, o1, c2, r2, o2, c3, r3, o3, question1, answer1_for_question1, answer2_for_question1, question2, answer_for_question2]
            writer.writerow(r)
        all_titles = load_json('./preprocess/all_titles.json')
        section_id = str(all_titles.index(title)) + '_' + str(section + 1)
        if (section_id not in u_dict['section_id']):
            u_dict['section_id'].append(section_id)
            u_dict['section_num'] += 1
        u_dict['word_label_num'] -= 1
        save_json('./user_data/' + username + '.json', u_dict)
        return "done"

@app.route('/init', methods=["GET"])
def init():
    if request.method == 'GET':
        username = str(request.args.get('username')).lower()
        if not os.path.isdir('./user_data'):
            os.makedirs("./user_data")
        if not os.path.isfile('./user_data/' + username + '.json'):
            f = open('./user_data/' + username + '.json', 'w', encoding='utf8')
            u_dict = {}
            u_dict['labeled_flag'] = 0
            u_dict['word'] = ''
            u_dict['retrieval'] = {}
            u_dict['para_dict'] = {}
            u_dict['section_id'] = []
            u_dict['word_label_num'] = 0
            u_dict['section_num'] = 0
            save_json('./user_data/' + username + '.json', u_dict)
        return "done"

if __name__ == '__main__':     
    app.run(debug = True, host = "0.0.0.0")