#!/usr/bin/env python
#===================================================================================
#title           : functions_prepare_elementtree_dot.py                            =
#description     : Prepare dot file                                                =
#author          : Shashi Narayan, shashi.narayan(at){ed.ac.uk,loria.fr,gmail.com})=                                    
#date            : Created in 2014, Later revised in April 2016.                   =
#version         : 0.1                                                             =
#===================================================================================


import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

def prettify_xml_element(element):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(element)
    reparsed = minidom.parseString(rough_string)
    prettyxml = reparsed.documentElement.toprettyxml(indent=" ")
    return prettyxml.encode("utf-8")

############################### Elementary Tree ##########################################

def prepare_write_sentence_element(output_stream, sentid, main_sentence, main_sent_dict, simple_sentences, boxer_graph, training_graph):
    # Creating Sentence element
    sentence = ET.Element('sentence')
    sentence.attrib={"id":str(sentid)}
        
    # Writing main sentence
    main = ET.SubElement(sentence, "main")
    mainsent = ET.SubElement(main, "s")
    mainsent.text = main_sentence
    wordinfo = ET.SubElement(main, "winfo")
    mainpositions  = main_sent_dict.keys()
    mainpositions.sort()
    for position in mainpositions:
        word = ET.SubElement(wordinfo, "w")
        word.text = main_sent_dict[position][0]
        word.attrib = {"id":str(position), "pos":main_sent_dict[position][1]}
        
    # Writing simple sentence
    simpleset = ET.SubElement(sentence, "simple-set")
    for simple_sentence in simple_sentences:
        simple = ET.SubElement(simpleset, "simple")
        simplesent = ET.SubElement(simple, "s")
        simplesent.text = simple_sentence

    # Writing boxer Data : boxer_graph
    boxer = boxer_graph.convert_to_elementarytree()
    sentence.append(boxer)

    # Writing Training Graph : training_graph
    traininggraph = training_graph.convert_to_elementarytree()
    sentence.append(traininggraph)

    output_stream.write(prettify_xml_element(sentence))
        
############################ Dot - PNG File ###################################################

def run_visual_graph_creator(sentid, main_sentence, main_sent_dict, simple_sentences, boxer_graph, training_graph):
    print "Creating boxer and training graphs for sentence id : "+sentid+" ..."
    
    # Start creating boxer graph
    foutput = open("/tmp/boxer-graph-"+sentid+".dot", "w")
    boxer_dotstring = boxer_graph.convert_to_dotstring(sentid, main_sentence, main_sent_dict, simple_sentences)
    foutput.write(boxer_dotstring)
    foutput.close()
    os.system("dot -Tpng /tmp/boxer-graph-"+sentid+".dot -o /tmp/boxer-graph-"+sentid+".png")
    

    # Start creating training graph
    foutput = open("/tmp/training-graph-"+sentid+".dot", "w")
    train_dotstring = training_graph.convert_to_dotstring(main_sent_dict, boxer_graph)
    foutput.write(train_dotstring)
    foutput.close()
    os.system("dot -Tpng /tmp/training-graph-"+sentid+".dot -o /tmp/training-graph-"+sentid+".png")
