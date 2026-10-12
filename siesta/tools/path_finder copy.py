import numpy as np
from ase.io import read
from ase.geometry import Cell, cellpar_to_cell
from ase.dft.kpoints import parse_path_string

TOL_LEN = 0.01                      # Å
TOL_ANG = 0.1                       # graus
NOMINAL_ANGLES = (60.0, 90.0, 120.0)
VAC_MIN = 7.0                       # Å, vácuo mínimo para considerar 2D


def agrupa_iguais(valores, tol):
    """Valores que diferem até tol viram a média do grupo."""
    v = np.array(valores, float)
    grupos = []
    for i in range(len(v)):
        for g in grupos:
            if any(abs(v[i] - v[j]) <= tol for j in g):
                g.append(i)
                break
        else:
            grupos.append([i])
    out = v.copy()
    for g in grupos:
        out[g] = v[g].mean()
    return out


def snap_angulos(angs):
    angs = np.array(angs, float)
    for i, x in enumerate(angs):
        for n in NOMINAL_ANGLES:
            if abs(x - n) <= TOL_ANG:
                angs[i] = n
    return agrupa_iguais(angs, TOL_ANG)


file = input("Arquivo.XV" + "\n") + ".XV"
atoms = read(file, format="siesta-xv")

a, b, c, alpha, beta, gamma = atoms.cell.cellpar()
R0 = atoms.cell.array.copy()

# --- 2D ou 3D ---
c_em_z = (np.allclose(R0[2, :2], 0.0, atol=TOL_LEN)
          and np.allclose(R0[:2, 2], 0.0, atol=TOL_LEN)
          and abs(R0[2, 2]) > TOL_LEN)

if c_em_z:  # maior vazio (periódico) ao longo de z
    z = np.sort(atoms.positions[:, 2] % R0[2, 2])
    vacuo = np.max(np.diff(np.append(z, z[0] + R0[2, 2])))
else:
    vacuo = 0.0

is_2d = c_em_z and vacuo >= VAC_MIN

# --- Regularização ---
if is_2d:
    pbc = [True, True, False]
    a2, b2 = agrupa_iguais([a, b], TOL_LEN)
    g2 = snap_angulos([gamma])[0]
    R = cellpar_to_cell([a2, b2, 1.0, 90.0, 90.0, g2])
    R[2, :] = 0.0
else:
    pbc = [True, True, True]
    lens = agrupa_iguais([a, b, c], TOL_LEN)
    angs = snap_angulos([alpha, beta, gamma])
    R = cellpar_to_cell([*lens, *angs])

cell = Cell(R)

# --- Caminho de alta simetria ---
bands = cell.bandpath(pbc=pbc)
segments = parse_path_string(bands.path)

# =============== SAÍDA ===============
fmt = lambda l: "Γ" if l == "G" else l

# print(f"{'2D' if is_2d else '3D'} {cell.get_bravais_lattice(pbc=pbc).name}")  # opcional
print()
for s, seg in enumerate(segments):
    if s > 0:
        print()
    for l in seg:
        k = bands.special_points[l]
        print(f"{fmt(l):<3}{k[0]:>11.6f}{k[1]:>11.6f}{k[2]:>11.6f}")