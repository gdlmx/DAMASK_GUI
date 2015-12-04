# -*- coding: utf-8 -*-
__copyright__ = "Copyright (C) 2015 Mingxuan Lin"

class FilterBase(object):
  mod_time=0
  opt_time=0
  name = 'FilterBase'

  def __init__(self, input=[]):
    self.output=[]
    self.result={}
    self.options={}
    self.input = input if isinstance( input,(list,tuple) ) else [input,]
    for i in self.input:
      if not self in i.output:
        i.output.append(self)

  def proc(self, source=None):
    if any( self.mod_time < i.mod_time for i in self.input ) or self.mod_time < self.opt_time:
      self.update(source)
    for o_obj in self.output:
      o_obj.proc(self)

  def update(self, src):
    pass

