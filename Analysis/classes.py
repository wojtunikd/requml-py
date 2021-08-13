import spacy
from nltk.corpus import wordnet


def conductClassesAnalysis(sentences):
    potentialCandidates = identifyPotentialClassCandidates(sentences)
    refinedCandidates = processPotentialClassCandidates(potentialCandidates)
    candidatesWithoutDuplicates = analyseClassSimilarities(refinedCandidates)
    return candidatesWithoutDuplicates


def analyseClassSimilarities(allClasses):
    classesWithoutDuplicates = list()

    for i, potentialClassObject in enumerate(allClasses):
        potentialClass = potentialClassObject["name"].split("_")

        if len(potentialClass) < 2:
            continue

        for j, nextClassObject in enumerate(allClasses):
            nextClass = nextClassObject["name"].split("_")

            if i == j:
                continue

            if len(nextClass) > 1:
                continue

            for word in potentialClass:
                try:
                    similarityScore = wordnet.synset(str(word) + ".n.01").wup_similarity(wordnet.synset(str(nextClass[0]) + ".n.01"))
                    if similarityScore == 1.0:
                        print("SIMILAR: " + word + " in " + " ".join(potentialClass) + " to " + nextClass[0])
                except Exception:
                    pass

    return {"classes": allClasses}
    # return {"classes": classesWithoutDuplicates}


def identifyPotentialClassCandidates(sentences):
    nlp = spacy.load("en_core_web_sm")
    potentialClassCandidates = list()

    for sentence in sentences:
        namedEntities = list()

        doc = nlp(sentence)

        # Checking for named entities in a user story and preparing an exclusion list
        for namedEntity in doc.ents:
            namedEntities.append(*namedEntity.lemma_.split())

        # Identifying noun chunks in each user story
        for chunk in doc.noun_chunks:
            # RULE: First word in a story is always a VERB, therefore it is not a class
            if chunk.text.split()[0] == sentence.split()[0]:
                continue

            candidate = {}
            chunkWords = chunk.lemma_.split()

            # Excluding any named entities from the list of words in the noun chunk to construct a general class name
            wordsExcludingNE = [word for word in chunkWords if word not in namedEntities]

            if len(wordsExcludingNE) < 1:
                continue

            headWordPOS = nlp(chunk.root.head.text)[0].pos_

            # Using the dependency parsing within the user story, identifying potential methods/functions for each candidate class
            if headWordPOS == "VERB":
                rootChunk = "".join(list(map(lambda word: word.capitalize(), wordsExcludingNE)))
                proposedFunction = chunk.root.head.lemma_.lower() + rootChunk + "()"
                candidate["methods"] = [proposedFunction]

            candidate["name"] = "_".join(list(map(lambda word: word.capitalize(), wordsExcludingNE)))

            potentialClassCandidates.append(candidate)

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

            # Copying potential class methods to merge duplicates, if the method name is unique
            for duplicate in listOfDuplicates:
                if "methods" in duplicate:
                    for method in duplicate["methods"]:
                        if "methods" in mergedCandidate:
                            if method not in mergedCandidate["methods"]:
                                mergedCandidate["methods"] = [*mergedCandidate["methods"], method]
                        else:
                            mergedCandidate["methods"] = [method]

            refinedCandidates.append(mergedCandidate)
        else:
            refinedCandidates.append(listOfDuplicates[0])

    return refinedCandidates
