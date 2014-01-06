import bpy
import bmesh
import mathutils

import math






def clean_slice(bm, me):
    # First, remove any double vert!
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])

    # Add common verts at each intersection of existing edges.
    if 1:
        edges = set(bm.edges)
        # Find all intersections.
        new_co = {}
        while edges:
            e1 = edges.pop()
            for e2 in edges:
                e1_co1, e1_co2 = (v.co for v in e1.verts)
                e2_co1, e2_co2 = (v.co for v in e2.verts)
                co = mathutils.geometry.intersect_line_line_2d(e1_co1, e1_co2, e2_co1, e2_co2)
                if co not in (None, e1_co1, e1_co2, e2_co1, e2_co2):
                    co = tuple(co)
                    if co in new_co:
                        new_co[co] |= {e1, e2}
                    else:
                        new_co[co] = {e1, e2}
        # Compute cut factors for each cut and each affected edge.
        edges_cuts = {}
        for co, eds in new_co.items():
            co = mathutils.Vector(co + (0.0,))
            for e in eds:
                e_co1, e_co2 = (v.co for v in e.verts)
                e_x = e_co1.x - e_co2.x
                e_y = e_co1.y - e_co2.y
                if e_x == e_y == 0.0:
                    print("Zero-length edge!!!")
                    continue
                f = ((e_co1.x - co.x) / e_x) if (abs(e_x) > abs(e_y)) else ((e_co1.y - co.y) / e_y)
                if f < 0.001 or f > 0.999:
                    continue
                if e in edges_cuts:
                    edges_cuts[e].append(f)
                else:
                    edges_cuts[e] = [f]
        # Finally, split the edges.
        # We may have several cuts per edge, makes things a bit more tricky...
        new_verts = []
        for e, factors in edges_cuts.items():
            factors.sort(reverse=True)
            prev_f = 1.0
            v = e.verts[0]
            for f in factors:
                f /= prev_f
                ne, nv = bmesh.utils.edge_split(e, v, f)
                if v in ne.verts:
                    e = ne
                new_verts.append(nv)
                prev_f = f
        bmesh.ops.remove_doubles(bm, verts=new_verts, dist=0.001)

    # Now, (try to!) split all faces with all edges using the newly created verts.
    # This way, we should not get anymore any faces overlapping partially each other.
    # At worst, we'll have some smaller faces completely overlapped by biger ones.
    if 1:
        new_verts = set(new_verts) & set(bm.verts)
        for v in new_verts:
            for e in v.link_edges:
                bmesh.ops.connect_verts(bm, verts=e.verts)

    # At this point, we have to remove all those ugly double edges and faces we just created!
    # Use Mesh.validate(), much simpler than re-creating the whole code for bmesh!
    bm.to_mesh(me)
    me.validate(False)  # XXX Set to False for release!
    bm.clear()
    bm.from_mesh(me)

    # Try to dissolve as much inner verts as possible.
    # This will drastically reduce the overall number of faces.
    if 1:
        for v in bm.verts[:]:
            if not v.is_valid or v.is_boundary or not v.link_faces:
                continue
            dissolve = True
            ref_n = v.link_faces[0].normal
            for f in v.link_faces[1:]:
                if f.normal.dot(ref_n) < 0.0:
                    dissolve = False
                    break
            if dissolve:
                try:
                    bmesh.ops.dissolve_verts(bm, verts=[v])
                except:
                    pass

    # Detect "face islands" (connected faces sharing the same normal).
    if 1:
        faces_todo = set(bm.faces)
        faces_done = set()
        islands = []
        while faces_todo:
            f = faces_todo.pop()
            faces_done.add(f)
            edges_todo = set(f.edges)
            edges_done = set()
            isl = {f}
            while edges_todo:
                e = edges_todo.pop()
                edges_done.add(e)
                for ff in e.link_faces:
                    if ff in faces_done:
                        continue
                    if f.normal.dot(ff.normal) > 0.0:
                        isl.add(ff)
                        faces_done.add(ff)
                        edges_todo |= set(ff.edges) - edges_done
            islands.append(isl)
            faces_todo -= faces_done

    # And now, we want to remove all faces that are completely inside another island than theirs.
    if 1:
        face_map = {f: [] for f in bm.faces}
        face_map_tmp = {}
        new_islands = []

        # First, get triangulated islands.
        for isl in islands:
            faces = {f.copy(False, False): f for f in isl} #tuple(f.copy(False, False) for f in isl)
            face_map_tmp.update(faces)
            ret = bmesh.ops.triangulate(bm, faces=tuple(faces.keys()))
            new_islands.append([isl, set(ret["faces"])])
            for tri, fc in ret["face_map"].items():
                face_map[face_map_tmp[fc]].append(tri)

        islands = new_islands
        del face_map_tmp

        # Remove from our islands faces contained into other islands.
        for isl, isl_tris in islands:
            for f in tuple(isl):
                f_in_isl = False
                for _, tris in ((i, t) for i, t in islands if i != isl):
                    f_in_this_isl = True
                    f_all_verts_shared = True
                    for v in f.verts:
                        v_in_isl = False
                        v_is_shared = False
                        for tri in tris:
                            if v in tri.verts:
                                v_in_isl = True
                                v_is_shared = True
                                break
                            cos = (v.co,) + tuple(v.co for v in tri.verts)
                            if mathutils.geometry.intersect_point_tri_2d(*cos):
                                v_in_isl = True
                                break
                        if not v_in_isl:
                            f_in_this_isl = False
                            break
                        if not v_is_shared:
                            f_all_verts_shared = False
                    # We do not want to remove faces that share all their verts with the other island
                    # (real duplicates have already been removed, so only remains those on the boundary
                    #  of the islands).
                    if f_in_this_isl and not f_all_verts_shared:
                        f_in_isl = True
                        break
                if f_in_isl:
                    # remove face from its island, and the related tris!
                    isl.remove(f)
                    for tri in face_map[f]:
                        isl_tris.remove(tri)

        # And finally, remove faces we don't want (together with temp geometry created by triangulation).
        faces_to_keep = set()
        faces_to_del = set()
        for isl, tris in islands:
            faces_to_keep |= isl
            faces_to_del |= tris
        faces_to_del |= set(bm.faces) - faces_to_keep
        for f in faces_to_del:
            bm.faces.remove(f)
        for e in bm.edges[:]:
            if not e.link_faces:
                bm.edges.remove(e)
        for v in bm.verts[:]:
            if not v.link_edges:
                bm.verts.remove(v)

    # Final cleanup: set all faces to same normal, and try again to dissolve as much inner verts as possible.
    # This will drastically reduce the overall number of faces.
    if 1:
        ref_n = mathutils.Vector((0.0, 0.0, 1.0))
        for f in bm.faces[:]:
            if f.normal.dot(ref_n) < 0.0:
                f.normal_flip()
        for v in bm.verts[:]:
            if not v.is_valid or v.is_boundary or not v.link_faces:
                continue
            try:
                bmesh.ops.dissolve_verts(bm, verts=[v])
            except:
                pass








scene = bpy.context.scene
obj = bpy.context.active_object
obj_name = obj.name

slice_height = 0.05  # Will be much smaller IRL, of course!

beam_width = 0.05
beam_overlap = 0.5  # factor, [0.0, 1.0[

# Create our bmesh object.
ref_bm = bmesh.new()
ref_bm.from_mesh(obj.data)

# Temp mesh, used to clean up things (validate(True))...
tmp_me = bpy.data.meshes.new("__TMP__")

min_z = max_z = None
for v in ref_bm.verts:
    z = v.co.z
    if min_z is None or min_z > z:
        min_z = z
    if max_z is None or max_z < z:
        max_z = z

#for i in range(0, math.ceil((max_z - min_z) / slice_height)):
i = 24
if i:
    h_low = min_z + (i - 0.5) * slice_height
    bm = ref_bm.copy()

    bmesh.ops.bisect_plane(bm, dist=0.0001, geom=bm.verts[:]+bm.edges[:]+bm.faces[:],
                           plane_co=(0.0, 0.0, h_low), plane_no=(0.0, 0.0, -1.0),
                           clear_inner=False, clear_outer=True)
    bmesh.ops.bisect_plane(bm, dist=0.0001, geom=bm.verts[:]+bm.edges[:]+bm.faces[:],
                           plane_co=(0.0, 0.0, h_low + slice_height), plane_no=(0.0, 0.0, 1.0),
                           clear_inner=False, clear_outer=True)

    for v in bm.verts:
        v.co.z = 0.0

    clean_slice(bm, tmp_me)

    bm.to_mesh(obj.data)


# We are done with this one!
bpy.data.meshes.remove(tmp_me)
