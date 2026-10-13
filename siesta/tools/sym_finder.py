

import spglib
from ase.io import read

# =====================================
# CONFIGURAÇÕES
# =====================================

arquivo = input("Arquivo.XSF" + "\n") + ".XSF"
symprec = 1e-3

# =====================================
# LEITURA DA ESTRUTURA 2D
# =====================================

atoms = read(arquivo)

cell = (
    atoms.cell.array,
    atoms.get_scaled_positions(wrap=True),
    atoms.get_atomic_numbers()
)

# =====================================
# DETERMINAÇÃO DA SIMETRIA 2D
# =====================================

layer = spglib.get_layergroup(
    cell,
    aperiodic_dir=2,
    symprec=symprec
)

# =====================================
# RESULTADOS
# =====================================

if layer is None:
    print("Não foi possível determinar a simetria 2D.")
else:
    print("Layer group:", layer.international)
    print("Número do layer group:", layer.number)
    print("Grupo pontual:", layer.pointgroup)