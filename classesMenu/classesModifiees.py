# -*- coding: utf-8 -*-

##################################
#Classes principales pour le jeu #
##################################

from tkinter import *

import sys
sys.path.insert(0, "..")

from constantes import *

#classes modifiées
##################

class FenetreGrande(Frame):
    """Un « écran » plein fenêtre de l'appli (Accueil, Jeu, ...).

    N'est PLUS une racine Tk() (contrairement à l'ancienne version) :
    c'est une Frame affichée à l'intérieur de la racine Tk unique et
    persistante `master` (voir constantes.root / tetris.py), qu'on peut
    détruire et recréer librement d'un écran à l'autre sans jamais
    toucher à la racine elle-même - c'est cette dernière qui plantait
    Tk sur macOS si on la détruisait puis en recréait une nouvelle.
    """

    def __init__(self, master, pseudoJoueur, **Arguments):
        Frame.__init__(self, master, **Arguments)
        self.master.title(pseudoJoueur)
        self.pack(fill=BOTH, expand=True)
        self.focus_set()

class FenetrePetite(Toplevel):

    def __init__(self, parent, geometryPetite, titre, gridOuPack, **Arguments):
        Toplevel.__init__(self, parent, **Arguments)
        self.geometry(geometryPetite)
        self.resizable(width=FALSE, height=FALSE)
        self.protocol('WM_DELETE_WINDOW', self.quitter)

        self.parent = parent
        self.bind('<Escape>', self.quitter)


        if gridOuPack == "g":
            Label(self, text=titre, font=("Helvetica", 20)).grid(column=1, row=1, columnspan=2)
        else:
            Label(self, text=titre, font=("Helvetica", 20)).pack(side=TOP, pady=10)

    def quitter(self, event=None):
        """fonction destroy modifiée pour remettre peutOuvrir à true quand on ferme une fenêtre satellite"""
        self.parent.peutOuvrir = True
        self.destroy()
