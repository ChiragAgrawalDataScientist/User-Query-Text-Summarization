from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import spacy
from googlesearch import search
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
import pandas as pd
from collections import Counter
import numpy as np
import pickle


app = Flask(__name__)


def get_url_of_query(user_query):
    # query = "S jaishankar best deal petrol"
    queries = []
    for j in search(user_query, tld="co.in", stop=10, pause=2):
        queries.append(j)
    articles_to_remove_with_words = ['wikipedia', 'trendlyne', 'indiainfoline',
                                     'economictimes']
    for i in articles_to_remove_with_words:
        for j in queries:
            if i in j:
                queries.remove(j)

    response = requests.get(queries[0])
    print(response.status_code)
    page_contents = response.text

    def remove_tags(html):
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.findAll('a', href=True):
            a.extract()
        # This for loop will remove all the tags and print only the text
        for data in soup(['style', 'script']):
            data.decompose()


        return ' '.join(soup.stripped_strings)

    page_contents = remove_tags(page_contents)
    page_contents = page_contents.lower()


    if 'watch right now' in page_contents:
        page_contents = page_contents.replace('watch right now', '')
    if 'download app copyright © 2022 living media india limited. for reprint rights' in page_contents:
        page_contents = page_contents.replace(
            'download app copyright © 2022 living media india limited. for reprint rights', '')
    if 'also read' in page_contents:
        page_contents = page_contents.replace('also read', '')
    if 'indiatoday.in' in page_contents:
        page_contents = page_contents.replace('indiatoday.in', '')
    if 'download app' in page_contents:
        page_contents = page_contents.replace('download app', '')
    if 'useful links' in page_contents:
        page_contents = page_contents.replace('useful links', '')
    if 'file photo' in page_contents:
        page_contents = page_contents.replace('file photo', '')
    if 'pti' in page_contents:
        page_contents = page_contents.replace('pti', '')
    if 'top takes' in page_contents:
        page_contents = page_contents.replace('top takes', '')
    if 'posted by' in page_contents:
        page_contents = page_contents.replace('posted by', '')
    if 'read this' in page_contents:
        page_contents = page_contents.replace('read this', '')
    if 'dark mode' in page_contents:
        page_contents = page_contents.replace('dark mode', '')
    if 'speak now' in page_contents:
        page_contents = page_contents.replace('speak now', '')
    if 'india news' in page_contents:
        page_contents = page_contents.replace('india news', '')
    if ' x ' in page_contents:
        page_contents = page_contents.replace(' x ', '')
    if 'advertisement new delhi august 17 2022 updated august 17 2022 1108 ist' in page_contents:
        page_contents = page_contents.replace('advertisement new delhi august 17 2022 updated august 17 2022 1108 ist', '')
    if 'FP Explainers' in page_contents:
        page_contents = page_contents.replace('FP Explainers', '')
    if 'f.brands' in page_contents:
        page_contents = page_contents.replace('f.brands', '')
    if 'rn' in page_contents:
        page_contents = page_contents.replace('rn', '')
    if 'cnbctv18' in page_contents:
        page_contents = page_contents.replace('cnbctv18', '')
    if 'image. pic courtesy' in page_contents:
        page_contents = page_contents.replace('image. pic courtesy', '')


    punct = '''!"#$%&'()*+,-/:;<=>?@[\]^_`{|}~'''
    for ele in page_contents:
        if ele in punct:
            page_contents = page_contents.replace(ele, "")
    page_contents = page_contents.replace('  ', ' ')


    # loading the english language small model of spacy
    en_small = spacy.load('en_core_web_sm')
    en_small.Defaults.stop_words.add(
        "read useful links download app copyright 2022 living media india limited reprint rights")
    sw_spacy_small = en_small.Defaults.stop_words
    words = [word for word in page_contents.split() if word not in sw_spacy_small]
    no_sw_text = " ".join(words)
    print(no_sw_text)
    print("Old length of text: ", len(page_contents))
    print("New length of text: ", len(no_sw_text))
    page_content = no_sw_text


    punct="."
    for ele in page_content:
        if ele in punct:
            page_content = page_content.replace(ele, "")

    word_tokens = word_tokenize(page_content)
    page_contents_word_freq = pd.Series(word_tokens).value_counts()
    page_contents_word_freq_dict = {}
    keys = page_contents_word_freq.index
    values = page_contents_word_freq.values
    page_contents_word_freq_dict.update(zip(keys, values))


    '''Dividing all the counts of all the words with the maximum count.'''
    page_contents_word_freq_dict = list(page_contents_word_freq_dict.values()) / max(
        page_contents_word_freq_dict.values())

    page_contents_word_freq_norm = {}
    keys = page_contents_word_freq.index
    values = page_contents_word_freq_dict
    page_contents_word_freq_norm.update(zip(keys, values))

    sent_token = sent_tokenize(page_contents)

    sent_score = []
    count = 0
    for i in sent_token:
        split = i.split()
        count_of_words_list = []
        key_values_list = []
        for key, value in page_contents_word_freq_norm.items():
            if key in split:
                count_of_words = split.count(key)
                count = count + count_of_words

                if count_of_words > 1:
                    mul_val = count_of_words * value
                else:
                    mul_val = value

                    # print(key + ' | '+ str(count_of_words) + ' | ' + str(mul_val))
                key_values_list.append(mul_val)
                count_of_words_list.append(count_of_words)

        score = sum(key_values_list) / sum(count_of_words_list)
        sent_score.append(score)

    imp_sent_dict = {}
    imp_sent_dict.update(zip(sent_token, sent_score))

    summary = {}
    keys = imp_sent_dict.keys()
    values = sorted(imp_sent_dict.values(), reverse=True)
    summary.update(zip(keys, values))
    summary_final = list(summary.keys())[:11]
    summary_final = ' '.join(summary_final)

    return summary_final


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        query = request.form.get('text')
        query_content = get_url_of_query(query)
        return query_content
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug = True)
