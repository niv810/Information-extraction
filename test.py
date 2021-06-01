import rdflib
from query_ontology import parse_answer


def write_answer():
    graph = rdflib.Graph()
    graph.parse("ontology.nt", format="nt")
    with open("question_long.txt", 'r', encoding='utf-8') as questions_file, open("answers_long.txt", 'w',
                                                                                  encoding='utf-8') as f:
        con = True
        while con:
            question = questions_file.readline()
            if question != '':
                question = question.rstrip()
                print(question)
                f.write(parse_answer(question) + "\n")
            else:
                con = False
    f.close()


def check_dif():
    file1 = open("answers_born.txt", "r")
    file2 = open("answers_born_fani.txt", "r")
    dict1 = file1.readlines()
    dict2 = file2.readlines()
    df = [x for x in dict1 if x not in dict2]
    df2 = [x for x in dict2 if x not in dict1]
    print(df)
    print(df2)


def write_answer_born():
    g = rdflib.Graph()
    g.parse("ontology.nt", format="nt")
    f = open("answers_born.txt", "w")
    q = "select ?p ?q where { ?p" + " <http://example.org/born>" + " ?q .}"
    x1 = g.query(q)
    for result in x1:
        person_url = str(result['p'])
        split_url = person_url.split("/")
        person_name = split_url[-1]
        person_name = person_name.replace("_", " ")

        born_url = str(result['q'])
        split_url = born_url.split("/")
        born_name = split_url[-1]

        str_r = person_name + " " + born_name + "\n"
        f.write(str_r)
    f.close()


def main():
    check_dif()
    # write_answer()
    # write_answer_born()


if __name__ == "__main__":
    main()
