
#===================================================================================
#description     : Methods for training graph and features exploration             =
#author          : Shashi Narayan, shashi.narayan(at){ed.ac.uk,loria.fr,gmail.com})=                                    
#date            : Created in 2014, Later revised in April 2016.                   =
#version         : 0.1                                                             =
#===================================================================================


from methods_training_graph import Method_LED, Method_OVERLAP_LED
from methods_feature_extract import Feature_Init, Feature_Nov27

def select_training_graph_method(METHOD_TRAINING_GRAPH):
    return{
	"method-0.99-lteq-lt": Method_OVERLAP_LED(0.99, "lteq", "lt"),
        "method-0.75-lteq-lt": Method_OVERLAP_LED(0.75, "lteq", "lt"),
        "method-0.5-lteq-lteq": Method_OVERLAP_LED(0.5, "lteq", "lteq"),
        "method-led-lteq": Method_LED("lteq", "lteq", "lteq"),
        "method-led-lt": Method_LED("lt", "lt", "lt")
        }[METHOD_TRAINING_GRAPH]

def select_feature_extract_method(METHOD_FEATURE_EXTRACT):
    return{
        "feature-init": Feature_Init(),
        "feature-Nov27": Feature_Nov27(),
        }[METHOD_FEATURE_EXTRACT]
