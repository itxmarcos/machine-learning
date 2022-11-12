# Text classification with Tensorflow

This repo is a modification and extension of the original implementation at [guillaumegenthial's Github](https://github.com/guillaumegenthial/sequence_tagging)

We have modified that code in order to face to different text classification tasks:

## I. NER
__SEQUENCE TAGGING__

Given a sentence, tag each word (quite well explained at the original repo)

Training data must be in CONLL2002 format.


## II. Sentiment Analysis 

__SENTENCE CLASSIFICATION__

Given a sentence, classify the whole sequence with a unique class.



## How to use it

1. Place GloVe vectors under `/glove` directory

2. Update configuration file at `model/config.py` for the given task

3. ~~Build vocabulary from available corpus~~
   ```
    python build_data_<task>.py
   ```

4. Train the model
    ```
     python train_<task>.py
    ```

5. Evaluate and interact with the model with
    ```
     python evaluate_<task>.py
    ```

Data iterators and data utils are placed in `model/data_utils.py`. 

Model with training/test procedures are in `model/<task>_model.py`, which extend from `model/base_model.py`

`/data` and `/results` folders have been supplied in order to store tasks resources.


## limits 

show log ( docker logs  argon-ner) message as  'Illegal instruction (core dumped)'
check with command 'grep flags /proc/cpuinfo'  hardware architect support AVX2 instructions 


