import os
import shutil
import periodictable as pt

def Obtain(fdf_file):
    Species = {}
    with open(fdf_file, 'r') as f:
        in_block = False

        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue
            
            if line == "%block ChemicalSpeciesLabel":
                in_block = True
                continue

            if line == "%endblock ChemicalSpeciesLabel":
                break

            if in_block:
                number, Z, symbol = line.split()
                Species[symbol] = {"Number": int(number), "Z": int(Z)}
    return Species

def psml_find(fdf_file,dir,path_psml):
    file_path = os.path.join(os.getcwd(), fdf_file)
    elements = []

    in_block = False

    with open(file_path,"r") as f:
        line = f.read().strip().split("\n")
        for info in line:
            if not info or info.startswith("#"):
                continue

            if "%block ChemicalSpeciesLabel" in info:
                in_block = True
                continue
            
            if "%endblock ChemicalSpeciesLabel" in info:
                in_block = False
                break

            if in_block:
                elements.append(info.strip().split()[-1])

    dir_psml = os.path.expanduser(path_psml)

    for element in elements:

        file_psml = os.path.join(dir_psml,f"{element}.psml")
        shutil.copy(file_psml, dir)
    return

def Pos_elements(args):
    species = {}

    with open("pos.dat", 'r') as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            data = line.split()
            symbol = data[5]

            if symbol not in species:
                number = len(species) + 1
                Z = pt.elements.symbol(symbol).number

                species[symbol] = {
                    "Number": number,
                    "Z": Z
                }
    
    aux_elements = ""
    
    for symbol, info in species.items():
        Z = pt.elements.symbol(symbol).number
        aux_elements += f"{info['Number']} {Z} {symbol}\n"


    with open(f"{args.label}.fdf", 'r') as f:
        lines = f.readlines()

    new_lines = []
    in_block = False

    with open("pos.dat", 'r') as f:
        pos = f.readlines()

    for line in lines:
        if "%block ChemicalSpeciesLabel" in line:
            new_lines.append(line)
            new_lines.extend(aux_elements)
            in_block = True
            continue
        
        if "%endblock ChemicalSpeciesLabel" in line:
            new_lines.append(line)
            in_block = False
            continue
        
        if not in_block:
            new_lines.append(line)
    
    with open(f"{args.label}.fdf", 'w') as f:
        f.writelines(new_lines)
    return
