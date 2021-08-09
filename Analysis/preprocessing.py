import string
from nltk.corpus import stopwords


def removePunctuation(sentence):
    return "".join([character for character in sentence if character not in string.punctuation])


def removeStopwords(tokens):
    englishStopwords = stopwords.words("english")
    return [token for token in tokens if token not in englishStopwords]
