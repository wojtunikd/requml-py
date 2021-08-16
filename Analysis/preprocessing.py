import string


def removePunctuation(sentence):
    return "".join([character for character in sentence if character not in string.punctuation])


def getDomainSpecificWords():
    return ["data"]


def getPOSExclusion():
    return ["JJR", "JJS", "PRP$", "DT", "RB"]


def getDependencyPhrases():
    return {"ROOT": "ROOT",
            "DIRECT_OBJECT": "dobj",
            "PREPOSITIONAL_OBJECT": "pobj",
            "PREPOSITION": "prep",
            "ADJ_MODIFIER": "amod",
            "COMPOUND": "compound",
            "CONJUGATION": "conj",
            "CLAUSAL_COMPLEMENT": "ccomp"}
