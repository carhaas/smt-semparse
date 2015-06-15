#!/usr/bin/env python
# -*- coding: utf-8 -*-
import parse_mrl
import os
import tempfile
import shutil
from extractor import Extractor
from smt_semparse_config import SMTSemparseConfig
from cdec import CDEC
from functionalizer import Functionalizer
import re


class NLParser:
    def __init__(self, experiment_dir):
        self.experiment_dir = experiment_dir
        # load config
        self.config = SMTSemparseConfig(experiment_dir + '/settings.yaml', experiment_dir + '/dependencies.yaml')
        prep_for_sed = re.sub(r"/", r"\/", experiment_dir)
        command = "sed -ie 's/feature_function=KLanguageModel .*mrl.arpa/feature_function=KLanguageModel " + prep_for_sed + "\/mrl.arpa/g' " + experiment_dir + "/cdec_test.ini"
        os.system(command)
        command = "sed -ie 's/= .*train.sa/= " + prep_for_sed + "\/train.sa/g' " + experiment_dir + "/extract.ini"
        os.system(command)

    # to use this for semparsing we need to give a nbest list of functionalised stuff already. for this we need a new functionaliser function that does not stop when it finds a valid one in nbest list but returns all valid ones
    def get_kbest(self, sentence):
        return self.process_set(sentence, True)

    def process_sentence(self, sentence):
        non_stemmed, sentence = self.preprocess_sentence(sentence)

        # we need a temp dir!
        temp_dir = tempfile.mkdtemp("", "semparse_process_sentence")

        # decode
        cdec = CDEC(self.config)
        cdec.decode_sentence(self.experiment_dir, sentence, temp_dir)

        # convert to bracket structure
        mrl = Functionalizer(self.config).run_sentence(self.experiment_dir, temp_dir, non_stemmed, sentence)

        # delete tmp files
        shutil.rmtree(temp_dir)

        answer = parse_mrl.run_query(mrl, 0)

        return (mrl, answer)

    def process_set(self, sentences, return_kbest=False):

        # we need a temp dir!
        temp_dir = tempfile.mkdtemp("", "semparse_process_set")

        non_stemmed = list(sentences)
        for counter, sentence in enumerate(sentences):
            non_stemmed_ele, sentence = self.preprocess_sentence(sentence)
            non_stemmed.append(non_stemmed_ele)
            sentences[counter] = sentence

        # decode
        cdec = CDEC(self.config)

        if return_kbest is True:
            return cdec.decode_set(self.experiment_dir, sentences, temp_dir, True)
        else:
            cdec.decode_set(self.experiment_dir, sentences, temp_dir)

        # convert to bracket structure
        mrls = Functionalizer(self.config).run_set(self.experiment_dir, temp_dir, non_stemmed, sentences)

        # delete tmp files
        shutil.rmtree(temp_dir)

        answers = []
        for counter, mrl in enumerate(mrls):
            answers.append(parse_mrl.run_query(mrl, 0))
        return (mrls, answers)

    def preprocess_sentence(self, sentence):
        # stem
        non_stemmed = sentence
        if non_stemmed[-2:] == ' .' or non_stemmed[-2:] == ' ?':
            non_stemmed = non_stemmed[:-2]
        if non_stemmed[-1:] == '.' or non_stemmed[-1:] == '?':
            non_stemmed = non_stemmed[:-1]

        sentence = Extractor(self.config).preprocess_nl(sentence)
        return non_stemmed, sentence
