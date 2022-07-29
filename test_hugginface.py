from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from pprint import pprint

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

sentences = \
    ['Nothing much to say as it is a macbook. the M1 processor works like a charm'
     , 'Amazing laptop, super performance with M1, its blazing fast',
     'Working very slow and takes 15-20 minutes to start thus not worth for money'
     ,
     'This is not a good laptop. It is very slow. It is taking 20 minutes to start'
     ]

sentence_embeddings = model.encode(sentences)
pprint(cosine_similarity(sentence_embeddings[0].reshape(1, -1),
       sentence_embeddings[1].reshape(1, -1))[0][0])