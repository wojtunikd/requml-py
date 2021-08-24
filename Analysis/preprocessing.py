import string
import spacy


def removePunctuation(sentence):
    return "".join([character for character in sentence if character not in string.punctuation])


def getDomainSpecificWords():
    return ["data"]


def getPOSExclusion():
    return ["JJR", "JJS", "PRP$", "DT", "RB"]


def recogniseAndRemoveBenefit(nlp, story):
    taggedStory = nlp(story)

    for i, word in enumerate(taggedStory):
        if word.pos_ == "SCONJ":
            if word.nbor(1).pos_ == "SCONJ":
                reducedStory = " ".join([storyWord.text for storyWord in taggedStory[:i]])
                return reducedStory

    return story


def getDependencyPhrases():
    return {"ROOT": "ROOT",
            "DIRECT_OBJECT": "dobj",
            "PREPOSITIONAL_OBJECT": "pobj",
            "PREPOSITION": "prep",
            "ADJ_MODIFIER": "amod",
            "COMPOUND": "compound",
            "CONJUGATION": "conj",
            "CLAUSAL_COMPLEMENT": "ccomp"}
