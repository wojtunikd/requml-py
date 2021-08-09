from nltk import word_tokenize, pos_tag, RegexpParser
from nltk.stem import WordNetLemmatizer


def conductClassesAnalysis(sentences):
    potentialCandidates = identifyPotentialClassCandidates(sentences)
    processedCandidates = processPotentialClassCandidates(potentialCandidates)


def identifyPotentialClassCandidates(sentences):
    potentialClassCandidates = list()

    for sentence in sentences:
        tokens = word_tokenize(sentence)

        tokens[0] = tokens[0].lower()
        tokens.insert(0, "I")

        taggedWords = pos_tag(tokens)

        grammar = """NP: {<JJ>?<NN|NNS><NN|NNS>*}"""
        results = RegexpParser(grammar).parse(taggedWords)

        for subtree in results.subtrees():
            if subtree.label() == "NP":
                leafList = list()
                for leaf in subtree.leaves():
                    leafList.append(leaf[0])
                potentialClassCandidates.append(leafList)

    return potentialClassCandidates


def processPotentialClassCandidates(candidates):
    processedCandidates = list()
    lemmatizer = WordNetLemmatizer()

    for candidate in candidates:
        lemmatizedCandidate = [lemmatizer.lemmatize(noun) for noun in candidate]
        lemmatizedCandidate[0] = lemmatizedCandidate[0].capitalize()

        lemmatizedCandidate = " ".join(lemmatizedCandidate)

        processedCandidates.append(lemmatizedCandidate)

    print(processedCandidates)

    return processedCandidates
