import bpy
import bmesh
from mathutils import Matrix

scene = bpy.context.scene
ob = bpy.context.object
me = ob.data

bm = bmesh.new()
bm.from_mesh(me)
#bm.from_object(ob, scene)
bm.transform(ob.matrix_world)

#bmesh.ops.triangulate(bm, faces=bm.faces)

cut_verts = []
cut_edges = []

for i in range(-10, 10):
    ret = bmesh.ops.bisect_plane(bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:],
              plane_co=(0,0,i), plane_no=(0,0,-1))
    
    cut_verts.extend([v.index for v in ret['geom_cut'] if isinstance(v, bmesh.types.BMVert)])
    cut_edges.extend([e.index for e in ret['geom_cut'] if isinstance(e, bmesh.types.BMEdge)])
    
    
    """ TODO: fill layers
    ret = bmesh.ops.holes_fill(bm,
              edges=[e for e in ret['geom_cut'] if isinstance(e, bmesh.types.BMEdge)])
        
    ret = bmesh.ops.triangle_fill(bm, use_dissolve=True, normal=(0,0,1),
              edges=[e for e in ret['geom_cut'] if isinstance(e, bmesh.types.BMEdge)])
    
    bmesh.ops.face_attribute_fill(bm, use_data=True,
        faces=[f for f in ret['geom'] if isinstance(f, bmesh.types.BMFace)])
    """


bm2 = bm.copy()


for e in bm2.edges:
    if e.index not in cut_edges:
        bm2.edges.remove(e)

for v in bm2.verts:
    if v.index not in cut_verts:
        bm2.verts.remove(v)

bm2.to_mesh(me)
ob.matrix_world = Matrix()
me.update()
