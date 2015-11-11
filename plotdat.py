#Copyright (c) 2015 Mingxuan Lin
import matplotlib.pyplot as plt
from pylab import *
import numpy as np
from optparse import OptionParser

def vMstress(S):
  S = np.array(S)
  S = S.reshape([3,3])
  S = S - (np.trace(S)/3.0)*np.eye(3)
  return np.sqrt(1.5 * np.sum(S**2))
  
def unpack_vec(y):
  f = lambda x: x if x else 0
  for k in range(4):
    try:
      if k==0:
        y1 = map(f,y)
      if k==1 and len(y[0])==9:
        y1 = map(vMstress, y);
      elif k==2:
        y1 = [i[0] for i in y]
      elif k==3:
        y1 = [i[0][0] for i in y]
      y1[0]**2
      return y1
    except TypeError:
      if k>=3: raise

if __name__ == "__main__":
    import re
    import json as pkl
    # positional parameters
    parser = OptionParser( usage='%prog [options] datafile', description = "parse DAMASK spectral terminal output", version = "beta1.0")
    parser.add_option('-o', '--out', dest='outfile',  metavar = 'FILE', help='name of output file')
    parser.add_option('-F',  dest='field',  metavar = 'hist_inc|hist_itr', default="hist_inc",  help='field')
    parser.add_option('-x',  dest='x',  metavar = 'NAME', default="inc", help='x')
    parser.add_option('-y',  dest='y',  metavar = 'NAME', default="Piola--Kirchhoff stress / MPa", help='y')
    parser.add_option('-l',  dest='is_list',  action = 'store_true',   help='list')
    (options, args) = parser.parse_args()
    
    with open(args[0],"rb") as f:
      a=pkl.load(f)
      
    if options.is_list:
      for k in a:
        print '[{0}]'.format(k)
        try:
          print '\t' + '\n\t'.join( a[k].keys() )
        except AttributeError:
          pass
      exit()

    y = unpack_vec(a[options.field][options.y]);
    x = unpack_vec(a[options.field][options.x]);
    
    plt.plot(x, y )
    plt.xlabel(options.x)
    plt.ylabel(options.y)
    
    if options.outfile:
      xname = ''.join(re.findall(r'\w+',options.x))
      yname = ''.join(re.findall(r'\w+',options.y))
      plt.savefig('['+xname+']-['+yname+']--'+options.outfile)
    else:
      plt.show()
