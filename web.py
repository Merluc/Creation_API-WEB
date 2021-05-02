from bottle import route, request, run
from requests import get

server_ip = 'localhost'
server_port = 8080


"""
Fonction qui affiche une interface graphique pour entrer un author.
"""

@route("/authors/name")
def input():
    return '''
        <form action="/authors/name" method="post">
            Authors name: <input name="s" type="text" />
            <input value="List coauthors" type="submit" />
        </form>
        '''

"""
Fonction qui appelle l'api avec l'author rentré pour obtenir la liste des coauthors et des publications de l'author.
"""

@route("/authors/name", method='POST')
def do_input():
    s = request.forms['s']
    r1 = get(f"http://{server_ip}:{server_port}/authors/{s}/coauthors")
    r2 = get(f"http://{server_ip}:{server_port}/authors/{s}/publications")
    return f"<h1>{s} publications: <br/>{r2.text}<br/>{s} coauthors: <br/>{r1.text}</h1>"

################################################################################

"""
Fonction qui affiche une interface graphique pour entrer deux author.
"""

@route("/authors/distance")
def input2():
    return '''
        <form action="/authors/distance" method="post">
            Author origin: <input name="s" type="text" />
            Author destination: <input name="l" type="text" />
            <input value="Distance" type="submit" />
        </form>
        '''

"""
Fonction qui appelle l'api avec les deux authors entré pour obtenir la distance minimale entre ces deux authors ainsi que le parcours.
"""

@route("/authors/distance", method='POST')
def do_input2():
    s = request.forms['s']
    l = request.forms['l']
    r1 = get(f"http://{server_ip}:{server_port}/authors/{s}/distance/{l}")
    return f"<h1>{r1.text}</h1>"

run(host='localhost', port=8081)
