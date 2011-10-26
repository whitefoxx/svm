# -*- coding: utf-8 -*-
"""
Spyder Editor

This temporary script file is located here:
C:\Users\cyb\.spyder2\.temp.py
"""
NGRAM = 5
term_table = {}
term_IG = {} 
used_term = set()
spam_email = 0
nonspam_email = 0

def doc_term_set(doc):
    doc_term = set()
    for i in range(0, len(doc), NGRAM):
        term = doc[i:i+NGRAM]
        if len(term) < NGRAM:
            break
        if term in doc_term:
            continue
        doc_term.add(term)
    return doc_term
    
def term_frequence(doc_term, label):
    for term in doc_term:
        if term in term_table:
            term_table[term][label] += 1
        else:
            term_table[term] = [0,0]
            term_table[term][label] += 1

def term_frequence_all_train_doc(corpus_path):
    global spam_email,nonspam_email
    index = open(corpus_path + "train_index","r")
    for line in index:
        label = line.split(" ")[0]
        path = line.split(" ")[1].strip()
        if label.lower() == "spam":
            label = 0
            spam_email += 1
        else:
            label = 1
            nonspam_email += 1
        email = open(corpus_path + path, "r")
        doc = email.read()
        email.close()
        doc_term = doc_term_set(doc)
        term_frequence(doc_term, label)
    index.close()

def convert_all_train_doc(corpus_path):
    index = open(corpus_path + "train_index","r")
    train_f = open(corpus_path + "../train", "w")
    global used_term
    for line in index:
        label = line.split(" ")[0]
        path = line.split(" ")[1].strip()
        if label.lower() == "spam":
            label = "-1"
        else:
            label = "+1"
        email = open(corpus_path + path, "r")
        doc = email.read()
        email.close()
        doc_term = doc_term_set(doc)
        train_cell = label
        i = 1        
        for term in used_term:
            if term in doc_term:
                train_cell += " " + str(i) + ":1"
            else:
                train_cell += " " + str(i) + ":0"
            i += 1
        train_f.write(train_cell + "\n")
    index.close()
    train_f.close()

def convert_all_test_doc(corpus_path):
    index = open(corpus_path + "test_index","r")
    train_f = open(corpus_path + "../test", "w")
    global used_term
    for line in index:
        label = line.split(" ")[0]
        path = line.split(" ")[1].strip()
        if label.lower() == "spam":
            label = "-1"
        else:
            label = "+1"
        email = open(corpus_path + path, "r")
        doc = email.read()
        email.close()
        doc_term = doc_term_set(doc)
        train_cell = label
        i = 1        
        for term in used_term:
            if term in doc_term:
                train_cell += " " + str(i) + ":1"
            else:
                train_cell += " " + str(i) + ":0"
            i += 1
        train_f.write(train_cell + "\n")
    index.close()
    train_f.close()
    
def cal_term_IG(corpus_path):
    import math
    term_frequence_all_train_doc(corpus_path)
    total_email = spam_email + nonspam_email
    p_spam = float(spam_email) / total_email    
    IG_sum = [0,0]

    count = 0
    for term in term_table:
        term_cell = term_table[term]
        term_count = term_cell[0] + term_cell[1]
        p1 = float(term_cell[0]) / term_count
        if total_email == term_count:
            p2 = 0
        else:
            p2 = float(spam_email - term_cell[0]) / (total_email - term_count)
        if p1 == 0:
            tmp1 = (1-p1) * math.log((1-p1) / (1 - p_spam),2)
        elif p1 == 1:
            tmp1 = p1 * math.log(p1 / p_spam,2)
        else:
            tmp1 = p1 * math.log(p1 / p_spam,2) + (1-p1) * math.log((1-p1) / (1 - p_spam),2)
        if p2 == 0:
            tmp2 = (1-p2) * math.log((1-p2) / (1 - p_spam),2)
        elif p2 == 1:
            tmp2 = p2 * math.log(p2 / p_spam,2)
        else:
            tmp2 = p2 * math.log(p2 / p_spam,2) + (1-p2) * math.log((1-p2) / (1 - p_spam),2)
        term_IG[term] = float(term_count) / total_email * tmp1 + (1 - float(term_count) / total_email) * tmp2
        IG_sum[0] += term_IG[term]
        IG_sum[1] += 1
        if term_IG[term] > 0.02:
            count += 1
            used_term.add(term)
    avg_IG = IG_sum[0] / IG_sum[1]
    print avg_IG
    print count,len(term_table),len(used_term)

def pickle_all_term(corpus_path):
    import cPickle
    pickle_f = open(corpus_path + "../termIG_pickle_" + str(NGRAM), "w")
    cPickle.dump(term_IG, pickle_f)
    pickle_f.close()
    pickle_f = open(corpus_path + "../used_term_pickle_" + str(NGRAM), "w")
    cPickle.dump(used_term, pickle_f)
    pickle_f.close()

def unpickle_used_term(corpus_path):
    import cPickle
    global used_term
    pickle_f = open(corpus_path + "../used_term_pickle_" + str(NGRAM), "r")
    used_term = cPickle.load(pickle_f)
    pickle_f.close()

def split_train_test(corpus_path, scale):
    import random
    index = open(corpus_path + "index","r")
    lines = index.readlines()
    index.close()
    n_test = len(lines) / scale
    line_sta = range(len(lines))
    while n_test > 0:
        for i in range(len(lines)):
            if line_sta[i] != -1 and random.randint(0,10) == 0:
                n_test -= 1
                line_sta[i] = -1
                if n_test == 0:
                    break
    train_f = open(corpus_path + "train_index","w")
    test_f = open(corpus_path + "test_index","w")
    for i in range(len(lines)):
        if line_sta[i] == -1:
            test_f.write(lines[i])
        else:
            train_f.write(lines[i])
    train_f.close()
    test_f.close()

if __name__ == '__main__':
    corpus_path = "E:/data/email/corpus/trec06c/trec06c/full/"
    split_train_test(corpus_path, 10)
    cal_term_IG(corpus_path)
    pickle_all_term(corpus_path)
#    unpickle_used_term(corpus_path)
    convert_all_train_doc(corpus_path)
    convert_all_test_doc(corpus_path)
    