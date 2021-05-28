import sys
from ontology import create
from query_ontology import parse_answer

if sys.argv[1] == 'create':
    create()
elif sys.argv[1] == "question":
    parse_answer(args[2])

