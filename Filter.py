class FilterBase(object):
  result=()
  options=()
  mod_time=0
  opt_time=0
  name = 'FilterBase'

  def __init__(self, input=[]):
    self.input =input
    for i in input:
      i.output.append(self)
    self.output=[]

  def proc(self, source):
    if any( self.mod_time < i.mod_time for i in self.input ) or self.mod_time < self.opt_time:
      self.update(source)
    for o_obj in self.output:
      o_obj.proc(self)
   
  def update(self, src):
    pass
   
  @property
  def ui_options(self):
    return [('str', 'this is a dumy filter')]
     
  @ui_options.setter
  def ui_options(self, value):
    print value