#!/usr/bin/env python
import os
import argparse
import sys
import random 
import base64
import uuid

import xml.etree.ElementTree as ET
from xml.dom import minidom
from nltk.metrics.distance import edit_distance

# import matplotlib.pyplot as plt

### Global Variables
CHUNK_SIZE=10000

## NewSella Dataset

ZHUDATA_FILE_ORG="/gpfs/scratch/snarayan/Sentence-Simplification/Newsella/V0V4_V1V4_V2V4_V3V4_V0V3_V0V2_V1V3.aner.ori.train"
ZHUDATA_FILE_MAIN="/gpfs/scratch/snarayan/Sentence-Simplification/Newsella/V0V4_V1V4_V2V4_V3V4_V0V3_V0V2_V1V3.aner.ori.train.src"
ZHUDATA_FILE_SIMPLE="/gpfs/scratch/snarayan/Sentence-Simplification/Newsella/V0V4_V1V4_V2V4_V3V4_V0V3_V0V2_V1V3.aner.ori.train.dst"

BOXER_DATADIR="/gpfs/scratch/snarayan/Sentence-Simplification/Newsella/train_split_boxer"

## Zhu Dataset

# ZHUDATA_FILE_ORG="/home/ankh/Data/Simplification/Zhu-2010/PWKP_108016"
# ZHUDATA_FILE_MAIN="/home/ankh/Data/Simplification/Zhu-2010/PWKP_108016.main.tokenize"
# ZHUDATA_FILE_SIMPLE="/home/ankh/Data/Simplification/Zhu-2010/PWKP_108016.simple.tokenize"

# ZHUDATA_FILE_ORG="/home/ankh/Data/Simplification/Zhu-2010/Head_100"
# ZHUDATA_FILE_MAIN="/home/ankh/Data/Simplification/Zhu-2010/Head_100.main.tokenize"
# ZHUDATA_FILE_SIMPLE="/home/ankh/Data/Simplification/Zhu-2010/Head_100.simple.tokenize"

# ZHUDATA_FILE_ORG="/home/ankh/Data/Simplification/Zhu-2010/Head_200"
# ZHUDATA_FILE_MAIN="/home/ankh/Data/Simplification/Zhu-2010/Head_200.main.tokenize"
# ZHUDATA_FILE_SIMPLE="/home/ankh/Data/Simplification/Zhu-2010/Head_200.simple.tokenize"

# BOXER_DATADIR="/home/ankh/Data/Simplification/Zhu-2010/Boxer-Data"

class Boxer_XML_Handler:
    def parse_boxer_xml(self, xdrs_elt):
        arg_dict = {}
        rel_nodes = []
        extra_nodes = []

        # Process all dr
        for dr in xdrs_elt.iter('dr'):
            arg = dr.attrib["name"]
            if arg not in arg_dict:
                arg_dict[arg] = {"position":[], "preds":[]}

            for index in dr.findall('index'):
                position = int(index.attrib["pos"])
                wordid = index.text

                if (position, wordid) not in arg_dict[arg]["position"]:
                    arg_dict[arg]["position"].append((position, wordid))
        
        # Process all prop
        for prop in xdrs_elt.iter('prop'):
            arg = prop.attrib["argument"]
            if arg not in arg_dict:
                arg_dict[arg] = {"position":[], "preds":[]}

            for index in prop.findall('index'):
                position = int(index.attrib["pos"])
                wordid = index.text

                if (position, wordid) not in arg_dict[arg]["position"]:
                    arg_dict[arg]["position"].append((position, wordid))   

        # Process all pred
        for pred in xdrs_elt.iter('pred'):
            arg = pred.attrib["arg"]
            symbol = pred.attrib["symbol"]

            if arg not in arg_dict:
                arg_dict[arg] = {"position":[], "preds":[]}

            predicate = [symbol, []]
            for index in pred.findall('index'):
                position = int(index.attrib["pos"])
                wordid = index.text

                if (position, wordid) not in arg_dict[arg]["position"]:
                    arg_dict[arg]["position"].append((position, wordid))
                if (position, wordid) not in predicate[1]:
                    predicate[1].append((position, wordid))   
            arg_dict[arg]["preds"].append(predicate)

        # Process all named
        for named in xdrs_elt.iter('named'):
            arg = named.attrib["arg"]
            symbol = named.attrib["symbol"]

            if arg not in arg_dict:
                arg_dict[arg] = {"position":[], "preds":[]}

            named_pred = [symbol, []]
            for index in named.findall('index'):
                position = int(index.attrib["pos"])
                wordid = index.text

                if (position, wordid) not in arg_dict[arg]["position"]:
                    arg_dict[arg]["position"].append((position, wordid))
                if (position, wordid) not in named_pred[1]:
                    named_pred[1].append((position, wordid))   
            arg_dict[arg]["preds"].append(named_pred)            

        # Process all card
        for card in xdrs_elt.iter('card'):
            arg = card.attrib["arg"]
            value = card.attrib["value"]

            if arg not in arg_dict:
                arg_dict[arg] = {"position":[], "preds":[]}

            card_pred = [value, []]
            for index in card.findall('index'):
                position = int(index.attrib["pos"])
                wordid = index.text

                if (position, wordid) not in arg_dict[arg]["position"]:
                    arg_dict[arg]["position"].append((position, wordid))
                if (position, wordid) not in card_pred[1]:
                    card_pred[1].append((position, wordid))   
            arg_dict[arg]["preds"].append(card_pred)

        # Process all timex
        for timex in xdrs_elt.iter('timex'):
            arg = timex.attrib["arg"]
            datetime = ""
            for date in timex.iter('date'):
                datetime = date.text
            for time in timex.iter('time'):
                datetime = time.text

            if arg not in arg_dict:
                arg_dict[arg] = {"position":[], "preds":[]}

            timex_pred = [datetime, []]
            for index in timex.findall('index'):
                position = int(index.attrib["pos"])
                wordid = index.text

                if (position, wordid) not in arg_dict[arg]["position"]:
                    arg_dict[arg]["position"].append((position, wordid))
                if (position, wordid) not in timex_pred[1]:
                    timex_pred[1].append((position, wordid))   
            arg_dict[arg]["preds"].append(timex_pred)            

        # Process not/or/imp/whq
        for not_node in xdrs_elt.iter('not'):
            index_list = not_node.findall('index')
            if len(index_list) != 0:
                not_pred = ["not", []]
                for index in index_list:
                    position = int(index.attrib["pos"])
                    wordid = index.text
                    if (position, wordid) not in not_pred[1]:
                        not_pred[1].append((position, wordid))
                extra_nodes.append(not_pred)
        for or_node in xdrs_elt.iter('or'):
            index_list = or_node.findall('index')
            if len(index_list) != 0:
                or_pred = ["or", []]
                for index in index_list:
                    position = int(index.attrib["pos"])
                    wordid = index.text
                    if (position, wordid) not in or_pred[1]:
                        or_pred[1].append((position, wordid))
                extra_nodes.append(or_pred)
        for imp_node in xdrs_elt.iter('imp'):
            index_list = imp_node.findall('index')
            if len(index_list) != 0:
                imp_pred = ["imp", []]
                for index in index_list:
                    position = int(index.attrib["pos"])
                    wordid = index.text
                    if (position, wordid) not in imp_pred[1]:
                        imp_pred[1].append((position, wordid))
                extra_nodes.append(imp_pred)        
        for whq_node in xdrs_elt.iter('whq'):
            index_list = whq_node.findall('index')
            if len(index_list) != 0:
                whq_pred = ["whq", []]
                for index in index_list:
                    position = int(index.attrib["pos"])
                    wordid = index.text
                    if (position, wordid) not in whq_pred[1]:
                        whq_pred[1].append((position, wordid))
                extra_nodes.append(whq_pred)                    
        
        # Process Rel node
        for rel_node in xdrs_elt.iter('rel'): 
            arg1 = rel_node.attrib["arg1"]
            arg2 = rel_node.attrib["arg2"]
            symbol = rel_node.attrib["symbol"]

            if arg1 not in arg_dict:
                arg_dict[arg1] = {"position":[], "preds":[]}
            if arg2 not in arg_dict:
                arg_dict[arg2] = {"position":[], "preds":[]}

            index_list = rel_node.findall('index')
            if (len(index_list) != 0) or (len(index_list) == 0 and symbol=="nn"):
                if symbol=="nn":
                    # Revert arguments
                    temp = arg2
                    arg2 = arg1
                    arg1 = temp
                    rel_nodes.append([symbol, arg1, arg2, []])
                    
                elif symbol=="eq":
                    if len(index_list) == 1:
                        position = int(index_list[0].attrib["pos"])
                        wordid = index_list[0].text
                        
                        for arg in arg_dict:
                            if (position, wordid) in arg_dict[arg]["position"]:
                                if ["event", []] in arg_dict[arg]["preds"]:
                                    rel_nodes.append([symbol, arg, arg1, [(position, wordid)]])
                                    rel_nodes.append([symbol, arg, arg2, [(position, wordid)]])
                else:
                    rel_pred = [symbol, arg1, arg2, []]
                    for index in index_list:
                        position = int(index.attrib["pos"])
                        wordid = index.text
                        if (position, wordid) not in rel_pred[3]:
                            rel_pred[3].append((position, wordid))
                    rel_nodes.append(rel_pred) 

        
        return arg_dict, rel_nodes, extra_nodes

class Boxer_Data_Tracker:
    def __init__(self, datatype, filefailed):
        self.datatype = datatype
        self.filefailed = filefailed

        self.xml_file = None
        self.xdrs_index = None
        self.xdrs_list = None

    def initialise_boxer_tracker(self, boxer_filename):
        print "Initialising a new boxer file: "+boxer_filename+" ..."
        self.xml_file = boxer_filename
        xdrs_output = ET.parse(BOXER_DATADIR+"/"+boxer_filename)
        self.xdrs_list = xdrs_output.findall('xdrs')
        print len(self.xdrs_list)
        self.xdrs_index = 0

    def graph_boxer_element(self, xdrs_elt, sent_span):
        # Parse the XDRS
        arg_dict, rel_nodes, extra_nodes = Boxer_XML_Handler().parse_boxer_xml(xdrs_elt)
        #print arg_dict, rel_nodes, extra_nodes        

        # Adding extra nodes to arg_dict/node dict
        extra_node_count = 1
        for nodeinfo in extra_nodes:
            arg_dict["E"+str(extra_node_count)] = {"position":nodeinfo[1][:], "preds":[nodeinfo[:]]}
            extra_node_count += 1
        
        # Creating edge list and relation dict
        edge_list = []
        rel_dict = {}

        rel_node_count = 1
        for relinfo in rel_nodes:
            relation = relinfo[0]
            parentarg = relinfo[1]
            deparg = relinfo[2]
            indexlist = relinfo[3]
            
            rel_dict["R"+str(rel_node_count)] = [relation, indexlist[:]]
            edge_list.append((parentarg, deparg, "R"+str(rel_node_count)))
            rel_node_count += 1

        # Get the boxer span
        boxer_span = []
        for arg in arg_dict:
            for position in arg_dict[arg]["position"]:
                if position not in boxer_span:
                    boxer_span.append(position)
        for relarg in rel_dict:
            for position in rel_dict[relarg][1]:
                if position not in boxer_span:
                    boxer_span.append(position)
        boxer_span.sort()
        boxer_span_ids = [elt[1] for elt in boxer_span]
        # Adding nodes for left out word positions in discourse
        out_of_dis_count = 1
        for elt in sent_span:
            if elt not in boxer_span_ids:
                arg_dict["OOD"+str(out_of_dis_count)] = {"position":[(-1, elt)], "preds":[]}
                out_of_dis_count += 1

        # Prepare Boxer Tree 
        boxer = ET.Element('box')
        nodes = ET.SubElement(boxer, "nodes")
        for arg in arg_dict:            
            # print arg
            # print arg_dict[arg]
            node = ET.SubElement(nodes, "node")
            node.attrib = {"sym":arg}

            span = ET.SubElement(node, "span")
            position_list = arg_dict[arg]["position"]
            position_list.sort()
            for position in position_list:
                location = ET.SubElement(span, "loc")
                location.attrib = {"id":position[1]}#{"pos":str(position[0]),"id":position[1]}

            preds = ET.SubElement(node, "preds")
            predicate_list = arg_dict[arg]["preds"]
            predicate_list.sort()
            for predinfo in predicate_list:
                # print predinfo
                pred = ET.SubElement(preds, "pred")
                predsymbol = predinfo[0]
                pred.attrib = {"sym":predsymbol}

                position_list = predinfo[1]
                position_list.sort()
                for position in position_list:
                    location = ET.SubElement(pred, "loc")
                    location.attrib = {"id":position[1]}#{"pos":str(position[0]),"id":position[1]}
                    
        rels = ET.SubElement(boxer, "rels")
        for relarg in rel_dict:
            rel = ET.SubElement(rels, "rel")
            rel.attrib = {"sym":relarg}
            pred = ET.SubElement(rel, "pred")
            pred.attrib = {"sym":rel_dict[relarg][0]}
            span = ET.SubElement(rel, "span")
            position_list = rel_dict[relarg][1]
            position_list.sort()
            for position in position_list:
                location = ET.SubElement(span, "loc")
                location.attrib = {"id":position[1]}#{"pos":str(position[0]),"id":position[1]}

        edges = ET.SubElement(boxer, "edges")
        for edgeinfo in edge_list:
            edge = ET.SubElement(edges, "edge")
            edge.attrib = {"par":edgeinfo[0], "dep":edgeinfo[1], "lab":edgeinfo[2]}
        return boxer

    def construct_boxer_element(self, boxer_filename, sentence_org):
        # print sentence_org
        if self.xml_file != boxer_filename:
            
            # Check everything is used from before, otherwise it could be an error
            if self.xdrs_list != None:
                if len(self.xdrs_list) != self.xdrs_index:
                    print "Not everything was consumed from previous file"
                    exit(0)
            

            self.initialise_boxer_tracker(boxer_filename)

        candidate_xdrs = self.xdrs_list[self.xdrs_index]

        # Creating Sentence Element
        sentence_xml = ""
        sentence_span = []
        sentence = ET.Element('s')
        words = (candidate_xdrs.find("words")).findall("word")
        postags = (candidate_xdrs.find("postags")).findall("postag")
        for word_elt, postag_elt in zip(words, postags):
            word = word_elt.text
            wordid = word_elt.get('{http://www.w3.org/XML/1998/namespace}id')# ("xml:id")
            pos = postag_elt.text
            posid = postag_elt.get("index")

            if wordid != posid:
                print "Warning: Both ids did not match."
                exit(0)
            else:
                sentence_xml += word +" "
                word_newelt = ET.SubElement(sentence, 'w')
                word_newelt.attrib = {"id":wordid, "pos":pos}
                word_newelt.text = word

                sentence_span.append(wordid) 
                
        sentence_xml = sentence_xml.strip()
        if sentence_xml !=  sentence_org:
            # It still could be the same sentence (825.000 --> 825.0 in Boxer output), edit distance at word level, sentence could have maximum 10 numbers
            if edit_distance(sentence_xml.split(), sentence_org.split()) > 10:
                # Assuming that boxer failed for this one so skip and return with sentence itself
                
                # print
                print sentence_xml
                # print sentence_org
                print "Both sentence did not match.\n"
                # exit(0)

                headelt = ET.Element(self.datatype)
                sentence = ET.SubElement(headelt, 's')
                sentence.text = sentence_org

                outputsent = sentence_org.encode("utf-8")
                self.filefailed.write(outputsent+"\n")
                return headelt
          
        # Creating the head element
        headelt = ET.Element(self.datatype)
        headelt.append(sentence)

        # Creating boxer element
        boxer = self.graph_boxer_element(candidate_xdrs, sentence_span)
        headelt.append(boxer)

        self.xdrs_index += 1
        return headelt

    def construct_boxer_element_simple(self, sentence_org):
        # Creating Sentence Element
        headelt = ET.Element(self.datatype)
        sentence = ET.SubElement(headelt, 's')
        sentence.text = sentence_org
        return headelt

### Extra Functions

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem)
    reparsed = minidom.parseString(rough_string)
    prettyxml = reparsed.documentElement.toprettyxml(indent=" ")
    return prettyxml.encode("utf-8")

###################

if __name__ == "__main__":
    datadir = os.path.dirname(ZHUDATA_FILE_ORG)

    # Start parsing Zhu Data File
    print "Start preparing Zhu Data file - Original ..."
    print "Start parsing "+ZHUDATA_FILE_ORG+" ..."
    fdata = open(ZHUDATA_FILE_ORG, "r")
    data_all = fdata.read().strip().split("\n\n")
    fdata.close()
    
    main_wiki_cnt = 0
    simple_wiki_cnt = 0
    simple_wiki_index = []
    index = 0
    for data in data_all:
        if len(data.strip()) != 0:
            lines = data.strip().split("\n")
            main_wiki_cnt += 1
            simple_sents_index = []
            for sent in lines[1:]:
                simple_wiki_cnt +=1 
                simple_sents_index.append(index)
                index += 1
            simple_wiki_index.append(simple_sents_index)
    print "Total number of sentences from main wikipedia: " + str(main_wiki_cnt)
    print "Total number of sentences from simple wikipedia: " + str(simple_wiki_cnt)

    # Start parsing Zhu Data file - Tokenized ..."
    print "\nStart preparing Zhu Data file - Tokenized ..."
    print "Start parsing "+ZHUDATA_FILE_MAIN+" ..."
    main_wiki = []
    fdata = open(ZHUDATA_FILE_MAIN, "r")
    main_wiki = fdata.read().strip().split("\n")
    fdata.close()
    print "Total number of sentences from main wikipedia (tokenized): " + str(len(main_wiki))

    print "Start parsing "+ZHUDATA_FILE_SIMPLE+" ..."
    simple_wiki = []
    fdata = open(ZHUDATA_FILE_SIMPLE, "r")
    simple_wiki = fdata.read().strip().split("\n")
    fdata.close()
    print "Total number of sentences from simple wikipedia (tokenized): " + str(len(simple_wiki))

    # print "\nStatistics of the training data ..."
    # maxlen_sent_complex = 0
    # avglen_sent_complex = 0
    # avglen_token_complex = 0
    # total_token_complex = 0
    # sentlen_complex_dict = {}

    # maxlen_sent_simple = 0
    # avglen_sent_simple = 0
    # avglen_token_simple = 0  
    # total_token_simple = 0
    # sentlen_simple_dict = {}

    # max_split = 0
    # avg_split = 0
    # split_count_dict = {}

    # for main_index in range(len(simple_wiki_index)):
    #     main_tokenized = main_wiki[main_index] 
    #     main_tokenized_list = main_tokenized.split()

    #     num_tokens = len(main_tokenized_list)
    #     if num_tokens > maxlen_sent_complex:
    #         maxlen_sent_complex = num_tokens
    #     avglen_sent_complex += num_tokens
    #     total_token_complex += num_tokens
    #     for token in main_tokenized_list:
    #         avglen_token_complex += len(token)
    #     if num_tokens not in sentlen_complex_dict:
    #         sentlen_complex_dict[num_tokens] = 1
    #     else:
    #         sentlen_complex_dict[num_tokens] += 1

    #     num_split = len(simple_wiki_index[main_index])
    #     if num_split > max_split:
    #         max_split = num_split
    #     avg_split += num_split
    #     if num_split not in split_count_dict:
    #         split_count_dict[num_split] = 1
    #     else:
    #         split_count_dict[num_split] += 1
    
    #     for simple_index in simple_wiki_index[main_index]:
    #         simple_tokenized = simple_wiki[simple_index]
    #         simple_tokenized_list = simple_tokenized.split()

    #         num_tokens = len(simple_tokenized_list)
    #         if num_tokens > maxlen_sent_simple:
    #             maxlen_sent_simple = num_tokens
    #         avglen_sent_simple += num_tokens
    #         total_token_simple += num_tokens
    #         for token in simple_tokenized_list:
    #             avglen_token_simple += len(token)
    #         if num_tokens not in sentlen_simple_dict:
    #             sentlen_simple_dict[num_tokens] = 1
    #         else:
    #             sentlen_simple_dict[num_tokens] += 1

    # print "Complex sentences: "
    # print "Max Length of a sentence : "+str(maxlen_sent_complex)
    # print "Avg Length of a sentence : "+str(float(avglen_sent_complex)/len(main_wiki))
    # print "Total number of tokens: "+str(total_token_complex)
    # print "Avg Length of tokens: "+str(float(avglen_token_complex)/total_token_complex)

    # print "\nSimple sentences: "
    # print "Max Length of a sentence : "+str(maxlen_sent_simple)
    # print "Avg Length of a sentence : "+str(float(avglen_sent_simple)/len(simple_wiki))
    # print "Total number of tokens: "+str(total_token_simple)
    # print "Avg Length of tokens: "+str(float(avglen_token_simple)/total_token_simple)    
    
    # print 
    # print "Max Number of split: "+str(max_split)
    # print "Avg Number of split: "+str(float(avg_split)/len(main_wiki))

    # print "\nPlots distribution of Complex Sentences ..."
    # keys = sentlen_complex_dict.keys()
    # keys.sort()
    # values = [sentlen_complex_dict[key] for key in keys]
    # plt.plot(keys, values, 'ro', keys, values, 'g-')
    # plt.xlabel('Sentence Length')
    # plt.ylabel('Frequency')
    # plt.title('Complex Sentence Length Distribution')
    # plt.axis([0, 650, -100, 5000])
    # plt.grid(True)
    # plt.show()
    # for key in keys:
    #     print str(key)+"\t"+str(sentlen_complex_dict[key])

    # print "\nPlots distribution of Simple Sentences ..."
    # keys = sentlen_simple_dict.keys()
    # keys.sort()
    # values = [sentlen_simple_dict[key] for key in keys]
    # plt.plot(keys, values, 'ro', keys, values, 'g-')
    # plt.xlabel('Sentence Length')
    # plt.ylabel('Frequency')
    # plt.title('Simple Sentence Length Distribution')
    # plt.axis([0, 550, -100, 8500])
    # plt.grid(True)
    # plt.show()
    # for key in keys:
    #     print str(key)+"\t"+str(sentlen_simple_dict[key])
        

    # print "\nSplit distribution ..."
    # keys = split_count_dict.keys()
    # keys.sort()
    # values = [split_count_dict[key] for key in keys]
    # plt.plot(keys, values, 'ro', keys, values, 'g-')
    # plt.xlabel('Number of Splits')
    # plt.ylabel('Training Pairs')
    # plt.title('Split Distribution')
    # plt.axis([0, 12, -1000, 110000])
    # plt.grid(True)
    # plt.show()
    # for key in keys:
    #     print str(key)+"\t"+str(split_count_dict[key])   
    

    # Start boxer data trackers
    print "\nStart boxer data trackers ..."
    
    main_failed = open("Main-Failed-Sentence","w")
    simple_failed = open("Simple-Failed-Sentence","w")

    main_data_trackers = Boxer_Data_Tracker("main", main_failed )
    simple_data_trackers = Boxer_Data_Tracker("simple", simple_failed)
    
    # Start attaching boxer data with main-simple wiki sentences
    print "\nStart attaching boxer data with main-simple wiki sentences and writing to XML files ..."
    boxer_missed = 0

    print "Generating XML file : "+ZHUDATA_FILE_ORG+".tokenized-boxer.xml ..."
    foutput = open(ZHUDATA_FILE_ORG+".tokenized-boxer.xml", "w")
    foutput.write("<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n")
    foutput.write("<Simplification-Data>\n")

    for main_index in range(len(simple_wiki_index)):
        
        print main_index+1

        # Start creating sentence subelement
        sentence = ET.Element('sentence')
        sentence.attrib={"id":str(main_index+1)}
        flag = True

        #print "main"

        # Process main sentence
        main_tokenized = main_wiki[main_index].decode('utf-8')
        lower_index = (main_index/CHUNK_SIZE)*CHUNK_SIZE
        
        ################

        # Zhu Case
        # boxer_main_filename = "main-boxer-"+str(lower_index)+"-"+str(lower_index+CHUNK_SIZE)+".tokenized.xml"
        
        # Newsella case
        boxer_main_filename = "V0V4_V1V4_V2V4_V3V4_V0V3_V0V2_V1V3.aner.ori.train.src."+str(lower_index+1)+"-"+str(lower_index+CHUNK_SIZE)
        
        ################

        main_boxer_element = main_data_trackers.construct_boxer_element(boxer_main_filename, main_tokenized)

        # Process Simple Sentences
        simple_set = ET.Element('simple-set')
        for simple_index in simple_wiki_index[main_index]:

            #print "simple"
            
            # # Process Simple Sentence [process boxer file]
            # simple_tokenized = simple_wiki[simple_index].decode('utf-8')
            # lower_index = (simple_index/CHUNK_SIZE)*CHUNK_SIZE
            # boxer_simple_filename = "simple-boxer-"+str(lower_index)+"-"+str(lower_index+CHUNK_SIZE)+".tokenized.xml"
            # simple_boxer_element = simple_data_trackers.construct_boxer_element(boxer_simple_filename, simple_tokenized)
            # simple_set.append(simple_boxer_element)

            # Process Simple sentence
            simple_tokenized = simple_wiki[simple_index].decode('utf-8')
            simple_boxer_element = simple_data_trackers.construct_boxer_element_simple(simple_tokenized)
            simple_set.append(simple_boxer_element)

        sentence.append(main_boxer_element)
        sentence.append(simple_set)
        foutput.write(prettify(sentence))

        # Print trace
        if main_index%1000==0:
            print str(main_index)+" sentences processed ..."
            # if main_index > 10000:
            #     exit(0)
            
    foutput.write("</Simplification-Data>\n")
    foutput.close()

    main_failed.close()
    simple_failed.close()

    print "Total number of boxer-missed sentences: "+str(boxer_missed)

