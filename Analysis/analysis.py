from Analysis.classes import conductClassesAnalysis
from Analysis.use_cases import conductUseCasesAnalysis
from controller import updateActorUseCases, updateClasses


def conductFullAnalysis(order):
    analysedUseCases = conductUseCasesAnalysis(order)
    analysedClasses = conductClassesAnalysis(order)

    classesUpdate = updateClasses(order["_id"], analysedClasses)
    ucUpdate = updateActorUseCases(order["_id"], analysedUseCases)

    return {"useCases": analysedUseCases, "classes": analysedClasses["classes"], "potentialDuplicates": analysedClasses["duplicates"], "ucParam": ucUpdate["useCasesParam"], "classParam": classesUpdate["classParam"]}
