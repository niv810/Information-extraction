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
    file1 = open("answers_long.txt", "r")
    file2 = open("answers_long_fani.txt", "r")
    dict1 = file1.readlines()
    dict2 = file2.readlines()
    df = [x for x in dict1 if x not in dict2]
    df2 = [x for x in dict2 if x not in dict1]
    print(df)
    print(df2)


def main():
    check_dif()
    # write_answer()


if __name__ == "__main__":
    main()
