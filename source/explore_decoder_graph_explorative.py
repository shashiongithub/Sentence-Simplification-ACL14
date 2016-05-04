#!/usr/bin/env python
#===================================================================================
#title           : explore_decoder_graph_explorative.py                            =
#description     : Explorative decoder                                             =
#author          : Shashi Narayan, shashi.narayan(at){ed.ac.uk,loria.fr,gmail.com})=                                    
#date            : Created in 2014, Later revised in April 2016.                   =
#version         : 0.1                                                             =
#===================================================================================

from training_graph_module import Training_Graph
import function_select_methods
import copy

class Explore_Decoder_Graph_Explorative:
    def __init__(self, DISCOURSE_SENTENCE_MODEL, MAX_SPLIT_PAIR_SIZE, RESTRICTED_DROP_REL, ALLOWED_DROP_MOD, probability_tables, METHOD_FEATURE_EXTRACT):
        self.DISCOURSE_SENTENCE_MODEL = DISCOURSE_SENTENCE_MODEL
        self.MAX_SPLIT_PAIR_SIZE = MAX_SPLIT_PAIR_SIZE
        self.RESTRICTED_DROP_REL = RESTRICTED_DROP_REL
        self.ALLOWED_DROP_MOD = ALLOWED_DROP_MOD

        self.probability_tables = probability_tables
        self.METHOD_FEATURE_EXTRACT = METHOD_FEATURE_EXTRACT

        self.method_feature_extract = function_select_methods.select_feature_extract_method(self.METHOD_FEATURE_EXTRACT)        

    # @@@@@@@@@@@@@@@@@@@@@@
    def explore_decoder_graph(self, sentid, main_sentence, main_sent_dict, boxer_graph):
        # Start a decoder graph
        decoder_graph = Training_Graph()
        nodes_2_process = []

        # Check if Discourse information is available
        if boxer_graph.isEmpty():
            # Adding finishing major node
            nodeset = boxer_graph.get_nodeset()
            filtered_mod_pos = []
            simple_sentences = []
            majornode_data = ("fin", nodeset, simple_sentences, filtered_mod_pos)
            
            # Creating major node
            majornode_name, isNew = decoder_graph.create_majornode(majornode_data)
            nodes_2_process.append(majornode_name) # isNew = True
        else:
            # DRS data is available for the complex sentence
            # Check to add the starting node
            nodeset = boxer_graph.get_nodeset()
            majornode_name, isNew = self.addition_major_node(main_sent_dict, boxer_graph, decoder_graph, "split", nodeset, [], [])
            nodes_2_process.append(majornode_name) # isNew = True
            
        # Start expanding the decoder graph, iteratively and not recursively (python has problem with recursive depth)
        while len(nodes_2_process) != 0:
            #print len(nodes_2_process)
            nodes_2_process = self.expand_decoder_graph(nodes_2_process[:], main_sent_dict, boxer_graph,  decoder_graph)
        return decoder_graph

    def expand_decoder_graph(self, nodes_2_process, main_sent_dict, boxer_graph,  decoder_graph):
        node_name = nodes_2_process[0]
        operreq = decoder_graph.get_majornode_type(node_name)
        nodeset = decoder_graph.get_majornode_nodeset(node_name)[:]
        oper_candidates = decoder_graph.get_majornode_oper_candidates(node_name)[:]
        processed_oper_candidates = decoder_graph.get_majornode_processed_oper_candidates(node_name)[:]
        filtered_postions = decoder_graph.get_majornode_filtered_postions(node_name)[:]

        #print node_name, decoder_graph.major_nodes[node_name]
        #print node_name, operreq, nodeset, oper_candidates, processed_oper_candidates, filtered_postions

        if operreq == "split":
            split_candidate_tuples = oper_candidates
            nodes_2_process = self.process_split_node_decoder_graph(node_name, nodeset, split_candidate_tuples, nodes_2_process, 
                                                                    main_sent_dict, boxer_graph, decoder_graph)

        if operreq == "drop-rel":
            relnode_candidates = oper_candidates
            processed_relnode_candidates = processed_oper_candidates 
            filtered_mod_pos = filtered_postions
            nodes_2_process = self.process_droprel_node_decoder_graph(node_name, nodeset, relnode_candidates, processed_relnode_candidates, filtered_mod_pos,
                                                                      nodes_2_process, main_sent_dict, boxer_graph, decoder_graph)
            
        if operreq == "drop-mod":
            mod_candidates = oper_candidates
            processed_mod_pos = processed_oper_candidates 
            filtered_mod_pos = filtered_postions
            nodes_2_process = self.process_dropmod_node_decoder_graph(node_name, nodeset, mod_candidates, processed_mod_pos, filtered_mod_pos,
                                                                      nodes_2_process, main_sent_dict, boxer_graph, decoder_graph)

        if operreq == "drop-ood":
            oodnode_candidates = oper_candidates
            processed_oodnode_candidates = processed_oper_candidates 
            filtered_mod_pos = filtered_postions
            nodes_2_process = self.process_dropood_node_decoder_graph(node_name, nodeset, oodnode_candidates, processed_oodnode_candidates, filtered_mod_pos,
                                                                      nodes_2_process, main_sent_dict, boxer_graph, decoder_graph)
        return nodes_2_process[1:]

    def process_split_node_decoder_graph(self, node_name, nodeset, split_candidate_tuples, nodes_2_process, main_sent_dict, boxer_graph, decoder_graph):
        # Calculate all parent and following subtrees
        parent_subgraph_nodeset_dict = boxer_graph.extract_parent_subgraph_nodeset_dict()
        #print "parent_subgraph_nodeset_dict : "+str(parent_subgraph_nodeset_dict)

        # Explore no-split options
        # Adding the operation node
        not_applied_cands = [item for item in split_candidate_tuples]
        opernode_data = ("split", None, not_applied_cands)
        opernode_name = decoder_graph.create_opernode(opernode_data)
        decoder_graph.create_edge((node_name, opernode_name, None))
        # Check for adding drop-rel or drop-mod or fin nodes
        child_nodeset = nodeset[:]
        child_majornode_name, isNew =  self.addition_major_node(main_sent_dict, boxer_graph, decoder_graph, "drop-rel", child_nodeset, [], [])
        if isNew:
            nodes_2_process.append(child_majornode_name)
        decoder_graph.create_edge((opernode_name, child_majornode_name, None))

        # Explore all split options
        for split_candidate in split_candidate_tuples:
            node_subgraph_nodeset_dict, node_span_dict = boxer_graph.partition_drs_for_successful_candidate(split_candidate, parent_subgraph_nodeset_dict)
            #print node_subgraph_nodeset_dict, node_span_dict
            
            # Sorting them depending on span
            split_results = []
            for tnodename in split_candidate:
                tspan = node_span_dict[tnodename]
                tnodeset = node_subgraph_nodeset_dict[tnodename][:]
                split_results.append((tspan, tnodeset, tnodename))
            split_results.sort()
            
            # Adding the operation node
            not_applied_cands = [item for item in split_candidate_tuples if item is not split_candidate]
            opernode_data = ("split", split_candidate, not_applied_cands)
            opernode_name = decoder_graph.create_opernode(opernode_data)
            decoder_graph.create_edge((node_name, opernode_name, split_candidate))

            # Adding children major nodes
            for item in split_results:
                child_nodeset = item[1][:]
                child_nodeset.sort()
                parent_child_nodeset = item[2]
                
                # Check for adding rel or subsequent nodes
                child_majornode_name, isNew =  self.addition_major_node(main_sent_dict, boxer_graph, decoder_graph, "drop-rel", child_nodeset, [], [])
                if isNew:
                    nodes_2_process.append(child_majornode_name)
                decoder_graph.create_edge((opernode_name, child_majornode_name, parent_child_nodeset))
        return nodes_2_process 

    def process_droprel_node_decoder_graph(self, node_name, nodeset, relnode_candidates, processed_relnode_candidates, filtered_mod_pos,
                                           nodes_2_process, main_sent_dict, boxer_graph, decoder_graph):
        relnode_to_process = relnode_candidates[0]
        processed_relnode_candidates.append(relnode_to_process)

        # Creating opernode for not droping
        opernode_data = ("drop-rel", relnode_to_process, "False")
        opernode_name = decoder_graph.create_opernode(opernode_data)
        decoder_graph.create_edge((node_name, opernode_name, relnode_to_process))
        # Check for adding REL or subsequent nodes, (nodeset is unchanged)
        child_nodeset = nodeset[:]
        child_filtered_mod_pos = filtered_mod_pos[:]
        child_majornode_name, isNew =  self.addition_major_node(main_sent_dict, boxer_graph, decoder_graph, "drop-rel", child_nodeset, processed_relnode_candidates, child_filtered_mod_pos)
        if isNew:
            nodes_2_process.append(child_majornode_name)
        decoder_graph.create_edge((opernode_name, child_majornode_name, "False"))
        
        # Creating opernode for droping 
        opernode_data = ("drop-rel", relnode_to_process, "True")
        opernode_name = decoder_graph.create_opernode(opernode_data)
        decoder_graph.create_edge((node_name, opernode_name, relnode_to_process))
        # Check for adding REL or subsequent nodes, (nodeset is changed)
        child_nodeset, child_filtered_mod_pos = boxer_graph.drop_relation(nodeset, relnode_to_process, filtered_mod_pos)
        child_majornode_name, isNew =  self.addition_major_node(main_sent_dict, boxer_graph, decoder_graph, "drop-rel", child_nodeset, processed_relnode_candidates, child_filtered_mod_pos)
        if isNew:
            nodes_2_process.append(child_majornode_name)
        decoder_graph.create_edge((opernode_name, child_majornode_name, "True"))
        return  nodes_2_process      

    def process_dropmod_node_decoder_graph(self, node_name, nodeset, mod_candidates, processed_mod_pos, filtered_mod_pos,
                                           nodes_2_process, main_sent_dict, boxer_graph, decoder_graph):
        modcand_to_process = mod_candidates[0]
        modcand_position_to_process = modcand_to_process[0]
        modcand_word = main_sent_dict[modcand_position_to_process][0]
        modcand_node = modcand_to_process[1]
        processed_mod_pos.append(modcand_position_to_process)

        # Dont drop this pos, adding the operation node
        opernode_data = ("drop-mod", modcand_to_process, "False")
        opernode_name = decoder_graph.create_opernode(opernode_data)
        decoder_graph.create_edge((node_name, opernode_name, modcand_to_process))
        # Check for adding further drop mods, (nodeset is unchanged)
        child_nodeset = nodeset
        child_majornode_name, isNew =  self.addition_major_node(main_sent_dict, boxer_graph, decoder_graph, "drop-mod", child_nodeset, processed_mod_pos, filtered_mod_pos)
        if isNew:
            nodes_2_process.append(child_majornode_name)
        decoder_graph.create_edge((opernode_name, child_majornode_name, "False"))

        # Drop this mod, adding the operation node
        opernode_data = ("drop-mod", modcand_to_process, "True")
        opernode_name = decoder_graph.create_opernode(opernode_data)
        decoder_graph.create_edge((node_name, opernode_name, modcand_to_process))
        # Check for adding further drop mods, (nodeset is unchanged)
        child_nodeset = nodeset[:]
        tfiltered_mod_pos = filtered_mod_pos[:]
        tfiltered_mod_pos.append(modcand_position_to_process)
        child_majornode_name, isNew =  self.addition_major_node(main_sent_dict, boxer_graph, decoder_graph, "drop-mod", child_nodeset, processed_mod_pos, tfiltered_mod_pos)
        if isNew:
            nodes_2_process.append(child_majornode_name)
        decoder_graph.create_edge((opernode_name, child_majornode_name, "True"))
        return nodes_2_process

    def process_dropood_node_decoder_graph(self, node_name, nodeset, oodnode_candidates, processed_oodnode_candidates, filtered_mod_pos,
                                           nodes_2_process, main_sent_dict, boxer_graph, decoder_graph):
        oodnode_to_process = oodnode_candidates[0]
        processed_oodnode_candidates.append(oodnode_to_process)

        # Creating opernode for not droping
        opernode_data = ("drop-ood", oodnode_to_process, "False")
        opernode_name = decoder_graph.create_opernode(opernode_data)
        decoder_graph.create_edge((node_name, opernode_name, oodnode_to_process))
        # Check for adding OOD or subsequent nodes, (nodeset is unchanged)
        child_nodeset = nodeset[:]
        child_majornode_name, isNew =  self.addition_major_node(main_sent_dict, boxer_graph, decoder_graph, "drop-ood", child_nodeset, processed_oodnode_candidates, filtered_mod_pos)
        if isNew:
            nodes_2_process.append(child_majornode_name)
        decoder_graph.create_edge((opernode_name, child_majornode_name, "False"))
        
        # Creating opernode for droping 
        opernode_data = ("drop-ood", oodnode_to_process, "True")
        opernode_name = decoder_graph.create_opernode(opernode_data)
        decoder_graph.create_edge((node_name, opernode_name, oodnode_to_process))
        # Check for adding OOD or subsequent nodes, (nodeset is changed)
        child_nodeset = nodeset[:]
        child_nodeset.remove(oodnode_to_process)              
        child_majornode_name, isNew =  self.addition_major_node(main_sent_dict, boxer_graph, decoder_graph, "drop-ood", child_nodeset, processed_oodnode_candidates, filtered_mod_pos)
        if isNew:
            nodes_2_process.append(child_majornode_name)
        decoder_graph.create_edge((opernode_name, child_majornode_name, "True"))
        return  nodes_2_process

    def addition_major_node(self, main_sent_dict, boxer_graph, decoder_graph, opertype, nodeset, processed_candidates, extra_data):
        # node type - value
        type_val = {"split":1, "drop-rel":2, "drop-mod":3, "drop-ood":4}
        operval = type_val[opertype]

        # simple sentences not available, used to match data structures
        simple_sentences = []

        # Checking for the addition of "split" major-node
        if operval <= type_val["split"]:
            if opertype in self.DISCOURSE_SENTENCE_MODEL:
                # Calculating Split Candidates - DRS Graph node tuples
                split_candidate_tuples = boxer_graph.extract_split_candidate_tuples(nodeset, self.MAX_SPLIT_PAIR_SIZE)
                # print "split_candidate_tuples : " + str(split_candidate_tuples)

                if len(split_candidate_tuples) != 0:
                    # Adding the major node for split
                    majornode_data = ("split", nodeset[:], simple_sentences, split_candidate_tuples)
                    majornode_name, isNew = decoder_graph.create_majornode(majornode_data)
                    return majornode_name, isNew

        if operval <= type_val["drop-rel"]:
            if opertype in self.DISCOURSE_SENTENCE_MODEL:
                # Calculate drop-rel candidates
                processed_relnode = processed_candidates[:] if opertype == "drop-rel" else []
                filtered_mod_pos = extra_data if opertype == "drop-rel" else []
                relnode_set = boxer_graph.extract_drop_rel_candidates(nodeset, self.RESTRICTED_DROP_REL, processed_relnode)
                if len(relnode_set) != 0:
                    # Adding the major nodes for drop-rel
                    majornode_data = ("drop-rel", nodeset[:], simple_sentences, relnode_set, processed_relnode, filtered_mod_pos)
                    majornode_name, isNew = decoder_graph.create_majornode(majornode_data)
                    return majornode_name, isNew

        if operval <= type_val["drop-mod"]:
            if opertype in self.DISCOURSE_SENTENCE_MODEL:
                # Calculate drop-mod candidates
                processed_mod_pos = processed_candidates[:] if opertype == "drop-mod" else []
                filtered_mod_pos = extra_data
                modcand_set = boxer_graph.extract_drop_mod_candidates(nodeset, main_sent_dict, self.ALLOWED_DROP_MOD, processed_mod_pos)
                if len(modcand_set) != 0:
                    # Adding the major nodes for drop-mod
                    majornode_data = ("drop-mod", nodeset[:], simple_sentences, modcand_set, processed_mod_pos, filtered_mod_pos)
                    majornode_name, isNew = decoder_graph.create_majornode(majornode_data)
                    return majornode_name, isNew

        if operval <= type_val["drop-ood"]:
            if opertype in self.DISCOURSE_SENTENCE_MODEL:
                # Check for drop-OOD node candidates
                processed_oodnodes = processed_candidates if opertype == "drop-ood" else []
                filtered_mod_pos = extra_data
                oodnode_candidates = boxer_graph.extract_ood_candidates(nodeset, processed_oodnodes)
                if len(oodnode_candidates) != 0:
                    # Adding the major node for drop-ood
                    majornode_data = ("drop-ood", nodeset[:], simple_sentences, oodnode_candidates, processed_oodnodes, filtered_mod_pos)
                    majornode_name, isNew = decoder_graph.create_majornode(majornode_data)
                    return majornode_name, isNew

        # None of them matched, create "fin" node
        filtered_mod_pos = extra_data[:]
        majornode_data = ("fin", nodeset[:], simple_sentences, filtered_mod_pos)
        majornode_name, isNew = decoder_graph.create_majornode(majornode_data)
        return majornode_name, isNew 

    # @@@@@@@@@@@@@@@@@@@@@@
    def start_probability_update(self, main_sentence, main_sent_dict, boxer_graph, decoder_graph):
        node_probability_dict = {}
        potential_edges = []
        
        bottom_nodes = decoder_graph.find_all_fin_majornode()
        nodes_to_process = bottom_nodes[:]
        while len(nodes_to_process) != 0:
            nodes_to_process, node_probability_dict, potential_edges = self.bottom_up_probability_update(nodes_to_process, node_probability_dict, potential_edges, 
                                                                                                         main_sentence, main_sent_dict, boxer_graph, decoder_graph)
        return node_probability_dict, potential_edges

    def bottom_up_probability_update(self, nodes_to_process, node_probability_dict, potential_edges, main_sentence, main_sent_dict, boxer_graph, decoder_graph):
        node_to_process = nodes_to_process[0]
        # Calculating probabilities and inserting potential children edges
        if node_to_process.startswith("MN"):
            # Major node
            if decoder_graph.get_majornode_type(node_to_process) == "fin":
                node_probability_dict[node_to_process] = 1
            else:
                children_oper_nodes = decoder_graph.find_children_of_majornode(node_to_process)
                probability_children = [(node_probability_dict[child], child) for child in children_oper_nodes]
                probability_children.sort(reverse=True)
                node_probability_dict[node_to_process] = probability_children[0][0]
                potential_edges.append((node_to_process, probability_children[0][1]))

            # Calculate parents_oper_nodes 
            parents_oper_nodes = decoder_graph.find_parents_of_majornode(node_to_process)
            # Inserting Parents to process if already not insterted and all children are already inserted
            for parent_oper_node in parents_oper_nodes:
                if (parent_oper_node not in nodes_to_process) and (parent_oper_node not in node_probability_dict):
                    children_major_nodes = decoder_graph.find_children_of_opernode(parent_oper_node)
                    flag = True
                    for child_major_node in children_major_nodes:
                        if (child_major_node not in nodes_to_process) and (child_major_node not in node_probability_dict):
                            flag = False
                            break
                    if flag == True:
                        nodes_to_process.append(parent_oper_node)
        else:
            # Oper node
            prob_oper_node = self.fetch_probability(node_to_process, main_sentence, main_sent_dict, boxer_graph, decoder_graph)
            children_major_nodes = decoder_graph.find_children_of_opernode(node_to_process)
            for child in children_major_nodes:
                prob_oper_node = prob_oper_node * node_probability_dict[child]
                potential_edges.append((node_to_process, child))
            node_probability_dict[node_to_process] = prob_oper_node
            
            # Calculate parent_major_node
            parent_major_node = decoder_graph.find_parent_of_opernode(node_to_process)
            # Inserting Parents to process, if already not insterted and all children are already inserted
            if (parent_major_node not in nodes_to_process) and (parent_major_node not in node_probability_dict):
                children_oper_nodes = decoder_graph.find_children_of_majornode(parent_major_node)
                flag = True
                for child_oper_node in children_oper_nodes:
                    if (child_oper_node not in nodes_to_process) and (child_oper_node not in node_probability_dict):
                        flag = False
                        break
                if flag == True:
                    nodes_to_process.append(parent_major_node)
        return nodes_to_process[1:], node_probability_dict, potential_edges

    def fetch_probability(self, oper_node, main_sentence, main_sent_dict, boxer_graph, decoder_graph):
        oper_node_type = decoder_graph.get_opernode_type(oper_node)
        if oper_node_type == "split":
            # Parent main sentence
            parent_major_node = decoder_graph.find_parent_of_opernode(oper_node)
            parent_nodeset = decoder_graph.get_majornode_nodeset(parent_major_node)
            parent_filtered_mod_pos = decoder_graph.get_majornode_filtered_postions(parent_major_node)
            parent_sentence = boxer_graph.extract_main_sentence(parent_nodeset, main_sent_dict, parent_filtered_mod_pos)

            # Children sentences
            children_major_nodes = decoder_graph.find_children_of_opernode(oper_node)
            children_sentences = []
            for child_major_node in children_major_nodes:
                child_nodeset = decoder_graph.get_majornode_nodeset(child_major_node)
                child_filtered_mod_pos = decoder_graph.get_majornode_filtered_postions(child_major_node)
                child_sentence = boxer_graph.extract_main_sentence(child_nodeset, main_sent_dict, child_filtered_mod_pos)
                children_sentences.append(child_sentence)

            total_probability = 1
            split_candidate = decoder_graph.get_opernode_oper_candidate(oper_node)
            if split_candidate != None:
                split_feature = self.method_feature_extract.get_split_feature(split_candidate, parent_sentence, children_sentences, boxer_graph)
                if split_feature in self.probability_tables["split"]:
                    total_probability = self.probability_tables["split"][split_feature]["true"]
                else:
                    total_probability = 0.5
                return total_probability
            else:
                not_applied_cands = decoder_graph.get_opernode_failed_oper_candidates(oper_node)
                for split_candidate_left in not_applied_cands:
                    split_feature_left = self.method_feature_extract.get_split_feature(split_candidate_left, parent_sentence, children_sentences, boxer_graph)
                    if split_feature_left in self.probability_tables["split"]:
                        total_probability = total_probability * self.probability_tables["split"][split_feature_left]["false"]
                    else:
                        total_probability = total_probability * 0.5
                return total_probability
                
        elif oper_node_type == "drop-rel":
            parent_major_node = decoder_graph.find_parent_of_opernode(oper_node)
            parent_nodeset = decoder_graph.get_majornode_nodeset(parent_major_node)
            rel_candidate = decoder_graph.get_opernode_oper_candidate(oper_node)
            drop_rel_feature = self.method_feature_extract.get_drop_rel_feature(rel_candidate, parent_nodeset, main_sent_dict, boxer_graph)
            isDropped = decoder_graph.get_opernode_drop_result(oper_node)
            dropVal = "true" if isDropped == "True" else "false"

            prob_value = 0
            if drop_rel_feature in self.probability_tables["drop-rel"]:
                prob_value = self.probability_tables["drop-rel"][drop_rel_feature][dropVal]
            else:
                prob_value = 0.5
            return prob_value

        elif oper_node_type == "drop-mod":
            mod_candidate = decoder_graph.get_opernode_oper_candidate(oper_node)
            drop_mod_feature = self.method_feature_extract.get_drop_mod_feature(mod_candidate, main_sent_dict, boxer_graph)
            isDropped = decoder_graph.get_opernode_drop_result(oper_node)
            dropVal = "true" if isDropped == "True" else "false"

            prob_value = 0
            if drop_mod_feature in self.probability_tables["drop-mod"]:
                prob_value = self.probability_tables["drop-mod"][drop_mod_feature][dropVal]
            else:
                prob_value = 0.5
            return prob_value

        elif oper_node_type == "drop-ood":
            parent_major_node = decoder_graph.find_parent_of_opernode(oper_node)
            parent_nodeset = decoder_graph.get_majornode_nodeset(parent_major_node)
            ood_candidate = decoder_graph.get_opernode_oper_candidate(oper_node)
            drop_ood_feature = self.method_feature_extract.get_drop_ood_feature(ood_candidate, parent_nodeset, main_sent_dict, boxer_graph)
            isDropped = decoder_graph.get_opernode_drop_result(oper_node)
            dropVal = "true" if isDropped == "True" else "false"
            
            prob_value = 0
            if drop_ood_feature in self.probability_tables["drop-ood"]:
                prob_value = self.probability_tables["drop-ood"][drop_ood_feature][dropVal]
            else:
                prob_value = 0.5
            return prob_value
       
    # @@@@@@@@@@@@@@@@@@@@@@@@
    def create_filtered_decoder_graph(self, potential_edges, main_sentence, main_sent_dict, boxer_graph, decoder_graph):
        filtered_decoder_graph = Training_Graph()

        root_major_node = "MN-1"
        filtered_decoder_graph.major_nodes["MN-1"] = copy.copy(decoder_graph.major_nodes["MN-1"])

        nodes_to_process = [root_major_node]
        while len(nodes_to_process) != 0:
            node_to_process = nodes_to_process[0]
            if node_to_process.startswith("MN"):
                filtered_decoder_graph.major_nodes[node_to_process] = copy.copy(decoder_graph.major_nodes[node_to_process])
            else:
                filtered_decoder_graph.oper_nodes[node_to_process] = copy.copy(decoder_graph.oper_nodes[node_to_process])
            
            for edge in potential_edges:
                if edge[0] == node_to_process:
                    dependent = edge[1]
                    nodes_to_process.append(dependent)

                    for tedge in decoder_graph.edges:
                        if tedge[0] == node_to_process and tedge[1] == dependent:
                            filtered_decoder_graph.edges.append(copy.copy(tedge))
                            
            nodes_to_process = nodes_to_process[1:]
            
        return filtered_decoder_graph
