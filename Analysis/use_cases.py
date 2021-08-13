from Analysis.preprocessing import removePunctuation, getDomainSpecificWords, getPOSExclusion

from nltk import WordNetLemmatizer, word_tokenize, pos_tag
from nltk.corpus import wordnet
from nltk.corpus.reader.wordnet import WordNetError

import spacy
from spacy import displacy

lemmatizer = WordNetLemmatizer()


def conductUseCasesAnalysis(order):
    cleanedActors = cleanActors(order["userStories"])
    cleanedStories = identifyActorSynonyms(cleanedActors)
    return getUseCasesFromStories(cleanedStories)


def verifyPhraseDomainWords(phrase):
    words = phrase.split()
    exclusion = getDomainSpecificWords()

    return any(element in words for element in exclusion)


def cleanActors(stories):
    nlp = spacy.load("en_core_web_sm")
    cleaned = list()

    for story in stories:
        actor = nlp(story["role"].lower())
        actorName = list()

        for chunk in actor.noun_chunks:
            actorName.append(chunk.lemma_ if not verifyPhraseDomainWords(chunk.text) else chunk.text)

        cleaned.append({"id": story["_id"], "actor": " ".join(actorName), "action": story["action"]})

    return cleaned


def removeDuplicates(values):
    return list(dict.fromkeys(values))


def getAllActors(stories):
    actors = list()

    for story in stories:
        actors.append(story["actor"])

    return removeDuplicates(actors)


def getAllStoriesOfActor(stories, actor):
    return [item for item in stories if item.get("actor") == actor]


# TODO: nltk.word_tokenize for compound actor noun and lemmatize every word
# such as in here: lemmatized_output = ' '.join([lemmatizer.lemmatize(w) for w in word_list])
# Source: https://www.machinelearningplus.com/nlp/lemmatization-examples-python/

# This function looks for synonyms among the names of actors. If a synonym is detected, one name for both
# actors is selected and the standardised name replaces the synonym in all user stories.
def identifyActorSynonyms(stories):

    def finaliseActorStories(allStories, cleanedActor, currentIDs):
        processedStories = list()
        processedIDs = list()
        storiesRetrieved = getAllStoriesOfActor(allStories, cleanedActor)

        for storyToProcess in storiesRetrieved:
            if not storyToProcess["id"] in currentIDs:
                processedStories.append({"actor": cleanedActor.capitalize(), "action": storyToProcess["action"]})
                processedIDs.append(storyToProcess["id"])
        return {"processedStories": processedStories, "processedIDs": processedIDs}

    cleanedStories = list()
    ids = list()
    actors = getAllActors(stories)

    for index, actor in enumerate(actors):
        actorsToReplace = [actor]
        actorSynonyms = []

        try:
            actorSynonyms = wordnet.synset(str(actor) + ".n.01")
        except WordNetError:
            pass

        # Check if the object has an attribute lemmas. In case synset failed to identify the word
        # (e.g. when it's a compound noun or a neologism), the object won't have any lemmas and
        # the stories for that actor will be processed and finalised without further steps.
        if not hasattr(actorSynonyms, "lemmas"):
            finalisedStories = finaliseActorStories(stories, actor, ids)

            cleanedStories.extend(finalisedStories["processedStories"])
            ids.extend(finalisedStories["processedIDs"])
            continue

        # Processes and finalises stories for the actor word, if the word has no known synonyms found by synset
        if len(actorSynonyms.lemmas()) == 1:
            finalisedStories = finaliseActorStories(stories, actor, ids)

            cleanedStories.extend(finalisedStories["processedStories"])
            ids.extend(finalisedStories["processedIDs"])
            continue

        # If synset identified synonyms for the actor word, all other actor words are checked to verify whether
        # some actor words are synonymic. In such a case, the similarity score between them will be 1.0.
        for nextActor in actors[index+1:]:
            nextActorSynonyms = []

            try:
                nextActorSynonyms = wordnet.synset(str(nextActor) + ".n.01")
            except WordNetError:
                pass

            if not hasattr(nextActorSynonyms, "lemmas"):
                finalisedStories = finaliseActorStories(stories, actor, ids)

                cleanedStories.extend(finalisedStories["processedStories"])
                ids.extend(finalisedStories["processedIDs"])
                continue

            if len(nextActorSynonyms.lemmas()) == 1:
                finalisedStories = finaliseActorStories(stories, actor, ids)

                cleanedStories.extend(finalisedStories["processedStories"])
                ids.extend(finalisedStories["processedIDs"])
                continue

            # If the next actor word is valid as per synset and has synonyms, the similarity between
            # the next actor word and the one currently in question is assessed.
            similarityScore = actorSynonyms.wup_similarity(nextActorSynonyms)

            # If the actor words are synonyms, replace the next actor word with the current one in all stories
            if similarityScore == 1.0:
                actorsToReplace.append(nextActor)

        # After all the following actor words are checked against the current actor word, the synonymic actors
        # will be replaced with the current actor words for every user story
        for actorToReplace in actorsToReplace:
            allActorStories = getAllStoriesOfActor(stories, actorToReplace)
            for storyToAppend in allActorStories:
                if not storyToAppend["id"] in ids:
                    cleanedStories.append({"actor": actor.capitalize(), "action": storyToAppend["action"]})
                    ids.append(storyToAppend["id"])

    return cleanedStories


def getUseCasesFromStories(stories):
    nlp = spacy.load("en_core_web_sm")

    actorsWithUseCases = list()
    storiesOnly = list()

    # The list of parts of speech that will be omitted from the action sentence
    exclusionRule = getPOSExclusion()

    for index, story in enumerate(stories):
        actionDoc = nlp(story["action"])
        print("__________________________")
        objects = list()
        for t, token in enumerate(actionDoc):
            currentObject = {"name": None, "attributes": list(), "methods": list(), "relationships": list()}
            childObjects = [child for child in token.children]

            if (token.dep_ == "dobj" and token.pos_ == "NOUN") or (token.dep_ == "pobj" and (token.pos_ == "ADP" or token.pos_ == "NOUN")):
                currentObject["name"] = token.lemma_ if not verifyPhraseDomainWords(token.text) else token.text

            if token.dep_ == "pobj":
                if token.head.dep_ == "prep":
                    # If the head of the preposition word is an object of a preposition or a direct object
                    if token.head.head.dep_ == "pobj" or token.head.head.dep_ == "dobj":
                        currentObject["relationships"] = [*currentObject["relationships"], token.head.head.lemma_ if not verifyPhraseDomainWords(token.head.head.text) else token.head.head.text]
                    # If the word directly preceding the preposition is an object of a preposition or a direct object
                    elif token.head.nbor(-1).dep_ == "pobj" or token.head.nbor(-1).dep_ == "dobj":
                        currentObject["relationships"] = [*currentObject["relationships"], token.head.nbor(-1).lemma_ if not verifyPhraseDomainWords(token.head.nbor(-1).text) else token.head.nbor(-1).text]

            if len(childObjects) > 0:
                for childObject in childObjects:
                    if childObject.dep_ == "amod" or childObject.dep_ == "compound":
                        currentObject["attributes"] = [*currentObject["attributes"], childObject.text]

            # Searching for potential methods/functions of the proposed candidate class
            for sentenceToken in actionDoc:
                if token.text in [child.text for child in sentenceToken.children]:
                    if sentenceToken.pos_ == "VERB":
                        methodFound = sentenceToken.lemma_.lower() + token.lemma_.capitalize() + "()"
                        currentObject["methods"] = [*currentObject["methods"], methodFound]

                        # Recognise conjugation of verbs that may form a method name
                        wordConjuncts = [conjunctWord for conjunctWord in sentenceToken.conjuncts]
                        for conjunct in wordConjuncts:
                            if conjunct.pos_ == "VERB":
                                conjMethodFound = conjunct.lemma_.lower() + token.lemma_.capitalize() + "()"
                                currentObject["methods"] = [*currentObject["methods"], conjMethodFound]

            if currentObject["name"] is not None:
                objects.append(currentObject)

            #print(token.text, token.dep_, token.head.text, token.head.pos_,[child for child in token.children])
        #if index == 11:
            #displacy.serve(doc, style="dep")

        # TODO Merge/combine the classes together

        #print(objects)

        # Pre-processing, remove any unnecessary punctuation
        storyAction = removePunctuation(story["action"])

        # Pre-processing, tokenizing words in a sentence
        tokens = word_tokenize(storyAction)

        # Part-of-speech tagging of each word in a sentence
        taggedWords = pos_tag(tokens)

        for i, word in enumerate(taggedWords):
            if word[1] == "IN":
                try:
                    nextWord = taggedWords[i+1]
                    # This is to recognise parts of sentence that describe the effect or benefit instead of
                    # an actual action and start with structures like "so that". These parts will be omitted.
                    if nextWord[1] == "IN":
                        taggedWords = taggedWords[:i]
                        if word[1] in exclusionRule:
                            taggedWords.pop(i)
                        break
                except IndexError:
                    print("No more proceeding words")

            # Excluding words that are of a speech part included in the exclusion rule
            if word[1] in exclusionRule:
                print(word[0])
                taggedWords.pop(i)

        for i, word in enumerate(taggedWords):
            if word[1] == "IN":
                if (i + 1) < len(taggedWords):
                    nextWord = taggedWords[i + 1]
                    if nextWord[1] == "IN":
                        taggedWords = taggedWords[:i]
                        break

        # TODO: Consider compound sentences with 'and'

        firstAction = list()

        for i, word in enumerate(taggedWords):
            firstAction.append(word[0])

        firstAction[0] = firstAction[0].capitalize()

        actorInList = False
        finalStory = " ".join(firstAction)
        storiesOnly.append(finalStory)

        for sublist in actorsWithUseCases:
            if sublist["actor"] == story["actor"]:
                sublist["useCases"].append(finalStory)
                actorInList = True

        if not actorInList:
            actorsWithUseCases.append({"actor": story["actor"], "useCases": [finalStory]})

    return {"actorsWithUseCases": actorsWithUseCases, "storiesOnly": storiesOnly}

