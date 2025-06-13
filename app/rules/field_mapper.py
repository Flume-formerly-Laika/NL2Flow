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

def map_fields(field_dict:dict)->dict:
    """
    
     @brief Maps field names using PyKE knowledge engine rules
     @param field_dict Dictionary of field names and their source values
     @return dict Dictionary with mapped field names and values
     @throws None (falls back to source value on error)
     
    """
    kb = engine.get_kb('field_mapping')
    result = {}
    for k, v in field_dict.items():
        facts = kb.get_fact_literals((k, None))
        mapped = facts[0][1] if facts else v
        result[k] = mapped
    return result
