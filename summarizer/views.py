from django.shortcuts import render
from django.http import JsonResponse
from django import utils

import json

import jwt

import langid

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize, sent_tokenize

from .models import Feedback, FeedbacksSum


armenian_stopwords = ['այդ','այլ','այն','այս','դու','դուք','եմ','են','ենք','ես','եք','է','էի','էին','էինք','էիր',
        'էիք','էր','ըստ','թ','ի','ին','իսկ','իր','կամ','համար','հետ','հետո','մենք','մեջ','մի',
        'ն','նա','նաև','նրա','նրանք','որ','որը','որոնք','որպես','ու','ում','պիտի','վրա','և']


# Create your views here.



def _create_summary(merged_feedbacks, new_feedback, lang):

    if lang == 'en':
        stop_words = set(stopwords.words("english"))
    elif lang == 'hy':
        stop_words = set(armenian_stopwords)
    else:
        return None
    
    if merged_feedbacks == '':
        content = new_feedback
    else:
        content = merged_feedbacks + ' ' + new_feedback

    # for armenian content
    if lang == 'hy':
        content = content.replace(':', '.')

    freq_table = _create_frequency_table(content, lang)

    sentences = sent_tokenize(content)

    sentence_scores = _score_sentences(sentences, freq_table)

    threshold = _find_average_score(sentence_scores)
    
    summary = _generate_summary(sentences, sentence_scores, 1.5 * threshold)

    # for armenian content
    if lang == 'hy':
        content = content.replace('.', ':')
        summary = summary.replace('.', ':')

    summary = summary.lstrip()

    return summary


def _create_frequency_table(text_string, lang) -> dict:

    if lang == 'en':
        stopWords = set(stopwords.words("english"))
    elif lang == 'hy':
        stopWords = set(armenian_stopwords)

    words = word_tokenize(text_string)
    ps = PorterStemmer()

    freqTable = dict()
    for word in words:
        word = ps.stem(word)
        if word in stopWords:
            continue
        if word in freqTable:
            freqTable[word] += 1
        else:
            freqTable[word] = 1

    return freqTable


def _score_sentences(sentences, freqTable) -> dict:
    sentenceValue = dict()

    for sentence in sentences:
        word_count_in_sentence = (len(word_tokenize(sentence)))
        for wordValue in freqTable:
            if wordValue in sentence.lower():
                if sentence[:10] in sentenceValue:
                    sentenceValue[sentence[:10]] += freqTable[wordValue]
                else:
                    sentenceValue[sentence[:10]] = freqTable[wordValue]

        sentenceValue[sentence[:10]] = sentenceValue[sentence[:10]] // word_count_in_sentence

    return sentenceValue


def _find_average_score(sentenceValue) -> int:
    sumValues = 0
    for entry in sentenceValue:
        sumValues += sentenceValue[entry]

    # Average value of a sentence from original text
    average = int(sumValues / len(sentenceValue))

    return average


def _generate_summary(sentences, sentenceValue, threshold):
    sentence_count = 0
    summary = ''

    for sentence in sentences:
        if sentence[:10] in sentenceValue and sentenceValue[sentence[:10]] > (threshold):
            summary += " " + sentence
            sentence_count += 1

    return summary