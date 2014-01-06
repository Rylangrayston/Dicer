
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
scn = bpy.context.scene

objToSlice = bpy.context.active_object.name

#scn.objects.active = bpy.data.objects[objToSlice.name]  
bpy.context.area.type = 'VIEW_3D'



# I cant seem to get bisect to take a variable in a loop. Iv commmented this code out.
# there is no error but bisect() just uses the first value of i over and over. 
#for i in range(0, 5):  
#    bpy.data.scenes[0].update()
#    bpy.ops.object.duplicate()
#    bpy.ops.object.editmode_toggle()
#    i = 0
#    bpy.ops.mesh.bisect(plane_co=(0.0, 0.0, i), plane_no=(0.0, 0.0, 0.9), use_fill=False, clear_inner=True, clear_outer=True, threshold=0.0001)
#    
#    bpy.ops.object.editmode_toggle()
#    scn.objects.active = bpy.data.objects[objToSlice]  


# instead ill just hard code what the for loop would do with the following repetative code:
bpy.ops.object.duplicate()
##############################iter 1
bpy.data.scenes[0].update()
bpy.ops.object.duplicate()
bpy.ops.object.editmode_toggle()
bpy.ops.mesh.bisect(plane_co=(0.0, 0.0, 0), plane_no=(0.0, 0.0, 0.9), use_fill=False, clear_inner=True, clear_outer=True, threshold=0.0001)
bpy.ops.object.editmode_toggle()
scn.objects.active = bpy.data.objects[objToSlice]  

###############################iter 2
bpy.data.scenes[0].update()
bpy.ops.object.duplicate()
bpy.ops.object.editmode_toggle()
bpy.ops.mesh.bisect(plane_co=(0.0, 0.0, 2), plane_no=(0.0, 0.0, 0.9), use_fill=False, clear_inner=True, clear_outer=True, threshold=0.0001)
bpy.ops.object.editmode_toggle()
scn.objects.active = bpy.data.objects[objToSlice]  



bpy.context.area.type = 'TEXT_EDITOR'





# bpy.ops.mesh.bisect(plane_co=(0.0, 0.0, 0.0), plane_no=(0.0, 0.0, 0.0), use_fill=False, clear_inner=False, clear_outer=False, threshold=0.0001, xstart=0, xend=0, ystart=0, yend=0, cursor=1002)
#
#    Cut geometry along a plane (click-drag to define plane)
#    Parameters:	
#
#        plane_co (float array of 3 items in [-inf, inf], (optional)) – Plane Point, A point on the plane
#        plane_no (float array of 3 items in [-inf, inf], (optional)) – Plane Normal, The direction the plane points
#        use_fill (boolean, (optional)) – Fill, Fill in the cut
#        clear_inner (boolean, (optional)) – Clear Inner, Remove geometry behind the plane
#        clear_outer (boolean, (optional)) – Clear Outer, Remove geometry in front of the plane
#        threshold (float in [0, 10], (optional)) – Axis Threshold
#        xstart (int in [-inf, inf], (optional)) – X Start
#        xend (int in [-inf, inf], (optional)) – X End
#        ystart (int in [-inf, inf], (optional)) – Y Start
#        yend (int in [-inf, inf], (optional)) – Y End
#        cursor (int in [0, inf], (optional)) – Cursor, Mouse cursor style to use during the modal operator
#
#
#
#
