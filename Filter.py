class FilterBase(object):
  mod_time=0
  opt_time=0
  name = 'FilterBase'

  def __init__(self, input=[]):
    self.input = input if isinstance( input,(list,tuple) ) else [input,]
    for i in self.input:
      i.output.append(self)
    self.output=[]
    self.result={}
    self.options={}

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

class DT(object):
    def __init__(self, tree=None):
        self.value = tree
    def __getitem__(self, index):
        if isinstance(self.value, dict):
            try:
                return DT(self.value[index])
            except KeyError:
                return DT(self.value['DT_default'])
        else:
            return DT(self.value)

class UIFilter(FilterBase):
    name = 'UIFilter'
    DEBUG=True
    options_def =  ((None,'str', 'NULL'),)  #[(Key, Type, defaultVal)]
    
#   def __init__(self,  *value):
#       super(UIFilter, self).__init__( *value )
        
    def ui_set_options(self):
        print self.options, self.options_def
        self.options_def =[ (k, type(v).__name__, v) for k,v in self.options.items() ]
        
        
    def set_optparser(self, p):
        """ read optparse.OptionParser object """
        self.options_def = []
        for opt in p.option_list:
            if not opt.dest: continue
            key = opt.dest
            # https://docs.python.org/2/library/optparse.html#optparse-standard-option-types
            # Decision tree
            oType = DT( { "store_true":"bool", "store_false":"bool",
                          "append":{'string':"str_ml"},
                          "DT_default":{'int':'int','long':'int','float':'float','choice':'list','DT_default':'str'}
                        } )[opt.action][opt.type].value
            if self.DEBUG : print('{0}\t{1}\t{2}'.format(opt, key, oType))
            
            # set default value
            default = opt.default
            if isinstance(default , (tuple,list) ) and default[0] == 'NO':
                default = ''
            if oType == 'bool':
                self.options[key] = default = bool(default)
            elif oType == 'str_ml':
                oType = 'str'
                default = "\n{0}\n".format(default)
            elif oType == 'list':
                Id = opt.choices.index(default)  if  default else 0 
                default = [ Id ] + opt.choices 
            elif not self.options.has_key(key):
                self.options[key] = default

            # set option definition
            self.options_def.append( (key, oType, default) )
        
        
    @property
    def ui_options(self):
        return [ ( key,  d_val) for key, typestr, d_val in self.options_def]

    @ui_options.setter
    def ui_options(self, value):
        i = 0
        time_inc = 0
        for key, typestr, d_val in self.options_def: 
            v = value[i] if typestr!='list' else d_val[value[i]+1]
            if self.options.has_key(key) and self.options[key] != v : time_inc = 1
            self.options[key] =  v
            i+=1
        self.opt_time += time_inc


class fooFltr(UIFilter):
    name = 'plot sin(n*x)'
    opt_time = 1
    
    def __init__(self, *value):
        super(fooFltr, self).__init__( *value )
        import numpy as np
        self.options = {'xlabel':'x', 'ylabel':'sin(x)', 'n':1.0}
        x = np.arange(0, 2 * 3.141, 0.1)
        self.result = {'x':x, 'y':np.sin(x), 'xlabel':'x', 'ylabel':'sin(x)'}
        self.ui_set_options()
        
    def update(self, src):
        import numpy as np
        x = self.result['x']
        n = self.options['n']
        self.result['y'] =  np.sin(n*x)
        for k in ['xlabel','ylabel'] :  self.result[k] = self.options[k]
        self.mod_time = self.opt_time