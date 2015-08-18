# -*- coding: utf-8 -*-

import codecs
import math
import sys

from pysmt.shortcuts import Symbol, And, Not, is_sat

from decimal import Decimal

def read_utf8_file_as_unicode(file):
    with codecs.open(file, 'rb', 'UTF-8') as f:
        return f.read()

class SuperScholar:
    def __init__(self):
        self.words = []
        self.dictionary = dict()
        self.translate_p = dict()
        self.propagate_p = dict()
        self.translate_vec = dict()
        self.propagate_vec = dict()
        self.translation = dict()
    def getDictSize(self):
        return len(self.dictionary)
    def getP(self, dict, occurency):
        # Hack.
        if occurency[0] == occurency[1]:
            return -1e100
        if occurency in dict:
            return dict[occurency]
        else:
            return -1e100
            # return math.log(1.0 / self.dictionary[occurency[0]])
    def trainModel(self, training_file):
        content = read_utf8_file_as_unicode(training_file)
        rules = content.split(u'。')
        for rule in rules:
            self.handleRule(rule)
        # Calculate the possibilities.
        for a in self.dictionary.keys():
            for b in self.dictionary.keys():
                occurency = "" + a + b
                if occurency in self.translate_vec:
                    self.translate_p[occurency] = math.log(1.0 * self.translate_vec[occurency] / self.dictionary[a])
                if occurency in self.propagate_vec:
                    self.propagate_p[occurency] = math.log(1.0 * self.propagate_vec[occurency] / self.dictionary[a])
    def writeModel(self, model_file):
        file = codecs.open(model_file, "w", "utf-8")
        dictn = len(self.dictionary)
        file.write(str(dictn) + "\n")
        file.write("\n")
        for a in self.dictionary.keys():
            if a not in self.translation:
                continue
            for b in self.translation[a]:
                occurency = "" + a + b
                file.write(a + b + " " + str(self.translate_p[occurency]) + "\n")
        file.write("\n")
        for a in self.dictionary.keys():
            for b in self.dictionary.keys():
                occurency = "" + a + b
                if occurency in self.propagate_p:
                    file.write(a + b + " " + str(self.propagate_p[occurency]) + "\n")
        file.close()
    def gao(self, s):
        length = len(s)
        dp_pre = dict()
        dp_cur = dict()
        for c in self.dictionary.keys():
            dp_pre[c] = self.getP(self.propagate_p, "" + s[0] + c)
        ps = dict()
        ps[0] = dict()
        for c in self.dictionary.keys():
            ps[0][c] = -1
        for i in range(1, length):
            # c is at ss[i].
            ps[i] = dict()
            for c in self.dictionary.keys():
                pa = self.getP(self.propagate_p, "" + s[i] + c)
                dp_cur[c] = Decimal('-Infinity')
                for cc in self.dictionary.keys():
                    new_p = dp_pre[cc] + self.getP(self.translate_p, "" + cc + c) + pa
                    if new_p > dp_cur[c]:
                        dp_cur[c] = new_p
                        ps[i][c] = cc
            dp_pre.clear()
            for c in self.dictionary.keys():
                dp_pre[c] = dp_cur[c]
        cc = ''
        mm = Decimal('-Infinity')
        for c in self.dictionary.keys():
            if dp_pre[c] > mm:
                cc = c
                mm = dp_pre[c]
        ans = cc
        for i in range(length - 1, 0, -1):
            ans += ps[i][cc]
            cc = ps[i][cc]
        print s, ans[::-1]
    def handleWord(self, word):
        if word == u'，':
            pass
        if word not in self.dictionary:
            self.dictionary[word] = 1
        else:
            self.dictionary[word] += 1
    def handlePropagate(self, occurency):
        if occurency not in self.propagate_vec:
            self.propagate_vec[occurency] = 1
        else:
            self.propagate_vec[occurency] += 1
    def handleTranslate(self, occurency):
        if occurency[0] == u'，' or occurency[1] == u'，':
            return
        if occurency not in self.translate_vec:
            self.translate_vec[occurency] = 1
            if occurency[0] not in self.translation:
                self.translation[occurency[0]] = [occurency[1]]
            else:
                self.translation[occurency[0]].append(occurency[1])
        else:
            self.translate_vec[occurency] += 1
    def handlePair(self, fs, ss):
        if len(fs) != len(ss):
            return
        length = len(fs)
        for i in range(length):
            self.handleWord(fs[i])
            self.handleWord(ss[i])
            # For propagation.
            self.handlePropagate("" + fs[i] + ss[i])
            self.handlePropagate("" + ss[i] + fs[i])
        for i in range(0, length - 1):
            # For translation.
            self.handleTranslate("" + fs[i] + fs[i + 1])
            self.handleTranslate("" + ss[i] + ss[i + 1])
    def isAtomic(self, rule):
        sep = rule[len(rule) / 2]
        return sep != u'对' and sep != u'送' and sep != u'；' and sep != u'，'
    def handleRule(self, rule):
        sep = rule[len(rule) / 2]
        parts = rule.split(sep)
        if sep == u'对' or sep == u'送' or sep == u'；':
            # 获得一个对偶句
            self.handlePair(parts[0], parts[1])
        elif sep == u'，':
            if self.isAtomic(parts[0]):
                self.handlePair(parts[0], parts[1])
            else:
                for rule in parts:
                    self.handleRule(rule)

def getCandidates():
    varA = Symbol("A")
    varB = Symbol("B")
    f = And([varA, Not(varB)])
    scholar = SuperScholar()
    scholar.trainModel('./trainingset/book.txt')
    scholar.writeModel('./model.txt')

    scholar.gao(u'南山南')
    scholar.gao(u'冰比冰水冰')
    scholar.gao(u'明天去操场操到天明')
    scholar.gao(u'大波美人鱼人美波大')

    scholar.gao(u'人')
    scholar.gao(u'人间')
    scholar.gao(u'人间美')
    scholar.gao(u'人间佳草')
    scholar.gao(u'人间一杯酒')
    scholar.gao(u'我爸是李刚')

if __name__ == '__main__':
    getCandidates()
