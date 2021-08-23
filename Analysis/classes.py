import spacy
from nltk.corpus import wordnet

from Analysis.preprocessing import getDomainSpecificWords, getDependencyPhrases


def conductClassesAnalysis(order):
    potentialCandidates = identifyPotentialClassCandidates(order)
    refinedCandidates = processPotentialClassCandidates(potentialCandidates)
    potentialDuplicates = analyseClassSimilarities(refinedCandidates)
    return {"classes": refinedCandidates, "duplicates": potentialDuplicates}


def verifyPhraseDomainWords(phrase):
    words = phrase.split()
    exclusion = getDomainSpecificWords()

    return any(element in words for element in exclusion)


def identifyPotentialClassCandidates(order):
    nlp = spacy.load("en_core_web_sm")

    potentialClassCandidates = list()
    dependency = getDependencyPhrases()
    sentences = order["userStories"]

    for index, story in enumerate(sentences):
        actionDoc = nlp(story["action"])
        sentenceClasses = list()

        for tokenIdx, token in enumerate(actionDoc):

            currentObject = {"name": None, "attributes": {"category": list(), "quality": list()}, "methods": list(), "relationships": list()}
            childObjects = [child for child in token.children]

            if tokenIdx != 0 and ((token.dep_ == dependency["DIRECT_OBJECT"] and token.pos_ == "NOUN") or (token.dep_ == dependency["PREPOSITIONAL_OBJECT"] and (token.pos_ == "ADP" or token.pos_ == "NOUN"))):
                currentObject["name"] = token.lemma_.capitalize() if not verifyPhraseDomainWords(token.text) else token.text.capitalize()

            if tokenIdx != 0 and token.dep_ == dependency["PREPOSITIONAL_OBJECT"]:
                if token.head.dep_ == dependency["PREPOSITION"]:

                    # If the head of the preposition word is an object of a preposition or a direct object
                    if (token.head.head.dep_ == dependency["PREPOSITIONAL_OBJECT"] and (token.head.head.pos_ == "ADP" or token.head.head.pos_ == "NOUN")) or (token.head.head.dep_ == dependency["DIRECT_OBJECT"] and token.head.head.pos_ == "NOUN"):
                        currentObject["relationships"] = [*currentObject["relationships"], token.head.head.lemma_.capitalize() if not verifyPhraseDomainWords(token.head.head.text) else token.head.head.text.capitalize()]

                    # If the word directly preceding the preposition is an object of a preposition or a direct object
                    elif (token.head.nbor(-1).dep_ == dependency["PREPOSITIONAL_OBJECT"] and (token.head.nbor(-1).pos_ == "ADP" or token.head.nbor(-1).pos_ == "NOUN")) or (token.head.nbor(-1).dep_ == dependency["DIRECT_OBJECT"] and token.head.nbor(-1).pos_ == "NOUN"):
                        currentObject["relationships"] = [*currentObject["relationships"], token.head.nbor(-1).lemma_.capitalize() if not verifyPhraseDomainWords(token.head.nbor(-1).text) else token.head.nbor(-1).text.capitalize()]

            if len(childObjects) > 0:
                for childObject in childObjects:
                    if childObject.dep_ == dependency["ADJ_MODIFIER"] or childObject.dep_ == dependency["COMPOUND"]:

                        if childObject.pos_ == "NOUN":
                            currentObject["attributes"]["category"] = [*currentObject["attributes"]["category"], childObject.text]

                        elif childObject.pos_ == "ADJ":
                            currentObject["attributes"]["quality"] = [*currentObject["attributes"]["quality"], childObject.text]

            # Searching for potential methods/functions of the proposed candidate class
            for sentenceToken in actionDoc:
                if token.text in [child.text for child in sentenceToken.children]:
                    if sentenceToken.pos_ == "VERB":
                        methodFound = sentenceToken.lemma_.lower() + token.lemma_.capitalize() + "()"
                        currentObject["methods"] = [*currentObject["methods"], methodFound]

                        # Recognise conjugation of verbs that may form a method name
                        wordConjuncts = [conjunctWord for conjunctWord in sentenceToken.conjuncts]
                        for conjunct in wordConjuncts:
                            if conjunct.pos_ == "VERB" or conjunct.dep_ == "ROOT":
                                conjMethodFound = conjunct.lemma_.lower() + token.lemma_.capitalize() + "()"
                                currentObject["methods"] = [*currentObject["methods"], conjMethodFound]

            if currentObject["name"] is not None:
                sentenceClasses.append(currentObject)

        potentialClassCandidates = [*potentialClassCandidates, *sentenceClasses]

    return potentialClassCandidates


class ContinueForResolvedDuplicates(Exception):
    pass


def processPotentialClassCandidates(candidates):
    continueForResolved = ContinueForResolvedDuplicates()

    refinedCandidates = list()

    for candidate in candidates:
        listOfDuplicates = [element for element in candidates if element["name"] == candidate["name"]]

        if len(listOfDuplicates) > 1:
            try:
                for existingCandidates in refinedCandidates:
                    if existingCandidates["name"] == candidate["name"]:
                        raise continueForResolved
            except ContinueForResolvedDuplicates:
                continue

            mergedCandidate = listOfDuplicates[0]

            for duplicate in listOfDuplicates:
                # Move all unique methods from the duplicate class to the refined class
                if "methods" in duplicate:
                    for method in duplicate["methods"]:
                        if "methods" in mergedCandidate:
                            if method not in mergedCandidate["methods"]:
                                mergedCandidate["methods"] = [*mergedCandidate["methods"], method]
                        else:
                            mergedCandidate["methods"] = [method]

                # Move all unique relationships from the duplicate class to the refined class
                if "relationships" in duplicate:
                    for relationship in duplicate["relationships"]:
                        if "relationships" in mergedCandidate:
                            if relationship not in mergedCandidate["relationships"]:
                                mergedCandidate["relationships"] = [*mergedCandidate["relationships"], relationship]
                        else:
                            mergedCandidate["relationships"] = [relationship]

                if "attributes" in duplicate:
                    # Move all unique values of the attribute category from the duplicate class to the refined class
                    if "category" in duplicate["attributes"]:
                        for category in duplicate["attributes"]["category"]:
                            if "attributes" in mergedCandidate:
                                if "category" in mergedCandidate["attributes"]:
                                    if category not in mergedCandidate["attributes"]["category"]:
                                        mergedCandidate["attributes"]["category"] = [*mergedCandidate["attributes"]["category"], category]
                                else:
                                    mergedCandidate["attributes"]["category"] = [category]
                            else:
                                mergedCandidate["attributes"] = {}
                                mergedCandidate["attributes"]["category"] = [category]

                    # Move all unique values of the attribute quality from the duplicate class to the refined class
                    if "quality" in duplicate["attributes"]:
                        for quality in duplicate["attributes"]["quality"]:
                            if "attributes" in mergedCandidate:
                                if "quality" in mergedCandidate["attributes"]:
                                    if quality not in mergedCandidate["attributes"]["quality"]:
                                        mergedCandidate["attributes"]["quality"] = [*mergedCandidate["attributes"]["quality"], quality]
                                else:
                                    mergedCandidate["attributes"]["quality"] = [quality]
                            else:
                                mergedCandidate["attributes"] = {}
                                mergedCandidate["attributes"]["quality"] = [quality]

            refinedCandidates.append(mergedCandidate)
        else:
            refinedCandidates.append(listOfDuplicates[0])

    return refinedCandidates


def analyseClassSimilarities(allClasses):
    potentialDuplicatePairs = list()

    for i, potentialClassObject in enumerate(allClasses):
        potentialClass = potentialClassObject["name"]

        for j in range(i, len(allClasses)):
            nextClass = allClasses[j]["name"]

            if i == j:
                continue

            try:
                similarityScore = wordnet.synset(str(potentialClass) + ".n.01").wup_similarity(wordnet.synset(str(nextClass) + ".n.01"))

                if similarityScore == 1.0:
                    potentialDuplicatePairs.append([potentialClass, nextClass])
            except:
                pass

    return potentialDuplicatePairs
