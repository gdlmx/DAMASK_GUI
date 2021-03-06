from __future__ import unicode_literals

from .Filter import FilterBase
import sys, os, random, time, warnings
from ipywidgets import widgets
from IPython.display import display

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

    def to_recalc(self, *args, **vargs):
        self.opt_time = self.mod_time + 1

    def set_optparser(self, p):
        """ read optparse.OptionParser object """
        self.options_def = []
        self.widgets={}
        self.opts   ={}
        for opt in p.option_list:
            if not opt.dest: continue
            key = opt.dest
            wdg = create_widget(opt)
            if hasattr(wdg, 'observe'):
                 wdg.observe(self.to_recalc)
            if hasattr(wdg, 'on_submit'):
                 wdg.on_submit(self.to_recalc)
            self.widgets[key] = wdg
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
        self._init_fig()

    def _init_fig(self):
        from matplotlib import pyplot as ppl
        print('Creating new figure')
        self.fig    = ppl.gcf()
        self.axes   = self.fig.add_subplot(111)
        self.canvas = self.fig.canvas
        ppl.show()

    def update(self, src):
        # plot data from input
        from matplotlib import pyplot as ppl
        data = self.input[0].result
        self.axes.plot(  data['x'], data['y'] )
        self.axes.set_xlabel(data['xlabel'])
        self.axes.set_ylabel(data['ylabel'])
        self.fig.tight_layout()
        self.axes.relim()
        self.fig.canvas.draw()
        # update ax.viewLim using the new dataLim
        # self.plt.axes.autoscale_view()

    def clear(self):
        from matplotlib import pyplot as ppl
        self.axes.clear()
        self.axes.cla()
        gca = ppl.gca()
        if not self.axes is gca:
            self._init_fig()
        self.axes.clear()
        self.axes.cla()

class ApplicationWindow(object):
    def __init__(self, filters=[]):
        self.filters = filters
        for f in filters:
            assert (isinstance(f, FilterBase)), 'unexpected type of filter'

    def _runtimeline(self):
        #self.filters[0].opt_time=1
        #self.filters[1].opt_time=self.filters[1].mod_time+1
        self.filters[0].proc(None)

    def get_or_create(self, propname, f):
        if not hasattr(self, propname):
            setattr(self, propname, f(self))
        return getattr(self,propname)

    def redrawfig(self, *args):
        import matplotlib.pyplot as ppl
        for f in self.filters:
            if f.name.startswith('Plot'):
                f.to_recalc()

        if not self.wdg_isholdon.value:
            self.plt.clear()
        self._runtimeline()
        #ppl.draw()

    def new_view(self, *args):
        display(self.plt.fig)

    def show(self):
        F_list=[]
        for n,f in enumerate(self.filters) :
            tab_list=[]
            for name, w in sorted(getattr(f,'widgets',{}).items()):
                tab_list.append(w)
            F_list.append(widgets.VBox(tab_list))
        tab = widgets.Accordion(children= F_list )
        for n,f in enumerate(self.filters) :
            tab.set_title(n, '[+] '+f.name)
        display(tab)

        btn = self.get_or_create( 'btn',
            lambda x: widgets.Button(  description='Refresh & Draw' )
            )
        btn.on_click(self.redrawfig)
        display(btn)

        btn_dupfig = self.get_or_create( 'btn_dupfig',
            lambda x: widgets.Button(  description='+' )
            )
        btn_dupfig.on_click(  self.new_view )
        display(btn_dupfig)

        wdg_isholdon = self.get_or_create('wdg_isholdon',
            lambda x: widgets.Checkbox(description='Hold on', value=False)
            )
        display(wdg_isholdon)


        plt = self.get_or_create('plt',
            lambda x: MPL_Plotter(self.filters[-1])
            )

        #display(plt.fig)

    def _patch_ipywidget_style_(self):
        from IPython.display import display, HTML
        css = """<style>
        .widget-label{  background-color:#F0F0F0;  max-width:30% !important;}
        .widget-label,.widget-text,.widget-checkbox{ width : 100%}
        div.output_subarea.output_text.output_error {max-height: 10em;}
        //::before{  content: "<a class=plus href=#>[+]</a><a href=#>[-]</a>"; }
        div.output_subarea.output_text.output_error:hover{ max-height: 100%;}
        div.output_subarea .ansired{display:inline}
        //a.plus-expand:focus{display: none}
        //a.plus-expand:not(:focus)~a{visibility: hidden}
        //a:focus~div.output_subarea{  max-height: 100%; }
        </style>"""
        display(HTML(css))

