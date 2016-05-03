#!/usr/bin/env python
#===================================================================================
#title           : saxparser_xml_stanfordtokenized_boxergraph.py                   =
#description     : Boxer-Graph-XML-Handler                                         =
#author          : Shashi Narayan, shashi.narayan(at){ed.ac.uk,loria.fr,gmail.com})=                                    
#date            : Created in 2014, Later revised in April 2016.                   =
#version         : 0.1                                                             =
#===================================================================================

from xml.sax import handler, make_parser

from boxer_graph_module import Boxer_Graph
from explore_training_graph import Explore_Training_Graph

class SAXPARSER_XML_StanfordTokenized_BoxerGraph:
    def __init__(self, process, xmlfile, output_stream, DISCOURSE_SENTENCE_MODEL, MAX_SPLIT_PAIR_SIZE, RESTRICTED_DROP_REL, ALLOWED_DROP_MOD, METHOD_TRAINING_GRAPH):
        # process: "training" or "testing" 
        self.process = process

        self.xmlfile = xmlfile

        # output_stream: file stream for training and dictionary for testing 
        self.output_stream = output_stream

        self.DISCOURSE_SENTENCE_MODEL = DISCOURSE_SENTENCE_MODEL
        self.MAX_SPLIT_PAIR_SIZE = MAX_SPLIT_PAIR_SIZE
        self.RESTRICTED_DROP_REL = RESTRICTED_DROP_REL
        self.ALLOWED_DROP_MOD = ALLOWED_DROP_MOD
        self.METHOD_TRAINING_GRAPH = METHOD_TRAINING_GRAPH
    
    def parse_xmlfile_generating_training_graph(self):
        handler = SAX_Handler(self.process, self.output_stream, self.DISCOURSE_SENTENCE_MODEL, self.MAX_SPLIT_PAIR_SIZE, 
                              self.RESTRICTED_DROP_REL, self.ALLOWED_DROP_MOD, self.METHOD_TRAINING_GRAPH)

        parser = make_parser()
        parser.setContentHandler(handler)
        parser.parse(self.xmlfile)

class SAX_Handler(handler.ContentHandler):
    def __init__(self, process, output_stream, DISCOURSE_SENTENCE_MODEL, MAX_SPLIT_PAIR_SIZE, 
                 RESTRICTED_DROP_REL, ALLOWED_DROP_MOD, METHOD_TRAINING_GRAPH):
        self.process = process
        self.output_stream = output_stream

        self.DISCOURSE_SENTENCE_MODEL = DISCOURSE_SENTENCE_MODEL
        self.MAX_SPLIT_PAIR_SIZE = MAX_SPLIT_PAIR_SIZE
        self.RESTRICTED_DROP_REL = RESTRICTED_DROP_REL
        self.ALLOWED_DROP_MOD = ALLOWED_DROP_MOD
        self.METHOD_TRAINING_GRAPH = METHOD_TRAINING_GRAPH

        # Training Graph Creator
        self.training_graph_handler = Explore_Training_Graph(self.output_stream, self.DISCOURSE_SENTENCE_MODEL, self.MAX_SPLIT_PAIR_SIZE, 
                                                             self.RESTRICTED_DROP_REL, self.ALLOWED_DROP_MOD, self.METHOD_TRAINING_GRAPH)

        # Sentence Data
        self.sentid = ""
        self.main_sentence = ""
        self.main_sent_dict = {}
        self.boxer_graph = Boxer_Graph()
        self.simple_sentencs = []

        # Sentence Flags, temporary variables
        self.isMain = False

        self.isS = False
        self.sentence = ""
        self.wordlist = []

        self.isW = False
        self.word = ""
        self.wid = ""
        self.wpos = ""
        
        self.isSimple = False
        
        # Boxer flags, temporary variables
        self.isNode = False
        self.isRel = False
        self.symbol = ""
        self.predsymbol = ""
        self.locationlist = []
        
    def startDocument(self):     
        print "Start parsing the document ..."
       
    def endDocument(self):
        print "End parsing the document ..."

    def startElement(self, nameElt, attrOfElt):
        if nameElt == "sentence":
            self.sentid = attrOfElt["id"]

            # Refreshing Sentence Data
            self.main_sentence = ""
            self.main_sent_dict = {}
            self.boxer_graph = Boxer_Graph()
            self.simple_sentences = []

        if nameElt == "main":
            self.isMain = True

        if nameElt == "simple":
            self.isSimple = True
                
        if nameElt == "s":
            self.isS = True
            self.sentence = ""
            self.wordlist = []

        if nameElt == "w":
            self.isW = True
            self.wid = int(attrOfElt["id"][1:])
            self.wpos = attrOfElt["pos"]
            self.word = ""
            
        if nameElt == "node":
            self.isNode = True
            self.symbol = attrOfElt["sym"]
            self.boxer_graph.nodes[self.symbol] = {"positions":[], "predicates":[]}

        if nameElt == "rel":
            self.isRel = True
            self.symbol = attrOfElt["sym"]
            self.boxer_graph.relations[self.symbol] = {"positions":[], "predicates":""} 

        if nameElt == "span":
            self.locationlist = []

        if nameElt == "pred":
            self.locationlist = []
            self.predsymbol = attrOfElt["sym"]
            
        if nameElt == "loc":
            if int(attrOfElt["id"][1:]) in self.main_sent_dict:
                self.locationlist.append(int(attrOfElt["id"][1:]))
            
        if nameElt == "edge":
            self.boxer_graph.edges.append((attrOfElt["par"], attrOfElt["dep"], attrOfElt["lab"]))
            
    def endElement(self, nameElt):
        if nameElt == "sentence":
            #print self.sentid
            # print self.main_sentence
            # print self.main_sent_dict
            # print self.simple_sentences
            # print self.boxer_graph

            if self.process == "training":
                self.training_graph_handler.explore_training_graph(self.sentid, self.main_sentence, self.main_sent_dict, self.simple_sentences, self.boxer_graph)
                
            if self.process == "testing":
                self.output_stream[self.sentid] = [self.main_sentence, self.main_sent_dict, self.boxer_graph]

            # if len(self.main_sentence) > 600:
            #     print self.sentid
            # if len(self.simple_sentences) == 6:
            #     print self.sentid

            if int(self.sentid)%10000 == 0:
                print self.sentid + " training data processed ..."            
            
        if nameElt == "main":
            self.isMain = False
            if len(self.wordlist) == 0:
                self.main_sentence = self.sentence.lower()
            else:
                self.main_sentence = (" ".join(self.wordlist)).lower()

        if nameElt == "simple":
            self.isSimple = False
            self.simple_sentences.append(self.sentence.lower())

        if nameElt == "s":
            self.isS = False
            
        if nameElt == "w":
            self.isW = False
            self.main_sent_dict[self.wid] = (self.word.lower(), self.wpos.lower())
            self.wordlist.append(self.word.lower())
        
        if nameElt == "node":
            self.isNode = False
            self.boxer_graph.nodes[self.symbol]["predicates"].sort()
            
        if nameElt == "rel":
            self.isRel = False

        if nameElt == "span":
            self.locationlist.sort()
            if self.isNode:
                self.boxer_graph.nodes[self.symbol]["positions"] = self.locationlist[:]
            if self.isRel:
                self.boxer_graph.relations[self.symbol]["positions"] = self.locationlist[:]
            
        if nameElt == "pred":
            self.locationlist.sort()
            if self.isNode:
                self.boxer_graph.nodes[self.symbol]["predicates"].append((self.predsymbol, self.locationlist[:]))
            if self.isRel:
                self.boxer_graph.relations[self.symbol]["predicates"] = self.predsymbol
            
    def characters(self, chrs):
        if self.isS:
            self.sentence += chrs

        if self.isW:
            self.word += chrs
            
