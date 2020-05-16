from django.shortcuts import render
from django.http import JsonResponse
from django import utils

import os

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

def feedback_sum(request):
    if request.method == 'POST':
        secret = os.environ.get('TOKEN_SECRET', '')
        try:
            token = request.headers['Authorization'].split()[1]
            decoded_jwt = jwt.decode(token, secret, options={'verify_aud': False}, algorithms=['HS256'])
        except:
            return JsonResponse({
                'msg': 'Unauthorized'
            }, status=401)

        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)

        feedback = body_data['feedback']
        feedback_lang, _ = langid.classify(feedback['content'])

        feedback_sums = FeedbacksSum.objects.all()
        feedback_sum_created = False
        for fs in feedback_sums:
            first_id = int(fs.feedback_ids.split(':::')[0])
            presentable_feedback = Feedback.objects.get(id=first_id)

            feedback_sum_lang, _ = langid.classify(fs.summary)
            
            if (presentable_feedback.organization_name == feedback['organization_name']
                and presentable_feedback.for_product == feedback['for_product']
                and presentable_feedback.product_id == feedback['product_id']
                and presentable_feedback.branch_address == feedback['branch_address']
                and presentable_feedback.sentiment == feedback['sentiment']
                and feedback_sum_lang == feedback_lang):
                
                feedback_sum_created = True

                new_summary = _create_summary(fs.feedback_all, feedback['content'], feedback_lang)
                fs.summary = new_summary
                fs.feedback_all = fs.feedback_all + ' ' + feedback['content']
                fs.feedback_ids = fs.feedback_ids + str(feedback['id']) + ':::'
                fs.update_date = utils.timezone.now()

                fs.save()

                kws = ''
                for kw in feedback['keywords']:
                    kws = kws + kw + ':::'

                f = Feedback(id=feedback['id'],
                    organization_name=feedback['organization_name'],
                    for_product=feedback['for_product'],
                    product_id=feedback['product_id'],
                    branch_address=feedback['branch_address'],
                    sentiment=feedback['sentiment'],
                    keywords=kws,
                    content=feedback['content'],
                    feedback_sum=fs)

                f.save()

                data = {
                    'id': fs.id,
                    'feedback_ids': fs.feedback_ids,
                    'feedback_all': fs.feedback_all,
                    'summary': fs.summary
                }

                return JsonResponse({
                    'data': data
                })

        if not feedback_sum_created:
            new_summary = _create_summary('', feedback['content'], feedback_lang)
            fs = FeedbacksSum(feedback_ids=str(feedback['id']) + ':::',
                feedback_all=feedback['content'],
                summary=new_summary)
            fs.save()


            kws = ''
            for kw in feedback['keywords']:
                kws = kws + kw + ':::'

            f = Feedback(id=feedback['id'],
                organization_name=feedback['organization_name'],
                for_product=feedback['for_product'],
                product_id=feedback['product_id'],
                branch_address=feedback['branch_address'],
                sentiment=feedback['sentiment'],
                keywords=kws,
                content=feedback['content'],
                feedback_sum=fs)

            f.save()

            data = {
                'id': fs.id,
                'feedback_ids': fs.feedback_ids,
                'feedback_all': fs.feedback_all,
                'summary': fs.summary
            }

            return JsonResponse({
                'data': data
            })
    else:
        return JsonResponse({
            'msg': 'No route identified'
        }, status=400)


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