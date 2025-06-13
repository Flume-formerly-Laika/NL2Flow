"""
/**
 * @file field_mapper.py
 * @brief Maps field names using PyKE knowledge engine rules
 * @author Huy Le (huyisme-005)
 */


"""

# Import PyKE.knowledge_engine for field mapping rules
from pyke import knowledge_engine
'''
/**
 * @var engine
 * @brief PyKE knowledge engine instance for field mapping rules
 * @type knowledge_engine.engine
 */
'''
engine = knowledge_engine.engine(__file__)
engine.activate('field_mapping')

def map_fields(field_dict):
    """
    
     @brief Maps field names using PyKE knowledge engine rules
     @param field_dict Dictionary of field names and their source values
     @return dict Dictionary with mapped field names and values
     @throws None (falls back to source value on error)
     
    """
    mapped = {}
    for name, source in field_dict.items():
        try:
            goal = engine.prove_1_goal('field_mapping.field_map($input, $output)', input=name)
            mapped[name] = goal['output'] if goal else source
        except:
            mapped[name] = source  # fallback
    return mapped
