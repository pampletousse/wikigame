# Python 3
# wikigame - sylvain loppin
from bs4 import BeautifulSoup
from tkinter import *
import urllib.request
import tkinter.font as tkFont
import sys as sys
import os as os
import copy
import subprocess as sp
import time as time
import _thread

# Classe de Lien
class Jeu():
    def __init__(self,tour):
        self.tour = 1
        self.choix = 1
        self.startItem = 1
        self.histo = [] 
        self.listeLiens = []
        self.listeBoxLiens = []
        self.score = 0
        
    def tourPlus(self):
        self.tour += 1
    
    def scorePlus(self):
        self.score += 1

    def resetJeu(self):
        self.tour = 1
        self.choix = -1
        self.startItem = 1
        self.histo = [] 
        self.listeLiens = []
        self.listeBoxLiens = []

# Classe de Jeu
class Lien():
    def __init__(self,index,nom,url):
        self.index = index
        self.nom = nom
        self.url = url

# Récupération et parsing webpage en html
def getPage(url):
    with urllib.request.urlopen(url) as response:
        webpage = response.read()
        soup = BeautifulSoup(webpage, 'html.parser')
    return soup

# Get titre de page
def getPageTitle(page):
    for title in page.find_all('h1',class_="firstHeading"):
        return title.getText()

# Set résumé de page
def setPageResume(page):
    resume = page.find('p')
    if resume.text.strip() != "":
        strResume.set(str(resume.text.strip()))

# Extract liens
def extractWebpage(soup,startItem):
        # Nettoyage
        soupp = soup.find('div',class_="mw-parser-output")
        for a in soupp.find_all('a',{'class':['extiw', 'internal','mw-redirect']}):
            a.extract()
        for div in soupp.find_all('div',{'class':['navbox-container', 'image','toc','reference-cadre']}):
            div.extract()
        for table in soupp.find_all('table',{'class':['infobox','infobox_v2','infobox_v3']}):
            table.extract()
        for sup in soupp.find_all('sup',{'class':['reference','prononciation']}):
            sup.extract()
        for portail in soupp.find_all('ul',class_="bandeau-portail"):
            portail.extract()
        for annotModif in soupp.find_all('span',class_="mw-editsection"):
            annotModif.extract()
        for bandeauEbauche in soupp.find_all('div',class_="bandeau-article"):
            bandeauEbauche.extract()
        for emptyp in soupp.find_all('p',class_="mw-empty-elt"):
            emptyp.extract()

        # mise a jour du résumé
        setPageResume(soupp)
        # Reset liste liens
        listeBoxLiens.delete(0,'end')
        jeu.listeLiens.clear()
        # Boucle extraction liens
        i = 1
        for anchor in soupp.find_all('a'):

            anchorText = str(anchor.getText())
            anchorLien = str(anchor.get("href"))

            if anchorText.strip() != '' and anchorLien[:6] == "/wiki/":
                if i >= startItem and i<= startItem+20:
                    listeBoxLiens.insert(i,str(i)+" => "+anchor.getText())
                jeu.listeLiens.append(Lien(i,anchor.getText(),anchor.get("href")))
                i += 1
        enableBtns(i)
        strResult.set(str(i-1)+" résultats")      

# Lancement du jeu -> trigger par btn
def start():
    tourJeu()
    startTimer()

def afficheVars():
    labelFrame.configure(text="Tour : "+str(jeu.tour)+" ")
    strDepart.set(str("Départ : "+getPageTitle(jeu.pageBase)))
    strCible.set(str("Cible : "+getPageTitle(jeu.pageCible)))
    strActuel.set(str("Actuelle : "+getPageTitle(jeu.pageActuelle)))

# Tour de jeu
def tourJeu():
    # Si les pages ne sont pas identiques le jeu continue
    if getPageTitle(jeu.pageBase) != getPageTitle(jeu.pageCible):

        # Gestion des btns
        enableBtns()

        # Affichage tour + pages
        labelFrame.configure(text="Tour : "+str(jeu.tour)+" ")
        strDepart.set(str("Départ : "+getPageTitle(jeu.pageBase)))
        strCible.set(str("Cible : "+getPageTitle(jeu.pageCible)))
        strActuel.set(str("Actuelle : "+getPageTitle(jeu.pageActuelle)))
        
        # Récupération des liens de la page actuelle
        extractWebpage(jeu.pageActuelle,jeu.startItem)
        listeBoxLiens.select_set(0)
    else:
        finJeu()

# Gestion des btns
def enableBtns(i=1):
    btnValider.config(state='normal')
    btnStart.config(state='disabled')
    btnRetour.config(state='disabled') if jeu.pageActuelle == jeu.pageBase or len(jeu.histo) < 0 else btnRetour.config(state='normal')
    btnAfficherBack.config(state='normal') if jeu.startItem >= 20 else btnAfficherBack.config(state='disabled')
    btnAfficherNext.config(state='normal')if len(jeu.listeLiens) > 20 and jeu.startItem+20 < i else btnAfficherNext.config(state='disabled')


# Gestion du choix utilisateur
def jeuChoix():
    try:
        listeBoxLiens.get(listeBoxLiens.curselection())
        index = int(listeBoxLiens.get(0,'end').index(listeBoxLiens.get(listeBoxLiens.curselection())))
        jeu.choix = index +jeu.startItem
    except:
        print("Choix invalide")
        raise

    jeu.histo.append(jeu.pageActuelle)

    jeu.startItem = 1
    jeu.tourPlus()

    jeu.pageActuelle = getPage("https://fr.wikipedia.org/"+str(jeu.listeLiens[jeu.choix-1].url))
    tourJeu()

# Affiche liens suivants
def afficheNext():
    jeu.startItem +=20
    tourJeu()

# Affiche liens précédents
def afficheBack():
    jeu.startItem -=20
    tourJeu()
    
# Retour -1 page
def retour():
    if len(jeu.histo) >= 1:
        jeu.startItem = 1 
        jeu.pageActuelle = jeu.histo[len(jeu.histo)-1]
        jeu.histo.pop()
    tourJeu()

# Fin du jeu
def finJeu():
    jeu.scorePlus()
    labelFrameEnd.pack(fill="both", expand="yes")
    strEndTour.set("one shot one kill, chance insolente") if jeu.tour == 1 else strEndTour.set("terminé en"+str(jeu.tour)+"coups.")
    btnEndFrame.pack()
    labelFrame.pack_forget()
    btnFrame.pack_forget()

# Restart
def restart():
    # Restart program
    #python = sys.executable
    #os.execl(python, python, * sys.argv)

    # Restart game
    print(getPageTitle(jeu.pageBase))
    jeu.pageBase = getPage(url)
    print(getPageTitle(jeu.pageBase))
    jeu.pageCible = getPage(url)
    jeu.resetJeu()

    labelFrame.pack(fill="both", expand="yes")
    btnFrame.pack(fill="both", expand="yes")
    labelFrameEnd.pack_forget()
    btnEndFrame.pack_forget()

    btnStart.config(state='normal')
    startTimer()

def timer(delay,labelTime):
    count = 0
    start = time.perf_counter()
    while count < 5:
        time.sleep(delay)
        count +=1
        elapsed = (time.perf_counter()-start)
        minute = '%02d' % int(elapsed / 60)
        seconds = '%02d' % int(elapsed % 60)
        strTime.set(str(minute)+":"+str(seconds))
    finJeu()

def startTimer():
    try:
        _thread.start_new_thread( timer, ( 1, labelTime) )
    except:
        print ("Error: unable to start thread : timer")

# Main
# Init vars
url = "https://fr.wikipedia.org/wiki/Sp%C3%A9cial:Page_au_hasard"
jeu = Jeu(1)
jeu.pageBase = getPage(url)
jeu.pageCible = getPage(url)
jeu.pageActuelle = jeu.pageBase

# Init window
window = Tk()
window.title("********** Wikigame **********")
window.geometry("500x500")
# Font
f1 = tkFont.Font(family='Helvetica', size=10, weight='bold')
f2 = tkFont.Font(family='Helvetica', size=10, weight='normal')

# init windows vars
labelFrame = LabelFrame(window, text="Tour : ", padx=10, pady=10)
labelFrameEnd = LabelFrame(window, text="Fin", padx=10, pady=10)
btnFrame = Frame(window,padx=5,pady=5)
btnEndFrame = Frame(window,padx=5,pady=5)

numTour = StringVar()
strEndTour = StringVar()
labelEndTour = Label(labelFrameEnd,textvariable=strEndTour)
labelEndTitre = Label(labelFrameEnd,text="********** FIN **********")

strTime = StringVar()
labelTime = Label(labelFrame,textvariable=strTime,font=f1,fg='black').pack()
strDepart = StringVar()
labelDepart = Label(labelFrame,textvariable=strDepart,font=f1).pack()
strCible = StringVar()
labelCible = Label(labelFrame,textvariable=strCible,font=f1).pack()
strActuel = StringVar()
labelActuel = Label(labelFrame,textvariable=strActuel,font=f1).pack()
strResume = StringVar()
labelResume = Label(labelFrame,textvariable=strResume,font=f2,wraplength=480,pady=10).pack()

strDepart.set("Départ : ")
strCible.set("Cible : ")
strActuel.set("Actuelle : ")

listeBoxLiens = Listbox(labelFrame,selectmode=SINGLE,width=50)
listeBoxLiens.pack()

strResult = StringVar()
labelResult = Label(labelFrame,textvariable=strResult).pack()

btnStart = Button(btnFrame,text='Jouer',command=start)
btnValider = Button(btnFrame,text='Valider',command=jeuChoix,state=DISABLED)
btnAfficherNext = Button(btnFrame,text='Afficher suivants',command=afficheNext,state=DISABLED)
btnAfficherBack = Button(btnFrame,text='Afficher précédents',command=afficheBack,state=DISABLED)
btnRetour = Button(btnFrame,text='Retour',command=retour,state=DISABLED)
btnRestart = Button(btnEndFrame,text='Rejouer',command=restart)

btnStart.pack(side=LEFT,padx=5,pady=5)
btnValider.pack(side=LEFT,padx=5,pady=5)
btnAfficherNext.pack(side=LEFT,padx=5,pady=5)
btnAfficherBack.pack(side=LEFT,padx=5,pady=5)
btnRetour.pack(side=LEFT,padx=5,pady=5)
btnRestart.pack(side=LEFT,padx=5,pady=5)

# pack Frame
labelFrame.pack(fill="both", expand="yes")
btnFrame.pack(fill="both")

# Tkinter main loop
window.mainloop()










    




