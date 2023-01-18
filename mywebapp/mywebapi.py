#!\bin\python3
from flask import Flask, request
from flask_restful import Resource, Api, abort, reqparse

import json,omdb
import ast #pour la conversion de string à dict
import datetime #pour la date de modif
import os #pour la suppression et le listing
from os import listdir #pour lister les videotheque présente

app = Flask(__name__)


#OK classe de l'Acteur
class Acteur:
    #définition de la classe acteur
    def __init__(self,name,surname):
        self.name=name
        self.surname=surname

    def afficherActor(self):
        print("\t",self.name," ",self.surname)

#OK classe du director
class Director:
 #définition de la classe directeur
    def __init__(self,name,surname):
        self.name=name
        self.surname=surname

    def afficherDirector(self):
        print("\t",self.name," ",self.surname)
  
#OK classe du film
class Film:
    #Définition de la classe film (titre, director, imgUrl, date, acteurs)
    def __init__(self,title,director,imgUrl,date,actors,synopsis,note):
        self.title=title
        self.director=director
        self.imgUrl=imgUrl
        self.date=date
        self.actors=actors
        self.synopsis=synopsis
        self.note=note
    
    #affichage
    def afficherFilm(self):
        print("Title :",self.title,"\nDirector :")
        self.director.afficherDirector()
        print("Date :",self.date,"\nActors :")
        acteur=self.actors
        for actor in acteur:
            actor.afficherActor() 
        print("Synopsis :",self.synopsis,"\nNote :",self.note)

#Ok classe du proprio de la videotheque
class Prop:
    #definition du proprio de la vidéothèque
    def __init__(self,*args):
        # si 5 arguments videotheque,name,surname,login,password
        if len(args)==5:
            self.videotheque=args[0]
            self.name=args[1]
            self.surname=args[2]
            self.login=args[3]
            self.password=args[4]
        # si un argument, on a donné un fichier json en entrée #obselete
        elif len(args)==1:
            with open(args[0]) as datajson:
                proprio = json.load (datajson)
            datajson.close()
            self.name=proprio["name"]
            self.surname=proprio["surname"]
            self.videotheque=proprio["videotheque"]
            self.login=proprio["login"]
            self.password=proprio["password"]      

    def setLogin(self,login):
        self.login=login
    
    def setPassword(self,password):
        self.password=password
    
    def creerProprioJson(self,fichier):
        proprio={"videotheque":self.videotheque,
            "name":self.name,
            "surname":self.surname,
            "login":self.login,
            "password":self.password}
        #Il faut vérifier que le fichier existe, sinon on le créer
        with open(fichier,'w') as outfile:
            json.dump(proprio,outfile)
        outfile.close()

    def afficherProprio(self):
        print("La videothèque ",self.videotheque," appartient à ",self.name," ",self.surname)

    def connexionProprio(self,login,password):
        if(self.login==login and self.password==password):
            return("Connexion réussie")
        else:
            return("Login ou mot de passe incorrect.")

#ajout du film dans le fichier spécifié
def ajoutFilmJson(fichier, film):
    with open(fichier) as datajson:
        films = json.load (datajson)
    datajson.close()
    filmJson={
        "title":film.title,
        "imgUrl":film.imgUrl,
        "date":film.date,
        "note":film.note,
        "synopsis":film.synopsis}
    director=Director(film.director.name,film.director.surname)
    directorJson={
        "name":director.name,
        "surname":director.surname
    }
    ActeursJson=[{"name":acteur.name,"surname":acteur.surname} for acteur in film.actors] #concaténation de dictionnaire Json
    filmJson["actors"]=ActeursJson
    filmJson["director"]=directorJson
    films["films"].append(filmJson)
    dateDuJour=datetime.date.today()
    films["lastModif"]=str(dateDuJour.day)+"/"+str(dateDuJour.month)+"/"+str(dateDuJour.year)
    with open(fichier,'w') as outfile:
        json.dump(films,outfile)
    outfile.close()

#vider une vidéotheque : utile pour la recherche
def viderVideotheque(fichier):
    films={"films":[], "lastModif": "", "proprietaire": {"login": "", "name": "", "password": "", "surname": "", "videotheque": "rechercheOMDB"}}
    with open(fichier,'w') as outfile:
        json.dump(films,outfile)
    outfile.close()

#booléen : retourne vrai ou faux, si le titre correspond au titre du film donné en paramètre #OBSELETE
def getFilm(valueSearch,film):
    if(film["title"] == valueSearch):
        return True
    return False

#supprimerFilmJson(fichier,film) pour supprimer un film du fichier json considéré
def supprimerFilmJson(fichier, film):
    with open(fichier) as datajson:
        films = json.load (datajson)
    datajson.close()
    #recherche du film dans le fichier, puis suppression s'il est présent
    k=len(films["films"])-1 #on récupère la taille de la vidéothèque
    i=0
    while i<=k:
        filmJson=films["films"][i]
        if(getFilm(film,filmJson)):
            #suppression du film
            print("Suppression du film : ",film)
            filmJson.clear()
            del(films["films"][i]) #nécessaire pour vider le fichier Json : enlever les éléments vides du tableau de dictionnaire
            i-=1
            k-=1
        i+=1
    dateDuJour=datetime.date.today()
    films["lastModif"]=str(dateDuJour.day)+"/"+str(dateDuJour.month)+"/"+str(dateDuJour.year)
    with open(fichier,'w') as outfile:
       json.dump(films,outfile)
    outfile.close()

def modificationFilmJson(fichier,film):
    with open(fichier) as datajson:
        films = json.load (datajson)
    datajson.close()
    #recherche du film dans le fichier, puis suppression s'il est présent
    k=len(films["films"])-1 #on récupère la taille de la vidéothèque
    i=0
    while i<=k:
        filmJson=films["films"][i]
        if(getFilm(film.title,filmJson)):
            #modification du film
            print("Modification du film : ",film)
            filmJson["note"]=film.note
            filmJson["synopsis"]=film.synopsis
            filmJson["actors"]=[]
            for act in film.actors:
                filmJson["actors"].append({"name":act.name,"surname":act.surname})
            filmJson["director"]={"name":film.director.name,"surname":film.director.surname}
            filmJson["date"]=film.date
            filmJson["imgUrl"]=film.imgUrl
            i-=1
            k-=1
        i+=1
    dateDuJour=datetime.date.today()
    films["lastModif"]=str(dateDuJour.day)+"/"+str(dateDuJour.month)+"/"+str(dateDuJour.year)
    with open(fichier,'w') as outfile:
       json.dump(films,outfile)
    outfile.close()

#rechercherFilmJson(fichier,title)
def rechercherFilm(fichier,valueSearch):
    with open(fichier) as datajson:
        films = json.load (datajson)
    datajson.close()
    #recherche du film dans le fichier, puis suppression s'il est présent
    films=films["films"]
    for film in films:
        acteurClasse=[Acteur(acteur["name"],acteur["surname"]) for acteur in film["actors"]]
        directorClasse=Director(film["director"]["name"],film["director"]["surname"])
        filmClasse=Film(film["title"],directorClasse,film["imgUrl"],film["date"],acteurClasse,film["synopsis"],film["note"])
        if(getFilm(valueSearch,film)):
            print("Film ",valueSearch ," trouvé")
            return True
    print("Film ",valueSearch ," non trouvé")
    return False


#afficher le contenu du fichier Json videotheque
def afficherJson(fichier):
    #affichage du contenu du fichier Json
    with open(fichier) as datajson:
        videotheque = json.load (datajson)
    datajson.close()
    #donnee proprio
    nomVideotheque=videotheque["proprietaire"]["videotheque"]
    nomProprio=videotheque["proprietaire"]["name"]
    prenomProprio=videotheque["proprietaire"]["surname"]
    loginProprio=videotheque["proprietaire"]["login"]
    passwordProprio=videotheque["proprietaire"]["password"]
    proprio=Prop(nomVideotheque,nomProprio,prenomProprio,loginProprio,passwordProprio)
    #proprio.afficherProprio()
    #last modif
    lastModif=videotheque["lastModif"]
    #print("Dernière modification :",lastModif)
    #nb de film
    nbFilm=len(videotheque["films"])
    #print("La vidéothèque possède ",nbFilm," films.")
    #donnee film
    for film in videotheque["films"]:
        filmClasse=Film(film["title"],film["director"],film["imgUrl"],film["date"],film["actors"],film["synopsis"],film["note"])
        #filmClasse.afficherFilm()
        #print("\n")
    return videotheque

#creer une vidéotheque vierge, à partir d'un propriétaire
def creerVideotheque(fichier,proprio):
    fichierJson=open(fichier,"w+")
    #dictionnaire pour json
    dateDuJour=datetime.date.today()
    contenuJson={
        "proprietaire":
        {
            "login": proprio.login,
            "name": proprio.name,
            "password": proprio.password,
            "surname": proprio.surname,
            "videotheque": proprio.videotheque
        },
        "lastModif":str(dateDuJour.day)+"/"+str(dateDuJour.month)+"/"+str(dateDuJour.year),
        "films":[]
    }
    json.dump(contenuJson,fichierJson)
    fichierJson.close()

#supprime une vidéotheque
def supprimerVideotheque(fichier):
    os.remove(fichier)

#affiche toutes les vidéothèques disponible dans le dossier indiqué
def afficherVideothequePresente(dossier):
    videothequeJson={}
    for file in listdir(dossier):
        ext = os.path.splitext(file)[1]
        if(ext==".json"):
            fichier=dossier+"/"+file
            with open(fichier) as datajson:
                videotheque = json.load (datajson)
            datajson.close()
            nomVideotheque=videotheque["proprietaire"]["videotheque"]
            nomProprio=videotheque["proprietaire"]["name"]
            prenomProprio=videotheque["proprietaire"]["surname"]
            #print("La videothèque ",nomVideotheque," appartient à ",nomProprio," ",prenomProprio)
            videothequeJson[os.path.splitext(file)[0]]={
                "videotheque":nomVideotheque,
                "proprietaire":{
                    "name":nomProprio,
                    "surname":prenomProprio
                }
            }
    #print(videothequeJson)
    return videothequeJson

def recupFichierVideothequePrecise(videoNameFichier,dossier):
    fichier=dossier+"/"+videoNameFichier+".json"
    videotheque={}
    with open(fichier) as datajson:
        videotheque = json.load (datajson)
    if(videotheque=={}):
        return False
    else:
        return videotheque


############################### PARTIE API SERVEUR ##########################
#récupère tous les noms des vidéothèques présentes sur le serveur
dossier="videotheque"
fichierRechercheTMP="recherche/rechercheTMP.json"
videotheque = afficherVideothequePresente(dossier)

def abort_if_videotheque_doesnt_exist(nameVideo):
    if nameVideo not in videotheque:
        abort(404, message="Videotheque {} doesn't exist".format(nameVideo))
    else:
        return videotheque[nameVideo]

def abort_if_videotheque_exist(nameVideo):
    if nameVideo in videotheque:
        abort(404, message="Videotheque {} already exist".format(nameVideo))
    else:
        return "Can create"

def listFilmVideotheque(nameVideo):
    abort_if_videotheque_doesnt_exist(nameVideo)
    videoName=recupFichierVideothequePrecise(nameVideo,dossier)
    films=videoName["films"]
    listeFilm=[]
    for film in films:
        listeFilm.append(film["title"])
    return listeFilm

def abort_if_film_doesnt_exist(nameVideo,nameFilm):
    films=listFilmVideotheque(nameVideo)
    if nameFilm not in films:
        abort(404, message="Film {} doesn't exist in Videotheque {}".format(nameFilm, nameVideo))
    else:
        fichier=dossier+"/"+nameVideo+".json"
        with open(fichier) as datajson:
            videotheque = json.load (datajson)
        datajson.close()
        infoFilm=videotheque["films"]
        for i in range(0,len(infoFilm)):
            if(infoFilm[i]["title"]==nameFilm):
                return infoFilm[i]
        return None

#curl http://localhost:5000
class AllVideotheque(Resource):
    #afficher toutes les vidéothèques présentes sur le serveur
    #possibilité d'ajouter une vidéothèque
    def get(self):
        videotheque = afficherVideothequePresente(dossier)
        return videotheque
    def post(self):
        donnees=request.get_json()
        #recup chaque élément
        title=donnees['title']
        abort_if_videotheque_exist(title)
        propP=donnees['propP']
        propN=donnees['propN']
        login=donnees['login']
        password=donnees['password']
        proprioClasse=Prop(title,propP,propN,login,password)
        listeFichier=os.listdir(dossier)
        entiers=[]
        for fichier in listeFichier:
            fichierNom=os.path.basename(fichier)
            entier=fichierNom.strip('.json').strip('videotheque')
            entiers.append(int(entier))
        entier=max(entiers)+1
        fichier=dossier+'/'+'videotheque'+str(entier)+'.json'
        creerVideotheque(fichier,proprioClasse)
    def delete(self):
        donnees=request.get_json()
        videoName=dossier+'/'+donnees["nomFichier"]+'.json'
        supprimerVideotheque(videoName)

#pour l'ajout d'argument en requete
#curl -X GET "http://localhost:5000/videotheque" -d "nameVideo=videotheque3"
class Videotheque(Resource):
    #obtenir une vidéotheque complète
    def get(self):
        nameVideo=request.form['nameVideo']
        videoName=abort_if_videotheque_doesnt_exist(nameVideo)
        fichier=dossier+"/"+nameVideo+".json"
        with open(fichier) as datajson:
            videotheque = json.load (datajson)
        datajson.close()
        return videotheque

#curl -X DELETE "http://localhost:5000/videotheque/info" -d "nameVideo=videotheque&nameFilm=Le Secret des poignards volant"
#curl -X GET "http://localhost:5000/videotheque/info" -d "nameVideo=videotheque"
#curl -X POST "http://localhost:5000/videotheque/info" -d "nameVideo=videotheque&nameFilm=Alien 2&date=1980"
omdb.set_default('apikey', '93b650b') #api gabi:8be17a6b greg:93b650b
class FilmVideotheque(Resource):   
    #get tous les films de la bibliotheque
    def get(self):
        nameVideo=request.form['nameVideo']
        videoName=abort_if_videotheque_doesnt_exist(nameVideo)
        listFilm=listFilmVideotheque(nameVideo)
        return listFilm
    #post film dans une vidéotheque
    def post(self):
        nameVideo=request.form['nameVideo']
        videoName=abort_if_videotheque_doesnt_exist(nameVideo)
        nameFilm=request.form['nameFilm']
        #on doit faire travailler l'api OMDB
        #Get data back from webpage
        date = str(request.form['date'])
        #Query to the database
        data = omdb.get(title=nameFilm,year=date,fullplot=True, tomatoes=True)
        print(data)
        #Getting data
        if(data=={}):
            return({"titre":"NONE"})
        title = data['title']
        #il peut y avoir plusieurs réalisateur, et il faut les séparer, prendre le premier, puis séparer nom/prénoms
        if('director' in data):
            director = data['director'].split(',')[0].split(' ')
            directorClasse=Director(director[0],director[1])
        else: directorClasse=Director("","")

        if('plot' in data): synopsis = data['plot']
        else : synopsis = ''
            
        if('actors' in data):
            actors = data['actors'].split(',')
            actorsClasse=[]
            for act in actors:
                act=act.lstrip()#pour supprimer les espaces en début et en fin de châine
                name=act.split(' ')[0]
                surname=act.split(' ')[1]
                actorsClasse.append(Acteur(name,surname))
        else :actorsClasse=[]

        if('poster' in data):imgUrl = data['poster']
        else:imgUrl=''

        if('year' in data):date = data['year'] 
        else:date=''

        if('ratings' in data):note = data['ratings'][0]['value']
        else : note=''
        film=Film(title,directorClasse,imgUrl,date,actorsClasse,synopsis,note)
        ajoutFilmJson(dossier+'/'+nameVideo+'.json',film)
        return({"titre":"OK"})
    #delete un film dans une vidéotheque
    def delete(self):
        nameVideo=request.form['nameVideo']
        videoName=abort_if_videotheque_doesnt_exist(nameVideo)
        nameFilm=request.form['nameFilm']
        filmName=abort_if_film_doesnt_exist(nameVideo,nameFilm)
        supprimerFilmJson(dossier+'/'+nameVideo+'.json',nameFilm)
        return "Suppression effectuée"
    def put(self):
        #on utilise put pour l'ajout
        donnees=request.get_json()
        nameVideo=donnees["nameVideo"]
        videoName=abort_if_videotheque_doesnt_exist(nameVideo)
        movie=donnees["movie"]
        title=movie["title"]
        directorClasse=Director(movie["director"]["name"],movie["director"]["surname"])
        imgUrl=movie["imgUrl"]
        date=movie["date"]
        synopsis=movie["synopsis"]
        note=movie["note"]
        actorsClasse=[]
        for act in movie["actors"]:
            actorsClasse.append(Acteur(act["name"],act["surname"]))
        film=Film(title,directorClasse,imgUrl,date,actorsClasse,synopsis,note)
        ajoutFilmJson(dossier+"/"+nameVideo+".json",film)
        return({"titre":"OK"})

#Ajouter manuellement un film dans le json (Si OMDB ne renvoit rien)
#curl -X POST "http://localhost:5000/videotheque/ajoutManuel" -d "nameVideo=videotheque&title=testFilm&date=2022&actors={\"name\":\"Alphonse\",\"surname\":\"Daudet\"}&actors={\"name\":\"Bernard\",\"surname\":\"Henry\"}&director={\"name\":\"André\",\"surname\":\"Rieux\"}&imgUrl=&note=&synopsis="
class AjoutVideothequeManuel(Resource):
    def post(self):
        #récupération des données en json
        donnees=request.get_json()
        #recup chaque élément
        nameVideo=donnees['nameVideo']
        videoName=abort_if_videotheque_doesnt_exist(nameVideo)
        title=donnees['title']
        #gestion des acteurs
        actors=donnees['actors']#5 maximum
        actorClasse=[]
        for act in actors:
            name=act["name"]
            surname=act["surname"]
            actorClasse.append(Acteur(name,surname))
        #gestion du réalisateur
        director=donnees['director']
        name=director["name"]
        surname=director["surname"]
        directorClass=Director(name,surname)
        #gestion des autres éléments
        date = str(donnees['date'])
        imgUrl=donnees['imgUrl']#potentiellement vide
        note=donnees['note']
        synopsis=donnees['synopsis']
        #l'utilisateur n'aura pas forcément tout indiquer, mais la requête sera complète
        film=Film(title,directorClass,imgUrl,date,actorClasse,synopsis,note)
        film.afficherFilm()
        ajoutFilmJson(dossier+"/"+nameVideo+".json",film)
        return "Film "+title+" ajouté"

class ModificationFilm(Resource):
    def post(self):
        #récupération des données en json
        donnees=request.get_json()
        #recup chaque élément
        nameVideo=donnees['nameVideo']
        videoName=abort_if_videotheque_doesnt_exist(nameVideo)
        title=donnees['title']
        #gestion des acteurs
        actors=donnees['actors']#5 maximum
        actorClasse=[]
        for act in actors:
            name=act["name"]
            surname=act["surname"]
            actorClasse.append(Acteur(name,surname))
        #gestion du réalisateur
        director=donnees['director']
        name=director["name"]
        surname=director["surname"]
        directorClass=Director(name,surname)
        #gestion des autres éléments
        date = str(donnees['date'])
        imgUrl=donnees['imgUrl']#potentiellement vide
        note=donnees['note']
        synopsis=donnees['synopsis']
        #l'utilisateur n'aura pas forcément tout indiquer, mais la requête sera complète
        filmModif=Film(title,directorClass,imgUrl,date,actorClasse,synopsis,note)
        filmModif.afficherFilm()
        modificationFilmJson(dossier+"/"+nameVideo+".json",filmModif)
        return "Film "+title+" modifié"

class RechercheFilm(Resource):
    def post(self):
        #récupération des données en json
        donnees=request.get_json()
        #recup chaque élément
        nameVideo=donnees['nameVideo']
        videoName=abort_if_videotheque_doesnt_exist(nameVideo)
        title=donnees['title']
        datas = omdb.search(title,fullplot=True, tomatoes=True)
        print(datas)
        #Getting data
        if(datas==[]):
            return({"titre":"NONE"})
        viderVideotheque(fichierRechercheTMP)
        for data in datas:
            title = data['title']
            #il peut y avoir plusieurs réalisateur, et il faut les séparer, prendre le premier, puis séparer nom/prénoms
            if('director' in data):
                director = data['director'].split(',')[0].split(' ')
                directorClasse=Director(director[0],director[1])
            else: directorClasse=Director("","")
            
            if('plot' in data): synopsis = data['plot']
            else : synopsis = ''
            if('actors' in data):
                actors = data['actors'].split(',')
                actorsClasse=[]
                for act in actors:
                    act=act.lstrip()#pour supprimer les espaces en début et en fin de châine
                    name=act.split(' ')[0]
                    surname=act.split(' ')[1]
                    actorsClasse.append(Acteur(name,surname))
            else :actorsClasse=[]

            if('poster' in data):imgUrl = data['poster']
            else:imgUrl=''

            if('year' in data):date = data['year'] 
            else:date=''

            if('ratings' in data):note = data['ratings'][0]['value']
            else : note=''

            film=Film(title,directorClasse,imgUrl,date,actorsClasse,synopsis,note)
            ajoutFilmJson(fichierRechercheTMP,film)
        videotheque={}
        with open(fichierRechercheTMP) as datajson:
            videotheque = json.load (datajson)
        if(videotheque=={}):
            return False
        else:
            films=videotheque["films"]
            listeFilm=[]
            for film in films:
                listeFilm.append(film)
            return listeFilm

api = Api(app)
api.add_resource(AllVideotheque, '/')
api.add_resource(Videotheque, '/videotheque')
api.add_resource(FilmVideotheque,'/videotheque/info')
api.add_resource(AjoutVideothequeManuel,'/videotheque/ajoutManuel')
api.add_resource(ModificationFilm, '/videotheque/modification')
api.add_resource(RechercheFilm,'/videotheque/recherche')

#main
if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000')
