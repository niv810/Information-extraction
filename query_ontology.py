from identify_q import get_question_type, URI_PATH
import rdflib
def parse_answer(question):
    graph = rdflib.Graph()
    answer_string = ""
    q_type, sparql_query = get_question_type(question)
    graph.parse("ontology.nt", format="nt")
    x = graph.query(sparql_query)
    if q_type == 3 or q_type == 7:  # yes/no questions
        if x:
            answer_string = 'Yes'
        else:
            answer_string = 'No'

    elif q_type >= 10 and q_type != 13:  # counting question
        answer_string = (len(x))

    else:  # list question
        res = []
        for result in x:
            parsed_result = extract_answer_from_string(result)
            res.append(parsed_result)
        res.sort()
        for result in res:
            if answer_string == "":
                answer_string = result
            else:
                answer_string = answer_string + ", " + result

    print(answer_string)


def extract_answer_from_string(answer):
    answer_parsed = str(answer).split(URI_PATH)[1]
    answer_parsed = answer_parsed.replace("'", "")
    answer_parsed = answer_parsed.replace(",", "")
    answer_parsed = answer_parsed.replace("_", " ")
    answer_parsed = answer_parsed.replace("))", "")
    return answer_parsed

