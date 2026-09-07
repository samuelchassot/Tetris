# -*- coding: utf-8 -*-

###############################
#Constantes pour le jeu tetris#
###############################

#importations
#############
from tkinter import *
from fonctionsConnexion import *

#racine Tk unique pour toute la durée de vie de l'appli
#########################################################
#
# Sur les versions récentes de Tk (macOS/Aqua notamment), détruire une
# racine Tk() puis en créer une nouvelle dans le même processus fait
# planter Tk dès le premier update()/mainloop() sur la nouvelle. On ne
# crée donc qu'UNE SEULE racine, ici, jamais détruite avant la fin du
# programme - tous les écrans (Accueil, Jeu, ...) s'affichent comme des
# Frame à l'intérieur de cette même racine (voir
# classesModifiees.FenetreGrande) au lieu d'être eux-mêmes des fenêtres
# Tk() qu'on détruit et recrée.

root = Tk()

#résolution de la fenêtre principales
#####################################

def obtenirDimensions(dim):
    """obtenirDimensions(string dim) --> hauteur ou largeur de l'écran selon <dim>
    utile pour centrer la fenêtre de jeu sur les différents écrans
    """
    if dim == "h":
        return root.winfo_screenheight()
    elif dim == "l":
        return root.winfo_screenwidth()

#dimensions fenêtre standard
############################

hauteur = 570
largeur = 480

#estimation de la meilleure position de la fenêtre
##################################################

hauteurCoin = int((obtenirDimensions("h")-hauteur)/10)
largeurCoin = int((obtenirDimensions("l")-largeur)/3)

geometry = "{}x{}+{}+{}".format(largeur, hauteur, largeurCoin, hauteurCoin)

#résolution de la fenêtre secondaire
####################################

largeur_fenetrePetite = 250
hauteur_fenetrePetite = 300
geometryPetite = "{}x{}+{}+{}".format(largeur_fenetrePetite, hauteur_fenetrePetite, largeurCoin+largeur+5, hauteurCoin)

#résolution du jeu
##################

cote_carre = 25

largeur_canevas = cote_carre*10+1
hauteur_canevas = cote_carre*22

hauteurCanPieces = 180
largeurCanPieces = cote_carre*6

#fichiers
#########

fichierDB = "BaseDeDonnees.sq3"
fichierJoueur = "joueur.txt"

#commandes
##########

texteCommandes = [
("Flèche haute", "Tourner la pièce"),
("Flèches bas", "Accélérer la chute"),
("Flèche gauche", "Déplacer la pièce vers la gauche"),
("Flèche droite", "Déplacer la pièce vers la droite"),
("Espace", "Faire tomber la pièce d'un coup"),
("Escape", "Mettre le jeu en pause"),
("m", "Lance ou coupe la musique")
]

#couleurs
#########

bgCouleur="white"
blanc = "white"
gris = "gray"
noir = "black"
fondPrincipal = "dark slate blue"
fondCadres = "ivory"
couleur_bouton = "navy"
couleur_barre = "turquoise1"
couleur_carre = "yellow"
couleur_te = "purple"
couleur_lambda = "orange"
couleur_gamma = "blue"
couleur_S = "red"
couleur_Z = "green"
