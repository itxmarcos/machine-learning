import os

from configuration.config import Config

class ConfigSentenceClassification(Config):
    def __init__(self, load=True):
        """Initialize hyperparameters and load vocabs
        Args:
            load_embeddings: (bool) if True, load embeddings into
                np array, else None
        """
        Config.__init__(self)

        # load if requested (default)
        if load:
            self.load()

    # General config
    dir_output = "results/tass2019/"
    dir_model  = dir_output + "intertass_es_glove_wiki_char10_100_m1.weights/"
    path_log   = dir_output + "log.txt"

    # Embeddings
    dim_word = 500 #Dim pretrained word embeddings
    dim_char = 100

    ## Word embeddings -> glove files
    use_pretrained = True  #False is not implemented
    filename_glove = "resources/glove_wiki/vectors.txt"

    ## Char embeddings ->
    use_chars = True  # if char embedding, training is 3.5x slower on CPU
    filename_chars = "resources/sentiment/chars.txt"

    # Dataset
    directory = "resources/tass2019/public_data_1_develop/es/"
    filename_train = directory + "intertass_es_train.xml"
    filename_dev = directory + "intertass_es_dev.xml"
    filename_test = filename_dev

    output_file = dir_output + "es_dev.tsv"

    delimiter = ","
    max_iter = None # if not None,500 max number of examples in Dataset

    filename_tags = directory + "tags.txt"
    ntags = 4

    # Training parameters
    train_embeddings = True #Wordembeddings
    nepochs          = 10
    dropout          = 0.5
    batch_size       = 8
    opt_method        = "adam"
    lr               = 0.001
    lr_decay         = 0.9
    # clip             = -1 # if negative, no clipping
    nepoch_no_imprv  = 5

    # Model hyperparameters
    hidden_size_char = 10 # lstm on chars
    hidden_size_lstm = 100 # lstm on word embeddings
    hidden_size_lstm2 = 10 # lstm 2nd layer


