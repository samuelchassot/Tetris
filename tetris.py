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
#
# Plein écran, sans bordure/barre de titre, dimensionné sur la
# résolution réelle de l'écran : overrideredirect(True) + une géométrie
# explicite plutôt que root.attributes('-fullscreen', True), car ce
# dernier dépend d'un gestionnaire de fenêtres qui applique le hint
# EWMH correspondant - ça ne marche pas de façon fiable sans (typique
# d'un Raspberry Pi en mode kiosque).
root.overrideredirect(True)
root.geometry("{}x{}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
# Pas de resizable(False, False) ici : overrideredirect(True) a déjà
# supprimé toute bordure/poignée de redimensionnement, donc il n'y a
# rien à contraindre - et cet appel, passé APRÈS geometry(), réinitialise
# la fenêtre à sa taille par défaut (200x200) au lieu de la taille
# plein écran qu'on vient de demander (vérifié : sans cet appel, la
# fenêtre occupe bien tout l'écran).
root.tk_setPalette(background="light sky blue", foreground="black")
root.config(cursor="none")
root.protocol('WM_DELETE_WINDOW', root.destroy)

Accueil(master=root, texteMenus=majListe(joueur),       #création de l'Accueil
        pseudoJoueur=majEntete(joueur))

root.mainloop()
