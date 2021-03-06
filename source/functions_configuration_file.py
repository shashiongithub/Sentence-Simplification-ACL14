#===================================================================================
#title           : functions_configuration_file.py                                 =
#description     : Prepare/READ configuration file                                 =
#author          : Shashi Narayan, shashi.narayan(at){ed.ac.uk,loria.fr,gmail.com})=                                    
#date            : Created in 2014, Later revised in April 2016.                   =
#version         : 0.1                                                             =
#===================================================================================

def write_config_file(config_filename, config_data_dict):
    config_file = open(config_filename, "w")
    
    config_file.write("##############################################################\n"+
                      "####### Discourse-Complex-Simple Congifuration File ##########\n"+
                      "##############################################################\n\n")

    config_file.write("# Generation Information\n")
    if "TRAIN-BOXER-GRAPH" in config_data_dict:
        config_file.write("[TRAIN-BOXER-GRAPH]\n"+config_data_dict["TRAIN-BOXER-GRAPH"]+"\n\n")

    if "TRANSFORMATION-MODEL" in config_data_dict:
        config_file.write("[TRANSFORMATION-MODEL]\n"+" ".join(config_data_dict["TRANSFORMATION-MODEL"])+"\n\n")
    
    if "MAX-SPLIT-SIZE" in config_data_dict:
        config_file.write("[MAX-SPLIT-SIZE]\n"+str(config_data_dict["MAX-SPLIT-SIZE"])+"\n\n")

    if "RESTRICTED-DROP-RELATION" in config_data_dict:
        config_file.write("[RESTRICTED-DROP-RELATION]\n"+" ".join(config_data_dict["RESTRICTED-DROP-RELATION"])+"\n\n")

    if "ALLOWED-DROP-MODIFIER" in config_data_dict:
        config_file.write("[ALLOWED-DROP-MODIFIER]\n"+" ".join(config_data_dict["ALLOWED-DROP-MODIFIER"])+"\n\n")
                          
    if "METHOD-TRAINING-GRAPH" in config_data_dict:
        config_file.write("[METHOD-TRAINING-GRAPH]\n"+config_data_dict["METHOD-TRAINING-GRAPH"]+"\n\n")

    if "METHOD-FEATURE-EXTRACT" in config_data_dict:
        config_file.write("[METHOD-FEATURE-EXTRACT]\n"+config_data_dict["METHOD-FEATURE-EXTRACT"]+"\n\n")

    if "NUM-EM-ITERATION" in config_data_dict:
        config_file.write("[NUM-EM-ITERATION]\n"+str(config_data_dict["NUM-EM-ITERATION"])+"\n\n")

    if "LANGUAGE-MODEL" in config_data_dict:
        config_file.write("[LANGUAGE-MODEL]\n"+config_data_dict["LANGUAGE-MODEL"]+"\n\n")

    config_file.write("# Step-1\n")
    if "TRAIN-TRAINING-GRAPH" in config_data_dict:
        config_file.write("[TRAIN-TRAINING-GRAPH]\n"+config_data_dict["TRAIN-TRAINING-GRAPH"]+"\n\n")
    
    config_file.write("# Step-2\n")
    if "TRANSFORMATION-MODEL-DIR" in config_data_dict:
        config_file.write("[TRANSFORMATION-MODEL-DIR]\n"+config_data_dict["TRANSFORMATION-MODEL-DIR"]+"\n\n")

    config_file.write("# Step-3\n")
    if "MOSES-COMPLEX-SIMPLE-DIR" in config_data_dict:
        config_file.write("[MOSES-COMPLEX-SIMPLE-DIR]\n"+config_data_dict["MOSES-COMPLEX-SIMPLE-DIR"]+"\n\n")
    
    config_file.close()


def parser_config_file(config_file):
    config_data = (open(config_file, "r").read().strip()).split("\n")
    config_data_dict = {}
    count = 0
    while count < len(config_data):
        if config_data[count].startswith("["):
            # Start Information
            if config_data[count].strip()[1:-1] == "TRAIN-BOXER-GRAPH":
                config_data_dict["TRAIN-BOXER-GRAPH"] = config_data[count+1].strip()

            if config_data[count].strip()[1:-1] == "TRANSFORMATION-MODEL":
                config_data_dict["TRANSFORMATION-MODEL"] = config_data[count+1].strip().split()
            
            if config_data[count].strip()[1:-1] == "MAX-SPLIT-SIZE":
                config_data_dict["MAX-SPLIT-SIZE"] = int(config_data[count+1].strip())

            if config_data[count].strip()[1:-1] == "RESTRICTED-DROP-RELATION":
                config_data_dict["RESTRICTED-DROP-RELATION"] = config_data[count+1].strip().split()

            if config_data[count].strip()[1:-1] == "ALLOWED-DROP-MODIFIER":
                config_data_dict["ALLOWED-DROP-MODIFIER"] = config_data[count+1].strip().split()            

            if config_data[count].strip()[1:-1] == "METHOD-TRAINING-GRAPH":
                config_data_dict["METHOD-TRAINING-GRAPH"] = config_data[count+1].strip()

            if config_data[count].strip()[1:-1] == "METHOD-FEATURE-EXTRACT":
                config_data_dict["METHOD-FEATURE-EXTRACT"] = config_data[count+1].strip()
                
            if config_data[count].strip()[1:-1] == "NUM-EM-ITERATION":
                config_data_dict["NUM-EM-ITERATION"] = int(config_data[count+1].strip())   

            if config_data[count].strip()[1:-1] == "LANGUAGE-MODEL":
                config_data_dict["LANGUAGE-MODEL"] = config_data[count+1].strip()

            # Step 1
            if config_data[count].strip()[1:-1] == "TRAIN-TRAINING-GRAPH":
                config_data_dict["TRAIN-TRAINING-GRAPH"] = config_data[count+1].strip()

            # Step 2
            if config_data[count].strip()[1:-1] == "TRANSFORMATION-MODEL-DIR":
                config_data_dict["TRANSFORMATION-MODEL-DIR"] = config_data[count+1].strip()
                
            # Step 3
            if config_data[count].strip()[1:-1] == "MOSES-COMPLEX-SIMPLE-DIR":
                config_data_dict["MOSES-COMPLEX-SIMPLE-DIR"] = config_data[count+1].strip()
            
            count += 2
        else:
            count += 1
    return config_data_dict
