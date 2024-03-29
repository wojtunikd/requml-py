from Analysis.preprocessing import removePunctuation, getDomainSpecificWords, getPOSExclusion, getDependencyPhrases, recogniseAndRemoveBenefit

from nltk import WordNetLemmatizer, word_tokenize, pos_tag
from nltk.corpus import wordnet
from nltk.corpus.reader.wordnet import WordNetError

import spacy
import copy

nlp = spacy.load("en_core_web_sm")
lemmatizer = WordNetLemmatizer()


def verifyPhraseDomainWords(phrase):
    words = phrase.split()
    exclusion = getDomainSpecificWords()

    return any(element in words for element in exclusion)


def conductUseCasesAnalysis(order):
    cleanedActors = cleanActors(order["userStories"])
    cleanedStories = findSynonymsAndTransferStories(cleanedActors)
    actorUseCases = getUseCasesFromStories(cleanedStories)
    return refineActorUseCases(actorUseCases)


def cleanActors(stories):
    cleaned = list()

    for story in stories:
        actor = nlp(story["role"].lower())
        actorName = list()

        # In case no obvious nouns are recognised or if some nouns are misclassified (e.g. a cook/to cook)
        if len([noun for noun in actor.noun_chunks]) == 0:
            actorName.append(story["role"].lower())
        else:
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


# This function looks for synonyms among the names of actors. If a synonym is detected, one name for both
# actors is selected and the standardised name replaces the synonym in all user stories.
def findSynonymsAndTransferStories(stories):

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
    actorsWithUseCases = list()
    storiesOnly = list()

    # The list of parts of speech that will be omitted from the action sentence
    exclusionRule = getPOSExclusion()

    for index, story in enumerate(stories):

        # Pre-processing, remove any unnecessary punctuation
        storyAction = removePunctuation(story["action"])

        # Pre-processing, remove benefit from sentence
        storyNoBenefit = recogniseAndRemoveBenefit(nlp, storyAction)

        # Pre-processing, tokenizing words in a sentence
        tokens = word_tokenize(storyNoBenefit)

        # Part-of-speech tagging of each word in a sentence
        taggedWords = pos_tag(tokens)

        for i, word in enumerate(taggedWords):

            # Excluding words that are of a speech part included in the exclusion rule
            if word[1] in exclusionRule and word[0] != "not" and i != 0:
                taggedWords.pop(i)

        firstAction = list()

        for i, word in enumerate(taggedWords):
            firstAction.append(word[0])

        firstAction[0] = firstAction[0].capitalize()

        actorInList = False
        finalStory = " ".join(firstAction)
        storiesOnly.append(finalStory)

        for sublist in actorsWithUseCases:
            if sublist["actor"] == story["actor"]:
                sublist["useCases"] = [*sublist["useCases"], {"useCase": finalStory, "core": list()}]
                actorInList = True

        if not actorInList:
            actorsWithUseCases.append({"actor": story["actor"], "useCases": [{"useCase": finalStory, "core": list()}]})

    return {"actorsWithUseCases": actorsWithUseCases}


def refineActorUseCases(actorsWithUseCases):
    refinedActorUseCases = copy.deepcopy(actorsWithUseCases)["actorsWithUseCases"]

    dependency = getDependencyPhrases()

    for actorIdx, actor in enumerate(refinedActorUseCases):
        for storyIdx, story in enumerate(actor["useCases"]):
            useCasesDoc = nlp(story["useCase"])

            for tokenIdx, token in enumerate(useCasesDoc):
                if token.dep_ == dependency["ROOT"] or tokenIdx == 0:
                    refinedActorUseCases[actorIdx]["useCases"][storyIdx]["core"].append(tokenIdx)

                elif token.dep_ == dependency["CONJUGATION"] and token.head.dep_ == dependency["ROOT"]:
                    refinedActorUseCases[actorIdx]["useCases"][storyIdx]["core"].append(tokenIdx)

                elif token.dep_ == dependency["DIRECT_OBJECT"] and (token.head.dep_ == dependency["ROOT"] or token.head.dep_ == dependency["CONJUGATION"]):
                    refinedActorUseCases[actorIdx]["useCases"][storyIdx]["core"].append(tokenIdx)

                elif token.dep_ == dependency["DIRECT_OBJECT"] and token.head.dep_ == dependency["CLAUSAL_COMPLEMENT"] and token.head.head.dep_ == dependency["ROOT"] and token.pos_ != "DET":
                    refinedActorUseCases[actorIdx]["useCases"][storyIdx]["core"].append(tokenIdx)

    return refinedActorUseCases
