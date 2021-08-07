##############################
# UTILITY FUNCTIONS FOR TEXT #
#         01/08/21           #
##############################


import unicodedata
import re
from nltk.stem.snowball import FrenchStemmer


stemmer = FrenchStemmer()


#############
# FUNCTIONS #
#############


def tokenize(sentence):
    sentence = normalize(sentence)
    sentence = re.sub(r"'", " ", sentence)
    return [stemmer.stem(word) for word in sentence.split()]


def normalize(text):
    text = unicodedata.normalize("NFD", text)\
           .encode("ascii", "ignore")\
           .decode("utf-8")

    return str(text).lower()
