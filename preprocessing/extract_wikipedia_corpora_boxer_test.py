#!/usr/bin/env python
import os
import argparse
import sys
import random 
import base64
import uuid

import xml.etree.ElementTree as ET
from xml.dom import minidom

### Global Variables

# # Zhu
# TEST_FILE_MAIN="/home/ankh/Data/Simplification/Test-Data/complex.tokenized"
# TEST_FILE_BOXER="/home/ankh/Data/Simplification/Test-Data/complex.tokenized.boxer.xml"

# # NewSella
# TEST_FILE_MAIN="/gpfs/scratch/snarayan/Sentence-Simplification/Newsella/V0V4_V1V4_V2V4_V3V4_V0V3_V0V2_V1V3.aner.ori.test.src"
# TEST_FILE_BOXER="/gpfs/scratch/snarayan/Sentence-Simplification/Newsella/boxer/V0V4_V1V4_V2V4_V3V4_V0V3_V0V2_V1V3.aner.ori.test.src"

# Wikilarge
# TEST_FILE_MAIN="/gpfs/scratch/snarayan/Sentence-Simplification/Newsella/V0V4_V1V4_V2V4_V3V4_V0V3_V0V2_V1V3.aner.ori.test.src"
# TEST_FILE_BOXER="/gpfs/scratch/snarayan/Sentence-Simplification/Newsella/boxer/V0V4_V1V4_V2V4_V3V4_V0V3_V0V2_V1V3.aner.ori.test.src"



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

### Extra Functions

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem)
    reparsed = minidom.parseString(rough_string)
    prettyxml = reparsed.documentElement.toprettyxml(indent=" ")
    return prettyxml.encode("utf-8")

###################

class Boxer_Element_Creator:
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

    def construct_boxer_element(self, xdrs_data):
        sentid = int(xdrs_data.get('{http://www.w3.org/XML/1998/namespace}id')[1:])
        
        # Creating Sentence Element
        sentence_xml = ""
        sentence_span = []
        sentence = ET.Element('s')
        words = (xdrs_data.find("words")).findall("word")
        postags = (xdrs_data.find("postags")).findall("postag")
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
          
        # Creating the head element
        headelt = ET.Element("main")
        headelt.append(sentence)

        # Creating boxer element
        boxer = self.graph_boxer_element(xdrs_data, sentence_span)
        headelt.append(boxer)
        return sentid, headelt

    def create_sentence_elt(self, main_sent):
        sentence = ET.Element('s')
        sentence.text = main_sent.decode('utf-8')

        # Creating the head element
        headelt = ET.Element("main")
        headelt.append(sentence)

        # Creating boxer element
        boxer = ET.Element("box")
        headelt.append(boxer)
        return headelt

    def get_sentence_elt(self, boxer_xml_file):
        sentid_sentence_dict = {}
        xdrs_output = ET.parse(boxer_xml_file)
        xdrs_list = xdrs_output.findall('xdrs')
        for xdrs_item in xdrs_list:
            sentid, head_elt = self.construct_boxer_element(xdrs_item)
            sentid_sentence_dict[sentid] = head_elt
        return sentid_sentence_dict

if __name__ == "__main__":
    datadir = os.path.dirname(TEST_FILE_MAIN)

    # Start parsing Zhu Data file - Tokenized ..."
    print "\nStart preparing Test Data file - Tokenized ..."
    print "Start parsing "+TEST_FILE_MAIN+" ..."
    main_wiki = []
    fdata = open(TEST_FILE_MAIN, "r")
    main_wiki = fdata.read().strip().split("\n")
    fdata.close()
    print "Total number of sentences from Test (tokenized): " + str(len(main_wiki))

    # Call boxer element creator
    print "\nStart boxer element creator ..."
    boxer_elt_creator = Boxer_Element_Creator()
    sentid_sentence_dict = boxer_elt_creator.get_sentence_elt(TEST_FILE_BOXER)
    
    # Start Writing final files
    print "Generating XML file : "+TEST_FILE_MAIN+".boxer-graph.xml ..."
    foutput = open(TEST_FILE_MAIN+".boxer-graph.xml", "w")
    foutput.write("<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n")
    foutput.write("<Test-Data>\n")

    main_index = 1
    for main_sent in main_wiki:
        # Start creating sentence subelement
        sentence = ET.Element('sentence')
        sentence.attrib={"id":str(main_index)}
        
        main_elt = ""
        if main_index in sentid_sentence_dict:
            main_elt = sentid_sentence_dict[main_index]
        else:
            main_elt = boxer_elt_creator.create_sentence_elt(main_sent)

        sentence.append(main_elt)
        foutput.write(prettify(sentence))
        main_index += 1

    
    foutput.write("</Test-Data>\n")
    foutput.close()

    print len(sentid_sentence_dict)
    
    print sentid_sentence_dict.keys()
