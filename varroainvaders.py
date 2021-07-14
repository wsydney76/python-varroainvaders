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
MINGEGNER = [2, 5, 10, 15, 20, 25, 30, 35]
MAXGEGNER = [5, 10, 15, 20, 25, 30, 35, 40]
RESERVEKUGELN = 10
INGEFAHR = 3
EINGEDRUNGENENDE = 3
KUGELBEWEGUNG = 10
GEGNERBEWEGUNG = [3, 3, 4, 5, 6, 7, 5, 8]
GEGNERSPRUNGX = 30
SPIELERBEWEGUNG = 7
SPIELERX = 50
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
SCHUSSSOUND = "sound/schuss.mp3"
GETROFFENSOUND = ["sound/treffer.mp3", "sound/treffer2.mp3"]
IMAUSSOUND = "sound/imaus.mp3"
SCOREDATEI = "files/score.txt"

# Init Game GUI
pygame.init()
fenster = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)


# Globale Spielvariablen
class Session:
    level = 0
    punkte = 0
    startpunkte = 0
    hintergrund = pygame.image.load(HINTERGRUNDBILD)
    scoredatei = shelve.open(SCOREDATEI)

    @classmethod
    def setze_startpunkte(cls):
        cls.startpunkte = cls.punkte

    @classmethod
    def punkte_zuruecksetzen(cls):
        cls.punkte = cls.startpunkte

    @classmethod
    def naechstes_level(cls):
        cls.level = min(len(MINGEGNER) - 1, cls.level + 1)


# Spiel
class Spiel:
    def __init__(self):
        self.aktiv = True
        self.sirenegespielt = False
        self.anzahlgegner = random.randint(MINGEGNER[Session.level], MAXGEGNER[Session.level])
        self.gegnergetroffen = 0
        self.versuche = 0
        self.maxversuche = self.anzahlgegner + RESERVEKUGELN
        self.kugelbild = pygame.image.load(KUGELBILD)
        self.gegner = []
        self.zuende1 = pygame.mixer.Sound(SCHEITERNSOUND1)
        self.highscore = Session.scoredatei['highscore']

        pygame.display.set_caption(CAPTION)
        pygame.mixer.music.stop()
        pygame.mixer.music.load(HINTERGRUNDSOUND)
        pygame.mixer.music.play(-1, 0.0)
        pygame.mixer.music.set_volume(.4)

        self.erzeuge_gegner()

    def spiel_warnung(self):
        if not self.sirenegespielt:
            sirene = pygame.mixer.Sound(SIRENENSOUND)
            pygame.mixer.Sound.play(sirene)
            self.sirenegespielt = True

    def hat_gegner_getroffen(self, index):
        self.gegnergetroffen += 1
        self.loesche_gegner(index)
        Session.punkte += abs(gegner.bewegung) * 200 + W - gegner.Y

    def anzahl_aktive_gegner(self):
        anzahl = 0
        for gegner in self.gegner:
            if gegner.status == 'aktiv':
                anzahl += 1
        return anzahl

    def in_gefahr(self):
        return self.maxversuche - self.versuche <= (self.anzahl_aktive_gegner() + INGEFAHR)

    def keine_gegner_mehr(self):
        gewonnen = self.anzahl_aktive_gegner() == 0
        if gewonnen and Session.punkte > self.highscore:
            Session.scoredatei['highscore'] = Session.punkte
        return gewonnen

    def keine_versuche_mehr(self):
        verloren = self.versuche >= self.maxversuche and self.anzahl_aktive_gegner()
        if verloren:
            Session.punkte_zuruecksetzen()
        return verloren

    def zuwenig_versuche(self):
        verloren = self.maxversuche - self.versuche < self.anzahl_aktive_gegner()
        if verloren:
            Session.punkte_zuruecksetzen()
        return verloren

    def gegner_eingedrungen(self):
        eingedrungen = 0
        for gegner in self.gegner:
            if gegner.status == "aktiv":
                if gegner.X <= (SPIELERX + spieler.bild.get_width() / len(SPIELERBILDBEREICH)) and (
                        abs(spieler.Y - gegner.Y) < 40):
                    gegner.status = "eingedrungen"
                    eingedrungen += 1
                    spieler.langsamer()
                    pygame.mixer.Sound.play(self.zuende1)
            else:
                if gegner.status == "eingedrungen":
                    eingedrungen += 1
        verloren = eingedrungen >= EINGEDRUNGENENDE
        if verloren:
            Session.punkte_zuruecksetzen()
        return verloren

    def zeichne_gegner(self):
        for gegner in self.gegner:
            fenster.blit(gegner.bild, (gegner.X, gegner.Y))

    def zeichne_kugellager(self):
        for x in range(self.maxversuche - self.versuche):
            fenster.blit(self.kugelbild, (0, H - (x * 10) - 20))

    def spielstand(self):
        text = "{} Tropfen für {} Milbe(n) Punkte: {} Highscore: {} Level: {}".format(
            self.maxversuche - self.versuche,
            self.anzahl_aktive_gegner(),
            Session.punkte,
            self.highscore, Session.level + 1)
        if spiel.in_gefahr():
            textfarbe = ROT
        else:
            textfarbe = SCHWARZ
        return font.render(text, True, textfarbe)

    def erzeuge_gegner(self):
        for x in range(self.anzahlgegner):
            self.gegner.append(Gegner())

    def bewege_gegner(self):
        for gegner in self.gegner:
            if gegner.status == "aktiv":
                gegner.Y += gegner.bewegung

                if gegner.Y < 0:
                    gegner.bewegung *= -1
                    gegner.X -= GEGNERSPRUNGX

                if gegner.Y > H - (gegner.offsety * 2):
                    gegner.bewegung *= -1
                    gegner.X -= GEGNERSPRUNGX
            else:
                gegner.Y = spieler.Y

    def loesche_gegner(self, i):
        del self.gegner[i]


# Spieler
class Spieler:
    def __init__(self):
        self.bild = pygame.image.load(SPIELERBILD)
        self.Y = 300
        self.bewegung = 0
        self.animbereich = 0
        self.bereich = SPIELERBILDBEREICH
        self.bewegungfaktor = 1
        self.bildbreite = self.bild.get_width() / len(SPIELERBILDBEREICH)

    def nach_oben(self):
        self.bewegung = -SPIELERBEWEGUNG * self.bewegungfaktor

    def nach_unten(self):
        self.bewegung = SPIELERBEWEGUNG * self.bewegungfaktor

    def anhalten(self):
        self.bewegung = 0

    def langsamer(self):
        self.bewegungfaktor *= SPIELERBEWEGUNGFAKTOR

    def bewege(self):
        # Spiellogik
        if self.bewegung != 0:
            self.Y += self.bewegung

        if self.Y < 0:
            self.Y = 0
            self.bewegung = 0

        if self.Y > H - 90:
            self.Y = H - 90
            self.bewegung = 0

    def zeichne(self):
        self.animbereich += 1

        if self.animbereich > 5:
            self.animbereich = 0

        fenster.blit(self.bild, (SPIELERX, self.Y), self.bereich[self.animbereich])


# Kugel
class Kugel:
    def __init__(self):
        self.bild = pygame.image.load(KUGELBILD)
        self.imaus = pygame.mixer.Sound(IMAUSSOUND)
        self.schuss = pygame.mixer.Sound(SCHUSSSOUND)
        self.X = 0
        self.Y = 0
        self.Xbewegung = KUGELBEWEGUNG
        self.status = False
        self.offsetx = (self.bild.get_width() / 2)
        self.offsety = (self.bild.get_height() / 2)
        self.startx = SPIELERX + spieler.bildbreite
        self.startyoffset = spieler.bild.get_height() / 2

    def zeichne(self):
        if self.status:
            fenster.blit(self.bild, (self.X, self.Y))

    def feuern(self, posY):
        self.status = True
        self.X = self.startx
        self.Y = posY + self.startyoffset
        pygame.mixer.Sound.play(self.schuss)
        spiel.versuche += 1

    def bewege(self):
        self.X += self.Xbewegung

    def kollisionskontrolle(self, gegner, durchgang):
        if gegner.status == "eingedrungen":
            return False

        # Mittelpunkte
        kugelx = self.X + self.offsetx
        kugely = self.Y + self.offsety
        gegnerx = gegner.X + gegner.offsetx
        gegnery = gegner.Y + gegner.offsety

        abstand = int(math.sqrt(math.pow(kugelx - gegnerx, 2) + math.pow(kugely - gegnery, 2)))
        # print("Abstand zwischen Kugel und Gegner: ", abstand)
        getroffen = abstand < gegner.offsety + self.offsety

        if getroffen:
            self.status = False
            gegner.spiele_treffersound()
            spiel.hat_gegner_getroffen(durchgang)

        return getroffen

    def aus_dem_feld(self):
        ausserhalb = (self.X - self.offsetx) > W
        if ausserhalb:
            pygame.mixer.Sound.play(self.imaus)
            self.status = False
        return ausserhalb


class Gegner:
    def __init__(self):
        self.bild = pygame.image.load(random.choice(GEGNERBILDER))
        self.offsetx = (self.bild.get_width() / 2)
        self.offsety = (self.bild.get_height() / 2)
        self.X = random.randint(int(W / 2) - 100, W - self.offsetx * 3)
        self.Y = random.randint(self.offsety * 2, H - self.offsety * 2)
        self.bewegung = random.randint(-GEGNERBEWEGUNG[Session.level], GEGNERBEWEGUNG[Session.level])
        self.status = "aktiv"
        self.getroffensound = pygame.mixer.Sound(random.choice(GETROFFENSOUND))

    def spiele_treffersound(self):
        pygame.mixer.Sound.play(self.getroffensound)


def zeige_ende_bildschirm(status, text=''):
    pygame.mixer.music.stop()
    if status == "gewonnen":
        pygame.time.wait(2000)
        sound = pygame.mixer.Sound(ERFOLGSOUND)
        pygame.mixer.Sound.play(sound)
        inhalt = "Spiel gewonnen! " + text
    else:
        sound = pygame.mixer.Sound(SCHEITERNSOUND1)
        pygame.mixer.Sound.play(sound)
        pygame.time.wait(2000)
        sound = pygame.mixer.Sound(SCHEITERNSOUND2)
        pygame.mixer.Sound.play(sound)
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
    pygame.mixer.Sound.stop(sound)


def erzeuge_neues_spiel(naechstes_level=False):
    global spiel, spieler, kugel
    # Neue Instanzen erzeugen
    if naechstes_level:
        Session.naechstes_level()
    Session.setze_startpunkte()
    spiel = Spiel()
    spieler = Spieler()
    kugel = Kugel()


def zeichne_spielfeld():
    # Spielfeld löschen
    fenster.fill(WEISS)
    fenster.blit(Session.hintergrund, (0, 0))

    # Spielstand ausgeben
    fenster.blit(spiel.spielstand(), (10, 10))

    # Spielfeld/figuren zeichnen

    # Spieler
    spieler.zeichne()

    # Kugel
    kugel.zeichne()
    spiel.zeichne_kugellager()

    # Gegner
    spiel.zeichne_gegner()

    # Fenster aktualisieren
    pygame.display.flip()
    clock.tick(FPS)


spiel = Spiel()
spieler = Spieler()
kugel = Kugel()

# Schleife Hauptprogramm
aktiv = True
while aktiv:
    # Überprüfen, ob Nutzer eine Aktion durchgeführt hat
    for event in pygame.event.get():
        # Beenden bei [ESC] oder [X]
        if event.type == QUIT:
            aktiv = False

        if event.type == KEYDOWN:
            # print("Spieler hat Taste gedrückt")

            # Taste für Spieler 1
            if event.key == K_UP:
                # print("Spieler hat Pfeiltaste hoch gedrückt")
                spieler.nach_oben()
            elif event.key == K_DOWN:
                # print("Spieler hat Pfeiltaste runter gedrückt")
                spieler.nach_unten()
            elif event.key == K_ESCAPE:
                aktiv = False

            elif event.key == K_SPACE:
                # print("Kugel abfeuern")
                # nur möglich, wenn keine Kugel sichtbar ist
                if not kugel.status:
                    kugel.feuern(spieler.Y)

        if event.type == KEYUP:
            # print("Spieler stoppt bewegung")
            spieler.anhalten()

    spieler.bewege()

    spiel.bewege_gegner()

    if kugel.status:
        kugel.bewege()

        durchgang = 0
        for gegner in spiel.gegner:
            getroffen = kugel.kollisionskontrolle(gegner, durchgang)

            if getroffen:
                break

            # Kugel verlässt den Bildschirm
            if kugel.aus_dem_feld():
                # Verloren, keine spiel.versuche mehr
                if spiel.keine_versuche_mehr():
                    zeige_ende_bildschirm("verloren", "Keine Honigtropfen mehr")
                    erzeuge_neues_spiel()

                # spiel.versuche reichen nicht mehr aus
                if spiel.zuwenig_versuche():
                    zeige_ende_bildschirm("verloren", "Zu viele Milben für zu wenig Honigtropfen")
                    erzeuge_neues_spiel()

                # Es ist bald zu Ende...
                if spiel.in_gefahr():
                    spiel.spiel_warnung()
            durchgang += 1

    # Spiel entschieden?
    # Gewonnen, keine Gegner mehr
    if spiel.keine_gegner_mehr():
        zeichne_spielfeld()
        zeige_ende_bildschirm("gewonnen")
        erzeuge_neues_spiel(True)

    # Verloren, Gegner sind eingedrungen
    if spiel.gegner_eingedrungen():
        zeichne_spielfeld()
        zeige_ende_bildschirm("verloren", "Zu viele Milben haben dich erwischt")
        erzeuge_neues_spiel()

    zeichne_spielfeld()
