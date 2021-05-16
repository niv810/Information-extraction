import rdflib
import requests
import lxml.html

url = "https://en.wikipedia.org/wiki/List_of_Academy_Award-winning_films"
g = rdflib.Graph()
prefix = "https://en.wikipedia.org"
URI_PATH = "http://example.org/"  # for ontology prefix


def create_ontology():
    res = requests.get(url)
    doc = lxml.html.fromstring(res.content)
    films(doc)

    # infobox = doc.xpath("//table[contains(@class, 'infobox')]")


def get_people(people):
    name = people.xpath("./text()")[0]
    link = prefix + people.xpath("./@href")[0]
    return [name, link]


def get_movie_details(movie):
    res = requests.get(movie[1])
    doc = lxml.html.fromstring(res.content)
    infobox = doc.xpath("//table[contains(@class, 'infobox')]/tbody")
    directors = get_people(infobox.xpath("//tr[contains(.,'Directed')]/td/a"))  # get [name,link]
    producers = get_people(infobox.xpath("//tr[contains(.,'Produced')]/td/a"))


def films(page):
    table = page.xpath("//table")[0]
    movies = table.xpath("./tbody//tr[td[2]//text()>=2010]//td[1]//a")
    for i in range(0, len(movies)):
        name = movies[i].xpath("./text()")[0]
        link = prefix + movies[i].xpath("./@href")[0]
        movies[i] = [name, link]
    for i in range(0, len(movies)):
        get_movie_details(movies[i])

    # //table//th/text()[contains(.,'Film')]
    # //table[.//th//text()[contains(.,'Film')]]
    # //table[//th[contains(.,'Film')]]//tr//td[2]//a[1]//text()
    print(movies)
    print(len(movies))


def main():
    create_ontology()
    g.serialize("ontology.nt", format="nt")


if __name__ == "__main__":
    main()
