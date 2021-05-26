import rdflib
import requests
import lxml.html

url = "https://en.wikipedia.org/wiki/List_of_Academy_Award-winning_films"
g = rdflib.Graph()
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
            born = infobox.xpath("//span[contains(@class,'bday')]")
            if len(born) > 0:
                born = born[0].xpath("./text()")[0]
            else:
                born = ""
            person.append(born)
            occupation = infobox.xpath("./tr[contains(.,'Occupation')]/td//text()")
            occupation = [e.lower() for e in occupation if e != "\n"]
            person.append(occupation)
        else:
            person += ["", []]
    else:
        person += ["", []]
    return person


"""
    res = requests.get(person[1])
    doc = lxml.html.fromstring(res.content)
    infobox = doc.xpath("//table[contains(@class, 'infobox')]/tbody")[0]
    born = infobox.xpath("//span[contains(@class,'bday')]")
    if len(born) > 0:
        born = born[0].xpath("./text()")[0]
    else:
        born = ""
    person.append(born)
    occupation = infobox.xpath("./tr[contains(.,'Occupation')]/td//text()")
    occupation = [e.lower() for e in occupation if e != "\n"]
    person.append(occupation)
    return person
"""
"""
    res = []
    if option:
        for person in people:
            link = person.xpath("./a")
            if len(link) > 0:
                link = link[0]
                name = (link.xpath("./@href")[0])[6:].replace("_", " ")
                link = prefix + link.xpath("./@href")[0]
            else:
                name = person.xpath("./text()")[0]
                link = ""
            uri = URI_PATH + name
            res.append([name, link, uri])
    else:
        name = (people.xpath("./@href")[0])[6:].replace("_", " ")
        link = prefix + people.xpath("./@href")[0]
        uri = URI_PATH + name
        res.append([name, link, uri])
    return res
"""


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
    people, bad = [], []
    # if len(cell.xpath("//a")) > 0:
    #     people = cell.xpath("//a/@href")
    #     bad = cell.xpath("//a/text()") + ["\n"]
    # tmp = cell.xpath("//text()")
    if len(infobox.xpath(cell + "a")) > 0:
        people = infobox.xpath(cell + "a/@href")
        bad = infobox.xpath(cell + "a/text()")
    bad.append("\n")
    tmp = infobox.xpath(cell + "text()")
    people += [e for e in tmp if e not in bad]  # we got all people name/link
    for i in range(len(people)):
        people[i] = get_person(people[i])

        """
        tmp = people[i]
        if tmp[:6] == "/wiki/":
            link = prefix + tmp
            name = tmp[6:]
            uri = URI_PATH + name
            name = name.replace("_", " ")
        else:
            name = tmp
            link = ""
            uri = URI_PATH + name.replace(" ", "_")
        people[i] = [name, link, uri]
    for i in range(len(people)):
        if people[i][1] != "":
            people[i] = get_person(people[i])
        else:
            people[i] += ["", []]
            """
    # print(" ")
    return people


""""

    tmp = infobox.xpath("//tr[contains(.,'Produced')]/td//li")
    tmp2 = infobox.xpath("//tr[contains(.,'Produced')]/td//br")
    option = 1
    if len(tmp) == 0 and len(tmp2) == 0:
        tmp = infobox.xpath("//tr[contains(.,'Produced')]/td/a")
        if len(tmp) > 0:
            tmp = tmp[0]
        else:
            return
            # need to add something for one person without link
        # tmp = infobox.xpath("//tr[contains(.,'Produced')]/td/a")[0]
        option = 0
    # elif len(tmp) > 0:
    #     producers = get_person(tmp, option)
    # else:
    #     producers = get_person(tmp2, option)
"""


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

    book = is_based(doc)
    global j
    if book:
        g.add((rdflib.URIRef(movie[2]), rdflib.URIRef(URI_PATH + "based_on"), rdflib.URIRef(URI_PATH + "book")))
        print(j)
    j += 1


"""
    cell = infobox.xpath("//tr[contains(.,'Directed')]/td")
    if len(cell) == 1:
        cell = cell[0]
        # tmp = infobox.xpath("//tr[contains(.,'Directed')]/td//li")
        tmp = infobox.xpath("//li")
        tmp2 = infobox.xpath("//br")
        option = 1
        if len(tmp) == 0 and len(tmp2) == 0:
            # tmp = infobox.xpath("//tr[contains(.,'Directed')]/td/a")[0]
            tmp = infobox.xpath("/a")[0]
            option = 0
        # elif len(tmp) > 0:
        #     directors = get_person(tmp, option)
        # else:
        #     directors = get_person(tmp2, option)
        # directors = get_person(tmp, option)  # get [name,link]
    else:
        directors = []
    cell = infobox.xpath("//tr[contains(.,'Produced')]/td")
    if len(cell) == 1:
        cell = cell[0]
        tmp = infobox.xpath("//tr[contains(.,'Produced')]/td//li")
        tmp2 = infobox.xpath("//tr[contains(.,'Produced')]/td//br")
        option = 1
        if len(tmp) == 0 and len(tmp2) == 0:
            tmp = infobox.xpath("//tr[contains(.,'Produced')]/td/a")
            if len(tmp) > 0:
                tmp = tmp[0]
            else:
                return
                # need to add something for one person without link
            # tmp = infobox.xpath("//tr[contains(.,'Produced')]/td/a")[0]
            option = 0
        # elif len(tmp) > 0:
        #     producers = get_person(tmp, option)
        # else:
        #     producers = get_person(tmp2, option)
    else:
        producers = []
"""


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


def main():
    create_ontology()
    g.serialize("ontology.nt", format="nt")


if __name__ == "__main__":
    main()
