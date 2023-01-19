#!/bin/python
from flask import Flask, render_template, request
import requests
import json 
app = Flask(__name__)

dictionnaire = None #va contenir le contenu json de la vidéothèque
dictionnaireRecherche = None #va contenir le contenu json de la recherche OMDB
videotheque = None #va contenir le nom du fichier de la vidéothèque
#url='http://127.0.0.1:5000' #URL du serveur contenant l'API, version locale
url='http://10.11.5.97:5000'

#page pour visualiser toutes les vidéotheques dispo
@app.route('/', methods=["GET"])
def videotheques():
    global videotheque
    #l'url sera a changer parfois
    urlLocale=url
    videotheque=json.loads(requests.get(urlLocale).content)
    return render_template('videotheques.html',videotheque=videotheque)

#pages d'index pour visualiser le contenu dans la videothèque selectionné
@app.route('/index',methods=["GET","POST"])
def index():
    global dictionnaire
    global videotheque
    urlLocale=url+'/videotheque'
    if(request.method=="POST"):
        videotheque=request.form.get('submit_data')
        dictionnaire=json.loads(requests.get(urlLocale,data={"nameVideo":videotheque}).content)
    return render_template('index.html', dictionnaire=dictionnaire)

#sera appelé à chaque ajout de film 
@app.route('/addMovie')
def addMovie():
    #ajout d'un film dans la bibliothèque
    return render_template('ajoutFilmOMDB.html')
#sera appelé à chaque ajout de film manuellement
@app.route('/addMovieManuel')
def addMovieManuel():
    #ajout d'un film manuellement dans la bibliothèque
    return render_template('ajoutFilmManuellement.html')
@app.route('/addMovieManuelValidate',methods=["GET","POST"])
def addMovieManuelValidate():
    global dictionnaire
    if(request.method=="POST"):
        title=request.form.get('title')
        date=request.form.get('date')
        
        directorN=request.form.get('directorN')
        directorP=request.form.get('directorP')
        actorN1=request.form.get('actorN1')
        actorP1=request.form.get('actorP1')
        actorN2=request.form.get('actorN2')
        actorP2=request.form.get('actorP2')
        actorN3=request.form.get('actorN3')
        actorP3=request.form.get('actorP3')
        actorN4=request.form.get('actorN4')
        actorP4=request.form.get('actorP4')
        actorN5=request.form.get('actorN5')
        actorP5=request.form.get('actorP5')

        note=request.form.get('note')
        imgUrl=request.form.get('imgUrl')
        synopsis=request.form.get('synopsis')
        
        urlLocale=url+'/videotheque/ajoutManuel'
        
        donnees={"nameVideo":videotheque,"title":title,"date":date,
        "director":{"name":directorN,"surname":directorP},
        "actors":[{"name":actorN1,"surname":actorP1},
            {"name":actorN2,"surname":actorP2},
            {"name":actorN3,"surname":actorP3},
            {"name":actorN4,"surname":actorP4},
            {"name":actorN5,"surname":actorP5}],
        "note":note,"imgUrl":imgUrl,"synopsis":synopsis}
        donnees['actors'] = list(donnees['actors'])
        headers = {"Content-Type": "application/json; charset=utf-8"}
        r=requests.post(urlLocale,headers=headers,json=donnees)

        urlLocale=url+'/videotheque'
        dictionnaire=json.loads(requests.get(urlLocale,data={"nameVideo":videotheque}).content)

    return render_template('index.html', dictionnaire=dictionnaire)

#affichage d'un film à partir des infos du fichier videotheque
@app.route('/showMovie')
def showMovie():
    global dictionnaire
    movie = str(request.args['submit_data'])
    for item in dictionnaire["films"]:
        if (item["title"] == movie):
            title = item["title"]
            director = item["director"]  
            synopsis = item["synopsis"]
            actors = item["actors"] 
            imgUrl = item["imgUrl"]
            date = item["date"]
            note = item["note"]   
            #Sending data
            return render_template('showmovie.html',title=title,director=director,synopsis=synopsis, actors=actors,imgUrl=imgUrl,date=date,note=note)
        else:
            print("Passage au film suivant...")
    return render_template('index.html',dictionnaire=dictionnaire)
#chercher des informations sur un film
@app.route('/searchMovie',methods=["GET","POST"])
def searchMovie():
    global dictionnaireRecherche
    if(request.method=="POST"):
        title=request.form.get('submit_data')
        urlLocale=url+'/videotheque/recherche'
        donnees={"nameVideo":videotheque,"title":title}
        headers = {"Content-Type": "application/json; charset=utf-8"}
        dictionnaireRecherche=json.loads(requests.post(urlLocale,json=donnees).content)
    return render_template('showSearchMovie.html', dictionnaireRecherche=dictionnaireRecherche)

@app.route('/showMovieRecherche',methods=["GET","POST"])
def showMovieRecherche():
    global dictionnaireRecherche
    global dictionnaire
    movie = str(request.args['submit_data'])
    for item in dictionnaireRecherche:
        if("title" in item):
            if (item["title"] == movie):
                title = item["title"]
                director = item["director"]  
                synopsis = item["synopsis"]
                actors = item["actors"] 
                imgUrl = item["imgUrl"]
                date = item["date"]
                note = item["note"]   
                #Sending data
                return render_template('showSearchMovieDetail.html',item=item,title=title,director=director,synopsis=synopsis, actors=actors,imgUrl=imgUrl,date=date,note=note)
            else:
                print("Passage au film suivant...")
    dictionnaireRecherche=None #remise à 0 nécessaire si rien trouvé
    return render_template('alerte.html',dictionnaire=dictionnaire)

@app.route('/addMovieOMDB',methods=["POST","GET"])
def addMovieOMDB():
    global dictionnaire
    global dictionnaireRecherche
    if(request.method=="POST"):
        title=request.form.get('title')
        date=request.form.get('date')
        urlLocale=url+'/videotheque/info'
        nameVideo=videotheque
        r=requests.post(urlLocale,data={"nameVideo":nameVideo,"nameFilm":title,"date":date})
        if(r.json()["titre"]=="NONE"):
            return render_template('alerte.html',dictionnaire=dictionnaire)
    if(request.method=="GET"):
        #on va utiliser une requête put pour contacter l'api
        movie = request.args['submit_data']
        urlLocale=url+'/videotheque/info'
        donnees={"nameVideo":videotheque,"movie":eval(movie)}
        headers = {"Content-Type": "application/json; charset=utf-8"}
        r=requests.put(urlLocale,headers=headers,json=donnees)
    urlLocale=url+'/videotheque'
    dictionnaire=json.loads(requests.get(urlLocale,data={"nameVideo":videotheque}).content)
    dictionnaireRecherche=None #remise à 0 nécessaire
    return render_template('index.html', dictionnaire=dictionnaire)

#supprimer un film de la vidéothèque
@app.route('/deleteMovie',methods=["GET","DELETE"])
def deleteMovie():
    global dictionnaire
    movie = str(request.args['submit_data'])
    urlLocale=url+'/videotheque/info'
    nameVideo=videotheque
    requests.delete(urlLocale,data={"nameVideo":nameVideo,"nameFilm":movie})

    urlLocale=url+'/videotheque'
    dictionnaire=json.loads(requests.get(urlLocale,data={"nameVideo":videotheque}).content)
    return render_template('index.html', dictionnaire=dictionnaire)
#ajouter une vidéothèque
@app.route('/addVideotheque')
def addVideotheque():
    return render_template('ajoutVideotheque.html')

@app.route('/addVideothequeValidate',methods=["GET","POST"])
def addVideothequeValidate():
    global videotheque
    if(request.method=="POST"):
        title=request.form.get('title')
        propN=request.form.get('propN')
        propP=request.form.get('propP')
        login=request.form.get('login')
        password=request.form.get('password')
        donnees={"title":title,"propN":propN,"propP":propP,"login":login,"password":password}
        headers = {"Content-Type": "application/json; charset=utf-8"}
        urlLocale=url
        r=requests.post(urlLocale,headers=headers,json=donnees)
    #l'url sera a changer parfois
    urlLocale=url
    videotheque=json.loads(requests.get(urlLocale).content)
    return render_template('videotheques.html',videotheque=videotheque)

#supprimer une vidéothèque
@app.route('/deleteVideotheque')
def deleteVideotheque():
    global dictionnaire
    global videotheque
    videotheque ={'nomFichier': str(request.args['submit_data'])}
    headers = {"Content-Type": "application/json; charset=utf-8"}
    urlLocale=url
    r=requests.delete(urlLocale,headers=headers,json=videotheque)
    
    urlLocale=url
    videotheque=json.loads(requests.get(urlLocale).content)
    return render_template('videotheques.html',videotheque=videotheque)

#modifier un film
@app.route('/modifyMovie')
def modifyMovie():
    global dictionnaire
    movie = str(request.args['submit_data'])
    for item in dictionnaire["films"]:
        if (item["title"] == movie):
            title = item["title"]
            director = item['director']  
            synopsis = item['synopsis']
            actors = item['actors'] 
            imgUrl = item['imgUrl']
            date = item['date']
            note = item['note']   
            #Sending data
            return render_template('modifymovie.html',title=title,director=director,synopsis=synopsis, actors=actors,imgUrl=imgUrl,date=date,note=note)
    return "TODO"
@app.route('/modifyMovieValidate',methods=["POST"])
def modifyMovieValidate():
    global dictionnaire
    if(request.method=="POST"):
        title=request.form.get('title')
        date=request.form.get('date')
        directorN=request.form.get('directorN')
        directorP=request.form.get('directorP')
        actorN1=request.form.get('actorN1')
        actorP1=request.form.get('actorP1')
        actorN2=request.form.get('actorN2')
        actorP2=request.form.get('actorP2')
        actorN3=request.form.get('actorN3')
        actorP3=request.form.get('actorP3')
        actorN4=request.form.get('actorN4')
        actorP4=request.form.get('actorP4')
        actorN5=request.form.get('actorN5')
        actorP5=request.form.get('actorP5')

        note=request.form.get('note')
        imgUrl=request.form.get('imgUrl')
        synopsis=request.form.get('synopsis')
        
        urlLocale=url+'/videotheque/modification'
        
        donnees={"nameVideo":videotheque,"title":title,"date":date,
        "director":{"name":directorN,"surname":directorP},
        "actors":[{"name":actorN1,"surname":actorP1},
            {"name":actorN2,"surname":actorP2},
            {"name":actorN3,"surname":actorP3},
            {"name":actorN4,"surname":actorP4},
            {"name":actorN5,"surname":actorP5}],
        "note":note,"imgUrl":imgUrl,"synopsis":synopsis}
        donnees['actors'] = list(donnees['actors'])
        headers = {"Content-Type": "application/json; charset=utf-8"}
        r=requests.post(urlLocale,headers=headers,json=donnees)
    
    urlLocale=url+'/videotheque'
    dictionnaire=json.loads(requests.get(urlLocale,data={"nameVideo":videotheque}).content)
    return render_template('index.html', dictionnaire=dictionnaire)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8000', debug=True)