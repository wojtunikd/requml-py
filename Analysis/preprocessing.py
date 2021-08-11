import string


def removePunctuation(sentence):
    return "".join([character for character in sentence if character not in string.punctuation])