import numpy as np
from ase.io import read
from ase.geometry import Cell, cellpar_to_cell
from ase.dft.kpoints import parse_path_string

len_crit = 0.01
ang_crit = 0.1
ang_imp = (60.0, 90.0, 120.0)
vac_min = 7.0

def equals_analyze(info, tol):
    lat = np.array(info, float)
    groups = []

    for i in range(len(lat)):
        for g in groups:
            if any(abs(lat[i] - lat[j]) <= tol for j in g):
                g.append(i)
                break
        else:
            groups.append([i])

    out = lat.copy()
    for g in groups:
        out[g] = lat[g].mean()
    return out

def ang_analyze(angs):
    angs = np.array(angs, float)

    for i, ang in enumerate(angs):
        for ang_aux in ang_imp:
            if abs(ang-ang_aux) <= ang_crit:
                angs[i] = ang_aux

    return equals_analyze(angs, ang_crit)

def clean_path(path):
    if "," in path or path[0] == path[-1]:
        return path
    last = path.rfind(path[0])
    return path[:last + 1] if last > 0 else path

def start_at_gamma(path):
    segs = parse_path_string(path)
    if len(segs) != 1:
        return path
    pts = segs[0]
    if "G" not in pts or pts[0] != pts[-1] or pts[0] == "G":
        return path
    loop = pts[:-1]
    i = loop.index("G")
    loop = loop[i:] + loop[:i]
    return "".join(loop + ["G"])

def rhombic_labels(cell, bands, pbc):
    sp = dict(bands.special_points)
    X, A1 = sp["X"], sp["A1"]
    sp = {"G": sp["G"], "X": X, "M": (X + A1) / 2, "H": A1, "Y": sp["Y"]}
    return cell.bandpath("GXMHYG", pbc=pbc, special_points=sp)

def run():

    #file = input("Arquivo.XV\n") + ".XV"
    file = "arquivo.XV"
    atoms = read(file, format="siesta-xv")

    cte_a, cte_b, cte_c, ang_a, ang_b, ang_g = atoms.cell.cellpar()
    R0 = atoms.cell.array.copy()

    C_out_plane = (np.allclose(R0[2,:2], 0.0, atol = len_crit) and np.allclose(R0[:2, 2], 0.0, atol = len_crit) and abs(R0[2, 2]) > len_crit)

    if C_out_plane:
        z = np.sort(atoms.positions[:,2] % abs(R0[2,2]))
        vac_aux = np.max(np.diff(np.append(z, z[0] + abs(R0[2, 2]))))
    else:
        vac_aux = 0.0

    is_2d = C_out_plane and vac_aux >= vac_min

    if is_2d:
        pbc = [True, True, False]

        cte_a2, cte_b2 = equals_analyze([cte_a, cte_b], len_crit)
        
        ang_g2 = ang_analyze([ang_g])[0]
        
        R = cellpar_to_cell([cte_a2, cte_b2, 0.0, 90.0, 90.0, ang_g2])
        
    else:
        pbc = [True, True, True]

        cte_a2, cte_b2, cte_c2 = equals_analyze([cte_a, cte_b, cte_c], len_crit)
        
        ang_a2, ang_b2, ang_g2 = ang_analyze([ang_a, ang_b, ang_g])
        
        R = cellpar_to_cell([cte_a2, cte_b2, cte_c2, ang_a2, ang_b2, ang_g2])    

    cell = Cell(R)

    print("Parâmetros da célula:", cell.cellpar())
    print("Vetor a:", cell[0])
    print("Vetor b:", cell[1])
    if pbc[2] == False:
        print("PBC: 2D", pbc)
    elif pbc[2] == True:
        print("PBC: 3D", pbc)

    bands = cell.bandpath(pbc=pbc)

    if is_2d:
        path = start_at_gamma(clean_path(bands.path))
        bands = cell.bandpath(path, pbc=pbc)

        if cell.get_bravais_lattice(pbc=pbc).name == "CRECT":
            bands = rhombic_labels(cell, bands, pbc)

    path = bands.path

    print("Caminho ASE:", path)
    print("Tipo de ponto:", bands.special_points)

    segments = parse_path_string(path)

    # =============== SAÍDA ===============
    is_gamma = lambda l: "Γ" if l == "G" else l

    print()
    for s, seg in enumerate(segments):
        if s > 0:
            print()
        for l in seg:
            k = bands.special_points[l]
            print(f"{is_gamma(l):<3}{k[0]:>11.6f}{k[1]:>11.6f}{k[2]:>11.6f}")
    return