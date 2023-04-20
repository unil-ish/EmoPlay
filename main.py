"""
    General pipeline for EmoPlay
"""

import glob

# Custom classes
import play
import senticnet
import vizualisation

def main():
    """ Main function """

    # (1) Loads senticnet [mandatory for emotions' search]
    stcnet = senticnet.Senticnet()

    # (2) Finds all xml files
    plays = glob.glob("theater/*.xml")

    # (3) Makes the whole process for each xml file [takes a long time]
    for path in plays:

        # (4) Loads the play into a new object
        p = play.Play(path)

        # Avoids processing not found plays
        if p.speech_amount > 0:
            # (5) Loops through each speech of each character to get
            # the emotions for each speech of the play
            for character in p.characters:
                for speech in character.speeches:
                    # Compute overall emotions of each speech
                    speech.getEmotions(stcnet)

            # (6) Exports the data to CSV, for later reuse
            p.to_csv()

            # (7) If needed, reimports everything from the csv
            #path_csv = "path/to/csv"
            #p.from_csv(path_csv)

            # (8) Generates and saves plots
            
            # UNCOMMENT WHAT FOLLOWS IF WISHED !

            # Bar plot for speeches
            #barPlotSpeeches = vizualisation.Vizualisation(p, "bps")
            #barPlotSpeeches.plot(True)

            # Bar plot for words
            #barPlotWords = vizualisation.Vizualisation(p, "bpw")
            #barPlotWords.plot(True)

            # Emotions by character
            #emotionByCharacter = vizualisation.Vizualisation(p, "ebc")
            #emotionByCharacter.plot(True)

            # Emotions by act
            #emotionByAct = vizualisation.Vizualisation(p, "eba")
            #emotionByAct.plot(True)

if __name__ == '__main__':
    main()
