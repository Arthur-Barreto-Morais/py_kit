import argparse as arg
import subprocess
import glob
import os
import shutil
from siesta.tools import path_finder as pf

def Phonopy(args, ph_args):

    create_input(args, ph_args)
    create_dir()
    run_siesta(ph_args)
    pos_run(args,ph_args)
    return

def get_parser():

    parser = arg.ArgumentParser(prog = "PhonoPy", formatter_class = arg.RawDescriptionHelpFormatter, description = "Program used to choose PhonoPy Configurations", epilog= """Some Examples: """)
    parser.add_argument("-d", dest = "dimension", type = int , required = True, metavar = "DIMENSION", default = 2, choices = [2, 3], help = "Dimension - 2 = 2D or 3 = 3D - Default (2)")
    parser.add_argument("-r", dest = "replication", type = int , required = True, metavar = "REPETITION", choices = [1, 2, 3, 4, 5, 6, 7, 8], help = "Quantity of Replication of Unit Cell")
    parser.add_argument("-p", dest = "points", type = int , required = False, metavar = "NUMBER_OF_POINTS", default= 60, help = "Number of points in phonon band calculation - Default (60)")
    parser.add_argument("-n", dest = "n_proc", type = int , required = False, metavar = "NUMBER_OF_PROCESSES", default = 16, help = "Number of processes to use - Default (16)")

    return parser

def create_input(args, ph_args):

    if ph_args.dimension == 2:

        command = ["phonopy-init", "--siesta", "-d", f"--dim={ph_args.replication} {ph_args.replication} 1", "--pa", "1", "0", "0", "0", "1", "0", "0", "0", "1", "-c", f"{args.label}.fdf"]

    elif ph_args.dimension == 3:

        command = [f"phonopy-init", "--siesta", "-d", f"--dim={ph_args.replication} {ph_args.replication} {ph_args.replication}", "--pa", "1", "0", "0", "0", "1", "0", "0", "0", "1", "-c", f"{args.label}.fdf"]
    
    else:

        print("ERROR: Invalid dimension. Please choose 2 or 3.")
        return
    
    subprocess.run(command, check=True)
    
    return

def create_dir():

    files = glob.glob("supercell-*.fdf")
    psml_files = glob.glob("*.psml")

    for file in files:

        number = os.path.basename(file).split("-")[1].split(".")[0]
        directory = f"sc_{number}"
        os.makedirs(directory, exist_ok=True)
        shutil.move(file, os.path.join(directory, file))

        for psml in psml_files:

            shutil.copy2(psml, directory)

    return

def run_siesta(ph_args):

    directory = [d for d in glob.glob("sc*") if os.path.isdir(d)]
    print(directory)
    for dir in directory:

        dir_num = dir.split("_")[1]
        file1 = "header.fdf"
        file2 = os.path.join(dir, f"supercell-{dir_num}.fdf")

        with open(file1, 'r') as f1, open(file2, 'r') as f2:

            info = f1.read() + "\n" + "\n".join(f2.read().splitlines()[1:])

        with open(os.path.join(dir,"input.fdf"), 'w') as f:

            f.write(info)

        command_run = ["/usr/bin/mpirun", "-np", str(ph_args.n_proc), "/home/usr/bin/siesta-5.0.0/MPICH2/bin/siesta"]
        os.environ["OMP_NUM_THREADS"] = "1"
        fdf_aux = os.path.join(dir,"input.fdf")
        out_aux = os.path.join(dir,"log.out")
        
        with open(out_aux, 'w') as f_out, open(fdf_aux, 'r') as f_in:

            subprocess.run(command_run, cwd =dir, stdin =f_in, stdout =f_out, stderr =subprocess.STDOUT, check =True)
    
    return

def pos_run(args,ph_args):

    args.info = False
    bands_block = pf.run(args)
    lines = bands_block.strip().split("\n")

    bands_v = []
    labels_v = []

    for line in lines:

        line = line.split()
        bands_v.append([float(x) for x in line[1:4]])
        labels_v.append(line[4])

    bands = " ".join(str(x) for row in bands_v for x in row)
    labels = " ".join(labels_v)

    with open("band.conf", 'w') as f:

        if ph_args.dimension == 2: 

            f.write(f"DIM = {ph_args.replication} {ph_args.replication} 1 \n")

        if ph_args.dimension == 3: 

            f.write(f"DIM = {ph_args.replication} {ph_args.replication} {ph_args.replication} \n")

        f.write("PRIMITIVE_AXIS = 1.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 1.0 \n")
        f.write(f"BAND = {bands} \n")
        f.write(f"BAND_POINTS = {ph_args.points} \n")
        f.write(f"BAND_LABELS = {labels} \n")

    command = ["phonopy-init", "--siesta", "-f", *sorted(glob.glob("sc_*/input.FA"))]
    subprocess.run(command, check=True)

    command = ["phonopy", "-p", "-s", "--config", "band.conf"]
    subprocess.run(command, check=True)

    command = ["phonopy-bandplot", "band.yaml"]

    subprocess.run(command, capture_output=True, text=True)

    command = ["phonopy-bandplot", "band.yaml", "-o", f"{args.label}_band.pdf"]

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"Erro ao gerar PDF:\n{result.stderr}")
    return