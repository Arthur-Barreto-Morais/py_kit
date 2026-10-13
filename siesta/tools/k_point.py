import os
import shutil
import subprocess
import argparse as arg
from . import chemical

def k_point(args):

    create_dir(args)

    run(args)

    return args

def get_parser():
    parser = arg.ArgumentParser(prog = "K_Point", formatter_class = arg.RawDescriptionHelpFormatter, description = "Program used to make the k point test", epilog= """Some Examples: """)

    parser.add_argument("-l", dest = "label", type = str, metavar = "LABEL", required = True, help = "Label of file")
    parser.add_argument("-k", dest = "k_points", nargs ="+", type=int, required = True, metavar = "k_points", help = "k_points values (in order)")
    parser.add_argument("-n", dest = "n_proc", type = str, required = True, metavar = "N_PROC", help = "Number of Processors")
    parser.add_argument("-d", dest = "dimension", type = int , required = True, metavar = "DIMENSION", choices = [2, 3], help = "Dimension - 2 = 2D or 3 = 3D")

    return parser

def create_dir(args):
    os.getcwd()

    dir_main = "kp"

    if os.path.exists(dir_main):
      shutil.rmtree(dir_main)
    os.makedirs(dir_main, exist_ok = True)
    
    for i, kp in enumerate(args.k_points):
        dir_kp = os.path.join(dir_main,f"kp_{kp}")

        os.makedirs(dir_kp, exist_ok = True)

        shutil(args.label + ".fdf", dir_kp)
        shutil(args.label + ".XV", dir_kp)
        shutil(args.label + ".DM", dir_kp)

        file_adjust(dir = dir_kp, args = args, kp = kp)
    return

def file_adjust(dir,args, kp):
    file_path = os.path.join(dir, 
    args.label + ".fdf")

    in_block = False

    with open(file_path, "r") as f:
        line = f.read().splitlines()

    new_lines = []
    in_block = False

    for info in line:

        if "MD.VariableCell" in info:
            new_lines.append("MD.VariableCell False")
            continue
        
        if "MD.Steps" in info:
            new_lines.append("MD.Steps 0")
            continue

        if "MD.UseSaveXV" in info:
            new_lines.append("MD.UseSaveXV True")
            continue

        if "DM.UseSaveDM" in info:
            new_lines.append("DM.UseSaveDM False")
            continue

        if "%block kgrid_Monkhorst_Pack" in info:
            in_block = True
            new_lines.append(info)
            block = kp_block(kp, args)
            new_lines.extend(block.splitlines()[1:-1])
            continue

        if "%endblock kgrid_Monkhorst_Pack" in info:
            in_block = False
            new_lines.append(info)
            continue

        if not in_block:
            new_lines.append(info)

    with open(file_path, "w") as f:
        f.write("\n".join(new_lines) + "\n")

def kp_block(kp, args):
    if args.dimension == "2":
        block = f"""%block kgrid_Monkhorst_Pack
    {kp} 0 0 {0.5 if kp % 2 == 0 else 0.0}
    0 {kp} 0 {0.5 if kp % 2 == 0 else 0.0}
    0 0 1 0.0
%endblock kgrid_Monkhorst_Pack"""
    elif args.dimension == "3":
        block = f"""%block kgrid_Monkhorst_Pack
    {kp} 0 0 {0.5 if kp % 2 == 0 else 0.0}
    0 {kp} 0 {0.5 if kp % 2 == 0 else 0.0}
    0 0 {kp} {0.5 if kp % 2 == 0 else 0.0}
%endblock kgrid_Monkhorst_Pack"""
    else:
        print("ERROR, Choose 2 (2D) or 3 (3D)")
    return block

def run(args):
    os.getcwd()
    for i, kp in enumerate(args.kp_points):
        dir_kp = os.path.join("kp",f"kp_{kp}")

        os.environ["OMP_NUM_THREADS"] = "1"

        command = ["/usr/bin/mpirun", "-np", str(args.n_proc), "/home/usr/bin/siesta-5.0.0/MPICH2/bin/siesta"]

        fdf_aux = os.path.join(dir_kp,args.label + ".fdf")
        out_aux = os.path.join(dir_kp,"log.out")
            
        with open(out_aux, 'w') as f_out, open(fdf_aux, 'r') as f_in:
            subprocess.run(
                command,
                cwd =dir_kp,
                stdin =f_in,
                stdout =f_out,
                stderr =subprocess.STDOUT,
                check =True
                            )        
    return