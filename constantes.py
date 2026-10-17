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

# On X11 the root uses overrideredirect(True) (see tetris.py) which bypasses
# the window manager. All secondary windows (FenetrePetite, dialogs) must also
# use overrideredirect so they live in the same X11 stack layer and lift() works.
# Patch Toplevel.__init__ to auto-lift every new Toplevel as a safety net.
_orig_toplevel_init = Toplevel.__init__

def _toplevel_init_autolift(self, master=None, **kw):
    _orig_toplevel_init(self, master, **kw)
    widget = self
    def _lift():
        try:
            widget.lift()
        except Exception:
            pass
    self.after(1, _lift)

Toplevel.__init__ = _toplevel_init_autolift


def _overrideredirect_dialog(title, message, buttons):
    """Modal dialog using overrideredirect — visible above the fullscreen root
    and FenetrePetite on X11/Raspberry Pi.

    buttons: list of (label, return_value) pairs; first is the default (Return key).
    """
    prev_focus = root.focus_get()
    result = [None]

    dlg = Toplevel()
    dlg.overrideredirect(True)
    dlg_w, dlg_h = 340, 170
    x = (root.winfo_screenwidth() - dlg_w) // 2
    y = (root.winfo_screenheight() - dlg_h) // 2
    dlg.geometry("{}x{}+{}+{}".format(dlg_w, dlg_h, x, y))
    dlg.configure(relief=RIDGE, borderwidth=3)
    dlg.lift()

    Label(dlg, text=title, font=("Helvetica", 13, "bold"), pady=8).pack()
    Label(dlg, text=message, font=("Helvetica", 10),
          wraplength=300, justify=CENTER, pady=4).pack(padx=10)

    btn_frame = Frame(dlg)
    btn_frame.pack(pady=12)

    def close(value):
        result[0] = value
        try:
            dlg.grab_release()
        except Exception:
            pass
        dlg.destroy()
        try:
            if prev_focus and prev_focus.winfo_exists():
                prev_focus.focus_force()
        except Exception:
            pass

    for label, value in buttons:
        Button(btn_frame, text=label, width=8,
               command=lambda v=value: close(v)).pack(side=LEFT, padx=8)

    dlg.bind('<Return>', lambda e: close(buttons[0][1]))
    dlg.bind('<space>',  lambda e: close(buttons[0][1]))
    if len(buttons) > 1:
        dlg.bind('<Escape>', lambda e: close(buttons[-1][1]))
        dlg.bind('n', lambda e: close(buttons[-1][1]))
        dlg.bind('N', lambda e: close(buttons[-1][1]))
    else:
        dlg.bind('<Escape>', lambda e: close(buttons[0][1]))

    dlg.grab_set()
    dlg.focus_force()
    dlg.wait_window()
    return result[0]


# These shadow tkinter.messagebox.show*/askquestion everywhere that does
# "from tkinter.messagebox import *" followed by "from constantes import *".
def showinfo(title=None, message=None, **kw):
    _overrideredirect_dialog(title or "", message or "", [("OK", "ok")])

def showwarning(title=None, message=None, **kw):
    _overrideredirect_dialog(title or "", message or "", [("OK", "ok")])

def showerror(title=None, message=None, **kw):
    _overrideredirect_dialog(title or "", message or "", [("OK", "ok")])

def askquestion(title=None, message=None, **kw):
    return _overrideredirect_dialog(
        title or "", message or "",
        [("Oui", "yes"), ("Non", "no")]
    )

#résolution de la fenêtre principales
#####################################

def obtenirDimensions(dim):
    """obtenirDimensions(string dim) --> hauteur ou largeur de l'écran selon <dim>
    utile pour centrer les fenêtres secondaires sur l'écran
    """
    if dim == "h":
        return root.winfo_screenheight()
    elif dim == "l":
        return root.winfo_screenwidth()
    raise ValueError("dim must be 'h' or 'l', got {!r}".format(dim))

#dimensions du contenu du jeu
##############################
#
# La fenêtre principale (root) tourne maintenant en plein écran (voir
# tetris.py) - hauteur/largeur ne dimensionnent donc plus une fenêtre
# mais juste le contenu (Accueil, Jeu), centré dans cet écran (voir
# FenetreGrande dans classesModifiees.py).

hauteur = 570
largeur = 480

#résolution de la fenêtre secondaire
####################################
#
# Les fenêtres secondaires (Connexion, Inscription, Règles, ...) restent
# des vraies fenêtres Toplevel, indépendantes du plein écran - centrées
# directement sur l'écran plutôt que positionnées relativement à
# l'ancienne fenêtre principale (qui n'existe plus en tant que telle).

largeur_fenetrePetite = 250
hauteur_fenetrePetite = 300
largeurCoinPetite = int((obtenirDimensions("l") - largeur_fenetrePetite) / 2)
hauteurCoinPetite = int((obtenirDimensions("h") - hauteur_fenetrePetite) / 2)
geometryPetite = "{}x{}+{}+{}".format(largeur_fenetrePetite, hauteur_fenetrePetite, largeurCoinPetite, hauteurCoinPetite)

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
