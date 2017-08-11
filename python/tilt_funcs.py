import numpy as np

def sin(angle):
    """ sin in degrees"""
    return np.sin(angle * np.pi/180.)

def cos(angle):
    """ cos in degrees"""
    return np.cos(angle * np.pi/180)

def rot_x(v, alpha):
    """ Rotate by alpha about x-axis"""
    Rx = np.array([
        [1, 0, 0],
        [0, cos(alpha), sin(alpha)],
        [0, -sin(alpha), cos(alpha)]
                  ])

    return Rx.dot(v)

def rot_y(v, beta):
    """ Rotate by beta about y-axis"""
    Ry = np.array([
        [cos(beta), 0, -sin(beta)],
        [0, 1, 0],
        [sin(beta), 0, cos(beta)]
                  ])

    return Ry.dot(v)

def sort_octahedron(atoms, origin):
    """Sort a set of 6 atoms that make up the vertices of an octahedron.
    Apical atoms are first and last.
    The in-plane atoms are ordered by angle with respect to origin G. """
    sortz = atoms[np.argsort(atoms[:,2]),:]
    angle = np.arctan2(sortz[1:5,1] - origin[1], sortz[1:5,0] - origin[0])
    sortxyz = sortz
    sortxyz[1:5] = sortxyz[1:5][np.argsort(angle)]
    return sortxyz

def generate_regular_lattice(a, c, extent):
    """ Make Copper and oxygen in regular positions

    Parameters
    ------------
    a : float
        - in-plane lattice constant
    c : float
        - out-of-plane lattice constant
    extent : int
        plane is 2*extent +1 *2*extent +1

    Returns
    -----------
    Gs : numpy array
        [H, K, L] x number of atoms
    coppers : numpy array
        [x, y, z] x number of atoms
    oxygens : numpy array
        [x, y, z] x number of atoms
    """
    abc = np.array([a, a, c])

    Gs = np.array([np.array([i, j, 0])
                      for i in range(-extent,extent+1)
                      for j in range(-extent,extent+1)])

    coppers = Gs * abc

    oxygen_cage = np.array([
                        [-1/2, 0, 0],
                        [0, -1/2, 0],
                        [0, 0, -1/2],
                        [0, 0, +1/2]
                        ])

    oxygens = []
    for G in Gs:
        atoms = oxygen_cage
        if G[0] == extent:
            atoms = np.vstack((atoms, np.array([1/2, 0, 0])))
        if G[1] == extent:
            atoms = np.vstack((atoms, np.array([0, 1/2, 0])))
        for O in atoms:
            oxygens.append((O+G)*abc)

    oxygens = np.array(oxygens)

    return Gs, coppers, oxygens

def apply_tilts(a, c, Gs, oxygens, alphas, betas):
    """ Tilts the octahedra

    Parameters
    -----------
    a : float
        - in-plane lattice constant
    c : float
        - out-of-plane lattice constant
    Gs : numpy array
        [H, K, L] x number of unit cells (Cu atoms)
    oxygens : numpy array
        [x, y, z] x number of O atoms
    alphas : numpy array
        [alpha] x number of unit cells (Cu atoms)
        rotations about x axis
    betas : numpy array
        [beta] x number of unit cells (Cu atoms)
        rotations about y axis

    Returns
    --------
    oxygens : numpy array
        [x, y, z] x number of atoms
    """
    abc = np.array([a, a, c])
    for G, alpha, beta in zip(Gs, alphas, betas):
        distances = np.abs(oxygens -G*abc).sum(axis=1)
        pickinds = np.argsort(distances)[:6]
        for index in pickinds:
            oxygens[index, :] = rot_y(rot_x(oxygens[index,:]-G*abc, alpha), beta) + G*abc
    return oxygens

# def apply_tilts(a, c, Gs, oxygens, alphas, betas):
#     """ Tilts the octahedra
#
#     Parameters
#     -----------
#     a : float
#         - in-plane lattice constant
#     c : float
#         - out-of-plane lattice constant
#     Gs : numpy array
#         [H, K, L] x number of unit cells (Cu atoms)
#     oxygens : numpy array
#         [x, y, z] x number of O atoms
#     alphas : numpy array
#         [alpha] x number of unit cells (Cu atoms)
#         rotations about x axis
#     betas : numpy array
#         [beta] x number of unit cells (Cu atoms)
#         rotations about y axis
#
#     Returns
#     --------
#     oxygens : numpy array
#         [x, y, z] x number of atoms
#     """
#     abc = np.array([a, a, c])
#     for G, alpha, beta in zip(Gs, alphas, betas):
#         for n in range(oxygens.shape[0]):
#             distance = np.abs(oxygens[n,:] -G*abc)
#             if np.sum(distance[:2]) < a*1.1/2 and distance[2] < c*1.1/2:
#                 oxygens[n,:] = rot_y(rot_x(oxygens[n,:]-G*abc, alpha), beta) + G*abc
#     return oxygens
