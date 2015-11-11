# -*- coding: utf-8
# Copyright (c) 2015 Mingxuan Lin
"""Parser for the terminal output (stdout) of DAMASK spectral program
"""
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
import codecs, sys,  re
import pdb

def arch_dict(arch, d):
    # assumed that arch is initially empty
    existing_keys = set(arch.keys()).intersection(d.keys())
    L0 = len(arch[existing_keys.pop()]) if existing_keys and len(existing_keys)<len(d) else 0
    for k,v in d.items():
      try:
        arch[k].append(v)
      except KeyError:
        arch[k] = [None]*L0 + [v]

#TODO: add rules for init echo
stdout_parser = Grammar("""
 main = element+
 element = iter_begin / iter_end / timestep / inc_end / incr_sep / infoline / ep / nl+ / any
 
 iter_begin = ws inc_num ws "@" ws  ~"Iteration +(\d+[^\d\s]){2}\d+"  nl
 iter_end   = ws ~"=+" nl
 
 timestep   = ws "Time" float "s:" ws inc_num  ~" +of load case +\d+/\d+" nl
 inc_end    = ws "increment" integer ws "converged" nl
 
 inc_num= "Increment" ws ~"(\d+)/(\d+)-(\d+)/(\d+)"
 
 incr_sep   = ws ~"#+" nl
 infoline   = ws dotsline ws keywords dotsline nl

 ep         = ws keywords  ~" *=" float+ ws range? nl
 range= "(" float  ~"[a-z ,=/]+"i  float  ")"

 any        = ~"(.+\\n?)|\\n"

 dotsline = ~"\.+"
 float    = ~"\s*?[-+]?\d*\.?\d+([eE][-+]?\d+)?"
 integer  = ~"\s*?[-+]?\d+"
 keywords = ~"([\w\-/]+ *)+"
 nl       = ws "\\n"
 ws       = ~"[ \t\v\f]*"
""")

class DamaskVisitor(NodeVisitor):
  def __init__(self, g):
    self.grammar = g
    self.unparsed=''
    
    self.prop = {}
    self.stat = {}
    self.hist_inc = {}         # convergedProp: converged quantities of each increment  
    self.hist_itr = {}         # quantities of each iteration  
    
  def visit_timestep(self, node, visited_children):
    # begin of increment/timestep
    # e.g. " Time 1.00000E+00s: Increment 1/600-1/1 of load case 1/1 "
    self.prop['time']  = float(node.children[2].text)
    self.prop.update(zip(
        ['inc', 'total_inc', 'sub_inc', 'total_sub_inc'], 
        self.get_inc(node.children[5])                  ))

  def visit_ep(self, node, visited_children):
    # expression
    # e.g. "error divergence =        91.97 (2.28E+06 / m, tol = 2.48E+04)"
    n_kw, n_values, n_range = node.children[1], node.children[3], node.children[5]
    name = n_kw.text.strip()
    value = tuple(float(v.text) for v in n_values if v.expr_name == "float")
    if n_range.children:
        ext_value = tuple(float(v.text) for v in n_range.children[0] if v.expr_name == "float")
        self.prop[name] = (value, ext_value)
    else:
        self.prop[name] = value

  def visit_iter_begin(self, node, visited_children):
    # begin of iteration
    # e.g. "Increment 300/300-1/1 @ Iteration 04?05?40"
    inc     = self.get_inc(node.children[1])
    assert (inc[0] == self.prop['inc']),  'the increment numbers mismatch\n' + node.text
    itr_num = [ int(v) for v in re.findall(r'\d+', node.children[5].text)]
    self.prop.update(zip(  ['itr_min', 'itr', 'itr_max']  ,  itr_num))
    self.count('acc_itr')
    
  def visit_inc_end(self, node, visited_children):
    # store converged results
    # e.g. "increment 1 converged"
    inc = int(node.children[2].text)
    assert (inc == self.prop['inc']),  'the increment numbers mismatch\n' + node.text
    self.append_hist(self.hist_inc)

  def visit_iter_end(self, node, visited_children):
    # store iteration results
    # e.g. "======================"
    self.append_hist(self.hist_itr)
    
    
  def visit_infoline(self, node, visited_children):
    # report certain operations
    # e.g. "... evaluating constitutive response ......................................"
    name = node.children[3].text.strip()
    self.count(name)

  def visit_any(self, node, visited_children):
    if node.text.strip():
      self.unparsed += node.text

  def generic_visit(self, node, visited_children):
    pass

  def get_inc(self, inc_num):
    return map(int,inc_num.children[2].match.groups())
    
  def count(self,name):
    try:
      self.stat[name] +=  1
    except KeyError:
      self.stat[name] = 0
    
  def append_hist(self, hist):
    arch_dict(hist, self.prop)
    arch_dict(hist, self.stat)
    L = map(len, hist.values())
    assert(min(L)==max(L)), 'history data corrupted\n' +  '\n'.join(map(str, zip(hist.keys(), L) )) + '\n'

  


if __name__ == "__main__":
    from optparse import OptionParser
    # positional parameters
    parser = OptionParser( usage='%prog [options] datafile', description = "parse DAMASK spectral terminal output", version = "beta1.0")
    parser.add_option('-o', '--out', dest='outfile',  metavar = 'FILE', help='name of output file')
    parser.add_option('-d', '--dump', dest='dumpfile',  metavar = 'FILE', help='name of dump file')
    (options, args) = parser.parse_args()

    # open input file
    with  codecs.open(args[0],"r",'utf-8') as file_in:
        file_data = file_in.read()

    # parse
    m = DamaskVisitor(stdout_parser)
    data = stdout_parser.parse( file_data )
    m.visit(data)

    # save results
    if options.dumpfile:
      with open(options.dumpfile,'w') as df:
        df.write(m.unparsed)

    # pickle the result object
    if options.outfile:
      import json as pkl
      data = {}
      for k in dir(m):
        v_k = getattr(m, k)
        if isinstance(v_k, (dict, basestring, list, tuple))  and k!="grammar" and not k.startswith('_'): 
          data[k] = v_k
      with open(options.outfile,'wb') as of:
        pkl.dump( data, of )