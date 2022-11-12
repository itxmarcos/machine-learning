import sys

#Configurations
from configuration.config import TASKS
from configuration.config_json import Config
#Datasets
from data.sentiment_TASS import SentimentDataset
#Models
from model.sentence_classification.sa_model import SentimentAnalysisModel
from model.sentence_classification.sa_model2 import SentimentAnalysisModel2
from model.sentence_classification.sa_modeln import SentimentAnalysisModelN
#Functions
from data.data_utils import process_line

#os.environ["CUDA_VISIBLE_DEVICES"] = "1"

"""
    Tranining and validation for the given task
    Current supported tasks: 'NER', 'SA'
"""
TASK = "SA"



def main():
    print("Training model: " + sys.argv[1])
    config_path = sys.argv[1]  # "results/tass2019/intertass_es_glove_sbwc_char100_300_m2.json"

    # Get config, model and datasets
    # 1. create instance of config --> It loads automatically vocabularies, callbacks and word embeddings
    # 2. create instance of model
    # 3. create instance for training & validation datasets
    if TASK == TASKS.NER.name:
        raise NotImplementedError

    elif TASK == TASKS.SA.name:
        config = Config(config_path) #ConfigSentenceClassification()

        if config.layers == 1:
            model = SentimentAnalysisModel(config)
        elif config.layers == 2:
            model = SentimentAnalysisModel2(config)
        elif config.layers > 2:
            model = SentimentAnalysisModelN(config)
        else:
            raise NotImplementedError

        if config.use_chars:
            train = SentimentDataset(config.filename_train, config.delimiter,
                                    processing_line=process_line(),
                                    processing_word=None,
                                    word2idx=config.word2idx,
                                    char2idx=config.char2idx,
                                    use_unk=config.use_unk)
            dev = SentimentDataset(config.filename_dev, config.delimiter,
                                    processing_line=process_line(),
                                    processing_word=None,
                                    word2idx=config.word2idx,
                                    char2idx=config.char2idx,
                                    use_unk=config.use_unk)
        else:
            train = SentimentDataset(config.filename_train, config.delimiter,
                                    processing_line=process_line(),
                                    processing_word=None,
                                    word2idx=config.word2idx,
                                    use_unk=config.use_unk)
            dev = SentimentDataset(config.filename_dev, config.delimiter,
                                    processing_line=process_line(),
                                    processing_word=None,
                                    word2idx=config.word2idx,
                                    use_unk=config.use_unk)
    else:
        sys.exit("Not a valid TASK")


    # Build model
    model.build()
    # model.restore_session("results/.../model.weights/") # optional, restore weights
    # model.reinitialize_weights("proj") # NN output layer !!


    # Train model
    model.train(train, dev)


if __name__ == "__main__":
    main()
