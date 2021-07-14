# Importieren u. initialisieren der Pygame-Bibliothek
from shelve import DbfilenameShelf

import pygame
from pygame.locals import *
from pygame.mixer import Sound
from pygame.surface import Surface

import random
import math
import shelve

# Variablen/KONSTANTEN setzen

# Fensterbreite
W: int = 800
# Fensterhöhe
H: int = 600
# Frames per second
FPS: int = 60
# Farben
SCHWARZ: tuple[int, int, int] = (0, 0, 0)
WEISS: tuple[int, int, int] = (255, 255, 255)
ROT: tuple[int, int, int] = (255, 0, 0)
# Level bei Start
STARTLEVEL: int = 0
# Punktevergabe: Geschwindigkeit * Multiplikator
PUNKTEMULTIPLIKATORBEWEGUNG: int = 200
# Punktevergabe: Entfernung * Multiplikator
PUNKTEMULTIPLIKATORENTFERNUNG: float = 2.0
# Anzahl/Geschwindigkeit Gegner je Level
MINGEGNER: list[int] = [2, 5, 10, 15, 20, 25, 30, 35]
MAXGEGNER: list[int] = [5, 10, 15, 20, 25, 30, 35, 40]
GEGNERBEWEGUNG: list[int] = [180, 180, 240, 300, 360, 420, 480, 540]
# 1 Kugel pro Gegner, plus diese Reserve
RESERVEKUGELN: int = 10
# Übrige Gegner, wenn Warnung gespielt werden soll
INGEFAHR: int = 3
# Spiel ist zu Ende, wenn diese Anzahl Gegner eingedrungen ist
EINGEDRUNGENENDE: int = 3
# Kugelgeschwindigkeit in Pixel/Sekunde
KUGELBEWEGUNG: int = 600
# Nährung in Pixel wenn Gegner Bildschirmende erreicht
GEGNERSPRUNGX: int = 30
# Keine Gegner links dieser Grenze platzieren
GEGNERLINKEGRENZE: int = 250
# Spielergeschwindigkeit in Pixel/Sekunde
SPIELERBEWEGUNG: int = 420
# Horizontale Spielerposition (linke Ecke)
SPIELERX: int = 50
# Um diesen Faktor wird die Spielergeschwindigkeit bei Eindringen eines Gegners reduziert
SPIELERBEWEGUNGFAKTOR: float = 0.8
# Fensterbeschriftunt
CAPTION: str = "Varroa Invaders"

# Bilder
HINTERGRUNDBILD: str = "bilder/bienenstock1.jpg"
SPIELERBILD: str = "bilder/biene-sprite-sheet1.png"
# Animationsbereiche des Spielerbildes
SPIELERBILDBEREICH: list[tuple[int, int, int, int]] = [
    (0, 0, 100, 100),
    (101, 0, 100, 100),
    (202, 0, 100, 100),
    (303, 0, 100, 100),
    (404, 0, 100, 100),
    (505, 0, 100, 100)
]
# Nach sovielen Frames soll der Animationsbereich gewechselt werden.
FRAMESPROBEREICH: int = 3

KUGELBILD: str = "bilder/honigtropfen.png"
GEGNERBILDER: list[str] = ['bilder/varroa.png', 'bilder/varroa2.png', 'bilder/varroa3.png', 'bilder/varroa4.png',
                           'bilder/varroa5.png', 'bilder/varroa6.png']
ERFOLGENDEBILD: str = "bilder/biene.jpg"
SCHEITERNENDEBILD: str = "bilder/totebiene.gif"
HINTERGRUNDSOUND: str = "sound/bienensummen.mp3"

# Sounds
SIRENENSOUND: str = "sound/sirene.mp3"
ERFOLGSOUND: str = "sound/tusch.mp3"
SCHEITERNSOUND1: str = "sound/help.mp3"
SCHEITERNSOUND2: str = "sound/time-to-say-goodbye.mp3"
SCHUSSSOUND: str = "sound/schuss.mp3"
GETROFFENSOUND: list[str] = ["sound/treffer.mp3", "sound/treffer2.mp3"]
IMAUSSOUND: str = "sound/imaus.mp3"

# Pfad zur Scoredatei
SCOREDATEI: str = "files/score.txt"

# Init Game GUI
pygame.init()
fenster = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)


# Globale Spielvariablen
class Session:
    level: int = 0
    punkte: int = 0
    startpunkte: int = 0
    hintergrund: Surface = pygame.image.load(HINTERGRUNDBILD)
    scoredatei: DbfilenameShelf = shelve.open(SCOREDATEI)

    @classmethod
    def setze_startpunkte(cls) -> None:
        """
        Speichert aktuellen Punktestand, kann mit punkte_zuruecksetzen wiederhergestellt werden
        """
        cls.startpunkte = cls.punkte

    @classmethod
    def punkte_zuruecksetzen(cls) -> None:
        """
        Setzt Punkte auf den Stand vor dem aktuellen Spiel zurück
        """
        cls.punkte = cls.startpunkte

    @classmethod
    def naechstes_level(cls) -> None:
        """
        Erhöhe das Spiellevel um 1, solange möglich
        """
        cls.level = min(len(MINGEGNER) - 1, cls.level + 1)

    @classmethod
    def vergebe_punkte(cls, gegner):
        """
        Punkte in Abhängigkeit von Gegnerposition und -geschwindigkeit vergeben
        :param gegner: Getroffener Gegner
        """
        cls.punkte += \
            abs(gegner.bewegung) * PUNKTEMULTIPLIKATORBEWEGUNG + \
            (W - gegner.Y) * PUNKTEMULTIPLIKATORENTFERNUNG


class Gegner:
    X: int
    Y: int
    bewegung: int
    bild: Surface
    getroffensound: Sound
    offsetx: int
    offsety: int
    status: str

    def __init__(self):
        self.bild = pygame.image.load(random.choice(GEGNERBILDER))
        self.offsetx = int(self.bild.get_width() / 2)
        self.offsety = int(self.bild.get_height() / 2)
        self.X = random.randint(GEGNERLINKEGRENZE, W - self.offsetx * 3)
        self.Y = random.randint(self.offsety * 2, H - self.offsety * 2)
        self.bewegung = random.randint(-int(GEGNERBEWEGUNG[Session.level] / FPS),
                                       int(GEGNERBEWEGUNG[Session.level] / FPS))
        self.status = "aktiv"
        self.getroffensound = pygame.mixer.Sound(random.choice(GETROFFENSOUND))

    def spiele_treffersound(self) -> None:
        """
        Spiele zufälliges Treffergeräusch
        """
        pygame.mixer.Sound.play(self.getroffensound)


# Spiel
class Spiel:
    aktiv: bool
    anzahlgegner: int
    gegner: list[Gegner]
    gegnergetroffen: int
    highscore: int
    kugelbild: Surface
    maxversuche: int
    sirenegespielt: bool
    versuche: int
    zuende1: Sound

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

    def spiel_warnung(self) -> None:
        """
        Warnsignal einmalig abspielen
        """
        if not self.sirenegespielt:
            sirene = pygame.mixer.Sound(SIRENENSOUND)
            pygame.mixer.Sound.play(sirene)
            self.sirenegespielt = True

    def hat_gegner_getroffen(self, index) -> None:
        """
        Gegner getroffen: Löschen, Punkte vergeben
        :param index: Index in Gegner-Liste
        :return: Gegner getroffen?
        """

        gegner: Gegner = self.gegner[index]
        Session.vergebe_punkte(gegner)
        self.gegnergetroffen += 1
        self.loesche_gegner(index)

    def anzahl_aktive_gegner(self) -> int:
        """
        Aktive, d.h. nicht gelöschte oder bereits eingedrungene Gegner zählen
        :return: Anzahl
        """
        anzahl: int = 0
        gegner: Gegner
        for gegner in self.gegner:
            if gegner.status == 'aktiv':
                anzahl += 1
        return anzahl

    def in_gefahr(self) -> int:
        return self.maxversuche - self.versuche <= (self.anzahl_aktive_gegner() + INGEFAHR)

    def keine_gegner_mehr(self) -> bool:
        """
        Prüft, ob keine aktiven Gegner mehr vorhanden sind, speichert ggfs. Highscore
        :return: Keine Gegner
        """
        gewonnen: bool = self.anzahl_aktive_gegner() == 0
        if gewonnen and Session.punkte > self.highscore:
            Session.scoredatei['highscore'] = Session.punkte
        return gewonnen

    def keine_versuche_mehr(self) -> bool:
        """
        Prüft, ob noch Versuche möglich sind
        :return: Versuche verbraucht?
        """
        verloren: bool = self.versuche >= self.maxversuche and self.anzahl_aktive_gegner()
        if verloren:
            Session.punkte_zuruecksetzen()
        return verloren

    def zuwenig_versuche(self) -> bool:
        """
        Prüft, ob noch genügend Versuche für aktive Gegner vorhanden sind
        :return: Versuche ungenügend
        """
        verloren: bool = self.maxversuche - self.versuche < self.anzahl_aktive_gegner()
        if verloren:
            Session.punkte_zuruecksetzen()
        return verloren

    def gegner_eingedrungen(self) -> bool:
        """
        Prüft ob neuer Gegner eingedrungen, klebt Gegner an Spieler, verloren wenn zu viele Gegner eingedrungen sind
        :return: Zu viele Gegner eingedrungen?
        """
        eingedrungen: int = 0
        gegner: Gegner
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

    def zeichne_gegner(self) -> None:
        """
        Zeichne alle Gegner
        """
        for gegner in self.gegner:
            fenster.blit(gegner.bild, (gegner.X, gegner.Y))

    def zeichne_kugellager(self) -> None:
        """
        Zeichne alle Kugeln im Lager
        """
        for x in range(self.maxversuche - self.versuche):
            fenster.blit(self.kugelbild, (0, H - (x * 10) - 20))

    def spielstand(self) -> Surface:
        """
        Erzeugt und formatiert Spielstand-Text
        :return: Textausgabe
        """
        text = "{} Tropfen für {} Milbe(n) Punkte: {} Highscore: {} Level: {}".format(
            self.maxversuche - self.versuche,
            self.anzahl_aktive_gegner(),
            int(Session.punkte),
            int(self.highscore), Session.level + 1)
        if spiel.in_gefahr():
            textfarbe = ROT
        else:
            textfarbe = SCHWARZ
        return font.render(text, True, textfarbe)

    def erzeuge_gegner(self) -> None:
        """
        Erstelle Gegner-Instanzen
        """
        for x in range(self.anzahlgegner):
            self.gegner.append(Gegner())

    def bewege_gegner(self) -> None:
        """
        Neue Koordinaten für alle Gegner errechnen
        """
        for gegner in self.gegner:
            if gegner.status == "aktiv":
                # Nächste Y-Koordinate
                gegner.Y += gegner.bewegung

                # Verlässt Bildschirm, Richtung umkehren
                if gegner.Y < 0:
                    gegner.bewegung *= -1
                    gegner.X -= GEGNERSPRUNGX
                if gegner.Y > H - (gegner.offsety * 2):
                    gegner.bewegung *= -1
                    gegner.X -= GEGNERSPRUNGX
            else:
                # Eingedrungen, an Spieler kleben
                gegner.Y = spieler.Y

    def loesche_gegner(self, i) -> None:
        """
        Getroffenen Gegner entfernen
        :param i: Index in der Gegner-Liste
        """
        del self.gegner[i]


# Spieler
class Spieler:
    Y: int
    animbereich: int
    animframe: int
    bereich: list[tuple[int, int, int, int]]
    bewegung: int
    bewegungfaktor: float
    bild: Surface
    bildbreite: float

    def __init__(self):
        self.bild = pygame.image.load(SPIELERBILD)
        self.Y = int(H / 2 - self.bild.get_height() / 2)
        self.bewegung = 0
        self.animbereich = 0
        self.animframe = 1
        self.bereich = SPIELERBILDBEREICH
        self.bewegungfaktor = 1
        self.bildbreite = self.bild.get_width() / len(SPIELERBILDBEREICH)

    def nach_oben(self) -> None:
        """
        Spieler nach oben bewegen
        """
        self.bewegung = int(-SPIELERBEWEGUNG / FPS * self.bewegungfaktor)

    def nach_unten(self) -> None:
        """
        Spieler nach unten bewegen
        """

        self.bewegung = int(SPIELERBEWEGUNG / FPS * self.bewegungfaktor)

    def anhalten(self) -> None:
        """
        Spielerbewegung stoppen
        """
        self.bewegung = 0

    def langsamer(self) -> None:
        """
        Spielerbewegungsgeschwindigkeit abbremsen
        """
        self.bewegungfaktor *= SPIELERBEWEGUNGFAKTOR

    def bewege(self) -> None:
        """
        Spielerkoordinaten für nächsten Frame berechnen
        """
        if self.bewegung != 0:
            self.Y += self.bewegung

        # Bewegung stoppen, wenn am Bildschirmrand
        if self.Y < 0:
            self.Y = 0
            self.bewegung = 0

        if self.Y > H - 90:
            self.Y = H - 90
            self.bewegung = 0

    def zeichne(self) -> None:
        """
        Animationsbereich des Spielerbildes ermitteln und zeichnen
        """

        # Bereich im aktuellen Frame ermitteln
        self.animframe += 1
        if self.animframe >= FRAMESPROBEREICH:
            self.animbereich += 1
            self.animframe = 1

        if self.animbereich > 5:
            self.animbereich = 0

        fenster.blit(self.bild, (SPIELERX, self.Y), self.bereich[self.animbereich])


# Kugel
class Kugel:
    bild: Surface
    imaus: Sound
    schuss: Sound
    X: int
    Y: int
    Xbewegung: int
    status: bool
    offsetx = int
    offsety = int
    startx = int
    startyoffset = int

    def __init__(self):
        self.bild = pygame.image.load(KUGELBILD)
        self.imaus = pygame.mixer.Sound(IMAUSSOUND)
        self.schuss = pygame.mixer.Sound(SCHUSSSOUND)
        self.X = 0
        self.Y = 0
        self.Xbewegung = int(KUGELBEWEGUNG / FPS)
        self.status = False
        self.offsetx = int(self.bild.get_width() / 2)
        self.offsety = int(self.bild.get_height() / 2)
        self.startx = int(SPIELERX + spieler.bildbreite)
        self.startyoffset = int(spieler.bild.get_height() / 2)

    def zeichne(self) -> None:
        """
        Kugel zeichnen, wenn unterwegs
        """
        if self.status:
            fenster.blit(self.bild, (self.X, self.Y))

    def feuern(self, posY) -> None:
        """
        Kugel aktivieren und Startkoordinaten setzen, Schussgeräusch, Versuche hochsetzen
        """
        self.status = True
        self.X = self.startx
        self.Y = posY + self.startyoffset
        pygame.mixer.Sound.play(self.schuss)
        spiel.versuche += 1

    def bewege(self) -> None:
        """
        Koordinaten für nächsten Frame berechnen
        """
        self.X += self.Xbewegung

    def kollisionskontrolle(self, gegner: Gegner, durchgang: int) -> bool:
        """
        Prüft Treffer anhand des Abstands zwischen Gegner und Kugel
        :param gegner: Aktuelle Gegner-Instanz
        :param durchgang: Index
        :return: hat getroffen?
        """
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
            # Kugel stoppen, Treffersound abspielen, Gegner löschen
            self.status = False
            gegner.spiele_treffersound()
            spiel.hat_gegner_getroffen(durchgang)

        return getroffen

    def aus_dem_feld(self) -> bool:
        """
        Hat die Kugel das Feld verlassen?
        """
        ausserhalb: bool = (self.X - self.offsetx) > W
        if ausserhalb:
            pygame.mixer.Sound.play(self.imaus)
            self.status = False
        return ausserhalb


def zeige_ende_bildschirm(status: str, text='') -> None:
    """
    Spiel beendet, zeige Ergebnisbildschirm
    :param status: gewonnen/verloren
    :param text:  Anzuzeigender Text
    """
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

    # Auf Benutzereingabe warten
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


def erzeuge_neues_spiel(naechstes_level: bool = False) -> None:
    """
    Neue Spielrunde erstellen: Session updaten,
    Instanzen spiel/spieler/kugel durch neue, frisch initialiierte Instanzen ersetzen
    :param naechstes_level: Soll Level erhöht werden?
    """
    global spiel, spieler, kugel

    if naechstes_level:
        Session.naechstes_level()
    Session.setze_startpunkte()

    # Neue Instanzen erzeugen
    spiel = Spiel()
    spieler = Spieler()
    kugel = Kugel()


def zeichne_spielfeld() -> None:
    """
    Spielfeld für nächsten Frame aufbauen, Hintergrund, Spielstand und alle Einzelobjekte zeichnen (lassen)
    neuen Bildschirm anzeigen und auf nächsten Frame warten
    """
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


# Instanzen für erste Runde erstellen
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

    # Neue Koordinaten für alle Objekte errechnen und Konsequenzen prüfen
    spieler.bewege()

    spiel.bewege_gegner()

    if kugel.status:
        kugel.bewege()

        # Alle Gegner auf Treffer prüfen und mögliches Spielende prüfen
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

    # Spielfeld anzeigen
    zeichne_spielfeld()
