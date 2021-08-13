import string


def removePunctuation(sentence):
    return "".join([character for character in sentence if character not in string.punctuation])


def getDomainSpecificWords():
    return ["data"]


def getPOSExclusion():
    return ["JJR", "JJS", "PRP$", "DT", "RB"]
