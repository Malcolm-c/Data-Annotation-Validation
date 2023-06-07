var raw_data = [];
var stopwords = [];

var data = [];
var init_state = 0;
var init_submit = 0;
var init_line = 0;
var switch_para = 0;
var marked_id = "";
var marked_word = "";
var marked_concept = "";
var prev_marked_concept = "";
var img = '<img src="../static/images/arrow_icon.png" width="20px" height="20px" hspace = 5px/>';
var word_list = [];
var annotated_words = [];
var knowledge_list = [];
var selected_triple = [];
var id = 0;
var title = "";
var s_id = "";
var story_num = 0;
var username = "";
var sub_time = 0;
var selected_index = 0;
var triple_flag = 0;
var q2 = "";    //first written qestion in validation
var a2 = "";    //first written answer in validation
var label_num = 0;   //number of annotated words
var rank_num = 0;   //number of ranked triples
var ranked_triple = []; //list of ranked top3 triples
var ranked_triple_id = []   //list of ranked top3 triples' id

function ShowLogin(){
    LoginBox.style.display = 'block';
    example_space.style.visibility="hidden";
    AnnotationSpace.style.visibility="hidden";
}

function Login(){
    username = InputUsername.value;
    username = username.toLowerCase();
    if(username == ""){
        alert("User name cannot be empty.");
    }
    else{
        LoginBox.style.display = "none";
        $.ajax({
            type: "GET",
            url: "/init",
            data: {
                'username': username.toLowerCase()
            },
            dataType: "text",
            success: function (result) {
                console.log("Got Username!");
                example_space.style.visibility="visible";
                AnnotationSpace.style.visibility="visible";
                get_paragraph();
            }
        })
    }
}

function update_color(c) {
    if (c == "pos") {
        return "deepskyblue";
    } else if (c == "neg") {
        return "indianred";
    }
}

function update_color_light(c) {
    if (c == "pos") {
        return "#c2ecff";
    } else if (c == "neg") {
        return "transparent";
    }
}

function get_paragraph(){
    $.ajax({
        type: "GET",
        url: "/new_paragraph",
        data: {
            "id": id,
            "title": title,
            "s_id": s_id,
            "username": username.toLowerCase()
        },
        dataType: "text",
        success: function (result) {
            if(result == "Haven't finished!"){
                alert(result);
                return;
            }
            if (result == "No more New Paragraphs"){
                alert("Annotation Finished！");
                clear_content();
                return;
            }
            res = JSON.parse(result);
            text = res['text'];
            annotated_words = res['annotated_words']
            console.log(annotated_words);
            title = text["title"];
            s_id = text["s_id"];
            id = text["id"];
            raw_data = text['words'];
            switch_para = 1;
            StoryTitle.innerHTML = title.replaceAll('-', ' ');
            marked_id = "";
            render_original();
            highlight_word();
            clear_content();
            switch_para = 0;
            story_num += 1;
            word_list[story_num] = "";
            console.log("new paragraph added");
            label_num = 0;
        }
    })
}

function render_original() {
    data = [];
    console.log(raw_data); 
    data = raw_data;
    //console.log(data); 
    let paragraph = document.createElement("div");
    paragraph.className = "paragraph";
    paragraph.innerHTML = "";
    data.forEach(function (e) {
        paragraph.innerHTML += `
            <div id="s${e.id}" class="sentence_no_choose">
                ${e.word}
            </div>`
    })
    console.log("new paragraph")
    if(text_space.childNodes.length==0){
        text_space.appendChild(paragraph);
    }
    else{
        text_space.replaceChild(paragraph, text_space.childNodes[0]);
    }
    if(init_line == 0){
        init_line = 1;
    }
    SelectWordInst.style.display = "block";
    SelectWordInst.innerHTML = "<p>Please click on the <p4>purple highlighted words</p4> <b>one by one</b> and select a triple for each of them.</p>"
    SelectWordInst.innerHTML += "<br><br><br><p3>*This annotation task is to create QA pairs beneficial for children's education, with the help of external knowledge from ConceptNet.</p3>"
}

function highlight_word(){
    for(let i = 0; i < annotated_words.length; i++){
        console.log(annotated_words[i].word_id);
        document.getElementById(`s${annotated_words[i].word_id}`).className = "sentence";
        document.getElementById(`s${annotated_words[i].word_id}`).setAttribute("onclick", `update_select(${i}, annotated_words[${i}].word_id, 'pos')`);
        document.getElementById(`s${annotated_words[i].word_id}`).style.background = "#a9a7ff";
    }
}

function update_select(i, d, c) {
    selected_index = i;
    if(init_submit == 1){
        init_state = 0;
    }
    if(data[Number(d)]['marked'] == 1){
        return;
    }
    let selected = document.getElementById("s" + d);
    selected.style.background = "#ffa5a5";
    if (c == 'pos') {
        console.log(marked_id, d);
        if(marked_id != ""){
            /*marked new word*/
            if (data[Number(marked_id)]['marked'] == 0){
                /*marked new word*/
                if(marked_id != d){
                    /*Restore the original background color*/ 
                    document.getElementById("s" + marked_id).style.background = "#a9a7ff";
                }/*update new bg color*/
                else{
                    selected.style.background = "#ffa5a5";
                }
            }/*marked old word*/
            else{
                document.getElementById("s" + marked_id).style.background = "#a9a7ff";
                if (marked_id == d){
                    marked_word = data[Number(d)].word;
                    marked_id = d;
                    return;
                }
            }
        }
        marked_word = data[Number(d)].word;
        add_concept(marked_word);
        marked_id = d;
    }
}

function add_concept(w) {
    $.ajax({
        type: "GET",
        url: "/search",
        data: {
            "word": JSON.stringify(w),
            "username": username.toLowerCase()
        },
        dataType: "text",
        success: function (result) {
            document.getElementById("submit").style.display = "block";
            write_meaning(result, w);
        }
    })
}

function show_qa() {
    SelectTripleInst.style.display = "none";
    pair.style.display = "block";
    submit.style.display = "block";
    CreateQAInst.style.display = "block";

    var c = annotated_words[selected_index].concept;
    var r = annotated_words[selected_index].relation;
    var o = annotated_words[selected_index].obj;
    console.log("!!!!!",c,r,o,knowledge_list);
    for(i = 0; i < knowledge_list.length; i++){
        entity = knowledge_list[i];
        if (entity[0] != c){
            continue;
        }
        if (entity[1] != r){
            continue;
        }
        if (entity[2] == o){
            selected_triple = entity;
            break;
        }
    }
    document.getElementById(`tr_${i}`).style.backgroundColor = "#a9a7ff";

    //CreateQAInst.innerHTML = `Now you need to create a Question and Answer for the story based on <p1>the word</p1> <p2>"${marked_word}"</p2> and its <p3>Meaning in Wiktionary</p3> and <p4>the ConceptNet Triple</p4> <p5>you choose</p5>.`
    CreateQAInst.innerHTML = `<p><b>Your co-worker selected this triple below:</b></p>`;
    CreateQAInst.innerHTML += `<table><tr id="tr_selected"><td width="30px"><input type="radio" id="radio_0" name="TripleSelected" value="tr_0"></td><td width="100px"><p1 style="background-color: #FFA5A5">${selected_triple[0]}</p1></td><td width="300px">${selected_triple[1]}</td><td width="300px">${selected_triple[2].replaceAll("_", " ")}</td></tr></table>`
    CreateQAInst.innerHTML +=`<p>Now please create a Question and Answer based on <p1>the word</p1> <p2>"${marked_word}"</p2> with this <p8>triple</p8>.</p> 
    <p6>· You can use its <p3>meaning in Wiktionary</p3>.</p6><br>
    <p6>· Preferrably including <p2>"${marked_word}"</p2> and its <p5>relationship</p5> in the question that can be answered by the <p4>related concept</p4>.</p6><br>
    <p6>· The QA-pair should be beneficial for children's education.</p6>`
    document.getElementById("tr_selected").style.backgroundColor = "#a9a7ff"

    document.getElementById("question").value = "";
    document.getElementById("answer").value = "";
    var qa_div = document.getElementById("QA");
    qa_div.style.display = "block";
    document.getElementById("submit")._tippy.show();
    document.styleSheets[0].insertRule(
        `@keyframes slide-down{
            0%{transform:translateY(100%);}
            100%{transform:translateY(0px);}
          }`
    )
    qa_div.style.animation = "slide-down 0.3s ease-in-out"
    document.getElementById("question").style.color = "black";
}

function write_meaning(data, word) {
    SelectWordInst.style.display = "none";
    CreateQAInst.style.display = "none";
    QA.style.display = "none";
    concept_space.style.display = "block";
    SelectTripleInst.style.display = "block";
    res = JSON.parse(data);
    meaning = res["meaning"].substring(res["triples"][0][0].length + 1).split(";");
    tab_space = "&nbsp;&nbsp;&nbsp;&nbsp;";
    meaning_str = res["triples"][0][0] + ": <br>" + tab_space;
    
    for(let i = 0; i < meaning.length; i++){
        if(i != 0){
            meaning_str += ';<br>' + tab_space;
        }
        meaning_str += meaning[i];
    }

    knowledge_list = res["triples"];
    console.log(typeof(knowledge_list), knowledge_list);
    if(typeof(meaning) == "undefined" || meaning == '' || knowledge_list.length == 0){
        console.log("no knowledge");
        clear_content();
        NoKnowledge.style.display = "block";
        NoKnowledge.innerHTML = "<p1>Please choose a more common word!</p1>";
        SelectTripleInst.style.display = "none";
        return;
    }
    NoKnowledge.style.display = "none";
    //var t_string = '<table onclick="show_qa()">';
    var t_string = '<table>';
    t_string += '<tr><td class="table_content" width="30px"></td><td class="table_content" width="100px">Concept</td><td class="table_rel">Relationship</td><td class="table_relcon">Related concept</td></tr>';
    console.log(knowledge_list.length);
    for (let i = 0; i < knowledge_list.length; i++) {
        entity = knowledge_list[i];
        var text = "";
        t_string += `<tr id="tr_${i}" onclick="get_row('tr_${i}')"><td width="30px"><i id="radio_${i}" class="fa-sharp fa-regular fa-square"></i></td>`;
        for (let j = 0; j < entity.length-1; j++) {
            if(j != 0){
                t_string += '<td width="300px">' + entity[j].replaceAll("_", " ") + '</td>'
            }
            else{
                t_string += '<td width="100px"><p1 style="background-color: #FFA5A5">' + entity[j] + '</p1></td>'
            }
            text += entity[j].toString() + ' ';
            /*if(j == 2){
                t_string += '<td width="300px">' + `related concept ${i+1}` + '</td>'
            }
            else if (j == 0){
                t_string += '<td width="100px"><p1 style="background-color: #FFA5A5">' + `concept ${i+1}` + '</p1></td>'
            }
            else{
                t_string += '<td width="100px">' + `relation ${i+1}` + '</td>'
            }
            text += entity[j].toString() + ' ';*/
        }
        t_string += '</tr>';
    }
    t_string += '</table>'
    
    AboveMeaning.innerHTML = "<p id='MeaningIns'>Meaning of '" + word + "' in Wiktionary:</p>";
    ShowMeaning.innerHTML = meaning_str;
    AboveTriples.innerHTML = "<p id='TripleIns'>Matching triples of '" + word + "' in ConceptNet:</p>";
    ShowTriples.innerHTML = t_string;
    SelectTripleInst.innerHTML = `<p>Please click on the boxes to<br>rank <b>TOP 3</b> <br><p1>triples of<p3>"${marked_word}"</p3> in ConceptNet</p1> that:</p><br><p2>1. provides external knowledge outside the story</p2><br><p2>2. is beneficial for children's education.</p2>`
}

function get_row(row_id){
    var r_index = ranked_triple_id.indexOf(Number(row_id.substring(3)));
    if (r_index != -1){
        ranked_triple_id.splice(r_index, 1);
        document.getElementById(row_id).style.backgroundColor = "white";
        document.getElementById('radio' + row_id.substring(2)).className = "fa-sharp fa-regular fa-square";
        for(let i = 0; i < ranked_triple_id.length; i++){
            document.getElementById('radio_' + ranked_triple_id[i].toString()).className = `fa-solid fa-${i+1}`;
        }
        rank_num --;
    }
    else{
        if(rank_num == 0){
            document.getElementById('radio' + row_id.substring(2)).className = "fa-solid fa-1";
            var dic = {concept: knowledge_list[Number(row_id.substring(3))][0], 
                relation: knowledge_list[Number(row_id.substring(3))][1],
                obj: knowledge_list[Number(row_id.substring(3))][2]};
            console.log("dict:", dic);
            ranked_triple.push(dic);
            ranked_triple_id.push(Number(row_id.substring(3)));
        }
        else if(rank_num == 1){
            document.getElementById('radio' + row_id.substring(2)).className = "fa-solid fa-2";
            var dic = {concept: knowledge_list[Number(row_id.substring(3))][0], 
                relation: knowledge_list[Number(row_id.substring(3))][1],
                obj: knowledge_list[Number(row_id.substring(3))][2]};
            ranked_triple.push(dic);
            ranked_triple_id.push(Number(row_id.substring(3)));
        }
        else if(rank_num == 2){
            document.getElementById('radio' + row_id.substring(2)).className = "fa-solid fa-3";
            var dic = {concept: knowledge_list[Number(row_id.substring(3))][0], 
                relation: knowledge_list[Number(row_id.substring(3))][1],
                obj: knowledge_list[Number(row_id.substring(3))][2]};
            ranked_triple.push(dic);
            ranked_triple_id.push(Number(row_id.substring(3)));
        }
        rank_num++;
        document.getElementById('radio' + row_id.substring(2)).checked = true;
        console.log("rank num:", rank_num);
        if (rank_num <= 3)
        {
            document.getElementById(row_id).style.backgroundColor = "#FFE49D";
        }
    }
    if (rank_num == 3){
        show_qa();
    }
    marked_concept = row_id.slice(3);
}

function sub() {
    var q = document.getElementById("question").value;
    var a = document.getElementById("answer").value;
    //var c = marked_concept;
    var c = marked_concept.toString();
    if(marked_id == ""){
        alert("You haven't chose a word!");
        return;
    }
    else if (marked_concept == ""){
        alert("You haven't chose a concept!");
        return;
    }
    if(q.length == 0){
        //alert("You haven't enter your question!");
        document.getElementById("question")._tippy.show();
    }
    if(a.length == 0){
        //alert("You haven't enter your answer!");
        document.getElementById("answer")._tippy.show();
    }
    if(q.length == 0 || a.length == 0){
        return;
    }
    console.log(init_state, q, a, c);
    show_submit = 0;
    if (sub_time == 0){
        sub_time ++;
        q2 = q;
        a2 = a;
        CreateQAInst.innerHTML = `<p><b>Your co-worker wrote the <p7>question</p7> below about this triple.</b></p>
        <table><tr id="tr_selected"><td width="30px"><input type="radio" id="radio_0" name="TripleSelected" value="tr_0"></td><td width="100px"><p1 style="background-color: #FFA5A5">${selected_triple[0]}</p1></td><td width="300px">${selected_triple[1]}</td><td width="300px">${selected_triple[2].replaceAll("_", " ")}</td></tr></table>
        <p>Now please answer the <b><p7>question</p7></b> based on <p1>the word</p1> <p2>"${marked_word}"</p2>.</p> 
        <p6>· Preferrably including <p2>"${marked_word}"</p2> and <p4>related concept</p4> in your answer.</p6><br>
        <p6>· You can use its <p3>meaning in Wiktionary</p3>.</p6><br>
        <p6>· The QA-pair should be beneficial for children's education.</p6>`;
        document.getElementById("tr_selected").style.backgroundColor = "#a9a7ff"
        document.getElementById("question").value = annotated_words[selected_index].question;
        document.getElementById("question").style.fontSize = "18px";
        document.getElementById("question").style.color = "#7653d8";
        document.getElementById("answer").value = "";
        return;
    }
    $.ajax({
        type: "GET",
        url: "/submit",
        data: {
            "question1": q,
            "answer1_for_question1": annotated_words[selected_index].answer,
            "answer2_for_question1": a,
            "question2": q2,
            "answer_for_question2": a2,
            "c1": ranked_triple[0].concept,
            "c2": ranked_triple[1].concept,
            "c3": ranked_triple[2].concept,
            "r1": ranked_triple[0].relation,
            "r2": ranked_triple[1].relation,
            "r3": ranked_triple[2].relation,
            "o1": ranked_triple[0].obj,
            "o2": ranked_triple[1].obj,
            "o3": ranked_triple[2].obj,
            "title": title,
            "section": id,
            'word_id': marked_id,
            "username": username.toLowerCase(),
        },
        dataType: "text",
        success: function () {
            init_submit = 1;
            console.log("Done!");
            word_list[story_num] += "<p class='words'>" + marked_word + "</p>";
            let selected = document.getElementById("s" + marked_id);
            selected.style.background = "#a9a7ff";
            data[Number(marked_id)]['marked'] = 1;
            label_num ++;
            clear_content();
            SelectWordInst.style.display = "block";
            console.log(label_num, annotated_words.length)
            if(label_num == annotated_words.length){
                SelectWordInst.innerHTML = "<p><b>You finished!</b> Please move on to a new paragraph.</p>"
                SelectWordInst.innerHTML += "<br><br><br><p3>*This annotation task is to create QA pairs beneficial for children's education, with the help of external knowledge from ConceptNet.</p3>"
            }
        }
    })
}

function initial_state(){
    init_state = 1;
    ShowLogin();
    //concept_space.style.display = "none";
}

function clear_content(){
    document.getElementById("question").value = "";
    document.getElementById("answer").value = "";
    AboveMeaning.innerHTML = "";
    ShowMeaning.innerHTML = "";
    AboveTriples.innerHTML = "";
    ShowTriples.innerHTML = "";
    document.getElementById("pair").style.display = "none";
    document.getElementById("submit").style.display = "none";
    concept_space.style.display = "none";
    QA.style.display = "none";
    //SelectWordInst.style.display = "none";
    SelectTripleInst.style.display = "none";
    CreateQAInst.style.display = "none";
    prev_marked_concept = "";
    //marked_id = "";
    marked_concept = "";
    selected_triple = [];
    sub_time = 0;
    q2 = "";
    a2 = "";
    rank_num = 0;
    ranked_triple = [];
    ranked_triple_id = [];
}

tippy('#question', {
    content: "You haven't enter your question!",
    trigger: 'manual',
    theme: 'material'
});

tippy('#answer', {
    content: "You haven't enter your answer!",
    trigger: 'manual',
    theme: 'material'
});

tippy('#submit', {
    content: "Click here to submit your question and answer!",
    trigger: 'manual',
    theme: 'material'
});

tippy('#finish_button', {
    content: "Click here to move on to a new paragraph!",
    trigger: 'mouseenter focus',
    theme: 'material'
})

function folder_section(){
    var fd = document.getElementsByClassName("folder");
    for (let i = 0; i < fd.length; i++){
        fd[i].addEventListener("click", function(){
            this.classList.toggle("active");
            var wordline = this.nextElementSibling;
            if (wordline.style.maxHeight){
                wordline.style.maxHeight = null;
            }else{
                wordline.style.maxHeight = wordline.scrollHeight + "px";
            }
        });
    }
}

//render_original();
initial_state();
folder_section();

