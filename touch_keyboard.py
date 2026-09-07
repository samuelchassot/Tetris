# -*- coding: utf-8 -*-

#####################################################################
# Clavier tactile système (squeekboard) : afficher/masquer à la     #
# demande sur un champ de texte.                                    #
#####################################################################
#
# squeekboard (le clavier virtuel utilisé sur les setups Wayland/Phosh
# comme celui visé pour l'écran tactile de la Raspberry Pi) ne détecte
# automatiquement le focus d'un champ de texte QUE pour les
# applications qui parlent le protocole Wayland text-input/input-method
# - ce qui exclut une appli Tk classique (X11/XWayland). On le pilote
# donc explicitement via son API D-Bus (sm.puri.OSK0.SetVisible), en
# l'invoquant nous-mêmes sur le focus/perte de focus d'un champ Entry.
#
# Ce fichier ne connaît rien à Tetris : bind_entry() marche sur
# n'importe quel widget Entry, dans n'importe quelle appli Tk.
#
# ATTENTION : l'appel D-Bus lui-même n'a pas pu être testé (pas de
# squeekboard ni de bus D-Bus correspondant disponible en dehors de la
# Raspberry Pi cible) - seul le câblage FocusIn/FocusOut -> show()/hide()
# a été vérifié. show()/hide() ne plantent jamais (dbus-send manquant ou
# squeekboard non lancé = no-op silencieux), donc au pire le clavier ne
# s'affiche simplement pas, sans casser le reste de l'appli - mais bien
# vérifier que ça affiche réellement le clavier une fois sur la Pi.

import subprocess

_BUS_NAME = "sm.puri.OSK0"
_OBJECT_PATH = "/sm/puri/OSK0"
_INTERFACE = "sm.puri.OSK0"


def _set_visible(visible):
    """Demande à squeekboard de s'afficher ou se masquer. Ne bloque
    jamais et ne plante jamais si dbus-send ou squeekboard sont absents
    (par ex. en développement sur une machine sans clavier tactile) -
    c'est un appel "au mieux", pas une dépendance dure."""
    try:
        subprocess.Popen(
            [
                "dbus-send", "--type=method_call",
                "--dest=" + _BUS_NAME, _OBJECT_PATH,
                _INTERFACE + ".SetVisible",
                "boolean:{}".format("true" if visible else "false"),
            ],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        pass  # dbus-send non installé - no-op silencieux


def show():
    _set_visible(True)


def hide():
    _set_visible(False)


def bind_entry(entry):
    """Affiche le clavier tactile quand `entry` prend le focus, le
    masque quand il le perd."""
    entry.bind('<FocusIn>', lambda e: show())
    entry.bind('<FocusOut>', lambda e: hide())
