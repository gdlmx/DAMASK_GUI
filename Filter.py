class FilterBase(object):
  def __init__(self, input=[]):
    self.input =input
    for i in input:
      i.output.append(self)
    self.output=[]
    self.result={'time':0}
    self.options={'time':0}

  def proc(self, source):
    for i_obj in self.input:
      if not ( self.mod_time >= i_obj.mod_time and self.mod_time >= self.options['time']):
        self.update(source)
        break
    for o_obj in self.output:
      o_obj.proc(self)

  @property
  def mod_time(self):
    return self.result['time']

  @mod_time.setter
  def mod_time(self, val):
    self.result['time'] = val