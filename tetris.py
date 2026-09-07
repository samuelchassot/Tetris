# -*- coding: utf-8 -*-

###############################
# Fichier de lancement du jeu #
###############################

#importations
#############

import os
import sqlite3
from constantes import *
from requetes import *
from tkinter import *
from fonctionsConnexion import *
import sys
sys.path.insert(0, "classesMenu") 						#modification du chemin relatif
from accueil import *

#création de la base de données
###############################

if not os.path.isfile(fichierDB):                       #création s'il n'éxiste pas du fichier de BD
    conn, cur = connexionDB(fichierDB)                  #connexion à la BD
    executeurDeRequetes(cur, [reqPlayer, reqScore], 0)  #remplissage de la BD
    deconnexionDB(conn, cur)                            #déconnexion de la BD

#création de l'accueil
######################


deconnexion(fichierJoueur)                              #déconnexion du joueur éventuellement connectée avant le lancement du jeu

joueur = nomJoueur(fichierJoueur)                       #connexion du joueur (aucun joueur)

# `root` (une seule racine Tk pour toute la durée de vie de l'appli) est
# créée dans constantes.py - voir le commentaire là-bas. On la configure
# ici une bonne fois pour toutes, puis chaque écran (Accueil, Jeu, ...)
# s'affiche comme une Frame à l'intérieur, sans jamais recréer de racine.
root.geometry(geometry)
root.resizable(width=FALSE, height=FALSE)
root.tk_setPalette(background="light sky blue", foreground="black")
root.protocol('WM_DELETE_WINDOW', root.destroy)

Accueil(master=root, texteMenus=majListe(joueur),       #création de l'Accueil
        pseudoJoueur=majEntete(joueur))

root.mainloop()
