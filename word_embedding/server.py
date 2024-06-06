import os
import socket
import selectors
import traceback
from libserver import Message, wiki_model_from_path
import argparse
#from ..src.kgqan.logger import logger
import logging

sel = selectors.DefaultSelector()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    #logger.info("accepted connection from", addr)
    conn.setblocking(False)
    message = Message(sel, conn, addr)
    sel.register(conn, selectors.EVENT_READ, data=message)


def main():
#    args_parser = argparse.ArgumentParser()
#    args_parser.add_argument(
#        "--data_dir",
#        help='data directory path',
#        required=True,
#    )
#    args_parser.add_argument(
#        "--word_embed_file",
#        help='wiki embeddings filename inside data_dir path',
#        required=True,
#    )
#
#    args = args_parser.parse_args()
    # wiki_word_embed_path = os.path.join(args.data_dir, args.word_embed_file)
    wiki_word_embed_path = os.path.join("data", "wiki-news-300d-1M.txt")
    logger.info(wiki_word_embed_path)
    wiki_model_from_path(wiki_word_embed_path)

    # host, port = sys.argv[1], int(sys.argv[2])
    host, port = "0.0.0.0", 9600
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Avoid bind() exception: OSError: [Errno 48] Address already in use
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lsock.bind((host, port))
    lsock.listen()
    logger.info("listening on %s:%s" % (host, port))

    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)

    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    message = key.data
                    try:
                        message.process_events(mask)
                    except Exception:
                        logger.error("exception for %s: %s" % (message.addr, traceback.format_exc()))
                        message.close()
    except KeyboardInterrupt:
        logger.info("caught keyboard interrupt, exiting")
    finally:
        sel.close()


if __name__ == "__main__":
    logger.info("in main word embedding....")
    #print("in main word embedding....")
    main()
