
            ##################################
            #              Dicer
            #blenders inernal slicer for 3d printing
            ##################################


#hey blender community Im working on an internal slicer for blender, to be used by 3d printers, Im going to call it Dicer for now because if it
# ends up working the way I think it will that will make sense.
# most of the work can be done by the new bisect() tool! which basically makes each slice.
# note that you may need a newer that stable relice of blender which has bpy.ops.mesh.bisect()

# so the plan as it stands now is to slice the selected object on the z axis using bisect(), and then convert the vertex xy locations to g-code, and or wav file(peachy printer).
# once we have that basic functionality The next important thing to do is detect faces that are too flat on the z axis and may be missed by the
# sliceing entirely! to solve this lets just create a function called overHangFaces(allFacesInCurrentZLayer) which will run thru all
# the face normals checking wich ones are pointed nearly straight up  or down in the current z
# and retun them in a list.

#next we need to put the faces returned from overHangFaces() thre a function called rasterFace(face) Which is fairly self explanatory.
# after that we just need to tackle in fill which id rather just do with a big block of infill and a unifi bolean modifier before sliceing.
# oh and I think suport material is best just done by hand for now.

# most importantly I want to write this slicer in a way that we can ask for each slice as the printer needs it.
# That is important for many reasons:
# 1. It will mean that you can hit print on your 3d printer and make changes to anything that hasten printed yet.
# 2. It will mean that the time that it takes to process the slicing can happen during the time it takes to print the model(other than a small buffer)
#    If you have used a 3d printer befor you will know how valuable this time is ... at our hacker space its a 2-3 hour process involving 3 or more programs
#    and file types just to get one print out!
# 3. It will mean you can click print before you have evan finished modeling, ie you could modle just ahead of the printer while it actually prints.
#    which could make for some fun speed modeling competitions :)

# a big thanks to who ever wrote bisect()  !! thats where all the magic happens
# hopefully this actually becomes blender internal but for now here is a quick script that shows that its already possible with a little bpy.
# Chears, Rylan Grayston.

import bpy
import mathutils
import math
from mathutils import Vector
import traceback

class DiceIt(object):
    def __init__(self, writer, layer_thickness, first_layer = 1, last_layer = 0):
        self.first_layer = 1
        self.layer_thickness = layer_thickness
        self.original = bpy.context.active_object
        if (self.original == None):
            raise Exception('No object selected')
        self.total_layers = math.ceil(self.original.dimensions.z / self.layer_thickness)

        if (last_layer == 0):
        	self._last_layer = self.total_layers
       	elif (last_layer <= self.total_layers):
       		self._last_layer = last_layer
       	else:
       		self._last_layer = self.total_layers

        print('Thickness   : %f' % self.layer_thickness)
        print('Total Layers: %d'  % self.total_layers)


    def run(self):
        print('Starting Calculations')
        original_mesh = self.original.to_mesh(bpy.context.scene, apply_modifiers = False, settings = 'PREVIEW', calc_tessface=False, calc_undeformed=False)
        self.original.data = self.original.to_mesh(bpy.context.scene, apply_modifiers = True, settings = 'PREVIEW', calc_tessface=False, calc_undeformed=False)
        omw = self.original.matrix_world
        zps = [(omw*vert.co)[2] for vert in self.original.data.vertices]
        maxz, minz = max(zps), min(zps)


        o = 0
        for sob in bpy.context.scene.objects:
            try:
                if sob['Slices']:
                    ob, me, o = sob, sob.data, 1
            except:
                pass


        if o == 0:
            me = bpy.data.meshes.new('Slices')
            ob, ob['Slices']  = bpy.data.objects.new('Slices', me), 1
            bpy.context.scene.objects.link(ob)
            
        bpy.context.scene.objects.active = self.original


        vlen = len(me.vertices)
        try:
            for ln in range(self.first_layer, self._last_layer):
                layer_height = minz + ln * self.layer_thickness
                
                if layer_height < maxz:
                    bpy.ops.object.mode_set(mode = 'EDIT')
                    bpy.ops.mesh.select_all(action = 'SELECT')
                    bpy.ops.mesh.bisect(plane_co=(0.0, 0.0, layer_height), plane_no=(0.0, 0.0, 1), use_fill=False, clear_inner=False, clear_outer=False, threshold=0.0001, xstart=0, xend=0, ystart=0, yend=0, cursor=1002)
                    bpy.ops.object.mode_set(mode = 'OBJECT')
                    coords, vlist, elist = [], [], []
                    sliceverts = [vert for vert in self.original.data.vertices if vert.select== True]
                    sliceedges = [edge for edge in self.original.data.edges if edge.select == True]


                    for vert in sliceverts:
                        me.vertices.add(1)
                        me.vertices[-1].co = omw*vert.co
               
                    for edge in sliceedges:
                        me.edges.add(1)
                        me.edges[-1].vertices[0] = me.vertices[[vert.index for vert in sliceverts].index(edge.vertices[0])+vlen].index
                        me.edges[-1].vertices[1] = me.vertices[[vert.index for vert in sliceverts].index(edge.vertices[1])+vlen].index
                    vlen = len(me.vertices)
                        
                    elist.append(sliceedges[0]) # Add this edge to the edge list
                    vlist.append(elist[0].vertices[0]) # Add the edges vertices to the vertex list
                    vlist.append(elist[0].vertices[1])
                    while len(vlist) < len(sliceverts):
                        va = 0
                        for e in sliceedges:
                             if e.vertices[0] not in vlist and e.vertices[1] == vlist[-1]: # If a new edge contains the last vertex in the vertex list, add the other edge vertex
                                 va = 1
                                 vlist.append(e.vertices[0])
                                 elist.append(e)
                             if e.vertices[1] not in vlist and e.vertices[0] == vlist[-1]:
                                 va = 1
                                 vlist.append(e.vertices[1])
                                 elist.append(e)
                             elif e.vertices[1] in vlist and e.vertices[0] in vlist and e not in elist: # The last edge already has it's two vertices in the vertex list so just add the edge
                                 elist.append(e)
                                 va = 1
                        if va == 0: #If no new edge was added a new ring of edges needs to be started
                             e1 = [e for e in sliceedges if e not in elist][0] # Select a new edge not in the edge list
                             elist.append(e1)
                             vlist.append(e1.vertices[0])
                             vlist.append(e1.vertices[1])
                    for sv in vlist:
                        coords.append((omw*self.original.data.vertices[sv].co)[0:2])
                    writer.moveToHeight(layer_height)
                    writer.drawPath(coords)
            self.original.data = original_mesh
        except Exception as e:
            print(traceback.format_exc())
            print('Dang it Broke: The model may be leaky')
            self.original.data = original_mesh

class MoveModes:
    RAPID = 'rapid'
    FEED = 'feed'

class GcodeWriter(object):
    """Takes layer information from the Blender slicer and saves it to a file in GCODE format."""
    def __init__(self, file, feed_rate, rapid_rate):
        self._file = file
        self._feed_rate = feed_rate
        self._rapid_rate = rapid_rate
        self._move_mode = None
        self._current_height = None
        self._current_location = None

    def moveToHeight(self, height):
        if self._current_height is not None:
            if height < self._current_height:
                raise AssertionError('Requested to move back down from height %f to height %f!' % (
                    self._current_height, height
                ))
            if height == self._current_height:
                return
        self._set_move_mode(MoveModes.RAPID)
        self._file.write('G1 Z%.2f F%.2f\n' % (height, self._rapid_rate))
        self._current_height = height

    def drawPath(self, path):
        if self._current_location is None or self._current_location != path[0]:
            self._set_move_mode(MoveModes.RAPID)
            self._move_to_location(path[0])
        self._set_move_mode(MoveModes.FEED)
        for location in path[1:]:
            self._move_to_location(location)

    def _set_move_mode(self, mode):
        if self._move_mode != mode:
            if mode == MoveModes.RAPID:
                self._file.write('M103\n')
            elif mode == MoveModes.FEED:
                self._file.write('M101\n')
            else:
                raise AssertionError('Unknown move mode "%s"' % mode)
            self._move_mode = mode

    def _move_to_location(self, location):
        if location == self._current_location:
            return
        if self._move_mode == MoveModes.FEED:
            rate = self._feed_rate
        elif self._move_mode == MoveModes.RAPID:
            rate = self._rapid_rate
        else:
            raise AssertionError('Unexpected move mode "%s"' % self._move_mode)
        self._file.write('G1 X%.2f Y%.2f F%.2f\n' % (location[0], location[1], rate))
        self._current_location = location

#manual run

path = 'output.gcode'
feed_rate = 100
rapid_rate = 600
slice_thinkness = 0.1

from os.path import expanduser, join
home = expanduser("~")
output_file = open(join(home,path),'w')
writer = GcodeWriter(output_file, feed_rate, rapid_rate)
dice_it = DiceIt(writer, slice_thinkness)
dice_it.run()
print('Complete')