from kgqan.logger import logger
import os
import json

knowledge_graph_to_uri = {}

logger.log_info("Collecting knowledge graph URIs")
knowledge_graphs = json.loads(os.environ["KNOWLEDGE_GRAPH_NAMES"])
if type(knowledge_graphs) != list:
    logger.log_error(f"The variable 'KNOWLEDGE_GRAPH_NAMES' has to be a list! Got: {type(knowledge_graphs)}")
    raise ValueError(f"Unexpected type for environment variable 'KNOWLEDGE_GRAPH_NAMES': expcted {type(list)} but got {type(knowledge_graphs)}")
for knowledge_graph_name in knowledge_graphs:
    knowledge_graph_uri = os.environ[knowledge_graph_name.upper() + "_URI"]
    knowledge_graph_to_uri[knowledge_graph_name] = knowledge_graph_uri
    logger.log_info(f"{knowledge_graph_name}: {knowledge_graph_uri}")
