# Importieren u. initialisieren der Pygame-Bibliothek
import pygame
from pygame.locals import *
import random
import math
import shelve

# Variablen/KONSTANTEN setzen
W, H = 800, 600
FPS = 60
SCHWARZ = (0, 0, 0)
WEISS = (255, 255, 255)
ROT = (255, 0, 0)
MINGEGNER = [5, 10, 20, 25, 30, 35]
MAXGEGNER = [10, 20, 30, 35, 40, 45]
RESERVEKUGELN = 10
INGEFAHR = 3
EINGEDRUNGENENDE = 3
KUGELBEWEGUNG = 10
GEGNERBEWEGUNG = [3, 4, 5, 6, 7, 8]
SPIELERBEWEGUNG = 7
SPIELERBEWEGUNGFAKTOR = 0.8
CAPTION = "Varroa Invaders"
HINTERGRUNDBILD = "bilder/bienenstock1.jpg"
SPIELERBILD = "bilder/biene-sprite-sheet1.png"
# Animationsbereiche
SPIELERBILDBEREICH = ['', '', '', '', '', '']
SPIELERBILDBEREICH[0] = (0, 0, 100, 100)
SPIELERBILDBEREICH[1] = (101, 0, 100, 100)
SPIELERBILDBEREICH[2] = (202, 0, 100, 100)
SPIELERBILDBEREICH[3] = (303, 0, 100, 100)
SPIELERBILDBEREICH[4] = (404, 0, 100, 100)
SPIELERBILDBEREICH[5] = (505, 0, 100, 100)
KUGELBILD = "bilder/honigtropfen.png"
GEGNERBILDER = ['bilder/varroa.png', 'bilder/varroa2.png', 'bilder/varroa3.png', 'bilder/varroa4.png',
                'bilder/varroa5.png', 'bilder/varroa6.png']
ERFOLGENDEBILD = "bilder/biene.jpg"
SCHEITERNENDEBILD = "bilder/totebiene.gif"
HINTERGRUNDSOUND = "sound/bienensummen.mp3"
SIRENENSOUND = "sound/sirene.mp3"
ERFOLGSOUND = "sound/tusch.mp3"
SCHEITERNSOUND1 = "sound/help.mp3"
SCHEITERNSOUND2 = "sound/time-to-say-goodbye.mp3"
GETROFFENSOUND = "sound/treffer.mp3"
SCOREDATEI = "files/score.txt"

# Init Game GUI
pygame.init()
fenster = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)

# Globale Spielvariablen
level = 0
punkte = 0
hintergrund = pygame.image.load(HINTERGRUNDBILD)
scoredatei = shelve.open(SCOREDATEI)


# Spiel
class Spiel:
    def __init__(self, level):
        self.aktiv = True
        self.sirenegespielt = False
        self.anzahlgegner = random.randint(MINGEGNER[level], MAXGEGNER[level])
        self.gegnergetroffen = 0
        self.versuche = 0
        self.maxversuche = self.anzahlgegner + RESERVEKUGELN
        self.kugelbild = pygame.image.load(KUGELBILD)
        self.gegner = []
        self.zuende1 = pygame.mixer.Sound(SCHEITERNSOUND1)
        self.highscore = scoredatei['highscore']

        pygame.display.set_caption(CAPTION)
        pygame.mixer.music.stop()
        pygame.mixer.music.load(HINTERGRUNDSOUND)
        pygame.mixer.music.play(-1, 0.0)
        pygame.mixer.music.set_volume(.4)
        self.getroffensound = pygame.mixer.Sound(GETROFFENSOUND)

        self.erzeugegegner()

    def sirene(self):
        if not self.sirenegespielt:
            sirene = pygame.mixer.Sound(SIRENENSOUND)
            pygame.mixer.Sound.play(sirene)
            self.sirenegespielt = True

    def hatgegnergetroffen(self, index):
        global punkte
        pygame.mixer.Sound.play(self.getroffensound)
        self.gegnergetroffen += 1
        self.loeschegegner(index)
        punkte += abs(gegner.bewegung) * 200 + W - gegner.Y

    def anzahlaktivegegner(self):
        anzahl = 0
        for gegner in self.gegner:
            if gegner.status == 'aktiv':
                anzahl += 1
        return anzahl

    def ingefahr(self):
        return self.maxversuche - self.versuche <= (self.anzahlaktivegegner() + INGEFAHR)

    def keinegegnermehr(self):
        gewonnen = self.anzahlaktivegegner() == 0
        if gewonnen and punkte > self.highscore:
            scoredatei['highscore'] = punkte
        return gewonnen

    def keineversuchemehr(self):
        global punkte
        verloren = self.versuche >= self.maxversuche and self.anzahlaktivegegner()
        if verloren:
            punkte = 0
        return verloren

    def zuwenigversuche(self):
        global punkte
        verloren = self.maxversuche - self.versuche < self.anzahlaktivegegner()
        if verloren:
            punkte = 0
        return verloren

    def gegnereingedrungen(self):
        global punkte
        eingedrungen = 0
        for gegner in self.gegner:
            if gegner.status == "aktiv":
                if gegner.X <= 180 and (abs(spieler.posY - gegner.Y) < 40):
                    gegner.status = "eingedrungen"
                    eingedrungen += 1
                    spieler.langsamer()
                    pygame.mixer.Sound.play(self.zuende1)
            else:
                if gegner.status == "eingedrungen":
                    eingedrungen += 1
        verloren = eingedrungen >= EINGEDRUNGENENDE
        if verloren:
            punkte = 0
        return verloren

    def zeichnegegner(self):
        for gegner in self.gegner:
            fenster.blit(gegner.bild, (gegner.X, gegner.Y))

    def zeichnekugellager(self):
        for x in range(self.maxversuche - self.versuche):
            fenster.blit(self.kugelbild, (0, H - (x * 10) - 20))

    def spielstand(self):
        inhalt = "Noch {} Tropfen für {} Milbe(n) Punkte: {} Highscore: {}".format(self.maxversuche - self.versuche,
                                                                                   self.anzahlaktivegegner(), punkte,
                                                                                   self.highscore)
        if spiel.ingefahr():
            textfarbe = ROT
        else:
            textfarbe = SCHWARZ
        return font.render(inhalt, True, textfarbe)

    def erzeugegegner(self):
        for x in range(self.anzahlgegner):
            self.gegner.append(Gegner())

    def bewegegegner(self):
        for gegner in self.gegner:
            if gegner.status == "aktiv":
                gegner.Y += gegner.bewegung

                if gegner.Y < 10:
                    gegner.bewegung *= -1
                    gegner.X -= 30

                if gegner.Y > H - 50:
                    gegner.bewegung *= -1
                    gegner.X -= 30
            else:
                gegner.Y = spieler.posY

    def loeschegegner(self, i):
        del self.gegner[i]


# Spieler
class Spieler:
    def __init__(self):
        self.bild = pygame.image.load(SPIELERBILD)
        self.posY = 300
        self.bewegung = 0
        self.animbereich = 0
        self.bereich = SPIELERBILDBEREICH
        self.bewegungfaktor = 1

    def up(self):
        self.bewegung = -SPIELERBEWEGUNG * self.bewegungfaktor

    def down(self):
        self.bewegung = SPIELERBEWEGUNG * self.bewegungfaktor

    def stop(self):
        self.bewegung = 0

    def langsamer(self):
        self.bewegungfaktor *= SPIELERBEWEGUNGFAKTOR

    def bewege(self):
        # Spiellogik
        if self.bewegung != 0:
            self.posY += self.bewegung

        if self.posY < 0:
            self.posY = 0
            self.bewegung = 0

        if self.posY > H - 90:
            self.posY = H - 90
            self.bewegung = 0

    def zeichne(self):
        self.animbereich += 1

        if self.animbereich > 5:
            self.animbereich = 0

        fenster.blit(self.bild, (100, self.posY), self.bereich[self.animbereich])


# Kugel
class Kugel:
    def __init__(self):
        self.bild = pygame.image.load(KUGELBILD)
        self.X = 0
        self.Y = 0
        self.Xbewegung = KUGELBEWEGUNG
        self.status = False

    def zeichne(self):
        if self.status:
            fenster.blit(self.bild, (self.X, self.Y))

    def feuern(self, posY):
        self.status = True
        self.X = 200
        self.Y = posY + 50
        spiel.versuche += 1

    def bewege(self):
        self.X += self.Xbewegung

    def kollisionskontrolle(self, gegner, durchgang):
        if gegner.status == "eingedrungen":
            return False

        # Korrektur wg. Bildgröße
        kugelx = self.X - 30
        kugely = self.Y - 25
        abstand = int(math.sqrt(math.pow(kugelx - gegner.X, 2) + math.pow(kugely - gegner.Y, 2)))
        # print("Abstand zwischen Kugel und Gegner: ", abstand)
        getroffen = abstand < 25

        if getroffen:
            self.status = False
            spiel.hatgegnergetroffen(durchgang)

        return getroffen

    def ausdemfeld(self):
        ausserhalb = self.X > W
        if ausserhalb:
            self.status = False
        return ausserhalb


class Gegner:
    def __init__(self):
        self.bild = pygame.image.load(random.choice(GEGNERBILDER))
        self.X = random.randint(int(W / 2) - 100, W - 50)
        self.Y = random.randint(50, H - 50)
        self.bewegung = random.randint(-GEGNERBEWEGUNG[level], GEGNERBEWEGUNG[level])
        self.status = "aktiv"


def ende_bildschirm(status, text=''):
    pygame.mixer.music.stop()
    if status == "gewonnen":
        pygame.time.wait(2000)
        tusch = pygame.mixer.Sound(ERFOLGSOUND)
        pygame.mixer.Sound.play(tusch)
        inhalt = "Spiel gewonnen! " + text
    else:
        zuende1 = pygame.mixer.Sound(SCHEITERNSOUND1)
        pygame.mixer.Sound.play(zuende1)
        pygame.time.wait(2000)
        zuende2 = pygame.mixer.Sound(SCHEITERNSOUND2)
        pygame.mixer.Sound.play(zuende2)
        inhalt = "Spiel verloren! " + text

    fenster.fill(WEISS)
    text = font.render(inhalt, True, SCHWARZ)
    fenster.blit(text, (20, 20))

    if status == "gewonnen":
        biene = pygame.image.load(ERFOLGENDEBILD)
        x = (W - biene.get_width()) / 2
        y = (H - biene.get_height()) / 2
        fenster.blit(biene, (x, y))
    else:
        tote_biene = pygame.image.load(SCHEITERNENDEBILD)
        x = (W - tote_biene.get_width()) / 2
        y = (H - tote_biene.get_height()) / 2
        fenster.blit(tote_biene, (x, y))

    pygame.display.flip()

    warte = True
    while warte:
        pygame.time.delay(100)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                warte = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                warte = False
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                warte = False
    pygame.mixer.music.stop()


def neuesspiel():
    global spiel, spieler, kugel, level
    if level >= len(MINGEGNER):
        level = len(MINGEGNER) - 1
    # Neue Instanzen erzeugen
    spiel = Spiel(level)
    spieler = Spieler()
    kugel = Kugel()


spiel = Spiel(0)
spieler = Spieler()
kugel = Kugel()

# Schleife Hauptprogramm
while spiel.aktiv:
    # Überprüfen, ob Nutzer eine Aktion durchgeführt hat
    for event in pygame.event.get():
        # Beenden bei [ESC] oder [X]
        if event.type == QUIT:
            spiel.aktiv = False

        if event.type == KEYDOWN:
            # print("Spieler hat Taste gedrückt")

            # Taste für Spieler 1
            if event.key == K_UP:
                # print("Spieler hat Pfeiltaste hoch gedrückt")
                spieler.up()
            elif event.key == K_DOWN:
                # print("Spieler hat Pfeiltaste runter gedrückt")
                spieler.down()
            elif event.key == K_ESCAPE:
                spiel.aktiv = False

            elif event.key == K_SPACE:
                # print("Kugel abfeuern")
                # nur möglich, wenn keine Kugel sichtbar ist
                if not kugel.status:
                    kugel.feuern(spieler.posY)

        if event.type == KEYUP:
            # print("Spieler stoppt bewegung")
            spieler.stop()

    spieler.bewege()

    spiel.bewegegegner()

    if kugel.status:
        kugel.bewege()

        durchgang = 0
        for gegner in spiel.gegner:
            getroffen = kugel.kollisionskontrolle(gegner, durchgang)
            durchgang += 1

            if getroffen:
                break

            # Kugel verlässt den Bildschirm
            if kugel.ausdemfeld():
                # Verloren, keine spiel.versuche mehr
                if spiel.keineversuchemehr():
                    ende_bildschirm("verloren", "Keine Honigtropfen mehr")
                    neuesspiel()

                # spiel.versuche reichen nicht mehr aus
                if spiel.zuwenigversuche():
                    ende_bildschirm("verloren", "Zu viele Milben für zu wenig Honigtropfen")
                    neuesspiel()

                # Es ist bald zu Ende...
                if spiel.ingefahr():
                    spiel.sirene()

    # Spiel entschieden?
    # Gewonnen, keine Gegner mehr
    if spiel.keinegegnermehr():
        ende_bildschirm("gewonnen")
        level += 1
        neuesspiel()

    # Verloren, Gegner sind eingedrungen
    if spiel.gegnereingedrungen():
        ende_bildschirm("verloren", "Zu viele Milben haben dich erwischt")
        neuesspiel()

    # Spielfeld löschen
    fenster.fill(WEISS)
    fenster.blit(hintergrund, (0, 0))

    # Spielstand ausgeben
    fenster.blit(spiel.spielstand(), (10, 10))

    # Spielfeld/figuren zeichnen

    # Spieler
    spieler.zeichne()

    # Kugel
    kugel.zeichne()
    spiel.zeichnekugellager()

    # Gegner
    spiel.zeichnegegner()

    # Fenster aktualisieren
    pygame.display.flip()
    clock.tick(FPS)
