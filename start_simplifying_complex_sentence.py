#!/usr/bin/env python
#===================================================================================
#title           : start_simplifying_complex_sentence.py                           =
#description     : This will apply simplification models to simplify sentences.    =
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
from nltk.metrics.distance import edit_distance

sys.path.append("./source")
MOSESTOOLDIR=""

import functions_configuration_file
import functions_model_files
import functions_prepare_elementtree_dot
from saxparser_xml_stanfordtokenized_boxergraph import SAXPARSER_XML_StanfordTokenized_BoxerGraph
from explore_decoder_graph_greedy import Explore_Decoder_Graph_Greedy
from explore_decoder_graph_explorative import Explore_Decoder_Graph_Explorative

def get_greedy_decoder_graph(test_boxerdata_dict, test_sentids, TRANSFORMATION_MODEL, MAX_SPLIT_SIZE, RESTRICTED_DROP_RELATION, ALLOWED_DROP_MODIFIER, probability_tables, METHOD_FEATURE_EXTRACT):
    mapper_transformation = {}
    moses_input = {}
    transformation_complex_count = 0

    # Transformation decoder
    decoder_graph_explorer = Explore_Decoder_Graph_Greedy(TRANSFORMATION_MODEL, MAX_SPLIT_SIZE, RESTRICTED_DROP_RELATION, ALLOWED_DROP_MODIFIER, probability_tables, METHOD_FEATURE_EXTRACT)
    for sentid in test_sentids:
        print sentid
        sent_data = test_boxerdata_dict[str(sentid)]
        main_sentence =  sent_data[0]
        main_sent_dict = sent_data[1]
        boxer_graph = sent_data[2]

        # Explore decoder graph
        decoder_graph = decoder_graph_explorer.explore_decoder_graph(str(sentid), main_sentence, main_sent_dict, boxer_graph)
        
        # # Generating boxer and decoder graph
        # if sentid not in  [13, 28, 41]:
        #     functions_prepare_elementtree_dot.run_visual_graph_creator(str(sentid), main_sentence, main_sent_dict, [], boxer_graph, decoder_graph) 

        sentence_pairs = decoder_graph.get_final_sentences(main_sentence, main_sent_dict, boxer_graph)
        transformed_sentences = [item[0] for item in sentence_pairs]

        # Writing transformation results
        mapper_transformation[sentid] = []
        for sent in transformed_sentences:
            mapper_transformation[sentid].append(transformation_complex_count)
            moses_input[transformation_complex_count] = sent
            transformation_complex_count += 1
    return mapper_transformation, moses_input

def get_explorative_decoder_graph(test_boxerdata_dict, test_sentids, TRANSFORMATION_MODEL, MAX_SPLIT_SIZE, RESTRICTED_DROP_RELATION, ALLOWED_DROP_MODIFIER, probability_tables, METHOD_FEATURE_EXTRACT):
    mapper_transformation = {}
    moses_input = {}
    transformation_complex_count = 0
    
    # Transformation decoder
    decoder_graph_explorer = Explore_Decoder_Graph_Explorative(TRANSFORMATION_MODEL, MAX_SPLIT_SIZE, RESTRICTED_DROP_RELATION, ALLOWED_DROP_MODIFIER, probability_tables, METHOD_FEATURE_EXTRACT)
    for sentid in test_sentids:
        print sentid
        sent_data = test_boxerdata_dict[str(sentid)]
        main_sentence =  sent_data[0]
        main_sent_dict = sent_data[1]
        boxer_graph = sent_data[2]

        # Explore decoder graph
        print "Building decoder graph ..."
        decoder_graph = decoder_graph_explorer.explore_decoder_graph(str(sentid), main_sentence, main_sent_dict, boxer_graph)

        # Start updating edges with the probabilities, for unseen : 0.5/0.5
        print "Updating probability bottom-up ..."
        node_probability_dict, potential_edges = decoder_graph_explorer.start_probability_update(main_sentence, main_sent_dict, boxer_graph, decoder_graph)

        # Filtered decoder graph
        print "Creating filtered decoder graph ..."
        filtered_decoder_graph = decoder_graph_explorer.create_filtered_decoder_graph(potential_edges, main_sentence, main_sent_dict, boxer_graph, decoder_graph)

        # Generating boxer and decoder graph
        functions_prepare_elementtree_dot.run_visual_graph_creator(str(sentid), main_sentence, main_sent_dict, [], boxer_graph, filtered_decoder_graph)

        sentence_pairs = filtered_decoder_graph.get_final_sentences(main_sentence, main_sent_dict, boxer_graph)
        transformed_sentences = [item[0] for item in sentence_pairs]

        # Writing transformation results
        mapper_transformation[sentid] = []
        for sent in transformed_sentences:
            mapper_transformation[sentid].append(transformation_complex_count)
            moses_input[transformation_complex_count] = sent
            transformation_complex_count += 1
    return mapper_transformation, moses_input

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(prog='python simplify_complex_sentence.py', description=('Start simplifying complex sentences.'))

    # Optional [default value: /disk/scratch/Sentence-Simplification/Zhu-2010/TestData/complex.tokenized.boxer-graph.xml]
    argparser.add_argument('--test-boxer-graph', help='The test corpus file (xml, stanford-tokenized, boxer-graph)', metavar=('Test_Boxer_Graph'),
                           default='/disk/scratch/Sentence-Simplification/Zhu-2010/TestData/complex.tokenized.boxer-graph.xml')

    # Optional [default value: 10]
    argparser.add_argument('--nbest-distinct', help='N Best Distinct produced from Moses', metavar=('N_Best_Distinct'), default='10')

    # Optional [default value: greedy]
    argparser.add_argument('--explore-decoder', help='Method for generating the decoder graph', metavar=('Explore_Decoder'), choices=['greedy', 'explorative'], default='greedy')

    # Compolsary 
    argparser.add_argument('--d2s-config', help='D2S Configuration file', required=True, metavar=('D2S_Config'))

    # Compolsary
    argparser.add_argument('--output-dir', help='The output directory', required=True, metavar=('Output_Directory'))
    # #####################################
    args_dict = vars(argparser.parse_args(sys.argv[1:]))
    # #####################################

    # STEP:1 Creating test directory in the output directory
    timestamp =  datetime.datetime.now().strftime("%A%d-%B%Y-%I%M%p")
    test_output_directory = args_dict['output_dir']+"/Test-Results-"+args_dict["explore_decoder"].upper()
    print timestamp+", Creating test result directory: "+test_output_directory
    try:
        os.mkdir(test_output_directory)
    except OSError:
        print test_output_directory + " directory already exists."
        
    # STEP:2 Configuration dictionary
    timestamp =  datetime.datetime.now().strftime("%A%d-%B%Y-%I%M%p")
    print "\n"+timestamp+", Reading the D2S Configuration file ..."
    D2S_Config_data = functions_configuration_file.parser_config_file(args_dict['d2s_config'])

    # STEP:3 Reading transformation model files
    timestamp =  datetime.datetime.now().strftime("%A%d-%B%Y-%I%M%p")
    print "\n"+timestamp+", Reading transformation model files ..."
    probability_tables = functions_model_files.read_model_files(D2S_Config_data["TRANSFORMATION-MODEL-DIR"], D2S_Config_data["TRANSFORMATION-MODEL"])

    # STEP:4 Reading the test corpus file (xml, stanford-tokenized, boxer-graph) ..."
    timestamp =  datetime.datetime.now().strftime("%A%d-%B%Y-%I%M%p")
    print "\n"+timestamp+", Start reading test corpus file (xml, stanford-tokenized, boxer-graph): "+args_dict['test_boxer_graph']+" ..." 
    print "Creating the SAX file (xml, stanford tokenized and boxer graph) handler ..."
    test_boxerdata_dict = {}
    test_sentids = []
    testing_xml_handler = SAXPARSER_XML_StanfordTokenized_BoxerGraph("testing", args_dict['test_boxer_graph'], test_boxerdata_dict, D2S_Config_data["TRANSFORMATION-MODEL"],
                                                                     D2S_Config_data["MAX-SPLIT-SIZE"], D2S_Config_data["RESTRICTED-DROP-RELATION"],
                                                                     D2S_Config_data["ALLOWED-DROP-MODIFIER"], D2S_Config_data["METHOD-TRAINING-GRAPH"])
    print "Start parsing "+args_dict['test_boxer_graph']+" ..."
    testing_xml_handler.parse_xmlfile_generating_training_graph()
    test_sentids = [int(item) for item in test_boxerdata_dict.keys()]
    test_sentids.sort()

    # STEP:5 Applying the transformation models and creating the output of transformation
    timestamp =  datetime.datetime.now().strftime("%A%d-%B%Y-%I%M%p")
    print "\n"+timestamp+", Applying the transformation models and writing complex sentences after transformation ..."
    mapper_transformation = {}
    moses_input = {}
    if args_dict["explore_decoder"] == "greedy":
        mapper_transformation, moses_input = get_greedy_decoder_graph(test_boxerdata_dict, test_sentids, D2S_Config_data["TRANSFORMATION-MODEL"], D2S_Config_data["MAX-SPLIT-SIZE"], 
                                                                      D2S_Config_data["RESTRICTED-DROP-RELATION"], D2S_Config_data["ALLOWED-DROP-MODIFIER"], 
                                                                      probability_tables, D2S_Config_data["METHOD-FEATURE-EXTRACT"])
    else:
        mapper_transformation, moses_input = get_explorative_decoder_graph(test_boxerdata_dict, test_sentids, D2S_Config_data["TRANSFORMATION-MODEL"], D2S_Config_data["MAX-SPLIT-SIZE"], 
                                                                           D2S_Config_data["RESTRICTED-DROP-RELATION"], D2S_Config_data["ALLOWED-DROP-MODIFIER"], 
                                                                           probability_tables, D2S_Config_data["METHOD-FEATURE-EXTRACT"])

    print "Writing "+test_output_directory+"/transformation-output.moses-input ..."
    d2s_complex_file = open(test_output_directory+"/transformation-output.moses-input", "w")
    for sentid in test_sentids:
        for moses_input_id in mapper_transformation[sentid]:
            transformed_sent = moses_input[moses_input_id]
            d2s_complex_file.write(transformed_sent.encode('utf-8')+"\n")
    d2s_complex_file.close()

    print "Writing "+test_output_directory+"/transformation-output.map ..."
    d2s_complex_map = open(test_output_directory+"/transformation-output.map", "w")
    sentids =   mapper_transformation.keys()
    sentids.sort()
    for sentid in sentids:
         d2s_complex_map.write(str(sentid)+" ")
         for item in mapper_transformation[sentid]:
             d2s_complex_map.write(str(item)+" ")
         d2s_complex_map.write("\n")
    d2s_complex_map.close()

    print "Writing "+test_output_directory+"/transformation-output.simple ..."
    d2s_complex_file = open(test_output_directory+"/transformation-output.simple", "w")
    for sentid in test_sentids:
        simple_sentence = []
        for moses_input_id in mapper_transformation[sentid]:
            transformed_sent = moses_input[moses_input_id]
            simple_sentence.append(transformed_sent)    
        d2s_complex_file.write((" ".join(simple_sentence)).encode('utf-8')+"\n")
    d2s_complex_file.close()

    # # STEP:6 Running Moses
    # timestamp =  datetime.datetime.now().strftime("%A%d-%B%Y-%I%M%p")
    # print "\n"+timestamp+", Applying the moses translation model ..."
    # command = (MOSESTOOLDIR+"/bin/moses -f "+D2S_Config_data["MOSES-COMPLEX-SIMPLE-DIR"]+"/model/moses.ini "+
    #            "-n-best-list "+test_output_directory+"/transformation-output.moses-"+args_dict['nbest_distinct']+"best-distinct.simple"+" "+args_dict['nbest_distinct']+" distinct "+
    #            "-input-file "+test_output_directory+"/transformation-output.moses-input")
    # os.system(command)

    # # Reading the moses output file
    # print "Parsing the moses output file: "+test_output_directory+"/transformation-output.moses-"+args_dict['nbest_distinct']+"best-distinct.simple"
    # moses_output = {}
    # finput = open(test_output_directory+"/transformation-output.moses-"+args_dict['nbest_distinct']+"best-distinct.simple", "r")
    # datalines = finput.readlines()
    # for line in datalines:
    #     parts = line.split(" ||| ")
    #     sentid = int(parts[0].strip())
    #     sent = parts[1].strip()
    #     if sentid not in moses_output:
    #         moses_output[sentid] = [sent]
    #     else:
    #         moses_output[sentid].append(sent)
    # finput.close()

    # # Storing the best moses output
    # timestamp =  datetime.datetime.now().strftime("%A%d-%B%Y-%I%M%p")
    # print "\n"+timestamp+", Best output of moses ..."
    # final_output_filename = test_output_directory+"/transformation-output.moses-"+args_dict['nbest_distinct']+"best-distinct.simple.best"
    # print "Writing to the file: "+final_output_filename
    # final_output_file = open(final_output_filename, "w")
    # for sentid in test_sentids:
    #     simple_sentence = []
    #     for moses_input_id in mapper_transformation[sentid]:
    #         moses_simple_output_best = moses_output[moses_input_id][0]
    #         simple_sentence.append(moses_simple_output_best)
    #     final_output_file.write(" ".join(simple_sentence)+"\n") 
    # final_output_file.close()

    # # Running posthoc reranking
    # timestamp =  datetime.datetime.now().strftime("%A%d-%B%Y-%I%M%p")
    # print "\n"+timestamp+", Running the post-hoc reranking ..."
    # posthoc_reranked = {}
    # for sentid in test_sentids:
    #     for moses_input_id in mapper_transformation[sentid]:
    #         moses_complex_input = moses_input[moses_input_id]
    #         moses_simple_outputs = moses_output[moses_input_id]

    #         posthoc_reranked[moses_input_id] = []
    #         for simple_output in moses_simple_outputs:
    #             edit_dist = edit_distance(simple_output, moses_complex_input)
    #             posthoc_reranked[moses_input_id].append((edit_dist, simple_output))

    #         # More different are ranked at top
    #         posthoc_reranked[moses_input_id].sort(reverse=True)
            
    # # Writing post-hoc reranked output
    # final_output_filename = test_output_directory+"/transformation-output.moses-"+args_dict['nbest_distinct']+"best-distinct.post-hoc-reranking.simple"
    # print "Writing to the file: "+final_output_filename
    # final_output_file = open(final_output_filename, "w")
    # for sentid in test_sentids:
    #     for moses_input_id in mapper_transformation[sentid]:
    #         for item in posthoc_reranked[moses_input_id]:
    #             final_output_file.write(str(moses_input_id)+"\t"+str(item[0])+"\t"+item[1]+"\n")
    #         final_output_file.write("\n")
    # final_output_file.close()

    # # Writing post-hoc reranked best output
    # final_output_filename = test_output_directory+"/transformation-output.moses-"+args_dict['nbest_distinct']+"best-distinct.post-hoc-reranking.simple.best"
    # print "Writing to the file: "+final_output_filename
    # final_output_file = open(final_output_filename, "w")
    # for sentid in test_sentids:
    #     simple_sentence = []
    #     for moses_input_id in mapper_transformation[sentid]:
    #         simple_output_best = posthoc_reranked[moses_input_id][0][1]
    #         simple_sentence.append(simple_output_best)
    #     final_output_file.write(" ".join(simple_sentence)+"\n") 
    # final_output_file.close()


    # # test_boxerdata_dict = {}
    # # test_sentids = []    

    # # mapper_transformation = {}
    # # moses_input = {}

    # # moses_output = {}
    
    # # posthoc_reranked = {}
