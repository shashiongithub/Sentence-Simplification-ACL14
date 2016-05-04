#!/usr/bin/env python
#===================================================================================
#title           : start_learning_training_models.py                               =
#description     : This will learn a model for sentence simplification.            =
#author          : Shashi Narayan, shashi.narayan(at){ed.ac.uk,loria.fr,gmail.com})=                                    
#date            : Created in 2014, Later revised in April 2016.                   =
#version         : 0.1                                                             =
#usage           : python2.7 start_learning_training_models.py -help               =
#notes           : Look at README for requirements.                                =
#===================================================================================

import os
import argparse
import sys
import datetime

sys.path.append("./source")
MOSESTOOLDIR=""
import functions_configuration_file
import functions_model_files
from saxparser_xml_stanfordtokenized_boxergraph import SAXPARSER_XML_StanfordTokenized_BoxerGraph
from saxparser_xml_stanfordtokenized_boxergraph_traininggraph import SAXPARSER_XML_StanfordTokenized_BoxerGraph_TrainingGraph

if __name__=="__main__":
    # Command line arguments ##############
    argparser = argparse.ArgumentParser(prog='python start_learn_training_models.py', description=('Start the training process.'))

    # Optional [default value: 1]
    argparser.add_argument('--start-state', help='Start state of the training process', choices=['1','2','3'], default='1', metavar=('Start_State'))

    # Optional [default value: 3]
    argparser.add_argument('--end-state', help='End state of the training process', choices=['1','2','3'], default='3', metavar=('End_State'))

    # Optional [default value: split:drop-ood:drop-rel:drop-mod] (Any of their combinations, order is not important), drop-ood only applied after split
    argparser.add_argument('--transformation', help='Transformation models learned', default="split:drop-ood:drop-rel:drop-mod", metavar=('TRANSFORMATION_MODEL'))

    # Optional [default value: 2]
    argparser.add_argument('--max-split', help='Maximum split size', choices=['2','3'], default='2', metavar=('MAX_SPLIT_SIZE'))

    # Optional [default value: agent:patient:eq:theme], (order is not important)
    argparser.add_argument('--restricted-drop-rel', help='Restricted drop relations', default="agent:patient:eq:theme", metavar=('RESTRICTED_DROP_REL'))

    # Optional [default value: jj:jjr:jjs:rb:rbr:rbs], (order is not important)
    argparser.add_argument('--allowed-drop-mod', help='Allowed drop modifiers', default="jj:jjr:jjs:rb:rbr:rbs", metavar=('ALLOWED_DROP_MOD'))

    # Optional [default value: update with most recent one]
    argparser.add_argument('--method-training-graph', help='Operation set for training graph file', choices=['method-led-lt', 'method-led-lteq', 'method-0.5-lteq-lteq', 
                                                                                                             'method-0.75-lteq-lt', 'method-0.99-lteq-lt'], 
                           default='method-0.99-lteq-lt', metavar=('Method_Training_Graph'))
    
    # Optional [default value: update with most recent one]
    argparser.add_argument('--method-feature-extract', help='Operation set for extracting features', choices=['feature-init', 'feature-Nov27'], default='feature-Nov27', 
                           metavar=('Method_Feature_Extract'))
    
    # Optional [default value: /home/ankh/Data/Simplification/Zhu-2010/PWKP_108016.tokenized.boxer-graph.xml]
    argparser.add_argument('--train-boxer-graph', help='The training corpus file (xml, stanford-tokenized, boxer-graph)', metavar=('Train_Boxer_Graph'),
                           default='/disk/scratch/Sentence-Simplification/Zhu-2010/TrainingData/PWKP_108016.tokenized.boxer-graph.xml')

    # Optional [default value: 10]
    argparser.add_argument('--num-em', help='The number of EM Algorithm iterations', metavar=('NUM_EM_ITERATION'), default='10')
        
    # Optional [default value: 0:3:/disk/scratch/Sentence-Simplification/Language-Model/simplewiki-20131030-data.srilm:0]
    argparser.add_argument('--lang-model', help='Language model information (in the moses format)', metavar=('Lang_Model'), 
                           default="0:3:/disk/scratch/Sentence-Simplification/Language-Model/simplewiki-20131030-data.srilm:0")

    # Optional (Cumpolsary when start state is >= 2)
    argparser.add_argument('--d2s-config', help='D2S Configuration file', metavar=('D2S_Config'))

    # Compulsary
    argparser.add_argument('--output-dir', help='The output directory',required=True, metavar=('Output_Directory'))
    # #####################################
    args_dict = vars(argparser.parse_args(sys.argv[1:]))
    # #####################################
    
    # Creating the output directory to store training models
    timestamp =  datetime.datetime.now().strftime("%A%d-%B%Y-%I%M%p")
    print timestamp+", Creating the output directory: "+args_dict['output_dir']
    try:
        os.mkdir(args_dict['output_dir'])
        print
    except OSError:
        print  args_dict['output_dir'] + " directory already exists.\n"

    # Configuration dictionary
    D2S_Config_data = {}
    D2S_Config = args_dict['d2s_config']
    if D2S_Config != None:
        D2S_Config_data = functions_configuration_file.parser_config_file(D2S_Config)
    else:
        D2S_Config_data["TRAIN-BOXER-GRAPH"] = args_dict['train_boxer_graph']
        D2S_Config_data["TRANSFORMATION-MODEL"] = args_dict['transformation'].split(":")
        D2S_Config_data["MAX-SPLIT-SIZE"] = int(args_dict['max_split'])
        D2S_Config_data["RESTRICTED-DROP-RELATION"] = args_dict['restricted_drop_rel'].split(":")
        D2S_Config_data["ALLOWED-DROP-MODIFIER"] = args_dict['allowed_drop_mod'].split(":")
        D2S_Config_data["METHOD-TRAINING-GRAPH"] = args_dict['method_training_graph']
        D2S_Config_data["METHOD-FEATURE-EXTRACT"] = args_dict['method_feature_extract']
        D2S_Config_data["NUM-EM-ITERATION"] = int(args_dict['num_em'])
        D2S_Config_data["LANGUAGE-MODEL"] = args_dict['lang_model']
        
    # Extracting arguments with their default values (default unless its specified)
    START_STATE = int(args_dict['start_state'])
    END_STATE = int(args_dict['end_state'])

    # Start state: 1, Starting building training graph
    state = 1
    if (int(args_dict['start_state']) <= state) and (state <= int(args_dict['end_state'])):
        timestamp = datetime.datetime.now().strftime("%A%d-%B%Y-%I%M%p")
        print timestamp+", Starting building training graph (Step-"+str(state)+") ..."
        
        print "Input training file (xml, stanford tokenized and boxer graph): " + D2S_Config_data["TRAIN-BOXER-GRAPH"] + " ..."
        TRAIN_TRAINING_GRAPH = args_dict['output_dir']+"/"+os.path.splitext(os.path.basename(D2S_Config_data["TRAIN-BOXER-GRAPH"]))[0]+".training-graph.xml"
        print "Generating training graph file (xml, stanford tokenized, boxer graph and training graph): "+TRAIN_TRAINING_GRAPH+" ..."
        
        foutput = open(TRAIN_TRAINING_GRAPH, "w")
        foutput.write("<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n")
        foutput.write("<Simplification-Data>\n")

        print "Creating the SAX file (xml, stanford tokenized and boxer graph) handler ..."
        training_xml_handler = SAXPARSER_XML_StanfordTokenized_BoxerGraph("training", D2S_Config_data["TRAIN-BOXER-GRAPH"], foutput, D2S_Config_data["TRANSFORMATION-MODEL"],
                                                                          D2S_Config_data["MAX-SPLIT-SIZE"], D2S_Config_data["RESTRICTED-DROP-RELATION"],
                                                                          D2S_Config_data["ALLOWED-DROP-MODIFIER"], D2S_Config_data["METHOD-TRAINING-GRAPH"])

        print "Start  generating training graph ..."
        print "Start parsing "+D2S_Config_data["TRAIN-BOXER-GRAPH"]+" ..."
        training_xml_handler.parse_xmlfile_generating_training_graph()

        foutput.write("</Simplification-Data>\n")
        foutput.close()

        D2S_Config_data["TRAIN-TRAINING-GRAPH"] = TRAIN_TRAINING_GRAPH
        timestamp = datetime.datetime.now().strftime("%A%d-%B%Y-%I%M%p")
        print timestamp+", Finished building training graph (Step-"+str(state)+")\n"

    # Start state: 2
    state = 2
    if (int(args_dict['start_state']) <= state) and (state <= int(args_dict['end_state'])):
        timestamp = datetime.datetime.now().strftime("%A%d-%B%Y-%I%M%p")
        print timestamp+", Starting learning transformation models (Step-"+str(state)+") ..."
        
        if "TRAIN-TRAINING-GRAPH" not in D2S_Config_data:
            print "The training graph file (xml, stanford tokenized, boxer graph and training graph) is not available."
            print "Please enter the configuration file or start with the State 1."
            timestamp = datetime.datetime.now().strftime("%A%d-%B%Y-%I%M%p")
            print timestamp+", No transformation models learned (Step-"+str(state)+")\n"
            exit(0)
            
        # @ Defining data structure @ 
        # Stores various sentence pairs (complex, simple) for SMT.
        smt_sentence_pairs = {} 
        # probability tables - store all probabilities
        probability_tables = {}
        # count tables - store counts in next iteration
        count_tables = {}
        # @ @
        
        print "Creating the em-training XML file (stanford tokenized, boxer graph and training graph) handler ..."
        em_training_xml_handler = SAXPARSER_XML_StanfordTokenized_BoxerGraph_TrainingGraph(D2S_Config_data["TRAIN-TRAINING-GRAPH"], D2S_Config_data["NUM-EM-ITERATION"], 
                                                                                           smt_sentence_pairs, probability_tables, count_tables,  D2S_Config_data["METHOD-FEATURE-EXTRACT"])

        print "Start Expectation Maximization (Inside-Outside) algorithm ..."
        timestamp = datetime.datetime.now().strftime("%A%d-%B%Y-%I%M%p")
        print timestamp+", Step "+str(state)+".1: Initialization of probability tables and populating smt_sentence_pairs ..."
        em_training_xml_handler.parse_to_initialize_probabilitytable()
        # print probability_tables

        timestamp = datetime.datetime.now().strftime("%A%d-%B%Y-%I%M%p")
        print timestamp+", Step "+str(state)+".2: Start iterating for EM Inside-Outside probabilities ..."
        em_training_xml_handler.parse_to_iterate_probabilitytable()
        # print probability_tables

        # Start writing model files
        timestamp = datetime.datetime.now().strftime("%A%d-%B%Y-%I%M%p")
        print timestamp+", Step "+str(state)+".3: Start writing model files ..."
        # Creating the output directory to store training models
        model_dir = args_dict['output_dir']+"/TRANSFORMATION-MODEL-DIR"
        timestamp =  datetime.datetime.now().strftime("%A%d-%B%Y-%I%M%p")
        print timestamp+", Creating the output model directory: "+model_dir 
        try:
            os.mkdir(model_dir)
        except OSError:
            print  model_dir + " directory already exists."
        # Wriing model files
        functions_model_files.write_model_files(model_dir, probability_tables, smt_sentence_pairs)

        D2S_Config_data["TRANSFORMATION-MODEL-DIR"] = model_dir
        timestamp = datetime.datetime.now().strftime("%A%d-%B%Y-%I%M%p")
        print timestamp+", Finished learning transformation models (Step-"+str(state)+")\n"

    # # Start state: 3
    # state = 3
    # if (int(args_dict['start_state']) <= state) and (state <= int(args_dict['end_state'])):
    #     timestamp = datetime.datetime.now().strftime("%A%d-%B%Y-%I%M%p")
    #     print timestamp+", Starting learning moses translation model (Step-"+str(state)+") ..."

    #     if "TRANSFORMATION-MODEL-DIR" not in D2S_Config_data:
    #         print "The moses training files are not available."
    #         print "Please enter the configuration file or start with the State 1."
    #         timestamp = datetime.datetime.now().strftime("%A%d-%B%Y-%I%M%p")
    #         print timestamp+", No moses models learned (Step-"+str(state)+")\n"
    #         exit(0)
        
    #     # Preparing the moses directory
    #     timestamp = datetime.datetime.now().strftime("%A%d-%B%Y-%I%M%p")
    #     print timestamp+", Step "+str(state)+".1: Preparing the moses directory ..."
    #     # Creating the output directory to store moses files
    #     moses_dir = args_dict['output_dir']+"/MOSES-COMPLEX-SIMPLE-DIR"
    #     timestamp =  datetime.datetime.now().strftime("%A%d-%B%Y-%I%M%p")
    #     print timestamp+", Creating the moses directory: "+moses_dir 
    #     try:
    #         os.mkdir(moses_dir)
    #     except OSError:
    #         print  moses_dir + " directory already exists."
    #     # Creating the corpus directory 
    #     moses_corpus_dir = args_dict['output_dir']+"/MOSES-COMPLEX-SIMPLE-DIR/corpus"
    #     timestamp =  datetime.datetime.now().strftime("%A%d-%B%Y-%I%M%p")
    #     print timestamp+", Creating the moses corpus directory: "+moses_corpus_dir 
    #     try:
    #         os.mkdir(moses_corpus_dir)
    #     except OSError:
    #         print  moses_corpus_dir + " directory already exists."    
            
    #     # Cleaning the moses training file
    #     timestamp = datetime.datetime.now().strftime("%A%d-%B%Y-%I%M%p")
    #     print timestamp+", Step "+str(state)+".2: Cleaning the moses training file ..."
    #     command = MOSESTOOLDIR+"/scripts/training/clean-corpus-n.perl "+D2S_Config_data["TRANSFORMATION-MODEL-DIR"]+"/D2S-SMT source target "+moses_corpus_dir+"/D2S-SMT-clean 1 95"
    #     os.system(command)

    #     # Running moses training 
    #     timestamp = datetime.datetime.now().strftime("%A%d-%B%Y-%I%M%p")
    #     print timestamp+", Step "+str(state)+".3: Running the moses training ..."
    #     command = (MOSESTOOLDIR+"/ools/moses/scripts/training/train-model.perl -mgiza -mgiza-cpus 3 -cores 3 -parallel -sort-buffer-size 3G -sort-batch-size 253 -sort-compress gzip -sort-parallel 3 "+
    #                "-root-dir "+moses_dir+" -corpus "+moses_corpus_dir+"/D2S-SMT-clean -f source -e target -external-bin-dir /home/ankh/Tools/mgizapp/bin "+
    #                "-lm "+D2S_Config_data["LANGUAGE-MODEL"])
    #     os.system(command)

    #     D2S_Config_data["MOSES-COMPLEX-SIMPLE-DIR"] = moses_dir
    #     timestamp = datetime.datetime.now().strftime("%A%d-%B%Y-%I%M%p")
    #     print timestamp+", Finished learning moses translation model (Step-"+str(state)+")\n"
        
    # Last Step
    config_file = args_dict['output_dir']+"/d2s.ini"
    print "Writing the configuration file: "+config_file+" ..."
    functions_configuration_file.write_config_file(config_file, D2S_Config_data)

    timestamp = datetime.datetime.now().strftime("%A%d-%B%Y-%I%M%p")
    print timestamp+", Learning process done!!!"

