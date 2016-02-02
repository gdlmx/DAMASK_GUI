# -*- coding: utf-8 -*-
__copyright__ = "Copyright (C) 2015 Mingxuan Lin"

__help__ = """
Dream3D Reader
==============

Transform the Dream3D RVE into DAMASK 'geometry' and 'material configuration' files.

"""

from ..ui import UIFilter
from .GeomFile import GeomFile
import numpy as np
from optparse import OptionParser
import h5py

# positional parameters
parser = OptionParser( usage='%prog [options] datafile', description = __help__, version = "")
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
        # fetch data arrays
        synDat     = f['DataContainers']['SyntheticVolumeDataContainer']
        FeatureIds = synDat['CellData']['FeatureIds']
        spc        = synDat['_SIMPL_GEOMETRY']['SPACING']

        EulerAng   = synDat['CellFeatureData']['EulerAngles']
        PhaseID    = synDat['CellFeatureData']['Phases']

        # copy and translate array shape
        arr  = deepCopyH5Array(FeatureIds)
        ph   = deepCopyH5Array(PhaseID)
        ph   = ph[1:].squeeze()
        eulr = deepCopyH5Array(EulerAng)
        eulr = eulr[1:] * (180.0/np.pi)

        # build mesh
        mesh=GeomFile(FeatureIds.shape[:3])
        mesh.info['size']          = spc * mesh.info['grid']
        mesh.info['homogenization']= self.options['homogenization']
        #mesh.info['origin']        =
        mesh.microstructure = arr
        mesh.enforceIntegrity()

        f.close()

        # write output
        with open(ofName, 'w') as of:
            mesh.write(of)

        with open(ofName+'.material.config', 'w') as of:
            saveMicroConfig(of, ph, eulr)

        # write result
        self.result['x'] =  np.arange(1, len(ph)+1)
        self.result['xlabel'] =  'microstructure id'
        self.result['y'] =  ph
        self.result['ylabel'] =  'phase id'
        self.mod_time =  self.opt_time


def deepCopyH5Array(A):
    # return A.value.copy()
    arr = np.zeros(A.shape, dtype=A.dtype)
    A.read_direct(arr)
    return arr

micro_tmpl = """[Grain{0:02d}]
crystallite 1
(constituent)  phase {1:d}   texture {0:02d}   fraction 1.0
"""

texture_tmpl = """[Grain{0:02d}]
(gauss)  phi1 {1:7.3f}    Phi {2:7.3f}    phi2 {3:7.3f}   scatter 0.0   fraction 1.0
"""
def saveMicroConfig(f, ph, euler):
    f.write("#-------------------#\n<microstructure>\n#-------------------#\n")

    for g, p in enumerate(ph,1):
        f.write(micro_tmpl.format(g, p))

    f.write('\n'*2+"#-------------------#\n<texture>\n#-------------------#\n")

    for g, e in enumerate(euler,1):
        f.write(texture_tmpl.format(g, e[0], e[1], e[2]))

if __name__ == "__main__":
    (options, args) = parser.parse_args()
    if args:
        options.read_from = args[0]
    m = Dream3dReader()
    m.options = vars(options)
    m.opt_time=m.mod_time+1
    m.proc()
