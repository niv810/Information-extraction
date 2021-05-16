import rdflib
import requests
import lxml.html

url = "https://en.wikipedia.org/wiki/List_of_Academy_Award-winning_films"
g = rdflib.Graph()
prefix = "https://en.wikipedia.org"
URI_PATH = "http://example.org/"  # for ontology prefix
counter = 0


def create_ontology():
    res = requests.get(url)
    doc = lxml.html.fromstring(res.content)
    films(doc)

    # infobox = doc.xpath("//table[contains(@class, 'infobox')]")


def get_person(people, option):  # 0 - one person, 1 - more than one
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


def is_based(movie):
    res = movie.xpath("//tr[contains(.,'Based')]")
    if len(res) > 0:
        global counter
        counter += 1
        return 1
    return 0


def add_movie(movie):
    res = requests.get(movie[1])
    doc = lxml.html.fromstring(res.content)
    infobox = doc.xpath("//table[contains(@class, 'infobox')]/tbody")[0]
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
    book = is_based(infobox)
    print("yes")


def films(page):
    table = page.xpath("//table")[0]
    movies = table.xpath("./tbody//tr[td[2]//text()>=2010]//td[1]//a")
    for i in range(0, len(movies)):
        name = (movies[i].xpath("./@href")[0])[6:].replace("_", " ")
        uri = URI_PATH + name
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
