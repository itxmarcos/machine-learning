import json
import tensorflow as tf
import os
from model.sentence_classification.sa_model2 import SentimentAnalysisModel2
from configuration.config_sentence_classification import ConfigSentenceClassification
#Functions
from data.data_utils import preprocess_word

REQUEST = json.dumps({
    'body': [ "me gusta mucho", "lo odio", "me da igual","es todo muy bonito"]
})
req = json.loads(REQUEST)


def predict_text(model, text):
    words_raw = text.strip().split(" ")
    preds = model.predict(words_raw)
    return preds

def main():
    tf.logging.set_verbosity(tf.logging.ERROR)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    
    print(json.dumps(req,indent=4))

    # create instance of config
    config = ConfigSentenceClassification()

    # Build and restore model
    model = SentimentAnalysisModel2(config)
    model.build()
    model.restore_session(config.dir_model)

    response_output = model.get_predictions(req['body'],
                                            processing_word=preprocess_word(),
                                            word2idx=config.word2idx,
                                            char2idx=config.char2idx)

#--------------------------------------------------------------------------------------------------------------------#

    output={}
    output["body"]=response_output
    print (json.dumps(output,indent=4))


if __name__ == "__main__":
    main()
