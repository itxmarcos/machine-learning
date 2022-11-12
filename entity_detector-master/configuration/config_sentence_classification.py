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
    dir_output = "results/sentiment/"
    dir_model  = dir_output + "model_glove_all_clean_char100_300.weights/"
    path_log   = dir_output + "log.txt"

    # Embeddings
    dim_word = 300 #Dim pretrained word embeddings
    dim_char = 100

    ## Word embeddings -> glove_wiki files
    use_pretrained = True  #False is not implemented
    filename_glove = "resources/glove_all/vectors300.txt"

    ## Char embeddings ->
    use_chars = True  # if char embedding, training is 3.5x slower on CPU
    filename_chars = "resources/sentiment/chars.txt"

    # Dataset
    directory = "resources/sentiment/"
    filename_train = directory + "Turismo_Comunicacion_Hackathon_5l-TAG.csv"  #"intertass-ES-development-tagged-categorical.csv" #
    filename_dev = directory + "SocialMoriarty_SentimentAnalysis_test1051.csv"  #"intertass-ES-development-tagged-categorical15.csv"
    filename_test = filename_dev

    delimiter = ","
    max_iter = None # if not None,500 max number of examples in Dataset

    filename_tags = directory + "tags.txt"
    ntags = 5

    # Training parameters
    train_embeddings = True #Wordembeddings
    nepochs          = 5
    dropout          = 0.5
    batch_size       = 32
    opt_method        = "adam"
    lr               = 0.001
    lr_decay         = 0.9
    # clip             = -1 # if negative, no clipping
    nepoch_no_imprv  = 20

    # Model hyperparameters
    hidden_size_char = 50 # lstm on chars
    hidden_size_lstm = 100 # lstm on word embeddings
    hidden_size_lstm2 = 150 # lstm 2nd layer


class ConfigSentenceClassification3l(Config):
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
    dir_output = "results/sentiment_3l/"
    dir_model  = dir_output + "model.weights/"
    path_log   = dir_output + "log.txt"

    # Embeddings
    dim_word = 500 #Dim pretrained word embeddings
    dim_char = 100

    ## Word embeddings -> glove_wiki files
    use_pretrained = True  #False is not implemented
    filename_glove = "resources/glove_wiki/vectors.txt"

    ## Char embeddings ->
    use_chars = True  # if char embedding, training is 3.5x slower on CPU
    filename_chars = "resources/sentiment/chars.txt"

    # Dataset
    directory = "resources/sentiment_3l/"
    filename_train = directory + "Turismo_Comunicacion_Hackathon_3l-TAG.csv"  #"intertass-ES-development-tagged-categorical.csv" #
    filename_dev = directory + "SocialMoriarty_SentimentAnalysis_test1051_3l.csv"  #"intertass-ES-development-tagged-categorical15.csv"
    filename_test = filename_dev

    delimiter = ","
    max_iter = None # if not None, max number of examples in Dataset

    filename_tags = directory + "tags.txt"
    ntags = 5

    # Training parameters
    train_embeddings = False  #Wordembeddings
    nepochs          = 15
    dropout          = 0.5
    batch_size       = 32
    opt_method        = "adam"
    lr               = 0.001
    lr_decay         = 0.9
    # clip             = -1 # if negative, no clipping
    nepoch_no_imprv  = 5

    # Model hyperparameters
    hidden_size_char = 50 # lstm on chars
    hidden_size_lstm = 200 # lstm on word embeddings


