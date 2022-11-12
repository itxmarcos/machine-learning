import sys

#Configurations
from configuration.config import TASKS
from configuration.config_json import Config
#Datasets
from data.sentiment import SentimentDataset
from data.conll import CoNLLDataset
#Models
from model.sentence_classification.sa_model import SentimentAnalysisModel
from model.sentence_classification.sa_model2 import SentimentAnalysisModel2
from model.sequence_tagging.ner_model import NERModel
#Functions
from data.data_utils import process_line

#os.environ["CUDA_VISIBLE_DEVICES"] = "1"

"""
    Tranining and validation for the given task
    Current supported tasks: 'NER', 'SA'
"""

args = sys.argv
# Set task
if len(args) > 1 and args[1] is not None:
    TASK = args[1]
else:
    TASK = "NER"

# Set configuration path
if len(args) > 1 and args[2] is not None:
    CONFIG_PATH = args[2]
else:
    CONFIG_PATH = "results/ner/config_test_3.json"  #"config_default.json"# "results/sentiment_3l/sentiment3l_config.json"

RESTORE = False

def main():

    # Get config, model and datasets
    # 1. create instance of config --> It loads automatically vocabularies, callbacks and word embeddings
    # 2. create instance of model
    # 3. create instance for training & validation datasets
    if TASK == TASKS.NER.name:
        config = Config(CONFIG_PATH) #ConfigSequenceTagging()
        model = NERModel(config)

        train = CoNLLDataset(config.filename_train,
                             processing_word=None,
                             processing_char=None,
                             word2idx=config.word2idx,
                             char2idx=config.char2idx,
                             max_iter=config.max_iter
                             )
        dev = CoNLLDataset(config.filename_dev,
                           processing_word=None,
                           processing_char=None,
                           word2idx=config.word2idx,
                           char2idx=config.char2idx,
                           max_iter=config.max_iter
                           )

    elif TASK == TASKS.SA.name:
        config = Config(CONFIG_PATH) #ConfigSentenceClassification()

        if config.layers == 1:
            model = SentimentAnalysisModel(config)
        elif config.layers == 2:
            model = SentimentAnalysisModel2(config)
        else:
            raise NotImplementedError

        if config.use_chars:
            train = SentimentDataset(config.filename_train, config.delimiter,
                                    processing_line=process_line(),
                                    processing_word=None,
                                    word2idx=config.word2idx,
                                    char2idx=config.char2idx)
            dev = SentimentDataset(config.filename_dev, config.delimiter,
                                    processing_line=process_line(),
                                    processing_word=None,
                                    word2idx=config.word2idx,
                                    char2idx=config.char2idx)
        else:
            train = SentimentDataset(config.filename_train, config.delimiter,
                                     processing_line=process_line(),
                                     processing_word=None,
                                     word2idx=config.word2idx)
            dev = SentimentDataset(config.filename_dev, config.delimiter,
                                   processing_line=process_line(),
                                   processing_word=None,
                                   word2idx=config.word2idx)
    else:
        sys.exit("Not a valid TASK")


    # Build model
    model.build()
    if RESTORE:
        print("We'll restore weights whenever possible...")
        # model.restore_session("results/.../model.weights/") # optional, restore weights
        # model.reinitialize_weights("proj") # NN output layer !!


    # Train model
    model.train(train, dev)


if __name__ == "__main__":
    main()
