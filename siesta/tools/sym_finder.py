#!/usr/bin/env python3
"""Space group e point group a partir de um arquivo .XV do SIESTA (ASE + spglib).

Funciona para estruturas 3D (bulk) e 2D (monocamada com vácuo na cela).

Uso:
    python simetria_xv.py sistema.XV
    python simetria_xv.py sistema.XV --symprec 1e-4 1e-3 1e-2   # tolerâncias (Å)
    python simetria_xv.py sistema.XV --dim 2                    # força 2D
    python simetria_xv.py sistema.XV --vacuum 8                 # limiar de vácuo (Å)

Dependências: ase, spglib   (pip install ase spglib)
"""
import argparse
import sys

import numpy as np
import spglib
from ase.io import read

DEFAULT_SYMPRECS = [1e-5, 1e-4, 1e-3, 1e-2, 1e-1]


def _get(obj, key):
    """spglib >= 2.5 devolve dataclasses; versões antigas devolvem dict."""
    return obj[key] if isinstance(obj, dict) else getattr(obj, key)


def vacuum_gaps(atoms):
    """Maior espaço vazio (Å) entre imagens periódicas ao longo de cada vetor da cela.

    Medido perpendicularmente ao plano dos outros dois vetores, então vale
    também para celas não ortogonais.
    """
    cell = np.asarray(atoms.cell)
    volume = abs(np.linalg.det(cell))
    scaled = atoms.get_scaled_positions(wrap=True)
    gaps = []
    for i in range(3):
        j, k = (i + 1) % 3, (i + 2) % 3
        height = volume / np.linalg.norm(np.cross(cell[j], cell[k]))
        u = np.sort(scaled[:, i])
        frac = np.diff(np.concatenate([u, [u[0] + 1.0]]))  # inclui o wrap-around
        gaps.append(frac.max() * height)
    return np.array(gaps)


def detect_dimensionality(atoms, vacuum, forced=None):
    """Devolve (dim, eixo_de_vácuo, gaps); dim é 2 ou 3."""
    gaps = vacuum_gaps(atoms)
    vac_axes = [i for i, g in enumerate(gaps) if g >= vacuum]

    if forced == 3:
        return 3, None, gaps
    if forced == 2:
        return 2, int(np.argmax(gaps)), gaps
    if len(vac_axes) == 0:
        return 3, None, gaps
    if len(vac_axes) == 1:
        return 2, vac_axes[0], gaps

    print(f"AVISO: vácuo em {len(vac_axes)} direções (estrutura 1D/0D?). "
          "A análise é a da cela periódica com vácuo.", file=sys.stderr)
    return 3, None, gaps


def analisar(atoms, symprec):
    """Simetria de `atoms` para a tolerância dada (None se o spglib falhar)."""
    cell = (np.asarray(atoms.cell), atoms.get_scaled_positions(), atoms.numbers)
    ds = spglib.get_symmetry_dataset(cell, symprec=symprec)
    if ds is None:
        return None
    tipo = spglib.get_spacegroup_type(_get(ds, "hall_number"))
    return {
        "numero": int(_get(ds, "number")),
        "simbolo": _get(ds, "international"),
        "pg_hm": _get(ds, "pointgroup").strip(),
        "pg_schoenflies": _get(tipo, "pointgroup_schoenflies"),
        "n_ops": len(_get(ds, "rotations")),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("xv", help="arquivo .XV do SIESTA")
    p.add_argument("--symprec", type=float, nargs="+", default=DEFAULT_SYMPRECS,
                   help="tolerância(s) de simetria em Å (padrão: 1e-5 ... 1e-1)")
    p.add_argument("--dim", type=int, choices=[2, 3], default=None,
                   help="força 2D ou 3D (padrão: detecção automática pelo vácuo)")
    p.add_argument("--vacuum", type=float, default=6.0,
                   help="vácuo mínimo (Å) para considerar a estrutura 2D (padrão: 6)")
    args = p.parse_args()

    # O ASE converte Bohr -> Å automaticamente ao ler o .XV
    atoms = read(args.xv, format="siesta-xv")
    dim, vac_axis, gaps = detect_dimensionality(atoms, args.vacuum, args.dim)

    try:
        formula = atoms.get_chemical_formula()
    except Exception:  # Z fora de 1..118 (átomos sintéticos etc.)
        formula = "?"
    a, b, c, alpha, beta, gamma = atoms.cell.cellpar()
    print(f"Arquivo     : {args.xv}")
    print(f"Átomos      : {len(atoms)}  ({formula})")
    print(f"Cela (Å, °) : a={a:.4f} b={b:.4f} c={c:.4f}  "
          f"α={alpha:.2f} β={beta:.2f} γ={gamma:.2f}")
    print("Maior vazio : " + "  ".join(f"a{i+1}={g:.2f} Å" for i, g in enumerate(gaps)))
    print(f"Dimensão    : 2D (vácuo ao longo de a{vac_axis+1})" if dim == 2
          else "Dimensão    : 3D")
    print()

    head = (f"{'symprec':>9}  {'space group':<13}{'nº':>4}  "
            f"{'point group':<12}{'Schoenflies':<12}{'ops':>4}")
    print(head)
    print("-" * len(head))
    for tol in args.symprec:
        r = analisar(atoms, tol)
        if r is None:
            print(f"{tol:>9.0e}  spglib não encontrou simetria")
            continue
        print(f"{tol:>9.0e}  {r['simbolo']:<13}{r['numero']:>4}  "
              f"{r['pg_hm']:<12}{r['pg_schoenflies']:<12}{r['n_ops']:>4}")

    if dim == 2:
        print("\nObs. (2D): o space group é o do cristal 3D formado pela cela com vácuo "
              "(o spglib não\nclassifica layer groups). O point group é o mesmo da monocamada.")


if __name__ == "__main__":
    main()