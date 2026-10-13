from siesta.tools  import chemical
from . import my_calc
import os 
import shutil
import argparse as arg
from ase.io import read as ase_read, write as ase_write
from ase.mep import NEB, DyNEB
from ase.optimize import BFGS

def neb_code(args):

    Images, neb_file = Create_Images(args)

    Create_dir(args, Images)

    Images = run_calc(args, Images)

    Images = neb_run(Images, neb_file)

    Dy_Images = Dy_run(args, Images)

    if args.CI_NEB:
        CI_run(args, Dy_Images)
    
    return

def get_parser():
    parser = arg.ArgumentParser(prog = "NEB_Code", formatter_class = arg.RawDescriptionHelpFormatter, description = "Program used for NEB calculations", epilog= """Some Examples: """)
    parser = arg.ArgumentParser()
    parser.add_argument("-l", dest = "label", type = str, required = True, help = "Label of file")
    parser.add_argument("-n", dest = "num_images", type = int, required = True, help = "Number of Images")
    parser.add_argument("-np", dest = "n_proc", type = int, required = True, help = "Number of Processors")
    parser.add_argument("-ci", dest = "CI_NEB", required= False, action = "store_true", help = "Enable CI-NEB calculations (Default False)")
    return parser

def Create_Images(args):
    os.getcwd()

    if not (os.path.exists('initial.XSF') and os.path.exists('final.XSF')):
        raise Exception("Files 'initial.XSF' and/or 'final.XSF' not found")
    
    img_initial = 'initial.XSF'
    xsf_initial = ase_read(img_initial, format='xsf')
    xsf_initial.pbc = [True, True, False]
    img_final = 'final.XSF'
    xsf_final = ase_read(img_final, format='xsf')
    xsf_final.pbc = [True, True, False]

    Images = []

    Images.append(xsf_initial)

    for i in range(args.num_images -2):
        image = xsf_initial.copy()
        Images.append(image)

    Images.append(xsf_final)    

    neb_file = NEB(Images, k = 0.10, climb = False, method = 'improvedtangent', remove_rotation_and_translation= True)

    neb_file.interpolate(mic = True)

    return Images, neb_file

def Create_dir(args, Images):
    dir_main = "neb"

    if os.path.exists(dir_main):
        shutil.rmtree(dir_main)
    os.makedirs(dir_main, exist_ok = True)

    for i,image in enumerate(Images):
        dir_neb = os.path.join(dir_main,f'image_{i}')

        os.makedirs(dir_neb, exist_ok = True)
        shutil.copy(args.label + ".fdf", dir_neb)
        
        file_adjust(args.label + ".fdf", dir_neb)

    return

def file_adjust(fdf_file, dir_neb):
    new_fdf_file = os.path.join(dir_neb,fdf_file)
    in_block = False

    with open(new_fdf_file, "r") as f:
        line = f.read().splitlines()

    new_lines = []

    for info in line:

        if "MD.VariableCell" in info:
            new_lines.append("MD.VariableCell False")
            continue
        
        elif "MD.Steps" in info:
            new_lines.append("MD.Steps 0")
            continue

        elif "MD.UseSaveXV" in info:
            new_lines.append("MD.UseSaveXV False")
            continue

        elif "DM.UseSaveDM" in info:
            new_lines.append("DM.UseSaveDM False")
            continue

        else:
            new_lines.append(info)
 
    with open(new_fdf_file, "w") as f:
        f.write("\n".join(new_lines) + "\n")
    
    return

def run_calc(args, Images):
    command_run = ["/usr/bin/mpirun", "-np", str(args.n_proc), "/home/usr/bin/siesta-5.0.0/MPICH2/bin/siesta"]
    for i,image in enumerate(Images):
        dir_neb = os.path.join("neb",f'image_{i}')

        image.calc = my_calc.Siesta(image_dir = dir_neb, label_name = args.label, species = chemical.Obtain(os.path.join(dir_neb,args.label + ".fdf")), command = command_run)
    
    return Images

def neb_run(Images, neb_file):
    for file in ['neb_final.traj', 'neb.log', 'neb_relax.traj']:
        if os.path.exists(file):
            os.remove(file)

    opt = BFGS(neb_file, logfile = 'neb.log', trajectory = "neb_relax.traj")

    opt.run(fmax = 1.0, steps = 300)

    ase_write('neb_final.traj',Images)
    
    return Images

def Dy_run(args, Images):
    Dy_Images = [image.copy() for image in Images]

    for i, image in enumerate(Dy_Images):
        dir_neb = os.path.join("neb",f'image_{i}')

        command_run = ["/usr/bin/mpirun", "-np", str(args.n_proc), "/home/usr/bin/siesta-5.0.0/MPICH2/bin/siesta"]

        image.calc = my_calc.Siesta(image_dir = dir_neb, label_name = args.label , species = chemical.Obtain(os.path.join(dir_neb,args.label + ".fdf")), command = command_run)

    Dy_neb_file = DyNEB(Dy_Images, k = 0.10, climb = False, dynamic_relaxation = True, method = 'improvedtangent', remove_rotation_and_translation= True)

    for file in ['Dy_neb_final.traj', 'Dy_neb.log', 'Dy_neb_relax.traj']:
        if os.path.exists(file):
            os.remove(file)

    Dy_opt = BFGS(Dy_neb_file,logfile = 'Dy_neb.log',trajectory = "Dy_neb_relax.traj")

    Dy_opt.run(fmax = 0.1, steps = 300)

    ase_write('Dy_neb_final.traj',Dy_Images)

    return Dy_Images

def CI_run(args, Dy_Images):
    CI_Images = [image.copy() for image in Dy_Images]

    for i, image in enumerate(CI_Images):
        dir_neb = os.path.join("neb",f'image_{i}')

        command_run = ["/usr/bin/mpirun", "-np", str(args.n_proc), "/home/usr/bin/siesta-5.0.0/MPICH2/bin/siesta"]
            
        image.calc = my_calc.Siesta(image_dir = dir_neb, label_name = args.label , species = chemical.Obtain(os.path.join(dir_neb,args.label + ".fdf")), command = command_run)

    CI_neb_file = NEB(CI_Images, k = 0.10, climb = True, method = 'improvedtangent', remove_rotation_and_translation= True)

    for file in ['CI_neb_final.traj', 'CI_neb.log', 'CI_neb_relax.traj']:
        if os.path.exists(file):
            os.remove(file)

    CI_opt = BFGS(CI_neb_file, logfile = 'CI_neb.log',trajectory = "CI_neb_relax.traj")

    CI_opt.run(fmax = 0.05, steps = 300)

    ase_write('CI_neb_final.traj', CI_Images)

    return 

