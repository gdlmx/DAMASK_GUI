#Copyright (c) 2015 Mingxuan Lin

from ..ui import UIFilter
from .GeomFile import GeomFile
import numpy as np
from optparse import OptionParser
import h5py

# positional parameters
parser = OptionParser( usage='%prog [options] datafile', description = "", version = "")
parser.add_option('-i', '--in', dest='read_from',  metavar = 'FILE', help='dream3d file')
parser.add_option('-o', '--out', dest='geomFileName',  metavar = 'FILE', help='geometry file')
parser.add_option('--homogenization', dest='homogenization', type='int',  default=1, help='homogenization index to be used [%default]')


class Dream3dReader(UIFilter):
    name = 'Read synthetic microstructure of Dream3D'
    opt_time = 1
    
    def __init__(self, *value):
        super(Dream3dReader, self).__init__( *value )
        self.set_optparser(parser)

    def update(self, src=None):
        ifName = self.options['read_from']
        ofName = self.options['geomFileName']
        
        f = h5py.File(ifName, "r")
        synDat     = f['DataContainers']['SyntheticVolumeDataContainer']
        FeatureIds = synDat['CellData']['FeatureIds']
        spc        = synDat['_SIMPL_GEOMETRY']['SPACING']
        EulerAng   = synDat['CellFeatureData']['EulerAngles']
        PhaseID    = synDat['CellFeatureData']['Phases']
        
        arr = np.zeros(FeatureIds.shape, dtype='int32')
        FeatureIds.read_direct(arr)
        
        mesh=GeomFile(FeatureIds.shape[:3])
        mesh.info['size']          = spc * mesh.info['grid']
        mesh.info['homogenization']= self.options['homogenization']
        #mesh.info['origin']        = 
        mesh.microstructure = arr
        
        f.close()
        
        with open(ofName, 'w') as of:
            mesh.enforceIntegrity()
            mesh.write(of)
        self.mod_time =  self.opt_time 


if __name__ == "__main__":
    (options, args) = parser.parse_args()
    options.read_from = args[0]
    m = Dream3dReader()
    m.options = vars(options)
    m.opt_time=m.mod_time+1
    m.proc()