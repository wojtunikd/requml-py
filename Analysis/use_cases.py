from nltk import WordNetLemmatizer, word_tokenize, pos_tag, RegexpParser
from nltk.corpus import wordnet
from nltk.corpus.reader.wordnet import WordNetError

lemmatizer = WordNetLemmatizer()


# Get a closer look at actors that consist of more than one word
def cleanActors(stories):
    cleaned = list()

    for story in stories:
        actor = story["role"].lower()
        actorWords = actor.split()

        for word in actorWords:
            if len(wordnet.synsets(str(word))) == 0:
                continue

        if len(actorWords) == 1:
            actor = lemmatizer.lemmatize(actor)

        cleaned.append({"id": story["_id"], "actor": actor, "action": story["action"]})

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
def identifyActorSynonyms(stories):
    cleanedStories = list()
    ids = list()
    actors = getAllActors(stories)

    for index, actor in enumerate(actors):
        actorsToReplace = [actor]

        try:
            actorSynonyms = wordnet.synset(str(actor) + ".n.01")

            if len(actorSynonyms.lemmas()) == 1:
                allActorStories = getAllStoriesOfActor(stories, actor)
                for storyToAppend in allActorStories:
                    if not storyToAppend["id"] in ids:
                        cleanedStories.append({"actor": actor.capitalize(), "action": storyToAppend["action"]})
                        ids.append(storyToAppend["id"])
                continue

            for nextActor in actors[index+1:]:
                try:
                    nextActorSynonyms = wordnet.synset(str(nextActor) + ".n.01")

                    if len(nextActorSynonyms.lemmas()) == 1:
                        allActorStories = getAllStoriesOfActor(stories, actor)
                        for storyToAppend in allActorStories:
                            if not storyToAppend["id"] in ids:
                                cleanedStories.append({"actor": actor.capitalize(), "action": storyToAppend["action"]})
                                ids.append(storyToAppend["id"])
                        continue

                    similarityScore = actorSynonyms.wup_similarity(nextActorSynonyms)
                    print(similarityScore)

                    if similarityScore > 0.9:
                        actorsToReplace.append(nextActor)
                except WordNetError as error:
                    print(error)

            for actorToReplace in actorsToReplace:
                allActorStories = getAllStoriesOfActor(stories, actorToReplace)
                for storyToAppend in allActorStories:
                    if not storyToAppend["id"] in ids:
                        cleanedStories.append({"actor": actor.capitalize(), "action": storyToAppend["action"]})
                        ids.append(storyToAppend["id"])
        except WordNetError as error:
            print(error)
        except Exception as error:
            print(error)

    print(cleanedStories)
    return cleanedStories


def getUseCasesFromStories(stories):
    actorsWithUseCases = list()
    exclusionRule = ["JJ", "JJR", "JJS", "RB", "RBR", "RBS", "PRP$", "DT", ",", "."]
    grammarRule = """
        S: {<PRP><ACTION><BENEFIT>},
        ACTION: {<[\.VI].*>*<[\.N].*>*<TO>?<[\.N].*>*}
    """

    for story in stories:
        tokens = word_tokenize("I " + story["action"])
        taggedWords = pos_tag(tokens)

        for i, word in enumerate(taggedWords):
            if word[1] == "IN":
                try:
                    nextWord = taggedWords[i+1]
                    if nextWord[1] == "IN":
                        taggedWords = taggedWords[:i]
                except IndexError:
                    print("No more proceeding words")

            if word[1] in exclusionRule:
                taggedWords.pop(i)

        for i, word in enumerate(taggedWords):
            if word[1] == "IN":
                if (i + 1) < len(taggedWords):
                    nextWord = taggedWords[i + 1]
                    if nextWord[1] == "IN":
                        taggedWords = taggedWords[:i]

        results = RegexpParser(grammarRule).parse(taggedWords)

        firstAction = []

# only the first action should be taken
        for subtree in results.subtrees():
            if subtree.label() == 'ACTION':
                print(subtree)
                for leave in subtree.leaves():
                    firstAction.append(leave[0])

        firstAction[0] = firstAction[0].capitalize()

        actorInList = False

        for sublist in actorsWithUseCases:
            if sublist["actor"] == story["actor"]:
                sublist["useCases"].append(" ".join(firstAction))
                actorInList = True

        if not actorInList:
            actorsWithUseCases.append({"actor": story["actor"], "useCases": [" ".join(firstAction)]})

    return actorsWithUseCases


def analyseForUseCases(order):
    print(order)
    cleanedActors = cleanActors(order["userStories"])
    cleanedStories = identifyActorSynonyms(cleanedActors)
    return getUseCasesFromStories(cleanedStories)
