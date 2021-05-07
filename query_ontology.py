from identify_q import get_question_type, URI_PATH
import rdflib
def parse_answer(question):
    answer_string = ""
    q_type, sparql_query = get_question_type(question)
    graph = rdflib.Graph()
    graph.parse("ontology.nt", format="nt")
    x = graph.query(sparql_query)
    if q_type == 3 or q_type == 7:  # yes/no questions
        print()  # do something

    elif q_type >= 10:  # counting question
        print(len(x))

    else:  # list question
        for result in x:
            parsed_result = extract_answer_from_string(result)
            if answer_string == "":
                answer_string = parsed_result
            else:
                answer_string = answer_string + ", " + parsed_result

    print(answer_string)


def extract_answer_from_string(answer):
    answer_parsed = str(answer).split(URI_PATH)[1]
    answer_parsed = answer_parsed.replace("'", "")
    answer_parsed = answer_parsed.replace(")", "")
    answer_parsed = answer_parsed.replace(",", "")
    answer_parsed = answer_parsed.replace("_", " ")
    return answer_parsed

