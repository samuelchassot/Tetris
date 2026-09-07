# -*- coding: utf-8 -*-
"""Diagnostic temporaire (pas fait pour être committé) : construit un
écran Jeu directement, comme le ferait Accueil, et rapporte precisement
ce qui a été dessiné sur can_jeu - pour savoir si l'overlay tactile est
bien créé (et où) même si rien n'est visible à l'écran.

Usage : depuis le dossier Tetris/, sur la Raspberry Pi :
    python3 diagnostic_touch.py
Puis copier-coller toute la sortie du terminal.
"""
import sys

print("Python:", sys.version)

import tkinter
print("Tk version:", tkinter.TkVersion, "Tcl version:", tkinter.TclVersion)

sys.path.insert(0, "classesMenu")

import constantes
print("constantes.py chargé OK, geometry =", constantes.geometry)

from tkinter import FALSE
constantes.root.geometry(constantes.geometry)
constantes.root.resizable(width=FALSE, height=FALSE)
constantes.root.tk_setPalette(background="light sky blue", foreground="black")
root = constantes.root
print("root créé OK")

from jeu import Jeu
print("import Jeu OK")

game = Jeu(master=root, pseudoJoueur="diagnostic")
print("Jeu construit OK")

root.update()
print("root.update() OK")

items = game.can_jeu.find_all()
print("Nombre total d'items sur can_jeu:", len(items))
print("Attendu si tout va bien: 17 (4 blocs de la piece qui tombe + 5 croix + 8 boutons)")
print()
print("Détail de chaque item (id, type, coordonnées):")
for item in items:
    print(" ", item, game.can_jeu.type(item), game.can_jeu.coords(item))

print()
print("self.touch existe ?", hasattr(game, "touch"))
if hasattr(game, "touch"):
    print("self.touch._specs (groupes ajoutés):", len(game.touch._specs))
    for spec in game.touch._specs:
        print("  -", spec["kind"], "canvas=", spec["canvas"], "center=", spec["center"],
              "button_size=", spec["button_size"], "items=", spec["items"])

print()
print("can_jeu winfo (position/taille réelles à l'écran):")
print("  width:", game.can_jeu.winfo_width(), "height:", game.can_jeu.winfo_height())
print("  rootx:", game.can_jeu.winfo_rootx(), "rooty:", game.can_jeu.winfo_rooty())
print("  screen width:", root.winfo_screenwidth(), "screen height:", root.winfo_screenheight())

print()
print("Fenêtre ouverte - regardez l'écran, puis fermez la fenêtre (ou Ctrl+C ici) pour terminer.")
root.mainloop()
