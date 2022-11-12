import sys

#Configurations
from configuration.config_json import Config
#Datasets
from data.sentiment_TASS import SentimentDataset
#Models
from model.sentence_classification.sa_model import SentimentAnalysisModel
from model.sentence_classification.sa_model2 import SentimentAnalysisModel2
from model.sentence_classification.sa_modeln import SentimentAnalysisModelN
#Functions
from data.data_utils import preprocess_word


def main():
    print("Getting predictions from model: " + sys.argv[1])
    config_path = sys.argv[1]

    config = Config(config_path)  # ConfigSentenceClassification()

    if config.layers == 1:
        model = SentimentAnalysisModel(config)
    elif config.layers == 2:
        model = SentimentAnalysisModel2(config)
    elif config.layers > 2:
        model = SentimentAnalysisModelN(config)
    else:
        raise NotImplementedError

    model.build()
    model.restore_session(config.dir_model)

    if config.use_chars:
        test = SentimentDataset(config.filename_test, config.delimiter,
                                 processing_word=preprocess_word(),
                                 word2idx=config.word2idx,
                                 char2idx=config.char2idx)
    else:
        test = SentimentDataset(config.filename_test, config.delimiter,
                                processing_word=preprocess_word(),
                                word2idx=config.word2idx)
    # evaluate and interact
    predictions, ids = model.get_predictions_tass(test,
                                processing_word=preprocess_word(),
                                word2idx=config.word2idx,
                                char2idx=config.char2idx)

    # Save predictions in TSV format
    import csv
    rows = zip(ids, predictions)
    with open(config.output_file, 'w', newline='') as tsvfile:
        writer = csv.writer(tsvfile, delimiter='\t')
        writer.writerows(rows)

    tsvfile.close()
    print('Predictions stored at {}'.format(config.output_file))

if __name__ == "__main__":
    main()