from pyke import knowledge_engine

engine = knowledge_engine.engine(__file__)
engine.activate('field_mapping')

def map_fields(field_dict):
    mapped = {}
    for name, source in field_dict.items():
        try:
            goal = engine.prove_1_goal('field_mapping.field_map($input, $output)', input=name)
            mapped[name] = goal['output'] if goal else source
        except:
            mapped[name] = source  # fallback
    return mapped
