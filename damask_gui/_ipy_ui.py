from __future__ import unicode_literals

from .Filter import FilterBase
import sys, os, random, time, warnings
from ipywidgets import widgets
Opt2Widget={
        None: (widgets.Checkbox,bool),
        'string':(widgets.Text,str),
        'int':(widgets.IntText,int),
        'long':(widgets.IntText,int),
        'float':(widgets.FloatText,float),
        'choice':(widgets.Select,str)
}

class UIFilter(FilterBase):
    name = 'UIFilter'
    DEBUG=None
    options_def =  ((None,'str', 'NULL'),)  #[(Key, Type, defaultVal)]

    @property   # obsoleted
    def ui_options(self):
        return [ ( key,  d_val) for key, typestr, d_val in self.options_def]

    @ui_options.setter # obsoleted
    def ui_options(self, value):
        valueList, self.widgetList = value
        pass

    def update_form(self, valueDict): # obsoleted
        for key, val in valueDict.items():
            self[key] = val
                
    def printmsg(self, msg, pauseTime=1000):
        print(msg)

    def set_options_def(self): # obsoleted
        pass

    def set_optparser(self, p):
        """ read optparse.OptionParser object """
        self.options_def = []
        self.widgets={}
        self.opts   ={}
        for opt in p.option_list:
            if not opt.dest: continue
            key = opt.dest
            self.widgets[key] = create_widget(opt)
            self.opts[key]=opt

    @property
    def options(self):
        return {k: self[k]  for k in self.widgets }
    
    @options.setter
    def options(self, v):
        pass

    def __getitem__(self, k):
        return self.widgets[k].value

    def __setitem__(self, k, v):
        set_widget(self.widgets[k], self.opts[k] , v)

def set_widget(w,opt, v):
    wType, pyType = Opt2Widget[opt.type]
    if opt.type == 'choice':
        w.options = v[1:]
        w.value = v[v[0]+1]
    else:
        w.value = pyType(v)

def create_widget(opt):
    if not opt.type:     assert(opt.action in ("store_true" , "store_false"))
    wType, pyType = Opt2Widget[opt.type]

    WidgetPropName={
        'choices':'options',
        'default':lambda x: ['value', pyType(x if not isinstance(x,(list,tuple)) else x[0])],
        'help':   lambda x: ["description", '{0} ({1})'.format(x, opt.dest)] ,
    }

    paras={ }
    for p,k in WidgetPropName.items():
        v = getattr(opt,p,None)
        if v:
            if callable(k):
                paras.update(dict([k(v)]))
            else:
                paras[k] = v
    paras.setdefault('description', opt.dest )
    if opt.type=='string' and opt.default==('NO','DEFAULT'):   paras['value']=''
    w = wType(**paras)

    return w

class MPL_Plotter(FilterBase):
    name = 'MPL_Plotter'

    def __init__(self, *value):
        super(MPL_Plotter, self).__init__( *value )
        from matplotlib import pyplot as ppl
        self.fig    = ppl.figure()
        self.axes   = self.fig.add_subplot(111)
        self.canvas = self.fig.canvas

    def update(self, src):
        # plot data from input
        data = self.input[0].result
        self.axes.plot(  data['x'], data['y'] )
        self.axes.set_xlabel(data['xlabel'])
        self.axes.set_ylabel(data['ylabel'])
        self.fig.tight_layout()
        from matplotlib import pyplot as ppl
        ppl.show()

class ApplicationWindow(object):
    def __init__(self, filters=[]):
        self.filters = filters
        for f in filters:
            assert (isinstance(f, FilterBase)), 'unexpected type of filter'

    def _runtimeline(self):
        self.filters[0].opt_time=1
        self.filters[1].opt_time=self.filters[1].mod_time+1
        self.filters[0].proc(None)

    def show(self):
        from IPython.display import display
        import matplotlib.pyplot as ppl

        def refresh(x):
            self._runtimeline()

        self.btn=widgets.Button(  description='Update' )

        self.btn.on_click(refresh)

        F_list=[]
        for n,f in enumerate(self.filters) :
            tab_list=[]
            for name, w in getattr(f,'widgets',[]).items():
                tab_list.append(w)
            F_list.append(widgets.VBox(tab_list))
        tab = widgets.Accordion(children= F_list )
        for n,f in enumerate(self.filters) :
            tab.set_title(n, '[+] '+f.name)
        display(tab)

        display(self.btn)

        self.plt=MPL_Plotter(self.filters[-1])
        ppl.show()
