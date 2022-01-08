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
# Fensterbeschriftung
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
