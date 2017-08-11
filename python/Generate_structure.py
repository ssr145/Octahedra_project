import bpy
import numpy as np
import sys
sys.path.append('/Users/Spencer/Desktop/BNL/Blender/')
from tilt_funcs import generate_regular_lattice, apply_tilts, sort_octahedron

# remove initial cube
bpy.ops.object.delete()

def makeMaterial(name, diffuse, specular, alpha):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = diffuse
    mat.diffuse_shader = "LAMBERT"
    mat.diffuse_intensity = 1.0
    mat.specular_color = specular
    mat.specular_shader = "COOKTORR"
    mat.specular_intensity = 0.5
    mat.alpha = alpha
    mat.ambient = 1
    return mat

faces = [
    [0, 1, 2, 0],
    [0, 2, 3, 0],
    [0, 3, 4, 0],
    [0, 4, 1, 0],
    [5, 1, 2, 5],
    [5, 2, 3, 5],
    [5, 3, 4, 5],
    [5, 4, 1, 5],
    ]

# construct regular lattice
a = 3.8
c = 6
extent = 3
Cu_size = 0.4
Cu_color = (200/255, 117/255, 51/255)
Cu_material = makeMaterial("Copper", Cu_color, Cu_color, 1)
O_size = 0.2
O_material = makeMaterial("Oxygen", (1, 0, 0), (1, 0, 0), 1)

Octahedron_material = makeMaterial("Octahedron", (0.2, 0.4, 0.6), (0.2, .4, 0.6), 0.15)

Gs, coppers, oxygens = generate_regular_lattice(a, c, extent)

# define and apply tilt pattern
beta = 10
def LTT_tilt(beta, G):
    if (G[0]+G[1]) % 2 == 0:
        return beta
    else:
        return -beta
betas = np.array([LTT_tilt(beta, G) for G in Gs])
alphas = betas*0

oxygens = apply_tilts(a, c, Gs, oxygens, alphas, betas)

# Add atoms
for Cu in coppers:
    bpy.ops.mesh.primitive_uv_sphere_add(location=Cu, size=Cu_size,
                                         segments=50, ring_count=50)
    bpy.context.object.data.materials.append(Cu_material)
    


for O in oxygens:
    bpy.ops.mesh.primitive_uv_sphere_add(location=O, size=O_size,
                                         segments=35, ring_count=35)
    bpy.context.object.data.materials.append(O_material)
    
    bpy.data.materials["Copper"].use_shadows = False

# Add octahedra
abc = np.array([a, a, c])
for G, alpha, beta in zip(Gs, alphas, betas):
    distances = np.abs(oxygens -G*abc).sum(axis=1)
    pickinds = np.argsort(distances)[:6]
    O_cage = sort_octahedron(oxygens[pickinds], G*abc)

    mesh_data = bpy.data.meshes.new("cube_mesh_data")
    mesh_data.from_pydata(O_cage, [], faces)
    mesh_data.update()
    obj = bpy.data.objects.new("My_Object", mesh_data)
    obj.data.materials.append(Octahedron_material)


    bpy.context.scene.objects.link(obj)

    bpy.data.materials["Octahedron"].use_transparency = True
    
    #bpy.context.object.data.materials.append(Octahedron_material)


    #obj.select = True



# Some aesthetic setting below here

# LAMP
lamp = bpy.data.lamps['Lamp']
lamp.energy = 1.3  # 10 is the max value for energy
lamp.type = 'SUN'  # in ['POINT', 'SUN', 'SPOT', 'HEMI', 'AREA']
lamp.distance = 100
bpy.ops.object.select_by_type(type='LAMP')
bpy.ops.transform.translate(value=(4.90688, 2.0304, 4.80896), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)


# CAMERA

bpy.ops.object.select_camera()
bpy.context.object.location[0] = 20.14
bpy.context.object.location[1] = -32.2
bpy.context.object.location[2] = 11.76
bpy.context.object.rotation_euler[0] = 1.2428
bpy.context.object.rotation_euler[1] = -0
bpy.context.object.rotation_euler[2] = 0.591579

# Horizon
bpy.context.scene.world.horizon_color = (0.744, 0.744378, 0.744378)






