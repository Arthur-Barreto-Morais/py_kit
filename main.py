import shlex
import os
from siesta.file_creator import create
from siesta.file_creator import options as opt
from siesta.tools import chemical
from siesta.tools import k_point
from siesta.neb import neb

path_psml = "~/Siesta_Standart_psml/Scalar_Relativistic/"

print("Choose the program:")
print("1 - SIESTA")
print("2 - Quantum Expresso (QE)")

programa = input("\nOpção: ").strip()

if programa == "1":
    print("\nChoose the operation:")
    print("1 - Criar arquivo fdf")
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
        
        create.Create(args)

        if args.elements is not None:
            chemical.psml_find(fdf_file = args.label + ".fdf", dir = os.getcwd(), path_psml = path_psml)
        
        if args.type == "bands":
            pass

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

        k_point.k_point(args)

        for i, kp in enumerate(args.k_points):
            dir_kp = os.path.join("kp",f"kp_{kp}")
            chemical.psml_find(fdf_file = args.label + ".fdf", dir = dir_kp, path_psml = path_psml)
        
    elif escolha == "3":
        print("path_finder ainda não implementado.")

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

        for i in range(args.num_images):
            dir_neb = os.path.join("neb",f'image_{i}')
            chemical.psml_find(fdf_file = args.label + ".fdf", dir = dir_neb, path_psml = path_psml)
        
        neb.neb_code(args)    

    else:
        print("Opção inválida.")

elif programa == "2":
    print("QE ainda não implementado.")

else:
    print("Opção inválida.")