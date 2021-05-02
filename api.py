from bottle import *
import xml.etree.ElementTree as ET
from re import *
from lxml import etree as ET

local_input = "dblp_2019_2020.xml"

p = ET.XMLParser(recover=True)
tree = ET.parse(local_input, parser=p)
root = tree.getroot()
print(f"XML File loaded and parsed, root is {root.tag}")

################################################################################

"""
Fonction qui retourne toutes les informations de la publication id.
erreur possible:
    - titre de la publication pas trouvé

return sous forme de string
"""

@route('/publications/<id>')
def search_id(id):
    global root
    cpt = 0
    tmp = ''
    for title in root.iter('title'):
        if (id == title.text):
            for i in root[cpt]:
                tmp += i.tag + ': ' + i.text + "<br/>"
            return tmp
        cpt += 1
    abort(404, "Not found: '/publications/" + id + "'")

################################################################################

"""
Fonction qui retourne toutes les informations des limit premieres publications.(par defaut 100)
paramètres possibles:
    - start: liste les publications apres start Publications
    - count/limit: liste les count/limit publications suivantes
    - order: trie la liste des publications en fonction de order (si order:author trie en fonction du premier author)

return sous forme de string
"""
@route('/publications')
def print_publi():
    global root
    L = []
    cpt = 0
    tmp = ''
    n = 1
    i = 0
    start = 0
    count = 100
    order = ''
    param = extracte(request.query.filter)
    while i < len(param):
        if param[i] == 'start':
            start = int(param[i+1])
        elif param[i] == 'count':
            count = int(param[i+1])
        elif param[i] == 'limit':
            count = int(param[i+1])
        elif param[i] == 'order':
            order = param[i+1]
        i += 2
    for publi in root:
        if n <= start:
            n += 1
        elif count > 0:

            l = []
            for i in publi:
                l += [str(i.tag)]
                l += [str(i.text)]
            if order:
                L = tri_pub(l, L, order)
            else:
                L += [l]
            count -= 1
    for i in L:
        for y in range(len(i)-1):
            if not y%2:
                tmp += i[y] + ': ' + i[y+1] + "<br/>"
        tmp += "<br/>"
    return tmp

################################################################################

"""
Fonction qui retourne le nombre de publications et de coauthors d'un auteur name.
erreurs possibles:
    - nom de l'auteur pas trouvé

paramètres possibles:
    - start: compte le nombre de coauthors et de publications après start authors
    - count: compte le nombre de coauthors et de publications que sur count publications

return sous forme de string
"""

@route('/authors/<name>')
def search_authos(name):
    global root
    L = []
    nb = 0
    nb_co = 0
    n = 1
    i = 0
    start = 0
    count = 100
    param = extracte(request.query.filter)
    while i < len(param):
        if param[i] == 'start':
            start = int(param[i+1])
        elif param[i] == 'count':
            count = int(param[i+1])
        i += 2
    for author in root.iter('author'):
        if n <= start:
            n += 1
        elif count > 0:
            if (name == author.text):
                for i in author.getparent():
                    if (i.tag == 'author' and i.text != name):
                        if i.text not in L:
                            L += [i.text]
                            nb_co += 1
                    elif (i.tag == 'title'):
                        nb += 1
                        count -= 1

    if not nb and not nb_co:
        abort(404, "Not found: '/authors/" + name + "'")
    return 'Nombre de publications en tant que co-auteur: ' + str(nb) + '<br/><br/>Nombre de co-auteur sur ses publications: ' + str(nb_co)

################################################################################

"""
Fonction qui retourne la liste des publications d'un auteur name.
erreurs possibles:
    - nom de l'auteur pas trouvé

paramètres possibles:
    - start: liste les publications après start publications
    - count: liste que count publications
    - order: trie la liste des publications en fonction de order (si order:author trie en fonction du premier author)

return sous forme de string
"""

@route('/authors/<name>/publications')
def list_publi(name):
    global root
    L = []
    publi = ''
    n = 1
    i = 0
    start = 0
    count = 100
    order = ''
    param = extracte(request.query.filter)
    while i < len(param):
        if param[i] == 'start':
            start = int(param[i+1])
        elif param[i] == 'count':
            count = int(param[i+1])
        elif param[i] == 'order':
            order = param[i+1]
        i += 2
    for author in root.iter('title'):
        if n <= start:
            n += 1
        elif count > 0:
            l =[]
            flag = 0
            for i in author.getparent():
                l += [str(i.tag)]
                l += [str(i.text)]
                if (i.tag == 'author'):
                    if (name == i.text):
                        flag = 1
            if flag:
                if order:
                    L = tri_pub(l, L, order)
                else:
                    L += [l]
                count -= 1
    for i in L:
        for y in range(len(i)-1):
            if not y%2:
                publi += i[y] + ': ' + i[y+1] + "<br/>"
        publi += "<br/>"
    if publi == '':
        abort(404, "Not found: '/authors/" + name + "/publications'")
    return publi

################################################################################

"""
Fonction qui retourne la liste des coauthors d'un auteur name.
erreurs possibles:
    - nom de l'auteur pas trouvé

paramètres possibles:
    - start: liste les coauthors après start authors
    - count: compte que count coauthors
    - order: trie la liste des authors si order:author sinon fait rien

return sous forme de string
"""

@route('/authors/<name>/coauthors')
def list_author(name):
    global root
    co = ''
    L = []
    n = 1
    i = 0
    start = 0
    count = 100
    ford = 0
    param = extracte(request.query.filter)
    while i < len(param):
        if param[i] == 'start':
            start = int(param[i+1])
        elif param[i] == 'count':
            count = int(param[i+1])
        elif param[i] == 'order' and param[i+1] == 'author':
            ford = 1
        i += 2
    for author in root.iter('author'):
        if n <= start:
            n += 1
        elif count > 0:
            if (name == author.text):
                for i in author.getparent():
                    if (i.tag == 'author' and i.text != name):
                        if i.text not in L and count > 0:
                            if ford:
                                L = tri_lexico(str(i.text), L)
                            else:
                                L += [i.text]
                            count -= 1
    for i in L:
        co += '- ' + i + "<br/>"
    if co == '':
        abort(404, "Not found: '/authors/" + name + "/coauthors'")
    return co

################################################################################

"""
Fonction qui retourne la liste des authors contenant la chaine searchString dans leur nom.
erreurs possibles:
    - aucun auteur trouvé comportant la chaine

paramètres possibles:
    - start: liste les authors après start authors
    - count: compte que count authors
    - order: trie la liste des authors si order:author sinon fait rien

return sous forme de string
"""

@route('/search/authors/<searchString>')
def string_author(searchString):
    global root
    co = ''
    L = []
    n = 1
    i = 0
    start = 0
    count = 100
    ford = 0
    param = extracte(request.query.filter)
    while i < len(param):
        if param[i] == 'start':
            start = int(param[i+1])
        elif param[i] == 'count':
            count = int(param[i+1])
        elif param[i] == 'order' and param[i+1] == 'author':
            ford = 1
        i += 2
    for author in root.iter('author'):
        if n <= start:
            n += 1
        elif count > 0:
            if (match('.*' + str(searchString) + '.*', str(author.text), re.IGNORECASE)):
                if author.text not in L:
                    if ford:
                        L = tri_lexico(str(author.text), L)
                    else:
                        L += [author.text]
                    count -= 1
    for i in L:
        co += '- ' + i + "<br/>"
    if not L:
        abort(404, "Not found: '/search/authors/" + searchString + "'")
    return co

################################################################################

"""
Fonction qui retourne la liste des publications contenant la chaine searchString dans leur titre.
erreurs possibles:
    - aucune publication trouvé comportant la chaine

paramètres possibles:
    - start: liste les publications après start publications
    - count: compte que count publications
    - order: trie la liste des publications en fonction de order (si order:author trie en fonction du premier author)
    - journal/author/title/...: liste les publications qui contiennent aussi les chaines dans le paramètre en question. (si author:Jean, listera dans les publications corrrespondantes que celles ayant un author contenant "Jean")

return sous forme de string
"""

@route('/search/publications/<searchString>')
def string_publi(searchString):
    global root
    L = []
    publi = ''
    n = 1
    i = 0
    y = 0
    start = 0
    count = 100
    order = ''
    param = extracte(request.query.filter)
    while i < len(param):
        if param[i] == 'start':
            start = int(param[i+1])
            y += 1
        elif param[i] == 'count':
            count = int(param[i+1])
            y += 1
        elif param[i] == 'order':
            order = param[i+1]
            y += 1
        i += 2
    for titre in root.iter('title'):
        if n <= start:
            n += 1
        elif count > 0:
            l =[]
            flag2 = 0
            if (match('.*' + str(searchString) + '.*', str(titre.text), re.IGNORECASE)):
                m = 0
                flag = -y
                test = 0
                if len(param) > 1:
                    while m < len(param):
                        flag += 1
                        for i in titre.getparent():
                            if (i.tag == param[m] and i.tag != 'start' and i.tag != 'count'):
                                if (match('.*' + str(param[m+1]) + '.*', str(i.text), re.IGNORECASE)):
                                    test += 1
                        m += 2
                if flag == test:
                    for i in titre.getparent():
                        l += [str(i.tag)]
                        l += [str(i.text)]
                    if order:
                        L = tri_pub(l, L, order)
                    else:
                        L += [l]
                    count -= 1
    for i in L:
        for y in range(len(i)-1):
            if not y%2:
                publi += i[y] + ': ' + i[y+1] + "<br/>"
        publi += "<br/>"
    if publi == '':
        if len(param) > 1:
            abort(404, "Not found: '/search/publications/" + searchString + "?filter=" + request.query.filter + "'")
        else:
            abort(404, "Not found: '/search/publications/" + searchString + "'")
    return publi

################################################################################

"""
Fonction qui retourne la distance minimale entre deux auteurs et liste le chemin d'auteur.
erreurs possibles:
    - aucun chemin trouvé entre les deux auteurs fournits

return sous forme de string
"""

@route('/authors/<name_origin>/distance/<name_destination>')
def dist_author(name_origin, name_destination):
    global root
    co = ''
    Liste = root.iter('author')
    min = 9999999
    B = [name_origin]
    fait = []
    L = [name_origin]
    min, B = test(name_origin, name_destination, L, min, B, fait)
    co = 'Disance min: ' + str(min) + '<br/>'
    if len(B) == 1:
        abort(404, "Not found: '/authors/" + name_origin + "/distance/" + name_destination + "'")
    for i in B:
        co += '- ' + i + "<br/>"
    return co

################################################################################

"""
Fonction qui prend en paramètre un mot name et l'introduit dans la liste L en respectant un ordre lexicographique.
"""

def tri_lexico(name, L):
    for i in range(len(L)):
        if L[i] >= name:
            L = L[:i] + [name] + L[i:]
            return L
    L += [name]
    return L

################################################################################

"""
Fonction qui prend en paramètre une liste publi et l'introduit dans la liste L en respectant un ordre lexicographique par rapport au champ donnée order.
"""

def tri_pub(publi, L, order):
    for i in range(len(L)):
        for y in range(len(L[i])):
            flag = 0
            if L[i][y] == order:
                for x in range(len(publi)):
                    if publi[x] == order:
                        if L[i][y+1] >= publi[x+1]:
                            L = L[:i] + [publi] + L[i:]
                            return L
                        flag = 1
                        break;
            if flag:
                break;
    L += [publi]
    return L

################################################################################

"""
Fonction qui retourne la liste des coauthors de name.
"""

def get_co(name):
    global root
    tmp = []
    for author in root.iter('author'):
        if (name == author.text):
            for i in author.getparent():
                if (i.tag == 'author' and i.text != name):
                    if i.text not in tmp:
                        tmp += [i.text]
    return tmp

################################################################################

"""
Fonction récursive qui prend un parametre name qui est l'author actuel, search qui est l'author recherché,
incrémente L durant son parcours ainsi que fait tout en stockant min et B si il trouve l'author search.
Permet donc de parcourir tout les authors pour trouver un chemin.
"""

def test(name, search, L, min, B, fait):
    global root
    fait += [name]
    liste = get_co(name)
    if search in liste:
        if len(L) < min:
            min = len(L)
            B = L + [search]
            return min, B
    for author in liste:
        if author not in fait:
            liste2 = get_co(author)
            if search in liste2:
                L += [author]
                if len(L) < min:
                    min = len(L)
                    B = L + [search]
                    return min, B
                L = L[:-1]
    if len(L)>50:
        return min, B
    for author in liste:
        if author not in fait:
            L += [author]
            min, B = test(author, search, L, min, B, fait)
            fait += [author]
            if len(B) > 1:
                return min, B
            L = L[:-1]
        # else:
    return min, B

################################################################################

"""
Fonction qui retourne la liste des paramètres placés dans l'URL.
"""

def extracte(url):
    L = []
    tmp = 0
    for i in range(len(url)):
        if url[i] == ':' or url[i] == ',':
            L += [url[tmp:i]]
            tmp = i + 1
    L += [url[tmp:]]
    return L

################################################################################

run(host = 'localhost', port = 8080)
