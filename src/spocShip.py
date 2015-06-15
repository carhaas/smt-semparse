#!/usr/bin/env python
# -*- coding: utf-8 -*-
import parse_mrl

class spocShip:

  def __init__(self, config):
    self.config = config

  def run(self, neg=False):
    if neg is True:
      self.write_queries(True)
      mrl_file = open('%s/eval_neg.pl' % self.config.experiment_dir).read().splitlines()
      true_answers = open('%s/test_neg.gold' % self.config.experiment_dir).read().splitlines()
      result_file = open('%s/eval_true_neg.scored' % self.config.experiment_dir, 'w')
      answer_file = open('%s/hyp_neg.answers' % self.config.experiment_dir, 'w')
    else:
      self.write_queries()
      mrl_file = open('%s/eval.pl' % self.config.experiment_dir).read().splitlines()
      true_answers = open('%s/test.gold' % self.config.experiment_dir).read().splitlines()
      result_file = open('%s/eval_true.scored' % self.config.experiment_dir, 'w')
      answer_file = open('%s/hyp.answers' % self.config.experiment_dir, 'w')
    for line_counter, mrl_sentence in enumerate(mrl_file):
      if mrl_sentence == "no mrl found": 
        print >>result_file, 'empty'
        print >>answer_file, 'empty'
        continue
      suggest_answer = parse_mrl.run_query(mrl_sentence,line_counter)
      print >>answer_file, suggest_answer
      if suggest_answer == true_answers[line_counter]:
        print >>result_file, 'yes'
      elif suggest_answer.strip()=="":
        print >>result_file, 'empty'   
      else:
        print >>result_file, 'no'

  def write_queries(self, neg=False):
    if neg is True:
      hyp_file = open('%s/hyp_neg.fun' % self.config.experiment_dir)
      query_file = open('%s/eval_neg.pl' % self.config.experiment_dir, 'w')
    else:
      hyp_file = open('%s/hyp.fun' % self.config.experiment_dir)
      query_file = open('%s/eval.pl' % self.config.experiment_dir, 'w')

    for hyp_line in hyp_file.readlines():
      if "no mrl found" in hyp_line:
        print >>query_file, "no mrl found"
      else:
        idx, hyp, scoreparts, score = hyp_line.split('|||')
        idx = int(idx)
        hyp = hyp.strip()
        print >>query_file, hyp
      
    hyp_file.close()
    query_file.close()