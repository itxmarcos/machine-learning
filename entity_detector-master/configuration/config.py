import os
import logging
from enum import Enum
import numpy as np
import json


class TASKS(Enum):
    NER = 1
    SA = 2


class Config():
    def __init__(self):
        # directory for training outputs
        if not os.path.exists(self.dir_output):
            os.makedirs(self.dir_output)

        # create instance of logger
        self.logger = get_logger(self.path_log)


    def load(self):
        """Loads word embeddings and char vocabulary
        """
        # ToDo --> Support for other types of embedding
        if self.use_pretrained:
            self.embeddings, self.word2idx = get_pretrained_embeddings(self.filename_glove, self.dim_word, self.dim_word)
        else:
            raise NotImplementedError

        if self.use_chars:
            self.char2idx = get_vocabulary_char(self.filename_chars)
            self.nchars = len(self.char2idx)


def get_logger(filename):
    """Return a logger instance that writes in filename

    Args:
        filename: (string) path to log.txt

    Returns:
        logger: (instance of logger)
    """
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)
    handler = logging.FileHandler(filename)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s: %(message)s'))
    logging.getLogger().addHandler(handler)

    return logger


def get_vocabulary_char(path):
    """Loads char vocabulary from a file

    :param path: file path
    :return: dictionary:{char:idx}
    """
    try:
        d = {}
        with open(path, 'r', encoding="utf8") as f:
            for idx, char in enumerate(f):
                char = char.strip('\n')
                d[char] = idx
    except IOError:
        exit(IOError)
    return d


def get_pretrained_embeddings(path, original_embedding_dim, embedding_dim):
    """ Load embeddings

    :param path: file path
    :param embedding_dim:
    :return: Embeddings matrix, Word2Idx
    """
    if os.path.isfile(os.path.splitext(path)[0]+".matrix.npy"):
        matrix = np.load(os.path.splitext(path)[0]+".matrix.npy")
        with open(os.path.splitext(path)[0]+".w2i", 'r') as f:
                word_to_idx = json.load(f)
    else:
        glove_vocab = []
        embedding_matrix = []
        #vocab_len = sum(1 for line in open('glove_wiki/vocab.txt', encoding="utf8"))
        with open(path, 'r',  encoding="utf8") as f:
            for idx, line in enumerate(f):
                try:
                    line = line.strip().split()
                    word = line[0]
                    vector = [float(x) for x in line[1:]]  #gets embedding for the given word (vector is a list of floats)

                    if len(vector) < original_embedding_dim:
                        print("Something very weird happen at index " + str(idx))
                        continue

                    if word not in glove_vocab:
                        embedding_matrix.append(vector[0:embedding_dim])
                        glove_vocab.append(word)

                    '''
                    try:
                        word_to_idx[word]
                        print("Word " + word + " has already been saved before at " + str(word_to_idx[word]))
                    except KeyError:
                        word_to_idx[word] = idx
                    '''
                except Exception as e:
                    print("Something very weird happen at index " + str(idx))
                    print(str(e))
                    continue

            embedding_matrix.append(np.random.uniform(-1.0, 1.0, (1, embedding_dim))[0]) # UNK
            glove_vocab.append('UNK')

            # w2i & i2w
            word_to_idx = {word:idx for idx, word in enumerate(glove_vocab)}
    #        idx_to_word = {idx:word for idx, word in enumerate(glove_vocab)}

            # Convert embedding matrix to array
            matrix = np.reshape(embedding_matrix, [-1, embedding_dim]).astype(np.float32) # vocab_size x embedding_dim

            np.save(os.path.splitext(path)[0]+".matrix", matrix)
            with open(os.path.splitext(path)[0]+".w2i", 'w') as file:
                file.write(json.dumps(word_to_idx))

    return matrix, word_to_idx
