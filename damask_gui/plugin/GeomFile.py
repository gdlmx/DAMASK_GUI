# -*- coding: UTF-8 no BOM -*-
# Copyright 2015 Mingxuan Lin 

import math
import numpy as np

class GeomFile(object):
    ofilename=""
    info={}
    microstructure=None
    header_fmt={}
    header_order=['grid' , 'size' , 'origin' , 'microstructures' , 'homogenization']
    header_dType={'grid':'int' , 'size': 'double' , 'origin': 'double' , 'microstructures':'int' , 'homogenization':'int'}


    def __init__(self,grid):
        self.info = {
            'grid'            : np.array (grid[:3],'i'),
            'size'            : np.ones(3,'d'),
            'origin'          : np.zeros(3,'d'),
            'microstructures' : 1,
            'homogenization'  : 1}
        self.header_fmt={
            'grid'     : "grid\ta {0:d}\tb {1:d}\tc {2:d}",
            'size'     : "size\tx {0:f}\ty {1:f}\tz {2:f}",
            'origin'   : "origin\tx {0:f}\ty {1:f}\tz {2:f}"}
        self.microstructure = np.zeros(grid[-1:-4:-1],'i')

    def enforceIntegrity(self):
        grid = self.info['grid']
        self.microstructure = self.microstructure.reshape( [grid[2]*grid[1], grid[0]] )
        self.info['microstructures'] = int(np.amax(self.microstructure))


    def write(self,ostr, onlyheader=False):
        # Order the headers stored in self.info
        OrderedItems  = [(k, self.info[k]) for k in self.header_order] + \
                        [(k, v) for k,v in self.info.items() if not k in self.header_order]
        # Fill the headers entries into the list >header<
        header = []
        for k,v in OrderedItems:
            try: iter(v)
            except TypeError: 
                v=[v,]
            try:
                header.append( self.header_fmt[k].format(*v) )
            except KeyError:
                header.append( k + '\t' + '\t'.join(str(i) for i in v)  )
        # Write the header into file
        header_str = '\n'.join(['%i\theader'%(len(header))] + header) + '\n'
        print header_str
        ostr.write(header_str)
        if onlyheader:
            return
        # Write the grid values
        digit_field_len = 1+int(np.log10(np.amax(self.microstructure)))
        np.savetxt(ostr, self.microstructure, fmt='%{0:d}d'.format(digit_field_len))
        
    def export2vts(self, filename):
        import vtk
        grid = self.info['grid']
        # Set grid points
        points = vtk.vtkPoints()
        for z in range (grid[2]):
          for y in range (grid[1]):
            for x in range (grid[0]):
              points.InsertNextPoint( [x , y , z ] )
        struGrid = vtk.vtkStructuredGrid()
        struGrid.SetDimensions( grid )
        struGrid.SetPoints( points )
        struGrid.Update()
        # Set point data
        grid_pt_num = struGrid.GetNumberOfPoints()
        array = vtk.vtkIntArray()
        array.SetNumberOfComponents(1) # this is 3 for a vector
        array.SetNumberOfTuples(grid_pt_num)
        array.SetName('MicrostructureID')
        matPoint = self.microstructure.reshape( [grid_pt_num] )
        for i in range(grid_pt_num):
            array.SetValue(i, matPoint[i])
        struGrid.GetPointData().AddArray(array)
        struGrid.Update()
        # Write output file
        outWriter = vtk.vtkXMLStructuredGridWriter()
        outWriter.SetDataModeToBinary()
        outWriter.SetCompressorTypeToZLib()
        outWriter.SetFileName( filename + '.vts' )
        outWriter.SetInput(struGrid)
        outWriter.Update()
        outWriter.Write()
        
    def read(self, ifile):
        header_len = None
        header_togo= None
        line_no = 0
        data_type = self.header_dType 
        # read header
        for line in ifile:
            line_no += 1
            cells = line.strip().lower().split()
            if len(cells)>=2:
              if cells[1]=="header":
                header_len = int(cells[0])
                header_togo=header_len
                continue
              if header_togo==0:
                break
              elif header_togo:
                header_togo-=1
                k = cells[0]
                value = []
                for v in cells[1:]:
                    try:  value.append(float(v.strip()))
                    except ValueError: pass
                self.info[k] = np.array(value, data_type.get(k,'float'))
        # read data
        griddim = self.info['grid']
        ifile.seek(0,0)
        matPoint = np.loadtxt(ifile,'int', skiprows=header_len+1)
        self.microstructure = matPoint.reshape( *griddim[-1:-4:-1] )

