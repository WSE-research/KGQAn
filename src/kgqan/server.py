import logging
import kgqan.nltk_setup
import traceback
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import io
import os
import time
from kgqan.kgqan import KGQAn
from kgqan.logger import logger
from kgqan.sparql_end_points import knowledge_graph_to_uri
import kgqan.embeddings_client as w2v

hostName = "0.0.0.0"
serverPort = 8899

max_Vs = 1
max_Es = 10
max_answers = 41
limit_VQuery = 600
limit_EQuery = 300

class MyServer(BaseHTTPRequestHandler):

    def running_example_answer(self):
        objs=[]
        obj1 = {'question': 'When did the Boston Tea Party take place and Who was it led by?',
                'sparql': 'SELECT * WHERE { <http://dbpedia.org/resource/Boston_Tea_Party> <http://dbpedia.org/property/date> ?When . <http://dbpedia.org/resource/Boston_Tea_Party> <http://dbpedia.org/property/leadfigures> ?whom }',
                'values': [
                    '1773-12-16    http://dbpedia.org/resource/East_India_Company',
                    '1773-12-16    http://dbpedia.org/resource/Paul_Revere',
                    '1773-12-16    http://dbpedia.org/resource/William_Molineux',
                    '1773-12-16    http://dbpedia.org/resource/British_Parliament',
                    '1773-12-16    http://dbpedia.org/resource/Samuel_Adams'],
                'named_entites': ['Boston Tea Party'],
                'extracted_relation': [['Boston Tea Party', "?when", 'take place'], [['Boston Tea Party', "?who", 'led by']]],
                'score': 1,
                "nodes": ['http://dbpedia.org/resource/Boston_Tea_Party'],
                'edges': ['<http://dbpedia.org/property/date>',
                          '<http://dbpedia.org/property/leadfigures>']}
        objs.append(obj1)
        obj2 = {'question': 'When did the Boston Tea Party take place and Who was it led by?',
                'sparql': 'SELECT * WHERE { <http://dbpedia.org/resource/Boston_Tea_Party> <http://dbpedia.org/property/date> ?When . <http://dbpedia.org/resource/Boston_Tea_Party> <http://dbpedia.org/property/leadfigures> ?whom .}',
                'values': [
                    'Boston, Massachusetts, British America    http://dbpedia.org/resource/East_India_Company',
                    'Boston, Massachusetts, British America   http://dbpedia.org/resource/Paul_Revere',
                    'Boston, Massachusetts, British America    http://dbpedia.org/resource/William_Molineux',
                    'Boston, Massachusetts, British America    http://dbpedia.org/resource/British_Parliament',
                    'Boston, Massachusetts, British America   http://dbpedia.org/resource/Samuel_Adams'],
                'named_entites': ['Boston Tea Party'],
                'extracted_relation': [['Boston Tea Party', "?when", 'take place'],
                                       [['Boston Tea Party', "?who", 'led by']]],
                'score': 1,
                "nodes": ['http://dbpedia.org/resource/Boston_Tea_Party'],
                'edges': ['<http://dbpedia.org/property/place>',
                          '<http://dbpedia.org/property/leadfigures>']}
        objs.append(obj2)
        return json.dumps(objs)

    def parse_answer(self, answers, entities, max_answers, edges):
        nodes = []
        if len(entities) != 0:
            nodes = list(entities)

        relations = []
        if len(edges) != 0:
            relations = list(edges(data='relation'))
        if 'uri' in nodes:
            nodes.remove('uri')
        objs = []
        for answer in answers:
            values = []
            if answer['results'] and answer['results']['bindings']:
                for value in answer['results']['bindings']:
                    values.append(value['uri']['value'])
            if len(values) > 0:
                obj = {'question': answer['question'], 'sparql': answer['sparql'], 'values': values, 'named_entites': nodes,
                       'extracted_relation': relations, 'score': answer['score'], "nodes": answer['nodes'],
                       'edges': answer['edges']}
                objs.append(obj)

            if len(objs) == max_answers:
                break

        return json.dumps(objs)

    def do_POST(self):
        logger.log_info("In post ")
        logger.log_info(self.request)
        try:
            content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
            post_data = self.rfile.read(content_length)  # <--- Gets the data itself
            logger.log_info("Before parsing %s" % post_data)
            # fix_bytes_value = post_data.replace(b"'", b'"')
            data = json.load(io.BytesIO(post_data))
            logger.log_info("After parsing %s" % data)
        except:
            self.send_error(500, "Failed to parse data from request")

        try:
            MyKGQAn = KGQAn(n_max_answers=max_answers, n_max_Vs=max_Vs, n_max_Es=max_Es,
                            n_limit_VQuery=limit_VQuery, n_limit_EQuery=limit_EQuery,
                            knowledge_graph_to_uri=knowledge_graph_to_uri)
            # TODO should be removed
            #if data['question'].lower() == 'when did the boston tea party take place and who was it led by?':
            #    result = self.running_example_answer()
            #else:
            answers, entities, edges, _, _, _ = MyKGQAn.ask(question_text=data['question'], knowledge_graph=data['knowledge_graph'])
            result = self.parse_answer(answers, entities, data['max_answers'], edges)
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(bytes(result, "utf-8"))
        except Exception as e:
            logger.log_info("Error from : %s" % e)
            logger.log_info("Stack trace")
            traceback.print_exc()
            self.send_error(500, "Failed to get the answer to the question")




def main():
    logger.log_info("Checking connection to word embedding server ... ")
    wait_interval = int(os.environ["WORD_EMBEDDING_CONNECTION_WAIT_INTERVAL"])
    max_tries = int(os.environ["WORD_EMBEDDING_CONNECTION_MAX_ATTEMPTS"])
    connected = False
    for i in range(max_tries):
        try:
            logger.log_info(f"Waiting {wait_interval} seconds for the word embedding server to respond.")
            time.sleep(wait_interval)
            sim = w2v.n_similarity(['intel'], ['intel', '80486dx'])
            # if this succeeds, then the server is responding properly
            logger.log_info("Word embedding server responding.")
            connected = True
            break
        except:
            logger.log_info(f"Word embedding server not responding after attempt {i+1} of {max_tries}.")

    if connected:
        webServer = HTTPServer((hostName, serverPort), MyServer)
        logger.log_info("Server started http://%s:%s" % (hostName, serverPort))

        try:
            webServer.serve_forever()
        except KeyboardInterrupt:
            pass
    else:
        raise RuntimeError(f"Could not connect to word embedding server after {max_tries * wait_interval} seconds!")

    webServer.server_close()
    logger.log_info("Server stopped.")

if __name__ == "__main__":
    main()
