import argparse as arg
import subprocess
import glob
import os
import shutil

def Phonopy(args,ph_args, path_psml):

    run(args, ph_args)
    create_dir()
    return

def get_parser():
    parser = arg.ArgumentParser(prog = "PhonoPy", formatter_class = arg.RawDescriptionHelpFormatter, description = "Program used to choose PhonoPy Configurations", epilog= """Some Examples: """)

    parser.add_argument("-d", dest = "dimension", type = int , required = True, metavar = "DIMENSION", default = 2, choices = [2, 3], help = "Dimension - 2 = 2D or 3 = 3D - Default (2)")
    parser.add_argument("-r", dest = "replication", type = int , required = True, metavar = "REPETITION", choices = [1, 2, 3, 4, 5, 6, 7, 8], help = "Quantity of Replication of Unit Cell")

    return parser

def run(args, ph_args):
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
        # Extrai o número da supercell
        number = os.path.basename(file).split("-")[1].split(".")[0]

        # Cria o diretório
        directory = f"sc_{number}"
        os.makedirs(directory, exist_ok=True)

        # Move o arquivo FDF
        shutil.move(file, os.path.join(directory, file))

        # Copia os arquivos PSML
        for psml in psml_files:
            shutil.copy2(psml, directory)

    return