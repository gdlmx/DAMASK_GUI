#Copyright (c) 2015 Mingxuan Lin

from .ui import *
import numpy as np
from optparse import OptionParser
import re

  
def Mises(tensor , mtype='stress'):
    tensor = np.array(tensor).reshape([3,3])
    PreFact = {'stress': 3.0/2.0, 'strain': 2.0/3.0}[mtype]
    dev = tensor - np.trace(tensor)/3.0*np.eye(3)
    symdev = 0.5*(dev+dev.T)
    return np.sqrt( np.sum(symdev**2) * PreFact)

def P2S(P, F):
    F = np.array(F).reshape([3,3])
    P = np.array(P).reshape([3,3])
    return 1.0/np.linalg.det(F)*np.dot(P,F.T)                 # [Cauchy] = (1/det(F)) * [P].[F_transpose]

def F2Strain(F, theStretch='V', theStrain = 'ln'):
    F = np.array(F).reshape([3,3])
    def operator(stretch,strain,eigenvalues):
        return {
            'V#ln':    np.log(eigenvalues)                                 ,
            'U#ln':    np.log(eigenvalues)                                 ,
            'V#Biot':  ( np.ones(3,'d') - 1.0/eigenvalues )                ,
            'U#Biot':  ( eigenvalues - np.ones(3,'d') )                    ,
            'V#Green': ( np.ones(3,'d') - 1.0/eigenvalues*eigenvalues) *0.5,
            'U#Green': ( eigenvalues*eigenvalues - np.ones(3,'d'))     *0.5,
               }[stretch+'#'+strain]
    (U,S,Vh) = np.linalg.svd(F)
    R = np.dot(U,Vh)
    stretch={}
    stretch['U'] = np.dot(np.linalg.inv(R),F)
    stretch['V'] = np.dot(F,np.linalg.inv(R))
    
    for i in range(9):
      if abs(stretch[theStretch][i%3,i//3]) < 1e-12:                                            # kill nasty noisy data
        stretch[theStretch][i%3,i//3] = 0.0
    (D,V) = np.linalg.eig(stretch[theStretch])                        # eigen decomposition (of symmetric matrix)
    for i,eigval in enumerate(D):
      if eigval < 0.0:                                                                          # flip negative eigenvalues
        D[i] = -D[i]
        V[:,i] = -V[:,i]
    if np.dot(V[:,i],V[:,(i+1)%3]) != 0.0:                                                      # check each vector for orthogonality
        V[:,(i+1)%3] = np.cross(V[:,(i+2)%3],V[:,i])                                            # correct next vector
        V[:,(i+1)%3] /= np.sqrt(np.dot(V[:,(i+1)%3],V[:,(i+1)%3].conj()))                       # and renormalize (hyperphobic?)
    d = operator(theStretch,theStrain,D)                              # operate on eigenvalues of U or V
    return np.dot(V,np.dot(np.diag(d),V.T)).real                      # build tensor back from eigenvalue/vector basis

  
def unpack_vec(y, k=0):
    try:
        if k==0:
          f = lambda x: x if x else 0
          y1 = map(f,y)
        elif k==1:
          y1 = [i[0] for i in y]
        elif k==2:
          y1 = [i[0][0] for i in y]
        else:
          raise ValueError()
        y1[0]**2
        return y1
    except TypeError:
        return unpack_vec(y, k+1)

# positional parameters
parser = OptionParser( usage='%prog [options] datafile', description = "", version = "")
parser.add_option('-o', '--out', dest='outfile',  metavar = 'FILE', help='name of output file')
parser.add_option('-F',  dest='field',  choices = ['hist_inc','hist_itr'], default="hist_inc",  help='field')
parser.add_option('-x',  dest='x',  choices = ["inc",'acc_itr'], default="inc")
parser.add_option('-y',  dest='y',  choices = ["Piola--Kirchhoff stress / MPa",'time'], default="Piola--Kirchhoff stress / MPa")
#parser.add_option('-l',  dest='is_list',  action = 'store_true',   help='list')


class PlotXY(UIFilter):
    name = 'Plot x,y'
    opt_time = 1
    
    def __init__(self, *value):
        super(PlotXY, self).__init__( *value )
        self.result = {'x':[0], 'y':[0], 'xlabel':'x', 'ylabel':'y'}
        self.set_optparser(parser)
        
    def update(self, src=None):
        options = self.options
        a = self.input[0].result
        field = a[options["field"]]
        
        # update UI
        #field_keys = a.keys()
        data_keys = field.keys()
        fId, xId, yId = [0]*3
        try:
            #fId = field_keys.index(options["field"])
            xId = data_keys.index(options["x"])
            yId = data_keys.index(options["y"])
        except ValueError:
            pass
        
        self.update_QComboBox({ "x":[xId]+data_keys, 'y': [yId]+data_keys }) #"field":[fId]+field_keys,
        
        # set result
        oFileName=[]
        for k in ['x','y']:
            label = options[k]
            value = field[label]
            if label.lower().startswith( 'piola--kirchhoff' ) and len(value[0])==9:
                self.result[k]  = [Mises( P2S(P,F)  ) for P,F in zip( value, field['deformation gradient aim'] )]
                label = 'Mises(Cauchy)'
            elif label.lower().startswith( 'deformation gradient' ) and len(value[0])==9:
                self.result[k]  = [Mises(F2Strain(i),'strain') for i in value]
                label = 'ln(V)'
            else:
                self.result[k]  = unpack_vec(value)
            self.result[k+'label']  = label
            oFileName.append( ''.join(re.findall(r'\w+',label)) )
        
        if options["outfile"].strip():
            import json as pkl
            oFileName.append(options["outfile"])
            with open('--'.join(oFileName)+'.json','wb') as of:
                pkl.dump( self.result, of )
        self.mod_time = max( self.opt_time, self.input[0].mod_time )


if __name__ == "__main__":
    (options, args) = parser.parse_args()
    #m = PlotXY()
    #m.options = vars(options)
    #m.update()
    #if options["is_list"]:
    #  for k in a:
    #    print '[{0}]'.format(k)
    #    try:
    #      print '\t' + '\n\t'.join( a[k].keys() )
    #    except AttributeError:
    #      pass
    #import re
    
