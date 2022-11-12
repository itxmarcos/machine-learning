import sys
#Configurations
from configuration.config import TASKS
from configuration.config_json import Config
#Datasets
from data.conll import CoNLLDataset
#Models
from model.sequence_tagging.ner_model import NERModel
#Functions
from data.data_utils import process_line


def align_data(data):
    """Given dict with lists, creates aligned strings

    Adapted from Assignment 3 of CS224N

    Args:
        data: (dict) data["x"] = ["I", "love", "you"]
              (dict) data["y"] = ["O", "O", "O"]

    Returns:
        data_aligned: (dict) data_align["x"] = "I love you"
                           data_align["y"] = "O O    O  "

    """
    spacings = [max([len(seq[i]) for seq in data.values()])
                for i in range(len(data[list(data.keys())[0]]))]
    data_aligned = dict()

    # for each entry, create aligned string
    for key, seq in data.items():
        str_aligned = ""
        for token, spacing in zip(seq, spacings):
            str_aligned += token + " " * (spacing - len(token) + 1)

        data_aligned[key] = str_aligned

    return data_aligned


def interactive_shell(model, config):
    """Creates interactive shell to play with model

    Args:
        model: instance of NERModel

    """
    model.logger.info("""
This is an interactive mode.
To exit, enter 'exit'.
You can enter a sentence like
input> I love Paris""")

    while True:
        try:
            # for python 2
            sentence = raw_input("input> ")
        except NameError:
            # for python 3
            sentence = input("input> ")

        words_raw = sentence.strip().split(" ")

        if words_raw == ["exit"]:
            break

        preds = model.get_predictions(words_raw,
                                      word2idx=config.word2idx,
                                      char2idx=config.char2idx
                                      )
        print(list(zip(words_raw,preds)))
        to_print = align_data({"input": words_raw, "output": preds})

        for key, seq in to_print.items():
            model.logger.info(seq)


def main():
    args = sys.argv
    # Set task
    if len(args) > 1 and args[1] is not None:
        print("Getting predictions from model: " + sys.argv[1])
        config_path = sys.argv[1]
    else:
        config_path = "config_default.json"  # "results/sentiment_3l/sentiment3l_config.json"

    config = Config(config_path)  # ConfigSentenceClassification()

    # build model
    model = NERModel(config)
    model.build()
    model.restore_session(config.dir_model)

    # create dataset
    test  = CoNLLDataset(config.filename_test,
                           processing_word=None,
                           processing_char=None,
                           word2idx=config.word2idx,
                           char2idx=config.char2idx,
                           )

    # evaluate and interact
    #model.evaluate(test)
    interactive_shell(model, config)


if __name__ == "__main__":
    main()
