import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON
URI_PATH = "http://example.org/"

def get_question_type(question):
    question = question[:len(question) - 1]
    first_word = question.split(' ')[0]
    if first_word == 'Who':
        second_word = question.split(' ')[1]
        if second_word == 'directed' or second_word == 'produced':
            return query_for_1_2(question)
        elif second_word == 'starred':
            return query_for_6(question)
        else:
            print("not a valid question")
            exit(1)

    elif first_word == 'Is':
         return query_for_3(question)

    elif first_word == 'When':
        relation = question.split(' ')[-1]
        if relation == 'released':
            return query_for_4(question)
        else:
            return query_for_8(question)

    elif first_word == 'How':
        return query_for_5(question)

    elif first_word == 'Did':

    elif first_word == 'What':

    elif first_word == 'How':

    else:
        print("not a valid question")
        exit(1)

def query_for_1_2(question):
    relation = question.split(" ")[1]
    film_with_spaces = question.split(" ", 2)[2]
    film = film_with_spaces.replace(" ", "_") #keep if URI is with underscore
    query = f"SELECT * WHERE {{ <{URI_PATH}{film}> <{URI_PATH}{relation}_by> ?e. }}"
    return query

def query_for_3(question):
    film_with_spaces = question.split(" based on a book?")[0]
    film_with_spaces = film_with_spaces.split(" ", 1)[1]
    film = film_with_spaces.replace(" ", "_")  # keep if URI is with underscore
    query = f"SELECT * WHERE {{ <{URI_PATH}{film}> <{URI_PATH}based_on> ?e. }}"
    return query

def query_for_4(question):
    entity_with_spaces = question.split("When was ")[1]
    entity_with_spaces = entity_with_spaces.split(" released")[0]
    entity = entity_with_spaces.replace(" ", "_") #keep if URI is with underscore
    query = f"SELECT * WHERE {{ <{URI_PATH}{entity}> <{URI_PATH}released_on> ?e. }}"
    return query

def query_for_5(question):
    film_with_spaces = question.split(" ", 3)[3]
    film = film_with_spaces.replace(" ", "_")  # keep if URI is with underscore
    query = f"SELECT * WHERE {{ <{URI_PATH}{film}> <{URI_PATH}running_time> ?e. }}"
    return query

def query_for_6(question):
    film_with_spaces = question.split(" ", 3)[3]
    film = film_with_spaces.replace(" ", "_")  # keep if URI is with underscore
    query = f"SELECT * WHERE {{ <{URI_PATH}{film}> <{URI_PATH}starring> ?e. }}"
    return query

def query_for_8(question):
    entity_with_spaces = question.split("When was ")[1]
    entity_with_spaces = entity_with_spaces.split(" born")[0]
    entity = entity_with_spaces.replace(" ", "_") #keep if URI is with underscore
    query = f"SELECT * WHERE {{ <{URI_PATH}{entity}> <{URI_PATH}born> ?e. }}"
    return query
