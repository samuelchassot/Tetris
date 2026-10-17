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
        # root tourne en plein écran (voir tetris.py) - on centre donc le
        # contenu (taille naturelle, non étirée) au milieu de l'écran au
        # lieu de le faire remplir toute la fenêtre.
        self.place(relx=0.5, rely=0.5, anchor=CENTER)
        self.focus_set()

class FenetrePetite(Toplevel):

    def __init__(self, parent, geometryPetite, titre, gridOuPack, **Arguments):
        Toplevel.__init__(self, parent, **Arguments)
        # Use overrideredirect so this window is in the same X11 layer as the
        # fullscreen root (which also uses overrideredirect). Without this,
        # WM-managed Toplevels stay below the override-redirect root regardless
        # of lift() calls. Side effects: no title bar, no WM close button —
        # both are handled via the <Escape> binding below.
        self.overrideredirect(True)
        self.geometry(geometryPetite)
        # resizable() resets geometry to 200x200 when combined with
        # overrideredirect — skip it (no resize handles exist anyway).
        # WM_DELETE_WINDOW is a no-op on overrideredirect windows.
        self.configure(highlightbackground="navy", highlightcolor="navy",
                       highlightthickness=3)
        self.lift()
        self.focus_force()

        self.parent = parent
        self.bind('<Escape>', self.quitter)


        if gridOuPack == "g":
            Label(self, text=titre, font=("Helvetica", 20)).grid(column=1, row=1, columnspan=2)
        else:
            Label(self, text=titre, font=("Helvetica", 20)).pack(side=TOP, pady=10)

    def destroy(self):
        """Return keyboard focus to parent before tearing down the window."""
        try:
            self.parent.focus_force()
        except Exception:
            pass
        super().destroy()

    def quitter(self, event=None):
        """fonction destroy modifiée pour remettre peutOuvrir à true quand on ferme une fenêtre satellite"""
        self.parent.peutOuvrir = True
        self.destroy()
