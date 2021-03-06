#!/usr/bin/env python
#===================================================================================
#title           : training_graph_module.py                                        =
#description     : Define Training Graph                                           =
#author          : Shashi Narayan, shashi.narayan(at){ed.ac.uk,loria.fr,gmail.com})=                                    
#date            : Created in 2014, Later revised in April 2016.                   =
#version         : 0.1                                                             =
#===================================================================================


import xml.etree.ElementTree as ET
import copy

class Training_Graph:
    def __init__(self):
        '''
        self.major_nodes["MN-*"]
        ("split", nodeset, simple_sentences, split_candidate_tuples)
        ("drop-rel", nodeset, simple_sentences, relnode_set, processed_relnode, filtered_mod_pos)
        ("drop-mod", nodeset, simple_sentences, modcand_set, processed_mod_pos, filtered_mod_pos)
        ("drop-ood", nodeset, simple_sentence, oodnode_set, processed_oodnode, filtered_mod_pos)
        ("fin", nodeset, simple_sentences, filtered_mod_pos)

        self.oper_nodes["ON-*"]
        ("split", split_candidate, not_applied_cands)
        ("split", None, not_applied_cands)
        ("drop-rel", relnode_to_process, "True")
        ("drop-rel", relnode_to_process, "False")
        ("drop-mod", modcand_to_process, "True")
        ("drop-mod", modcand_to_process, "False")
        ("drop-ood", oodnode_to_process, "True")
        ("drop-ood", oodnode_to_process, "False")

        self.edges = [(par, dep, lab)]

        '''
        self.major_nodes = {}
        self.oper_nodes = {}
        self.edges = []

    def get_majornode_type(self, majornode_name):
        majornode_tuple = self.major_nodes[majornode_name]
        return majornode_tuple[0]

    def get_majornode_nodeset(self, majornode_name):
        majornode_tuple = self.major_nodes[majornode_name]
        return majornode_tuple[1]

    def get_majornode_simple_sentences(self, majornode_name):
        majornode_tuple = self.major_nodes[majornode_name]
        return majornode_tuple[2]

    def get_majornode_oper_candidates(self, majornode_name):
        majornode_tuple = self.major_nodes[majornode_name]
        if majornode_tuple[0] != "fin":
            return majornode_tuple[3]
        else:
            return []
    
    def get_majornode_processed_oper_candidates(self, majornode_name):
        majornode_tuple = self.major_nodes[majornode_name]
        if majornode_tuple[0] != "fin" and majornode_tuple[0] != "split":
            return majornode_tuple[4]
        else:
            return []
    
    def get_majornode_filtered_postions(self, majornode_name):
        majornode_tuple = self.major_nodes[majornode_name]
        if majornode_tuple[0] == "fin":
            return majornode_tuple[3]
        elif majornode_tuple[0] == "drop-rel" or majornode_tuple[0] == "drop-mod" or majornode_tuple[0] == "drop-ood":
            return majornode_tuple[5]
        else:
            return []

    def get_opernode_type(self, opernode_name):
        opernode_tuple = self.oper_nodes[opernode_name]
        return opernode_tuple[0]

    def get_opernode_oper_candidate(self, opernode_name):
        opernode_tuple = self.oper_nodes[opernode_name]
        return opernode_tuple[1]

    def get_opernode_failed_oper_candidates(self, opernode_name):
        opernode_tuple = self.oper_nodes[opernode_name]
        if opernode_tuple[0] == "split":
            return opernode_tuple[2]
        else:
            return []
    
    def get_opernode_drop_result(self, opernode_name):
        opernode_tuple = self.oper_nodes[opernode_name]
        if opernode_tuple[0] != "split":
            return opernode_tuple[2]
        else:
            return None

    # @@@@@@@@@@@@@@@@@@@@@ Create nodes @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    def create_majornode(self, majornode_data):
        copy_data = copy.copy(majornode_data)

        # Check if node exists
        for node_name in self.major_nodes:
            node_data = self.major_nodes[node_name]
            if node_data == copy_data:
                return node_name, False

        # Otherwise create new node
        majornode_name = "MN-"+str(len(self.major_nodes)+1)
        self.major_nodes[majornode_name] = copy_data 
        return majornode_name, True

    def create_opernode(self, opernode_data):
        copy_data = copy.copy(opernode_data)
        opernode_name = "ON-"+str(len(self.oper_nodes)+1)
        self.oper_nodes[opernode_name] = copy_data
        return opernode_name

    def create_edge(self, edge_data):
        self.edges.append(copy.copy(edge_data))

    # @@@@@@@@@@@@@@@@@@@@@@@@ Final sentences @@@@@@@@@@@@@@@@@@@@@@@@@@
    
    def get_final_sentences(self, main_sentence, main_sent_dict, boxer_graph):
        fin_nodes = self.find_all_fin_majornode()
        print 
        node_sent = []
        for node in fin_nodes:
            # intpart = int(node[3:]) # removing "MN-", lower int part sentence comes before
            if boxer_graph.isEmpty():
                #main_sentence = main_sentence.encode('utf-8')
                simple_sentences = self.get_majornode_simple_sentences(node)
                simple_sentence = " ".join(simple_sentences)
                #node_sent.append((intpart, main_sentence, simple_sentence))

                node_span = (0, len(main_sentence.split()))
                node_sent.append((node_span, main_sentence, simple_sentence))

            else:
                nodeset = self.get_majornode_nodeset(node)
                node_span = boxer_graph.extract_span_min_max(nodeset)
                filtered_pos = self.get_majornode_filtered_postions(node)
                main_sentence = boxer_graph.extract_main_sentence(nodeset, main_sent_dict, filtered_pos)
                simple_sentences = self.get_majornode_simple_sentences(node)
                simple_sentence = " ".join(simple_sentences)
                #node_sent.append((intpart, main_sentence, simple_sentence))
                node_sent.append((node_span, main_sentence, simple_sentence))
        node_sent.sort()
        sentence_pairs = [(item[1], item[2]) for item in node_sent]
        #sentence_pairs = [(item[1].encode('utf-8'), item[2].encode('utf-8')) for item in node_sent]
        #print sentence_pairs
        return sentence_pairs


    # @@@@@@@@@@@@@@@@@@@@@ Find nodes in Training Graph @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        
    def find_all_fin_majornode(self):
        fin_nodes = []
        for major_node in self.major_nodes:
            if self.major_nodes[major_node][0] == "fin":
                fin_nodes.append(major_node)
        return fin_nodes 

    def find_children_of_majornode(self, major_node):
        children_oper_nodes = []
        for edge in self.edges:
            if edge[0] == major_node:
                children_oper_nodes.append(edge[1])
        return children_oper_nodes
        
    def find_children_of_opernode(self, oper_node):
        children_major_nodes = []
        for edge in self.edges:
            if edge[0] == oper_node:
                children_major_nodes.append(edge[1])
        return children_major_nodes        

    def find_parents_of_majornode(self, major_node):
        parents_oper_nodes = []
        for edge in self.edges:
            if edge[1] == major_node:
                parent_oper_node = edge[0]
                parents_oper_nodes.append(parent_oper_node)
        return parents_oper_nodes

    def find_parent_of_opernode(self, oper_node):
        parent_major_node = ""
        for edge in self.edges:
            if edge[1] == oper_node:
                parent_major_node = edge[0]
                break
        return parent_major_node

    # @@@@@@@@@@@@ Training Graph -> Elementary Tree @@@@@@@@@@@@@@@@@@@@
        
    def convert_to_elementarytree(self):
        traininggraph = ET.Element("train-graph") 

        # Major nodes
        major_nodes_elt = ET.SubElement(traininggraph, "major-nodes")
        for major_nodename in self.major_nodes:
            major_nodetype = self.get_majornode_type(major_nodename)
            major_nodeset = self.get_majornode_nodeset(major_nodename)
            major_simple_sentences = self.get_majornode_simple_sentences(major_nodename)
            oper_candidates = self.get_majornode_oper_candidates(major_nodename)
            processed_oper_candidates = self.get_majornode_processed_oper_candidates(major_nodename)
            filtered_postions = self.get_majornode_filtered_postions(major_nodename)
            
            major_node_elt = ET.SubElement(major_nodes_elt, "node")
            major_node_elt.attrib = {"sym":major_nodename}

            # Opertype
            major_nodetype_elt = ET.SubElement(major_node_elt, "type")
            major_nodetype_elt.text = major_nodetype

            # Nodeset
            major_nodeset_elt = ET.SubElement(major_node_elt, "nodeset")
            for node in major_nodeset:
                node_elt = ET.SubElement(major_nodeset_elt, "n")
                node_elt.attrib = {"sym":node}
                
            # Simple sentences
            major_simple_sentences_elt = ET.SubElement(major_node_elt, "simple-set")
            for simple_sentence in major_simple_sentences:
                major_simple_sentence_elt = ET.SubElement(major_simple_sentences_elt, "simple")
                sent_data_elt = ET.SubElement(major_simple_sentence_elt, "s")
                sent_data_elt.text = simple_sentence
            
            # Oper Candidates
            if major_nodetype == "split":
                split_candidate_tuples = oper_candidates
                major_split_candidates_elt = ET.SubElement(major_node_elt, "split-candidates")
                for split_candidate in split_candidate_tuples:
                    major_split_candidate_elt = ET.SubElement(major_split_candidates_elt, "sc")
                    for node in split_candidate:
                        node_elt = ET.SubElement(major_split_candidate_elt, "n")
                        node_elt.attrib = {"sym":str(node)}
                
            if major_nodetype == "drop-rel":
                relnode_set = oper_candidates
                major_relnode_set_elt = ET.SubElement(major_node_elt, "rel-candidates")
                for node in relnode_set:
                    node_elt = ET.SubElement(major_relnode_set_elt, "n")
                    node_elt.attrib = {"sym":str(node)}

                processed_relnodes = processed_oper_candidates
                major_processed_relnodes_elt = ET.SubElement(major_node_elt, "rel-processed")
                for node in processed_relnodes:
                    node_elt = ET.SubElement(major_processed_relnodes_elt, "n")
                    node_elt.attrib = {"sym":str(node)} 

                filtered_mod_pos = filtered_postions
                major_filtered_mod_pos_elt = ET.SubElement(major_node_elt, "mod-loc-filtered")
                for node in filtered_mod_pos:
                    node_elt = ET.SubElement(major_filtered_mod_pos_elt, "loc")
                    node_elt.attrib = {"id":str(node)}  
                    
            if major_nodetype == "drop-mod":
                modcand_set = oper_candidates
                major_modcand_set_elt = ET.SubElement(major_node_elt, "mod-candidates")
                for node in modcand_set:
                    node_elt = ET.SubElement(major_modcand_set_elt, "n")
                    node_elt.attrib = {"sym":node[1],"loc":str(node[0])}

                processed_mod_pos = processed_oper_candidates
                major_processed_mod_pos_elt = ET.SubElement(major_node_elt, "mod-loc-processed")
                for node in processed_mod_pos:
                    node_elt = ET.SubElement(major_processed_mod_pos_elt, "loc")
                    node_elt.attrib = {"id":str(node)}   

                filtered_mod_pos = filtered_postions
                major_filtered_mod_pos_elt = ET.SubElement(major_node_elt, "mod-loc-filtered")
                for node in filtered_mod_pos:
                    node_elt = ET.SubElement(major_filtered_mod_pos_elt, "loc")
                    node_elt.attrib = {"id":str(node)}       

            if major_nodetype == "drop-ood":
                oodnode_set = oper_candidates
                major_oodnode_set_elt = ET.SubElement(major_node_elt, "ood-candidates")
                for node in oodnode_set:
                    node_elt = ET.SubElement(major_oodnode_set_elt, "n")
                    node_elt.attrib = {"sym":str(node)}

                processed_oodnodes = processed_oper_candidates
                major_processed_oodnodes_elt = ET.SubElement(major_node_elt, "ood-processed")
                for node in processed_oodnodes:
                    node_elt = ET.SubElement(major_processed_oodnodes_elt, "n")
                    node_elt.attrib = {"sym":str(node)}

                filtered_mod_pos = filtered_postions
                major_filtered_mod_pos_elt = ET.SubElement(major_node_elt, "mod-loc-filtered")
                for node in filtered_mod_pos:
                    node_elt = ET.SubElement(major_filtered_mod_pos_elt, "loc")
                    node_elt.attrib = {"id":str(node)}  

            if major_nodetype == "fin":
                filtered_mod_pos = filtered_postions
                major_filtered_mod_pos_elt = ET.SubElement(major_node_elt, "mod-loc-filtered")
                for node in filtered_mod_pos:
                    node_elt = ET.SubElement(major_filtered_mod_pos_elt, "loc")
                    node_elt.attrib = {"id":str(node)}   

        # Oper nodes
        oper_nodes_elt = ET.SubElement(traininggraph, "oper-nodes")
        for oper_nodename in self.oper_nodes:
            oper_node_elt = ET.SubElement(oper_nodes_elt, "node")
            oper_node_elt.attrib = {"sym":oper_nodename}
            
            oper_nodedata = self.oper_nodes[oper_nodename]

            # Nodetype
            oper_nodetype = oper_nodedata[0]
            oper_nodetype_elt = ET.SubElement(oper_node_elt, "type")
            oper_nodetype_elt.text = oper_nodetype

            if oper_nodetype == "split":
                split_cand_applied = oper_nodedata[1]
                split_cand_applied_elt = ET.SubElement(oper_node_elt, "split-candidate-applied")
                if split_cand_applied != None:
                    split_candidate_elt = ET.SubElement(split_cand_applied_elt, "sc")
                    for node in split_cand_applied:
                        node_elt = ET.SubElement(split_candidate_elt, "n")
                        node_elt.attrib = {"sym":node}
                
                split_cand_left = oper_nodedata[2]
                split_cand_left_elt = ET.SubElement(oper_node_elt, "split-candidate-left")
                for split_candidate in split_cand_left:
                    split_candidate_elt = ET.SubElement(split_cand_left_elt, "sc")
                    for node in split_candidate:
                        node_elt = ET.SubElement(split_candidate_elt, "n")
                        node_elt.attrib = {"sym":node}

            if oper_nodetype == "drop-ood":
                oodnode_to_process = oper_nodedata[1]
                oodnode_to_process_elt = ET.SubElement(oper_node_elt, "ood-candidate")
                node_elt = ET.SubElement(oodnode_to_process_elt, "n")
                node_elt.attrib = {"sym":oodnode_to_process}

                dropped = oper_nodedata[2]
                dropped_elt = ET.SubElement(oper_node_elt, "is-dropped")
                dropped_elt.attrib = {"val":dropped}
                
            if oper_nodetype == "drop-rel":
                relnode_to_process = oper_nodedata[1]
                relnode_to_process_elt = ET.SubElement(oper_node_elt, "rel-candidate")
                node_elt = ET.SubElement(relnode_to_process_elt, "n")
                node_elt.attrib = {"sym":relnode_to_process}

                dropped = oper_nodedata[2]
                dropped_elt = ET.SubElement(oper_node_elt, "is-dropped")
                dropped_elt.attrib = {"val":dropped}
            
            if oper_nodetype == "drop-mod":
                modcand_to_process = oper_nodedata[1]
                modcand_to_process_elt = ET.SubElement(oper_node_elt, "mod-candidate")
                node_elt = ET.SubElement(modcand_to_process_elt, "n")
                node_elt.attrib = {"sym":modcand_to_process[1],"loc":str(modcand_to_process[0])}

                dropped = oper_nodedata[2]
                dropped_elt = ET.SubElement(oper_node_elt, "is-dropped")
                dropped_elt.attrib = {"val":dropped}

        tg_edges_elt = ET.SubElement(traininggraph, "tg-edges")
        for tg_edge in self.edges:
            tg_edge_elt = ET.SubElement(tg_edges_elt, "edge")
            tg_edge_elt.attrib = {"lab":str(tg_edge[2]), "par":tg_edge[0], "dep":tg_edge[1]}
            
        return traininggraph

    # @@@@@@@@@@@@ Training Graph -> Dot Graph @@@@@@@@@@@@@@@@@@@@

    def convert_to_dotstring(self, main_sent_dict, boxer_graph):
        dot_string = "digraph boxer{\n"

        nodename = 0
        node_graph_dict = {}
        # Writing Major nodes
        for major_nodename in self.major_nodes:
            major_nodetype = self.get_majornode_type(major_nodename)
            major_nodeset = self.get_majornode_nodeset(major_nodename)
            major_simple_sentences = self.get_majornode_simple_sentences(major_nodename)
            oper_candidates = self.get_majornode_oper_candidates(major_nodename)
            processed_oper_candidates = self.get_majornode_processed_oper_candidates(major_nodename)
            filtered_postions = self.get_majornode_filtered_postions(major_nodename)

            main_sentence = boxer_graph.extract_main_sentence(major_nodeset, main_sent_dict, filtered_postions)
            simple_sentence_string = " ".join(major_simple_sentences)
            major_node_data = [major_nodetype, major_nodeset[:], main_sentence, simple_sentence_string]
            
            if major_nodetype == "split":
                major_node_data += [oper_candidates[:]]

            if major_nodetype == "drop-rel" or major_nodetype == "drop-mod" or major_nodetype == "drop-ood":
                major_node_data += [oper_candidates[:], processed_oper_candidates[:], filtered_postions[:]]
            
            if major_nodetype == "fin":
                major_node_data += [filtered_postions[:]]
					
            major_node_string, nodename = self.textdot_majornode(nodename, major_nodename, major_node_data[:])
            node_graph_dict[major_nodename] = "struct"+str(nodename)
            dot_string += major_node_string+"\n"

        # Writing operation nodes
        for oper_nodename in self.oper_nodes:
            oper_node_string, nodename = self.textdot_opernode(nodename, oper_nodename, self.oper_nodes[oper_nodename])
            node_graph_dict[oper_nodename] = "struct"+str(nodename)
            dot_string += oper_node_string+"\n"

        # Writing edges
        for edge in self.edges:
            par_graphnode = node_graph_dict[edge[0]]
            dep_graphnode = node_graph_dict[edge[1]]
            dot_string += par_graphnode+" -> "+dep_graphnode+"[label=\""+str(edge[2])+"\"];\n"
        dot_string += "}"
        return dot_string

    def textdot_majornode(self, nodename, node, nodedata):
        textdot_node = "struct"+str(nodename+1)+" [shape=record,label=\"{"
        textdot_node += "major-node: "+node+"|"
        index = 0
        for data in nodedata:
            textdot_node += self.processtext(str(data))
            index += 1
            if index < len(nodedata):
                textdot_node += "|"  
        textdot_node += "}\"];"
        return textdot_node, nodename+1
	
    def textdot_opernode(self, nodename, node, nodedata):
        textdot_node = "struct"+str(nodename+1)+" [shape=record,label=\"{"
        textdot_node += "oper-node: "+node+"|"
        index = 0
        for data in nodedata:
            textdot_node += self.processtext(str(data))
            index += 1
            if index < len(nodedata):
                textdot_node += "|"  
        textdot_node += "}\"];"
        return textdot_node, nodename+1
	
    def processtext(self, inputstring):
        linesize = 100
        outputstring = ""
        index = 0
        substr = inputstring[index*linesize:(index+1)*linesize]
        while (substr!=""):
            outputstring += substr
            index += 1
            substr = inputstring[index*linesize:(index+1)*linesize]
            if substr!="":
                outputstring += "\\n"
        return outputstring

    # @@@@@@@@@@@@@@@@@@@@@@@@@@ DONE @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
