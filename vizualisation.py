"""
    Module Vizualisation
"""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

class Vizualisation:
    """
        Vizualisation class.

        It is used to display statistics of the play.
        Optionnally, each graphic can be exported as svg.

    """

    vtypes = ["bps", "bpw", "ebc", "eba"]

    def __init__(self, play, vtype):
        """
            Constructor of the Vizualisation class.
        Args:
            play: The play to vizualise. (Play)
            vtype:  The type of vizualisation to display. (str)
        """
        if vtype not in self.vtypes:
            print('# This vizualisation does not exist.')
            print(f"# Please choose between {', '.join(self.vtypes)}")
            return

        self.play = play
        self.vtype = vtype

    def plot(self, save=False):
        """
            Calls the right method depending on the vizualisation type,
            and optionnally saves the graphic inside the same directory.
        Args:
            save: If the graphic must be saved. (bool)
        Returns: None
        Examples:
            >>> viz = Vizualisation(play, "bps")
            >>> viz.plot()
            >>> viz.plot(save=True)

        """
        if self.vtype == "bps":
            self.barPlotSpeech(save)
        elif self.vtype == "bpw":
            self.barPlotWords(save)
        elif self.vtype == "ebc":
            self.emotionsByCharacter(save)
        elif self.vtype == "eba":
            self.emotionsByAct(save)
        else:
            print("# No plot found!")

    def barPlotSpeech(self, save=False):
        """ Displays what speaker spoke the most (speeches).
         Args:
            save: If the graphic must be saved. (bool)
        Returns: None
        Examples:
            >>> viz = Vizualisation(play, "bps")
            >>> viz.barPlotSpeech()
            >>> viz.barPlotSpeech(save=True)

         """

        valeurs = {}

        # Make statistics
        for c in self.play.characters:
            valeurs[c.name] = c.countSpeeches

        # Orders the dict by the value
        valeursList = sorted((value, key) for (key, value) in valeurs.items())
        valeursList.reverse()
        valeursSorted = dict([(k, v) for v, k in valeursList])

        keys = list(valeursSorted.keys())[:5]
        values = list(valeursSorted.values())[:5]

        # Renders plot
        plt.figure(figsize=(8,6))
        ax = sns.barplot(x=values, y=keys)
        plt.title('Top 5 characters who spoke the most')
        ax.set(xlabel='Speech amount', ylabel='Character')
        plt.subplots_adjust(left=0.15)

        # If must save the image
        if save:
            name = self.play.title + " - Bar plot of speeches.svg"
            plt.savefig(name)
            print("# Successfully saved figure!")
        else:
            plt.show()

    def barPlotWords(self, save=False):
        """ Displays what speaker spoke the most (words).
        Args:
            save: If the graphic must be saved. (bool)
        Returns: None
        Examples:
            >>> viz = Vizualisation(play, "bpw")
            >>> viz.barPlotWords()
            >>> viz.barPlotWords(save=True)

        """

        valeurs = {}

        # Make statistics
        for c in self.play.characters:
            valeurs[c.name] = c.countWords

        # Orders the dict by the value
        valeursList = sorted((value, key) for (key, value) in valeurs.items())
        valeursList.reverse()
        valeursSorted = dict([(k, v) for v, k in valeursList])

        keys = list(valeursSorted.keys())[:5]
        values = list(valeursSorted.values())[:5]

        # Renders plot
        plt.figure(figsize=(8,6))
        ax = sns.barplot(x=values, y=keys)
        plt.title('Top 5 characters who spoke the most')
        ax.set(xlabel='Word amount', ylabel='Character')
        plt.subplots_adjust(left=0.15)

        # If must save the image
        if save:
            name = self.play.title + " - Bar plot of words.svg"
            plt.savefig(name)
            print("# Successfully saved figure!")
        else:
            plt.show()

    def emotionsByCharacter(self, save=False):
        """ Displays emotion across acts for some characters.
        Args:
            save: If the graphic must be saved. (bool)
        Returns: None
        Examples:
            >>> viz = Vizualisation(play, "ebc")
            >>> viz.emotionsByCharacter()
            >>> viz.emotionsByCharacter(save=True)

            """

        # Gets the three characters that spoke the most
        valeurs = {}

        for c in self.play.characters:
            valeurs[c.name] = c.countSpeeches

        # Orders the dict by the value
        valeursList = sorted((value, key) for (key, value) in valeurs.items())
        valeursList.reverse()
        valeursSorted = dict([(k, v) for v, k in valeursList])

        keys = list(valeursSorted.keys())[:4]

        # Creates new df with values per speech
        df = pd.DataFrame(columns=['speaker', 'emotion', 'scene'])

        for c in self.play.characters:
            for s in c.speeches:
                emotions = [str(s.primary_emotion), str(s.secondary_emotion)]
                for e in emotions:
                    if e != 'nan':
                        df = pd.concat([df,df.from_dict({
                            'speaker':[c.name],
                            'emotion':[e],
                            'scene':[s.scene]
                        })], ignore_index=True)

        # Drops useless characters
        df = df[df.speaker.isin(keys) == True]

        # Gets all emotions
        emotions = df.drop_duplicates(subset=['emotion']).emotion.tolist()
        emotions.sort()
        emotions_amount = {}

        # Gets the five most frequent emotions only
        for e in emotions:
            emotions_amount[e] = sum(df['emotion'] == e)

        # Sorts dict by values
        emotions_amount = sorted(emotions_amount.items(), key=lambda x:x[1])
        emotions_amount.reverse()

        # Keeps only the first 5 emotions
        kept_emotions = []

        for i in range(len(emotions_amount)):
            kept_emotions.append(emotions_amount[i][0])

        kept_emotions = kept_emotions[:5]

        # Drops emotions that are not in the top 5
        df = df[df.emotion.isin(kept_emotions) == True]

        # Renders plot
        plt.figure(figsize=(16,12))
        figr = sns.displot(df, x="speaker", hue="emotion", multiple="dodge")
        figr.set(xlabel='Speaker', ylabel='Emotion count')
        plt.title('Emotions for the main characters')
        plt.subplots_adjust(top=0.9)

        # If must save the image
        if save:
            name = self.play.title + " - Emotions for the main characters.svg"
            plt.savefig(name)
            print("# Successfully saved figure!")
        else:
            plt.show()

    def emotionsByAct(self, save=False):
        """ Displays the most frequent emotions for each act.
        Args:
            save: If the graphic must be saved. (bool)
        Returns: None
        Examples:
            >>> viz = Vizualisation(play, "eba")
            >>> viz.emotionsByAct()
            >>> viz.emotionsByAct(save=True)
            """

        # Creates new df with emotions and acts
        df = pd.DataFrame(columns=['emotion', 'scene'])

        for c in self.play.characters:
            for s in c.speeches:
                emotions = [str(s.primary_emotion), str(s.secondary_emotion)]
                for e in emotions:
                    if e != 'nan':
                        df = pd.concat([df,
                            df.from_dict({
                                'emotion':[e],
                                'scene':[str(s.scene)]
                            })], ignore_index=True)

        # Renders plot
        plt.figure(figsize=(16,12))
        fig = sns.histplot(data=df, x="scene", hue="emotion", multiple="dodge", shrink=.8)
        fig.set(xlabel='Act or Scene', ylabel='Emotions count')
        plt.title('Emotions for each act or scene in the play')
        plt.subplots_adjust(top=0.9)

        # If must save the image
        if save:
            name = self.play.title + " - Emotions by act.svg"
            plt.savefig(name)
            print("# Successfully saved figure!")
        else:
            plt.show()
