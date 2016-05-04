#!/usr/bin/env python
#===================================================================================
#title           : functions_model_files.py                                        =
#description     : Model file Handler                                              =
#author          : Shashi Narayan, shashi.narayan(at){ed.ac.uk,loria.fr,gmail.com})=                                    
#date            : Created in 2014, Later revised in April 2016.                   =
#version         : 0.1                                                             =
#===================================================================================

def read_model_files(model_dir, transformation_model):
    probability_tables = {}
    for trans_method in transformation_model:
        modelfile = model_dir+"/D2S-"+trans_method.upper()+".model"
        probability_tables[trans_method] = {}            
        with open(modelfile) as infile:
                for line in infile:
                    data = line.split()
                    if data[0] not in probability_tables[trans_method]:
                        probability_tables[trans_method][data[0]] = {data[1]:float(data[2])}
                    else:
                        probability_tables[trans_method][data[0]][data[1]] = float(data[2])
        print modelfile + " done ..."
    return probability_tables 

def write_model_files(model_dir, probability_tables, smt_sentence_pairs):
    if "split" in probability_tables:
        print "Writing "+model_dir+"/D2S-SPLIT.model ..."
        foutput = open(model_dir+"/D2S-SPLIT.model", "w")
        split_feature_set = probability_tables["split"].keys()
        split_feature_set.sort()
        for item in split_feature_set:
            foutput.write(item.encode('utf-8')+"\t"+"true"+"\t"+str(probability_tables["split"][item]["true"])+"\n")
            foutput.write(item.encode('utf-8')+"\t"+"false"+"\t"+str(probability_tables["split"][item]["false"])+"\n")
        foutput.close()
        
    if "drop-ood" in probability_tables:
        print "Writing "+model_dir+"/D2S-DROP-OOD.model ..."
        foutput = open(model_dir+"/D2S-DROP-OOD.model", "w")
        drop_ood_feature_set = probability_tables["drop-ood"].keys()
        drop_ood_feature_set.sort()
        for item in drop_ood_feature_set:
            foutput.write(item.encode('utf-8')+"\t"+"true"+"\t"+str(probability_tables["drop-ood"][item]["true"])+"\n")
            foutput.write(item.encode('utf-8')+"\t"+"false"+"\t"+str(probability_tables["drop-ood"][item]["false"])+"\n")
        foutput.close()
        
    if "drop-rel" in probability_tables:
        print "Writing "+model_dir+"/D2S-DROP-REL.model ..."
        foutput = open(model_dir+"/D2S-DROP-REL.model", "w")
        drop_rel_feature_set = probability_tables["drop-rel"].keys()
        drop_rel_feature_set.sort()
        for item in drop_rel_feature_set:
            foutput.write(item.encode('utf-8')+"\t"+"true"+"\t"+str(probability_tables["drop-rel"][item]["true"])+"\n")
            foutput.write(item.encode('utf-8')+"\t"+"false"+"\t"+str(probability_tables["drop-rel"][item]["false"])+"\n")
        foutput.close()

    if "drop-mod" in probability_tables:
        print "Writing "+model_dir+"/D2S-DROP-MOD.model ..."
        foutput = open(model_dir+"/D2S-DROP-MOD.model", "w")
        drop_mod_feature_set = probability_tables["drop-mod"].keys()
        drop_mod_feature_set.sort()
        for item in drop_mod_feature_set:
            foutput.write(item.encode('utf-8')+"\t"+"true"+"\t"+str(probability_tables["drop-mod"][item]["true"])+"\n")
            foutput.write(item.encode('utf-8')+"\t"+"false"+"\t"+str(probability_tables["drop-mod"][item]["false"])+"\n")
        foutput.close()       

    # Writing SMT training data
    print "Writing "+model_dir+"/D2S-SMT.source ..."
    print "Writing "+ model_dir+"/D2S-SMT.target ..."
    fsource = open(model_dir+"/D2S-SMT.source", "w")
    ftarget = open(model_dir+"/D2S-SMT.target", "w")
    for sentid in smt_sentence_pairs:
        # print sentid
        # print smt_sentence_pairs[sentid]
        for pair in smt_sentence_pairs[sentid]:
            fsource.write(pair[0].encode('utf-8')+"\n")
            ftarget.write(pair[1].encode('utf-8')+"\n")
    fsource.close()
    ftarget.close()
