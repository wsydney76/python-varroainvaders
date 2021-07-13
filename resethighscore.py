import shelve
SCOREDATEI = "files/score.txt"
scoredatei = shelve.open(SCOREDATEI)

def score_eingabe():
    while True:
        score = input("Bitte neuen Score eingeben oder x zum Beenden: ")
        if score == 'x':
            return 'x'

        try:
            score = int(score)
        except ValueError:
            print("Bitte Zahl eingeben")
        else:
            if score < 0:
                print("Bitte positive Zahl eingeben")
            else:
                return score


score = score_eingabe()

if score == 'x':
    exit()

scoredatei['highscore'] = score
print('Highscore gesetzt')