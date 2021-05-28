import rdflib
import requests
import lxml.html
from query_ontology import parse_answer

url = "https://en.wikipedia.org/wiki/List_of_Academy_Award-winning_films"
g = rdflib.Graph()
bad = {"\n", ' ', ' (p.g.a)', 'p.g.a', ')', 'Executive Producer', ': ', ',', '(', ''}
prefix = "https://en.wikipedia.org"
URI_PATH = "http://example.org/"  # for ontology prefix
counter = 0
j = 1


def create_ontology():
    res = requests.get(url)
    doc = lxml.html.fromstring(res.content)
    films(doc)


def get_person(person):  # 0 - one person, 1 - more than one

    if person[:6] == "/wiki/":
        link = prefix + person
        name = person[6:]
        uri = URI_PATH + name
        name = name.replace("_", " ")
    else:
        name = person
        link = ""
        uri = URI_PATH + name.replace(" ", "_")
    person = [name, link, uri]
    if person[1] != "":

        res = requests.get(person[1])
        doc = lxml.html.fromstring(res.content)
        infobox = doc.xpath("//table[contains(@class, 'infobox')]/tbody")
        if len(infobox) != 0:
            infobox = infobox[0]
            born = infobox.xpath("//tr[th[contains(.,'Born')]]//span[contains(@class,'bday')]")
            if len(born) > 0:
                born = born[0].xpath("./text()")[0]
            else:
                born = ""
                tmp = infobox.xpath("//tr[th[contains(.,'Born')]]/td//text()")
                if len(tmp) > 0:
                    tmp = tmp[0][:4]
                    if tmp.isnumeric() and "1900" <= tmp <= "2020":
                        born = tmp
            # else:
                # born = ""
            person.append(born)
            res, bad2 = [], []
            occupation = infobox.xpath("./tr[contains(.,'Occupation')]/td//text()")
            # bad = ["\n", ' ', ' (p.g.a)', 'p.g.a', ')', 'Executive Producer', ': ', ',', '(']
            if len(infobox.xpath("./tr[contains(.,'Occupation')]/td//style")) > 0:
                # bad2 = infobox.xpath("./tr[contains(.,'Occupation')]/td/style/text()")
                occupation.pop(0)
            for elem in occupation:
                tmp = elem.split(", ")
                for e in tmp:
                    if e not in bad and "   " not in e:
                        res.append(e.lower())
            # occupation = [e.lower() for e in occupation if e not in bad if e not in bad2]
            person.append(res)
        else:
            person += ["", []]
    else:
        person += ["", []]
    return person


def is_based(movie):
    res = movie.xpath("(//table[contains(@class, 'infobox')]/tbody)[1]/tr[contains(.,'Based on')]")
    if len(res) > 0:
        global counter
        counter += 1
        return 1
    return 0


def find_people(occupation, infobox):  # occupation is Produced or Directed
    cell = infobox.xpath("//tr[contains(.,'" + occupation + "')]/td")
    if len(cell) == 0:
        return []
    cell = "(//tr[contains(.,'" + occupation + "')]/td)[1]//"
    # cell = infobox.xpath("(//tr[contains(.,'"+occupation+"')]/td)[1]")[0]
    people, bad2 = [], []
    # if len(cell.xpath("//a")) > 0:
    #     people = cell.xpath("//a/@href")
    #     bad = cell.xpath("//a/text()") + ["\n"]
    # tmp = cell.xpath("//text()")
    # bad = ["\n", ' ', ' (p.g.a)', 'p.g.a', ')', 'Executive Producer', ': ', ',', '(']
    if len(infobox.xpath(cell + "a")) > 0:
        people = infobox.xpath(cell + "a/@href")
        bad2 = infobox.xpath(cell + "a/text()")
    tmp = infobox.xpath(cell + "text()")
    people += [e for e in tmp if e not in bad if e not in bad2]  # we got all people name/link
    for i in range(len(people)):
        people[i] = get_person(people[i])

    # print(" ")
    return people


def add_person_to_ontology(people):
    for person in people:
        if person[3] != "":
            g.add((rdflib.URIRef(person[2]), rdflib.URIRef(URI_PATH + "born"), rdflib.URIRef(URI_PATH + person[3])))
        for occupation in person[4]:
            g.add((rdflib.URIRef(person[2]), rdflib.URIRef(URI_PATH + "occupation"),
                   rdflib.URIRef(URI_PATH + occupation.replace(" ", "_"))))


def add_movie(movie):
    res = requests.get(movie[1])
    doc = lxml.html.fromstring(res.content)
    infobox = doc.xpath("(//table[contains(@class, 'infobox')]/tbody)[1]")[0]

    people = find_people("Directed", infobox)
    for person in people:
        g.add((rdflib.URIRef(movie[2]), rdflib.URIRef(URI_PATH + "directed_by"), rdflib.URIRef(person[2])))
    add_person_to_ontology(people)

    people = find_people("Produced", infobox)
    for person in people:
        g.add((rdflib.URIRef(movie[2]), rdflib.URIRef(URI_PATH + "produced_by"), rdflib.URIRef(person[2])))
    add_person_to_ontology(people)

    people = find_people("Starring", infobox)
    for person in people:
        g.add((rdflib.URIRef(movie[2]), rdflib.URIRef(URI_PATH + "starring"), rdflib.URIRef(person[2])))
    add_person_to_ontology(people)

    global j
    if is_based(doc):
        g.add((rdflib.URIRef(movie[2]), rdflib.URIRef(URI_PATH + "based_on"), rdflib.URIRef(URI_PATH + "book")))
        print(j)
    j += 1

    dates = infobox.xpath("//span[contains(@class,'dtstart')]")
    if len(dates) > 0:
        dates = infobox.xpath("//span[contains(@class,'dtstart')]/text()")
    for date in dates:
        g.add((rdflib.URIRef(movie[2]), rdflib.URIRef(URI_PATH + "released_on"), rdflib.URIRef(URI_PATH + date)))

    runtime = infobox.xpath("//tr[contains(.,'Running time')]/td//text()")
    runtime = [e.replace(" ", "_") for e in runtime if e not in bad if "minutes" in e]
    for time in runtime:
        g.add((rdflib.URIRef(movie[2]), rdflib.URIRef(URI_PATH + "running_time"), rdflib.URIRef(URI_PATH + time)))


def films(page):
    table = page.xpath("//table")[0]
    movies = table.xpath("./tbody//tr[td[2]//text()>=2010]//td[1]//a")
    for i in range(0, len(movies)):
        name = (movies[i].xpath("./@href")[0])[6:]
        uri = URI_PATH + name
        name = name.replace("_", " ")
        link = prefix + movies[i].xpath("./@href")[0]
        # name = movies[i].xpath("./text()")[0]
        movies[i] = [name, link, uri]
    for i in range(0, len(movies)):
        add_movie(movies[i])

    # //table//th/text()[contains(.,'Film')]
    # //table[.//th//text()[contains(.,'Film')]]
    # //table[//th[contains(.,'Film')]]//tr//td[2]//a[1]//text()
    # print(movies)
    print(len(movies))
    print(counter)


def create():
    create_ontology()
    g.serialize("ontology.nt", format="nt")


if __name__ == "__main__":
    create()
    # parse_answer("Who directed Ida_(film)?")
