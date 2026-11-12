import shlex
import os
#from py_kit.siesta.file_creator.create import Create_Phonon
from siesta import create, options as opt, k_point, neb, path_finder as pf, input_info as ii, chemical

path_psml = os.path.join(os.path.dirname(__file__), "siesta", "Siesta_Standart_psml", "Scalar_Relativistic")

print("Choose the program:")
print("1 - SIESTA")
print("2 - Quantum Expresso (QE)")

programa = input("\nOpção: ").strip()

if programa == "1":
    print("\nChoose the operation:")
    print("1 - Create fdf file")
    print("2 - K_point")
    print("3 - path_finder")
    print("4 - neb_code")

    escolha = input("\nOption: ").strip()

    if escolha == "1":
        parser = opt.Build_Parser()
        parser.print_help()

        while True:
            linha = input("\nChoose the arguments: ")
            try:
                args = parser.parse_args(shlex.split(linha))
                break

            except SystemExit:
                print("\nERROR.")

        with open("Arguments.txt", 'w') as f:
            for key, value in vars(args).items():
                f.write(f"{key}={value}\n")
        
        create.Create(args,os.getcwd(),path_psml)

        if os.path.exists(f"{args.label}.XSF"):

            if os.path.exists("vec.dat"):
                os.remove("vec.dat")

            if os.path.exists("pos.dat"):
                os.remove("pos.dat")

            var_num, var_elements = ii.get_XSF(args)

            if os.path.exists("vec.dat") and os.path.exists("pos.dat"):
                ii.check_right_hand(args)
                ii.add_vec(args.label)
                ii.add_pos(args.label)

            if args.num_atoms or args.elements is None:
                ii.add_nums(args.label, var_num, var_elements)
                chemical.Pos_elements(args)
                chemical.psml_find(f"{args.label}.fdf", os.getcwd(),path_psml)

        if args.type == "pho":
            create.Create_Phonon(args, path_psml)
    elif escolha == "2":
        parser = k_point.get_parser()
        parser.print_help()

        while True:
            linha = input("\nChoose the arguments: ")
            try:
                args = parser.parse_args(shlex.split(linha))
                break
            except SystemExit:
                print("\nERROR.")

        with open("Arguments_kp.txt", 'w') as f:
            for key, value in vars(args).items():
                f.write(f"{key}={value}\n")

        k_point.k_point(args, path_psml)
        
    elif escolha == "3":
        parser = pf.get_parser()      
        parser.print_help()

        while True:
            linha = input("\nChoose the arguments: ")
            try:
                args = parser.parse_args(shlex.split(linha))
                break
            except SystemExit:
                print("\nERROR.")
        
        pf.run(args)

    elif escolha == "4":
        parser = neb.get_parser()        
        parser.print_help()

        while True:
            linha = input("\nChoose the arguments: ")
            try:
                args = parser.parse_args(shlex.split(linha))
                break
            except SystemExit:
                print("\nERROR.")

        with open("Arguments_neb.txt", 'w') as f:
            for key, value in vars(args).items():
                f.write(f"{key}={value}\n")   
        
        neb.neb_code(args, path_psml)    

    else:
        print("Opção inválida.")

elif programa == "2":
    print("QE ainda não implementado.")

else:
    print("Opção inválida.")