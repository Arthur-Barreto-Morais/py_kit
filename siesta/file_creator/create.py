from . import writer as wt
from siesta.tools import chemical, path_finder as pf, phonopy as ph, input_info as ii
import shlex
 
def Create(args,dir,path_psml):
    """ This function organize others functions that write the information blocks belonging to the FDF file"""

    fdf_file = args.label + ".fdf"

    with open(fdf_file, 'w') as f:

        f.write(wt.Label_of_System(args)+"\n"+"\n")

        f.write(wt.Input_Parameters(args)+"\n"+"\n")

        f.write(wt.Structural_Info(args)+"\n"+"\n")

        if args.type == "bands":

            args.info = False
            path_block = pf.run(args)
            f.write(wt.Bands_and_DOS_Info(args, path_block)+"\n"+"\n")

        f.write(wt.Theoretical_Info(args)+"\n"+"\n")

        f.write(wt.SCF_Info(args)+"\n"+"\n")
        
        f.write(wt.MD_Info(args)+"\n"+"\n")

        f.write(wt.Grimme_Info(args)+"\n"+"\n")

        f.write(wt.Re_Run_Info(args)+"\n"+"\n")

        f.write(wt.Write_Output(args)+"\n"+"\n")

        if args.elements is not None:
            
            chemical.psml_find(fdf_file = args.label + ".fdf", dir = dir, path_psml = path_psml)  

    return

def Create_Phonon(args, path_psml):
    """ This function construct the "header.fdf" file, necessary for phonon calculations"""

    fdf_file = "header.fdf"

    with open(fdf_file, 'w') as f:
   
        f.write(wt.Write_Header(args)+"\n"+"\n")     

    parser = ph.get_parser()
    parser.print_help()      

    while True:

        linha = input("\nChoose the arguments: ")
        
        try:
            
            ph_args = parser.parse_args(shlex.split(linha))
            break
        
        except SystemExit:
            
            print("\nERROR.")         

    var_num, var_elements = ii.get_XSF(args)

    if ph_args.dimension == 2:

        var_num = var_num * ph_args.replication * ph_args.replication 

    elif ph_args.dimension == 3:

        var_num = var_num * ph_args.replication * ph_args.replication * ph_args.replication
        
    ii.add_nums("header", var_num, var_elements)

    chemical.Pos_elements(args)
    
    ph.Phonopy(args, ph_args, path_psml)

    return
