import periodictable as pt

def get_XSF(args):
    with open(f"{args.label}.XSF", 'r') as f:
        lines = [line.strip() for line in f.readlines()]

    vectors = lines[4:7]
    num_atom = int(lines[9].split()[0])
    positions = lines[10:10+num_atom]

    elements = {}

    with open("vec.dat", 'w') as f:
        for line in vectors:
            f.write(line + "\n")

    with open("pos.dat", 'w') as f:
        for i, line in enumerate(positions):
            data = line.split()

            element = pt.elements[int(data[0])].symbol
            x, y, z = data[1:4]

            if element not in elements:
                elements[element] = len(elements) + 1

            element_index = elements[element]

            f.write(f"{float(x):15.8f} {float(y):15.8f} {float(z):15.8f} {element_index:5d} {i+1:5d} {element:>5s}\n")
    return int(num_atom), int(len(elements))

def add_vec(args):
    with open(f"{args.label}.fdf", 'r') as f:
        lines = f.readlines()

    new_lines = []
    in_block = False

    with open("vec.dat", 'r') as f:
        vectors = f.readlines()

    for line in lines:
        if "%block LatticeVectors" in line:
            new_lines.append(line)
            new_lines.extend(vectors)
            in_block = True
            continue
        
        if "%endblock LatticeVectors" in line:
            new_lines.append(line)
            in_block = False
            continue

        if not in_block:
            new_lines.append(line)
    
    with open(f"{args.label}.fdf", 'w') as f:
        f.writelines(new_lines)
    return

def add_pos(args):
    with open(f"{args.label}.fdf", 'r') as f:
        lines = f.readlines()

    new_lines = []
    in_block = False

    with open("pos.dat", 'r') as f:
        pos = f.readlines()

    for line in lines:
        if "%block AtomicCoordinatesAndAtomicSpecies" in line:
            new_lines.append(line)
            new_lines.extend(pos)
            in_block = True
            continue
        
        if "%endblock AtomicCoordinatesAndAtomicSpecies" in line:
            new_lines.append(line)
            in_block = False
            continue
        
        if not in_block:
            new_lines.append(line)
    
    with open(f"{args.label}.fdf", 'w') as f:
        f.writelines(new_lines)
    return

def add_nums(args, num_atoms, num_elements):
    with open(f"{args.label}.fdf", 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if "NumberOfAtoms" in line:
            lines[i] = f"NumberOfAtoms {num_atoms}\n"
            break
    for i, line in enumerate(lines):
        if "NumberOfSpecies" in line:
            lines[i] = f"NumberOfSpecies {num_elements}\n"
            break
    with open(f"{args.label}.fdf", 'w') as f:
        f.writelines(lines)

def check_right_hand(*args):
    with open("vec.dat", 'r') as f:
        vectors = [
            [float(x) for x in line.split()]
            for line in f.readlines()
        ]

    a, b, c = vectors

    # Calcula o determinante
    det = (
        a[0]*(b[1]*c[2] - b[2]*c[1])
        - b[0]*(a[1]*c[2] - a[2]*c[1])
        + c[0]*(a[1]*b[2] - a[2]*b[1])
    )

    if abs(det) < 1e-10:
        raise ValueError("Invalid lattice: determinant is zero.")

    if det < 0:
        # Inverte o segundo vetor
        vectors[1] = [-x for x in vectors[1]]
        print("Left-handed cell detected. Vector b inverted.")

    else:
        print("Right-handed cell. No changes required.")

    # Salva os vetores corrigidos
    with open("vec.dat", 'w') as f:
        for vector in vectors:
            f.write(
                f"{vector[0]:15.8f} "
                f"{vector[1]:15.8f} "
                f"{vector[2]:15.8f}\n"
            )

    return