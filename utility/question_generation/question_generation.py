import json
from utility.question_generation.pipelines import pipeline
def question_answers(inputText):

    nlp1 = pipeline("question-generation", model="valhalla/t5-base-qg-hl")
    question_set1 = nlp1(inputText)

    """ nlp2 = pipeline("multitask-qa-qg")
    question_set2 = nlp2(inputText)

    question_set1.extend(question_set2) """

    print("\n")
    print(json.dumps(question_set1, sort_keys=False, indent=4))
    print("\n")

    return question_set1


