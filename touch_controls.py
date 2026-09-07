# -*- coding: utf-8 -*-

##############################################################
# Overlay tactile générique : croix directionnelle + A/B/X/Y #
##############################################################
#
# Composant réutilisable, indépendant du jeu : dessine une croix
# directionnelle façon Game Boy et 4 boutons A/B/X/Y façon manette SNES,
# en surimpression grisée façon overlay d'émulateur, et simule de VRAIES
# touches clavier sur le widget cible quand on les touche. Ce fichier ne
# connaît rien à Tetris : il ne fait que traduire "bouton pressé/relâché"
# en évènements <KeyPress-x>/<KeyRelease-x>, donc n'importe quel widget
# qui écoute déjà le clavier (comme Jeu dans classesMenu/jeu.py)
# fonctionne sans la moindre modification.
#
# Sous X11/Aqua, un écran tactile est vu par Tk comme une souris : un
# appui du doigt déclenche <ButtonPress-1>, un relâché <ButtonRelease-1>.
# Donc aucune API tactile spécifique n'est nécessaire ici - mais Tk (et la
# plupart des pilotes d'écrans tactiles Raspberry Pi) n'émule qu'un seul
# pointeur, donc appuyer sur deux boutons en même temps (par ex. bouger à
# gauche ET tourner) n'est pas garanti fonctionner.
#
# Un canvas de jeu qui se redessine en effaçant tout (canvas.delete(ALL))
# effacerait les boutons avec le reste : appeler redraw() juste après un
# tel nettoyage recrée tous les boutons ajoutés jusque là. Si le canvas
# se contente d'empiler de nouveaux éléments par-dessus (par ex. un
# rectangle de pause) sans tout effacer, raise_all() suffit à remonter
# les boutons au-dessus - sinon ils deviennent invisibles ET intouchables
# (Tk ne délivre les clics qu'à l'élément le plus "haut" à cet endroit).

from tkinter import *

# direction/bouton -> (keysym clavier Tk, mode)
#
# mode:
#   'repeat' : simule le maintien d'une touche clavier (répétition
#              automatique de KeyPress tant qu'on garde le doigt appuyé,
#              comme le ferait le système avec une vraie touche) - pour
#              les actions qu'on veut pouvoir maintenir (déplacement,
#              rotation).
#   'once'   : une seule pression a chaque appui tactile, même si on
#              maintient le doigt - pour les actions qui n'ont pas de
#              sens répétées en rafale (chute directe, pause).
#   'hold'   : envoie un KeyPress au toucher et un KeyRelease au
#              relâchement, sans répétition - pour les touches dont le
#              jeu suit lui-même l'état "maintenue" (la descente
#              accélérée de Jeu.descendreAppui/descendreRelache).
DEFAULT_DPAD_KEYMAP = {
    'up':    ('Up', 'repeat'),
    'down':  ('Down', 'hold'),
    'left':  ('Left', 'repeat'),
    'right': ('Right', 'repeat'),
}

# Disposition façon SNES/GBA : X en haut, Y à gauche, A à droite, B en bas.
DEFAULT_FACE_KEYMAP = {
    'x': ('Up', 'repeat'),   # alias tactile de la rotation (bouton plus
                              # grand et mieux placé pour le pouce que le
                              # haut de la croix)
    'y': ('m', 'once'),      # bascule musique (actuellement un no-op
                              # dans le jeu, câblé pour le futur)
    'a': ('space', 'once'),  # chute directe
    'b': ('Escape', 'once'), # pause
}


class TouchControls:
    """Overlay tactile : croix directionnelle et/ou boutons A/B/X/Y.

    Ne dessine rien tout seul : appeler add_dpad()/add_face_buttons() pour
    ajouter chaque groupe de boutons sur le(s) canvas de son choix (ils
    peuvent être sur des canvas différents - utile par exemple pour poser
    la croix sur le plateau de jeu et les boutons sur le panneau latéral).
    Toutes les touches simulées sont envoyées à `target` (le widget qui
    possède les bind() clavier réels, en général la fenêtre du jeu
    elle-même).

    Si l'appelant efface tout son canvas pour le redessiner (typiquement
    `canvas.delete(ALL)`), appeler redraw() ensuite recrée tous les
    boutons ajoutés jusque là - sans perdre l'état "touche maintenue" en
    cours, indexé par keysym et non par identifiant de forme. Si
    l'appelant empile juste de nouveaux éléments par-dessus (par ex. un
    cache de pause) sans tout effacer, raise_all() suffit à remonter les
    boutons au-dessus.
    """

    def __init__(self, target, repeat_delay_ms=350, repeat_interval_ms=60,
                 fill_color="#888888", outline_color="#dddddd",
                 opacity_stipple="gray50"):
        self.target = target
        self.repeat_delay_ms = repeat_delay_ms
        self.repeat_interval_ms = repeat_interval_ms
        self.fill_color = fill_color
        self.outline_color = outline_color
        self.opacity_stipple = opacity_stipple

        # description de chaque groupe ajouté (dpad ou face buttons), pour
        # pouvoir se redessiner soi-même sur demande - voir redraw()
        self._specs = []
        # keysym -> mode, pour les touches actuellement maintenues
        self._active = {}
        # keysym -> id retourné par canvas.after(), pour pouvoir l'annuler
        self._repeat_jobs = {}
        # canvas utilisé pour after()/after_cancel() (n'importe lequel
        # utilisé fait l'affaire, Tk les partage tous)
        self._scheduler = None

    # ------------------------------------------------------------------
    # Construction des boutons
    # ------------------------------------------------------------------

    def add_dpad(self, canvas, center, keymap=None, button_size=28, gap=4):
        """Ajoute une croix directionnelle à 4 branches centrée sur
        `center` (x, y) dans les coordonnées de `canvas`."""
        spec = {
            'kind': 'dpad', 'canvas': canvas, 'center': center,
            'keymap': DEFAULT_DPAD_KEYMAP if keymap is None else keymap,
            'button_size': button_size, 'gap': gap, 'items': [],
        }
        self._specs.append(spec)
        self._remember_scheduler(canvas)
        self._draw_dpad(spec)

    def add_face_buttons(self, canvas, center, keymap=None, button_size=28, gap=8):
        """Ajoute les 4 boutons ronds A/B/X/Y en losange (X en haut, Y à
        gauche, A à droite, B en bas - disposition SNES/GBA) centrés sur
        `center` (x, y) dans les coordonnées de `canvas`."""
        spec = {
            'kind': 'face', 'canvas': canvas, 'center': center,
            'keymap': DEFAULT_FACE_KEYMAP if keymap is None else keymap,
            'button_size': button_size, 'gap': gap, 'items': [],
        }
        self._specs.append(spec)
        self._remember_scheduler(canvas)
        self._draw_face(spec)

    def redraw(self):
        """Recrée tous les boutons ajoutés jusqu'ici, sur leur(s) canvas
        respectif(s). À appeler après un canvas.delete(ALL) qui aurait
        effacé les boutons en même temps que le reste."""
        for spec in self._specs:
            for item in spec['items']:
                spec['canvas'].delete(item)
            spec['items'] = []
            if spec['kind'] == 'dpad':
                self._draw_dpad(spec)
            else:
                self._draw_face(spec)

    def raise_all(self):
        """Remonte tous les boutons au-dessus de tout ce qui a pu être
        dessiné par-dessus depuis (sans les recréer) - utile quand
        l'appelant empile un nouvel élément sur le même canvas sans tout
        effacer (par ex. un cache de pause)."""
        for spec in self._specs:
            for item in spec['items']:
                spec['canvas'].tag_raise(item)

    # ------------------------------------------------------------------
    # Dessin
    # ------------------------------------------------------------------

    def _draw_dpad(self, spec):
        canvas = spec['canvas']
        cx, cy = spec['center']
        s = spec['button_size']
        g = spec['gap']
        keymap = spec['keymap']

        # bouton central, purement esthétique (croix pleine comme une
        # vraie manette) - ne déclenche rien
        spec['items'].append(self._draw_rect(canvas, cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2))

        positions = {
            'up':    (cx,          cy - s - g),
            'down':  (cx,          cy + s + g),
            'left':  (cx - s - g,  cy),
            'right': (cx + s + g,  cy),
        }
        for direction, (bx, by) in positions.items():
            keysym, mode = keymap.get(direction, (None, None))
            item = self._draw_rect(canvas, bx - s / 2, by - s / 2, bx + s / 2, by + s / 2)
            self._bind_item(canvas, item, keysym, mode)
            spec['items'].append(item)

    def _draw_face(self, spec):
        canvas = spec['canvas']
        cx, cy = spec['center']
        s = spec['button_size']
        g = spec['gap']
        keymap = spec['keymap']

        positions = {
            'x': (cx,          cy - s - g),
            'y': (cx - s - g,  cy),
            'a': (cx + s + g,  cy),
            'b': (cx,          cy + s + g),
        }
        for label, (bx, by) in positions.items():
            keysym, mode = keymap.get(label, (None, None))
            item = self._draw_oval(canvas, bx - s / 2, by - s / 2, bx + s / 2, by + s / 2)
            text = canvas.create_text(bx, by, text=label.upper(), fill=self.outline_color,
                                       font=("Helvetica", max(8, int(s * 0.5)), "bold"))
            self._bind_item(canvas, item, keysym, mode)
            self._bind_item(canvas, text, keysym, mode)
            spec['items'].extend([item, text])

    def _draw_rect(self, canvas, x0, y0, x1, y1):
        return canvas.create_rectangle(x0, y0, x1, y1, fill=self.fill_color,
                                        outline=self.outline_color,
                                        stipple=self.opacity_stipple)

    def _draw_oval(self, canvas, x0, y0, x1, y1):
        return canvas.create_oval(x0, y0, x1, y1, fill=self.fill_color,
                                   outline=self.outline_color,
                                   stipple=self.opacity_stipple)

    def _remember_scheduler(self, canvas):
        if self._scheduler is None:
            self._scheduler = canvas

    # ------------------------------------------------------------------
    # Simulation clavier
    # ------------------------------------------------------------------

    def _bind_item(self, canvas, item, keysym, mode):
        if keysym is None:
            return
        canvas.tag_bind(item, '<ButtonPress-1>', lambda e, k=keysym, m=mode: self._on_press(k, m))
        canvas.tag_bind(item, '<ButtonRelease-1>', lambda e, k=keysym, m=mode: self._on_release(k, m))

    def _on_press(self, keysym, mode):
        if keysym in self._active:
            return  # déjà en cours (le doigt a glissé sur un bouton qui partage la touche)
        self._active[keysym] = mode
        self._send('KeyPress', keysym)
        if mode == 'repeat':
            self._schedule_repeat(keysym, self.repeat_delay_ms)

    def _on_release(self, keysym, mode):
        if keysym not in self._active:
            return
        del self._active[keysym]
        self._cancel_repeat(keysym)
        if mode == 'hold':
            self._send('KeyRelease', keysym)

    def _schedule_repeat(self, keysym, delay_ms):
        if keysym not in self._active:
            return
        self._repeat_jobs[keysym] = self._scheduler.after(delay_ms, self._fire_repeat, keysym)

    def _fire_repeat(self, keysym):
        if keysym not in self._active:
            return
        self._send('KeyPress', keysym)
        self._schedule_repeat(keysym, self.repeat_interval_ms)

    def _cancel_repeat(self, keysym):
        job = self._repeat_jobs.pop(keysym, None)
        if job is not None:
            self._scheduler.after_cancel(job)

    def _send(self, event_type, keysym):
        self.target.event_generate('<{}-{}>'.format(event_type, keysym))


# ----------------------------------------------------------------------
# Démo autonome : ouvre une fenêtre avec juste l'overlay, pour vérifier
# le câblage sans passer par la connexion/le jeu complet. Les touches
# clavier reçues (réelles ou simulées par un appui tactile) sont
# affichées dans le titre de la fenêtre.
# ----------------------------------------------------------------------

if __name__ == '__main__':
    root = Tk()
    root.title("Touch controls demo")
    root.resizable(width=False, height=False)

    canvas = Canvas(root, width=300, height=300, bg="black")
    canvas.pack()

    log = Label(root, text="Touchez ou cliquez un bouton...", font=("Helvetica", 12))
    log.pack(pady=8)

    controls = TouchControls(target=root)
    controls.add_dpad(canvas, center=(70, 220))
    controls.add_face_buttons(canvas, center=(220, 220))

    def _on_key(event):
        log.config(text="KeyPress: {}".format(event.keysym))

    def _on_key_release(event):
        log.config(text="KeyRelease: {}".format(event.keysym))

    root.bind('<KeyPress>', _on_key)
    root.bind('<KeyRelease>', _on_key_release)

    root.mainloop()
