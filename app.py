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
import re


app = Flask(__name__)


def get_url_of_query(user_query):
    # query = "S jaishankar best deal petrol"
    queries = []
    for j in search(user_query, tld="co.in", stop=10, pause=2):
        queries.append(j)
    articles_to_remove_with_words = ['wikipedia', 'trendlyne', 'indiainfoline',
                                     'economictimes', 'livemint', 'youtube',
                                     'rottentomatoes', 'encrypted']
    for i in articles_to_remove_with_words:
        for j in queries:
            if i in j:
                queries.remove(j)

    response = requests.get(queries[0])
    print(response.status_code)

    page_contents = response.text
    print('length of page contents is :', len(page_contents))
    soup = BeautifulSoup(page_contents, "html.parser")
    title_data = soup.title.text
    p_tag = soup.find_all('p', )
    for a in soup.findAll('a', href=True):
        a.extract()
    p_text = []
    for text in p_tag:
        p_text.append(text.text)

    p_text = str(p_text)
    p_text = p_text.replace('\n', '')
    p_text = p_text.replace('\\n', '')
    p_text = p_text.replace('\t', '')
    p_text = p_text.replace('\r', '')
    p_text = p_text.replace('\\r', '')
    p_text = p_text.replace('\xa0', '')
    p_text = p_text.replace('\\t', '')
    p_text = p_text.replace('\\xa0', '')
    p_text = p_text.replace('topics', '')

    p_text = re.sub(r'http\S+', '', p_text)
    p_text = p_text.lower()
    p_text = re.sub('\d{2}(:)\d{2}\s(ist)', '', p_text)
    # p_text = re.sub('\d{4}\d{2}', '\d{4}(:)\d{2}', p_text)
    page_contents = p_text

    # response = requests.get(queries[0])
    # print(response.status_code)
    # page_contents = response.text
    # soup = BeautifulSoup(page_contents, "html.parser")
    # '''Store the title of webpage in title_data variable'''
    # title_data = soup.title.text
    #
    # def remove_tags(html):
    #     soup = BeautifulSoup(html, "html.parser")
    #     for a in soup.findAll('a', href=True):
    #         a.extract()
    #     # This for loop will remove all the tags and print only the text
    #     for data in soup(['style', 'script']):
    #         data.decompose()
    #
    #     return ' '.join(soup.stripped_strings)

    '''Splitting the title and removing all unwanted text from title'''
    title_data = title_data.split('|', 1)[0]
    title_data = title_data.split('-', 1)[0]
    '''Replace title of webpage from the page contents'''
    if title_data in page_contents:
        page_contents = page_contents.replace(title_data, '')

    # page_contents = remove_tags(page_contents)
    page_contents = page_contents.lower()


    page_contents = page_contents.replace('watch right now', '')
    page_contents = page_contents.replace('download app copyright © 2022 living media india limited. for reprint rights', '')
    page_contents = page_contents.replace('also read', '')
    page_contents = page_contents.replace('indiatoday.in', '')
    page_contents = page_contents.replace('download app', '')
    page_contents = page_contents.replace('useful links', '')
    page_contents = page_contents.replace('file photo', '')
    page_contents = page_contents.replace('2min read', '')
    page_contents = page_contents.replace('pti', '')
    page_contents = page_contents.replace('top takes', '')
    page_contents = page_contents.replace('posted by', '')
    page_contents = page_contents.replace('read this', '')
    page_contents = page_contents.replace('dark mode', '')
    page_contents = page_contents.replace('speak now', '')
    page_contents = page_contents.replace('india news', '')
    page_contents = page_contents.replace(' x ', '')
    page_contents = page_contents.replace('advertisement new delhi august 17 2022 updated august 17 2022 1108 ist', '')
    page_contents = page_contents.replace('FP Explainers', '')
    page_contents = page_contents.replace('f.brands', '')
    page_contents = page_contents.replace('rn', '')
    page_contents = page_contents.replace('cnbctv18', '')
    page_contents = page_contents.replace('image. pic courtesy', '')
    page_contents = page_contents.replace('sign in', '')
    page_contents = page_contents.replace('topics', '')
    page_contents = page_contents.replace('follow us', '')
    page_contents = page_contents.replace('(@_sayema)', '')
    page_contents = page_contents.replace('eng', '')
    page_contents = page_contents.replace("’s", '')
    # mar 30, 2022
    if 'updated on' in page_contents:
        page_contents = re.sub('(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s\d{2}(,)\s\d{4}', ' ',
                               page_contents)
    # mar 30th, 2022
    if 'updated on' in page_contents:
        page_contents = re.sub('(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s\d{2}(th|st|rd|nd)(,)\s\d{4}', ' ',
                               page_contents)
    # Mar 30th 2022
    if 'updated on' in page_contents:
        page_contents = re.sub('(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s\d{2}(th|st|rd|nd)\s\d{4}', ' ',
                               page_contents)
    # mar 30 2022
    if 'updated on' in page_contents:
        page_contents = re.sub('(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s\d{2}\s\d{4}', ' ',
                               page_contents)

    # march 30th, 2022
    if 'updated on' in page_contents:
        page_contents = re.sub(
            '(january|february|march|april|may|june|july|august|september|october|november|december)\s\d{2}(th|st|rd|nd)(,)\s\d{4}',
            ' ', page_contents)
    # march 30, 2022
    if 'updated on' in page_contents:
        page_contents = re.sub(
            '(january|february|march|april|may|june|july|august|september|october|november|december)\s\d{2}(,)\s\d{4}',
            ' ', page_contents)
    # march 30th 2022
    if 'updated on' in page_contents:
        page_contents = re.sub(
            '(january|february|march|april|may|june|july|august|september|october|november|december)\s\d{2}(th|st|rd|nd)\s\d{4}',
            ' ', page_contents)
    # march 30 2022
    if 'updated on' in page_contents:
        page_contents = re.sub(
            '(january|february|march|april|may|june|july|august|september|october|november|december)\s\d{2}\s\d{4}',
            ' ', page_contents)

    if 'published on' in page_contents:
        page_contents = re.sub('(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s\d{2}\s\d{4}', ' ',
                               page_contents)
    if 'published on' in page_contents:
        page_contents = re.sub('(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s\d{2}(th|st|rd|nd)\s\d{4}', ' ',
                               page_contents)
    if 'published on' in page_contents:
        page_contents = re.sub('(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s\d{2}(,)\s\d{4}', ' ',
                               page_contents)
    if 'published on' in page_contents:
        page_contents = re.sub('(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s\d{2}(th|st|rd|nd)(,)\s\d{4}', ' ',
                               page_contents)

    if 'published on' in page_contents:
        page_contents = re.sub(
            '(january|february|march|april|may|june|july|august|september|october|november|december)\s\d{2}(th|st|rd|nd)(,)\s\d{4}',
            ' ', page_contents)
    if 'published on' in page_contents:
        page_contents = re.sub(
            '(january|february|march|april|may|june|july|august|september|october|november|december)\s\d{2}(th|st|rd|nd)\s\d{4}',
            ' ', page_contents)
    if 'published on' in page_contents:
        page_contents = re.sub(
            '(january|february|march|april|may|june|july|august|september|october|november|december)\s\d{2}(,)\s\d{4}',
            ' ', page_contents)
    if 'published on' in page_contents:
        page_contents = re.sub(
            '(january|february|march|april|may|june|july|august|september|october|november|december)\s\d{2}\s\d{4}',
            ' ', page_contents)
    page_contents = re.sub(
        '(january|february|march|april|may|june|july|august|september|october|november|december)\s\d{2}(,)\s\d{4}', ' ',
        page_contents)
    page_contents = re.sub(
        '(january|february|march|april|may|june|july|august|september|october|november|december)\s\d{2}\s\d{4}', ' ',
        page_contents)
    page_contents = re.sub(
        '(january|february|march|april|may|june|july|august|september|october|november|december)\s\d{2}(th|st|rd|nd)\s\d{4}',
        ' ', page_contents)
    page_contents = re.sub(
        '(january|february|march|april|may|june|july|august|september|october|november|december)\s\d{2}(th|st|rd|nd)(,)\s\d{4}',
        ' ', page_contents)

    page_contents = re.sub('(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s\d{2}(th|st|rd|nd)\s\d{4}', ' ',
                           page_contents)
    page_contents = re.sub('(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s\d{2}(th|st|rd|nd)(,)\s\d{4}', ' ',
                           page_contents)
    page_contents = re.sub('(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s\d{2}\s\d{4}', ' ', page_contents)
    page_contents = re.sub('(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s\d{2}(,)\s\d{4}', ' ', page_contents)

    page_contents = page_contents.replace('kindly visit the to discover the benefits of this programme', '')
    page_contents = page_contents.replace('enjoy reading', '')
    page_contents = page_contents.replace('team business standard', '')
    page_contents = page_contents.replace('copyright © 2022', '')
    page_contents = page_contents.replace(
        'only the headline and picture of this report may have been reworked by the business standard staff the rest of the content is autogenerated from a syndicated feed. business standard has always strived hard to provide uptodate information and commentary on developments that are of interest to you and have wider political and economic implications for the country and the world. your encouragement and constant feedback on how to improve our offering have only made our resolve and commitment to these ideals stronger. even during these difficult times arising out of covid19 we continue to remain committed to keeping you informed and updated with credible news authoritative views and incisive commentary on topical issues of relevance.we however have a request.as we battle the economic impact of the pandemic we need your support even more so that we can continue to offer you more quality content. our subscrion model has seen an encouraging response from many of you who have subscribed to our online content. more subscrion to our online content can only help us achieve the goals of offering you even better and more relevant content. we believe in free fair and credible joualism. your support through more subscrions can help us practise the joualism to which we are committed.support quality joualism and .digital editor previous story next story copyrights 2022 business standard private ltd. all rights reserved. upgrade to premium services business standard is happy to inform you of the launch of business standard premium services as a premium subscriber you get an across device unfettered access to a range of services which include premium services in partnership with dear guest welcome to the premium services of business standard brought to you courtesy fis',
        '')

    punct = '''!"#$%&'()*+,-/:;<=>?@[\]^_`{|}~»—'''
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
    summary_final = list(summary.keys())[:15]
    summary_final = ' '.join(summary_final)
    summary_final = title_data + '\n' + summary_final

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
