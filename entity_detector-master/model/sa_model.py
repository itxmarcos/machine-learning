import tensorflow as tf
import numpy as np
from model.abstract_model import Model
from model.general_utils import Progbar

from data.data_utils import minibatches, pad_sequences

from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import confusion_matrix
from pandas_ml import ConfusionMatrix


class SentimentAnalysisModel(Model):
    """ Simplest TF model """

    def __init__(self, config):
        super(SentimentAnalysisModel, self).__init__(config)

    def build(self, n_tags=1):
        self.logger.info("Building " + SentimentAnalysisModel.__name__)

        # Graph assembling
        self.set_placeholders()
        self.set_embeddings()
        self.set_lstm()
        self.set_loss()

        # Training operation: optimizer algorithm
        self.set_minimize_operation(self.config.opt_method, self.config.lr, self.loss)

        # Prepare graph for predict
        self.set_prediction_operation()

        # Set TF session and initialize varibles
        self.initialize_session()

    def set_placeholders(self):
        """ Placeholders = Input data """
        # shape = (batch size, max length of sentence)
        self.word_ids = tf.placeholder(tf.int32, shape=[None, None], name="word_ids")

        # shape = (batch size)
        self.sequence_lengths = tf.placeholder(tf.int32, shape=[None], name="sequence_lengths")

        # shape = (batch size, max length of sentence, max length of word)
        self.char_ids = tf.placeholder(tf.int32, shape=[None, None, None], name="char_ids")

        # shape = (batch_size, max_length of sentence)
        self.word_lengths = tf.placeholder(tf.int32, shape=[None, None], name="word_lengths")

        # shape = (batch size)
        self.labels = tf.placeholder(tf.int32, shape=[None], name="labels")

        self.dropout = tf.placeholder(dtype=tf.float32, shape=[], name="dropout")
        self.lr = tf.placeholder(dtype=tf.float32, shape=[], name="lr")

    def set_embeddings(self):
        """Defines self.embeddings

         If self.config.embeddings is not None (np array initialized with pre-trained word vectors),
         word_embeddings is just a look-up table (no training is done).
         Otherwise, a random matrix with the correct shape is initialized.
         """
        # WORDS
        with tf.variable_scope("words"):
            if self.config.embeddings is None:
                self.logger.info("WARNING: randomly initializing word vectors")
                _word_embeddings = tf.get_variable(
                    name="_word_embeddings",
                    dtype=tf.float32,
                    shape=[self.config.nwords, self.config.dim_word])
            else:
                _word_embeddings = tf.Variable(
                    self.config.embeddings,
                    name="_word_embeddings",
                    dtype=tf.float32,
                    trainable=self.config.train_embeddings)

            word_embeddings = tf.nn.embedding_lookup(_word_embeddings, self.word_ids, name="word_embeddings")

        # CHARS
        with tf.variable_scope("chars"):
            if self.config.use_chars:
                # Char embeddings matrix
                _char_embeddings = tf.get_variable(
                    name="_char_embeddings",
                    dtype=tf.float32,
                    shape=[self.config.nchars + 1, self.config.dim_char])  ###Don't know why, but self.config.nchars+1
                char_embeddings = tf.nn.embedding_lookup(_char_embeddings, self.char_ids, name="char_embeddings")

                # Reshapes --> ToDo Check shapes
                s = tf.shape(char_embeddings)  ###[batchSize, sentenceLength, wordLength, hiddenSize = charDim]
                char_embeddings = tf.reshape(char_embeddings, shape=[s[0] * s[1], s[-2], self.config.dim_char])
                word_lengths = tf.reshape(self.word_lengths, shape=[s[0] * s[1]])

                # bi lstm on chars
                cell_fw = tf.contrib.rnn.LSTMCell(self.config.hidden_size_char, state_is_tuple=True)
                cell_bw = tf.contrib.rnn.LSTMCell(self.config.hidden_size_char, state_is_tuple=True)
                _, ((_, output_fw), (_, output_bw)) = tf.nn.bidirectional_dynamic_rnn(
                    cell_fw,
                    cell_bw,
                    char_embeddings,
                    sequence_length=word_lengths,
                    dtype=tf.float32)

                # Concat output
                output = tf.concat([output_fw, output_bw], axis=-1)

                # shape = (batch size, max sentence length, 2*char hidden size)
                output = tf.reshape(output, shape=[s[0], s[1], 2*self.config.hidden_size_char])

                # Concatenate word embeddings & char embeddings
                word_embeddings = tf.concat([word_embeddings, output], axis=-1)

        self.embeddings = tf.nn.dropout(word_embeddings, self.config.dropout)

    def set_lstm(self):
        """ Defines self.logits
            Gets embedding representation (words and, optionally, chars) as input
            Computes forward pass, and calculates predictions at the final layer.
        """
        with tf.variable_scope("bi-lstm"):
            cell_fw = tf.contrib.rnn.LSTMCell(self.config.hidden_size_lstm)
            cell_bw = tf.contrib.rnn.LSTMCell(self.config.hidden_size_lstm)
            (output_fw, output_bw), (output_state_fw, output_state_bw) = tf.nn.bidirectional_dynamic_rnn(
                cell_fw,
                cell_bw,
                self.embeddings,
                sequence_length=self.sequence_lengths,
                dtype=tf.float32)

            # Concatenate just final states (axis=2 -> hidden_size_lstm)
            #   --> concatenamos sobre cada secuencia/instancia del batch
            output = tf.concat([output_state_fw[0], output_state_bw[0]], 1) ### ToDo DUDA con la indexación!
            output = tf.nn.dropout(output, self.config.dropout) #Add dropout

        ### Projection over our decission space: hidden state --> tag space
        with tf.variable_scope("proj"):
            W = tf.get_variable("W", dtype=tf.float32,
                                shape=[2 * self.config.hidden_size_lstm, self.config.ntags])

            b = tf.get_variable("b", shape=[self.config.ntags],
                                dtype=tf.float32, initializer=tf.zeros_initializer())

            output = tf.reshape(output, [-1, 2 * self.config.hidden_size_lstm])  ###[numSentences, 2*hiddenState]
            ### 'Linear layer'
            pred = tf.matmul(output, W) + b
            self.logits = tf.reshape(pred, [-1, self.config.ntags])  ###[numSentences, numTags]

    def set_loss(self):
        """ Output layer """
        output = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=self.logits, labels=self.labels)
        self.loss = tf.reduce_mean(output)
        # Tensorboard
        tf.summary.scalar("loss", self.loss)

    def set_minimize_operation(self, method, lr, loss):
        self.set_optimizer(method, lr)
        self.optimize = self.optimizer.minimize(loss)

    def set_prediction_operation(self):
        """ Defines prediction operation
            ...
        """
        self.prediction = tf.cast(tf.argmax(self.logits, axis=-1), tf.int32)

    def run_epoch(self, train, dev, epoch):
        """
        Trains over the whole training set once
        Evaluates over the development set

        :return: validation metrics
        """

        batch_size = self.config.batch_size
        nbatches = (len(train) + batch_size - 1) // batch_size #len(train)=numero sentencias -> make sure we have at least 1 batch
        prog = Progbar(target=nbatches)

        # TRAIN iterate over dataset by minibatches
        ## Sentences --> Encoded sentences (word_ids)
        ## Labels --> Real class
        for i, (sentences, labels) in enumerate(minibatches(train, batch_size)):
            fd = self.get_feed_dict(sentences, labels, self.config.lr, self.config.dropout)

            _, train_loss, summary = self.sess.run(
                    [self.optimize, self.loss, self.sumaries], feed_dict=fd)

            prog.update(i + 1, [("train loss", train_loss)]) #i = minibatch in #minibatches
            #self.logger.info("Batch {} of {} --> Loss: {}".format(i, nbatches, train_loss))

            #Tensorboard
            if i % 10 == 0:
                self.file_writer.add_summary(summary, epoch*nbatches + i)

        if epoch == 0:
            self.save_tags(train.tag2idx)

        # VALIDATION
        #dev.set_tagset(self.restore_tags())
        dev.set_tagset(train.get_tagset())
        metrics = self.run_evaluate(dev)
        msg = " - ".join(["{} {:04.2f}".format(k, v) for k, v in metrics.items()])
        self.logger.info(msg)

        return metrics["f1"]  # metrics["acc"]

    def get_feed_dict(self, sentences, labels=None, lr=None, dropout=None):
        """Builds feed dictionary in order to execute computation.

        :return: feed dictionary
        """
        if self.config.use_chars:
            char_ids, word_ids = zip(*sentences)  # unzip
            word_ids, sequence_lengths = pad_sequences(word_ids, 0) #sequence_lengths = sentence_lengths
            char_ids, word_lengths = pad_sequences(char_ids, pad_tok=0, nlevels=2)
        else:
            word_ids, sequence_lengths = pad_sequences(sentences, 0)

        # Build feed dictionary (keys=placeholders defined previously, values=actual data)
        feed = {
            self.word_ids: word_ids,
            self.sequence_lengths: sequence_lengths
        }

        if self.config.use_chars:
            feed[self.char_ids] = char_ids
            feed[self.word_lengths] = word_lengths

        if labels is not None:
            labels = [item for sublist in labels for item in sublist]  #Flatten! minibatches() introduces an extra list level
            feed[self.labels] = labels

        if lr is not None:
            feed[self.lr] = lr

        if dropout is not None:
            feed[self.dropout] = dropout

        return feed

    def run_evaluate(self, test):
        """Evaluates performance on a test set

        :return: metrics (acc, f1)
        """
        accs = []
        y, y_pred = [], []
        for sentences, labels in minibatches(test, self.config.batch_size):
            labels = [item for sublist in labels for item in sublist]  #Flatten! minibatches() introduces an extra list level
            labels_pred = self.predict(sentences)

            for lab, lab_pred in zip(labels, labels_pred): #foreach sentence
                accs += [1 if lab == lab_pred else 0]
                y += [lab]
                y_pred += [lab_pred]

        #ToDo
        #p  = correct_preds / total_preds if correct_preds > 0 else 0
        #r  = correct_preds / total_correct if correct_preds > 0 else 0
        #f1 = 2 * p * r / (p + r) if correct_preds > 0 else 0
        acc = np.mean(accs)

        ##### Alternative...
        precision, recall, f1, _ = precision_recall_fscore_support(y, y_pred, average='weighted')
        '''
        print('precision: {}'.format(precision))
        print('recall: {}'.format(recall))
        print('fscore: {}'.format(f1))
        '''
        #cm = confusion_matrix(y, y_pred)
        tag_to_idx = self.restore_tags()
        idx_to_tag = {v: k for k, v in tag_to_idx.items()} #Reverse dict
        y_tag = [idx_to_tag[p] for p in y]
        y_tag_pred = [idx_to_tag[p] for p in y_pred]

        pcm = ConfusionMatrix(y_tag, y_tag_pred)
        pcm.print_stats()

        return {"precision": 100 * precision, "recall": 100 * recall, "f1": 100 * f1}

    def get_predictions(self, raw_sentences,  processing_word=None, word2idx=None, char2idx=None):
        """ Predicts class for unseen instances

        :return: predicted classes
        """
        # Encoded text into word/char ids
        sentences = []
        for s in raw_sentences:
            words = []
            #ToDo --> Use common function to dataset(sentiment.py)
            tokens = s.strip().split(' ')  # Tokenization
            for token in tokens:
                if processing_word is not None:  # OJO! Podemos tener tokens vacíos = ''
                    word = processing_word(token)
                if word in word2idx:
                    #words += [word2idx[word]]
                    word_id = word2idx[word]
                else:
                    #words += [word2idx['UNK']]
                    word_id = word2idx['UNK']

                # Process chars
                if char2idx is not None:
                    char_ids = []
                    for char in word:
                        if char in char2idx:  # ignore chars out of vocabulary
                            char_ids += [char2idx[char]]
                    words += [(char_ids, word_id)]
                else:
                    words += [word_id]

            if type(words[0]) == tuple:
                words = zip(*words)

            sentences +=[words]

        # Get class predictions and map them to predefined tags
        pred_ids = self.predict(sentences)
        tag_to_idx = self.restore_tags()
        idx_to_tag = {v: k for k, v in tag_to_idx.items()} #Reverse dict
        predictions = [idx_to_tag[p] for p in pred_ids]
        return predictions

    def predict(self, sentences):
        """ Gets raw predictions (class idx) from encoded texts

        :return: raw predictions
        """
        fd = self.get_feed_dict(sentences, dropout=1.0)
        labels_pred = self.sess.run(self.prediction, feed_dict=fd)
        return labels_pred