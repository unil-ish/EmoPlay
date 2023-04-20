"""
    Module Character
"""

class Character:
    """
        Character class.

        It is used to store the name and speeches of a character
        in the play, and allows the user to easily obtain the
        values they are looking for (e.g. the amount of total
        words spoken by a character, etc.).

        It requires the Speech class to work as expected.
    """

    def __init__(self, name):
        self.name = name
        self.speeches = []
        self.primary_emotion = None
        self.secondary_emotion = None

    def getSpeeches(self, scene=0):
        """ Returns the speeches of the specified scene. """

        speech_list = []

        # Loops through each speech
        for speech in self.speeches:
            # Testing scene if in the same scene
            if scene > 0:
                if speech.scene == scene:
                    speech_list.append(speech)
                else:
                    continue
            else:
                speech_list.append(speech)

        return speech_list

    def getEmotions(self, scene=0):
        """ Estimates the general emotion of the character throughout the play. """

        speeches = self.getSpeeches(scene)

        # Finds the average primary/secondary emotion for all the speeches
        primary_emotions = {}
        secondary_emotions = {}

        # Loops through each speech and stores emotions
        for speech in speeches:
            primary_emotion = speech.primary_emotion
            secondary_emotion = speech.secondary_emotion

            # Adds to dict (primary emotions)
            if primary_emotion in primary_emotions:
                primary_emotions[primary_emotion] += 1
            else:
                primary_emotions[primary_emotion] = 1

            # Adds to dict (secondary emotions)
            if secondary_emotion in secondary_emotions:
                secondary_emotions[secondary_emotion] += 1
            else:
                secondary_emotions[secondary_emotion] = 1

        # Removes "None"
        primary_emotions[None] = -1
        secondary_emotions[None] = -1

        # Finds max
        primary_emotion_max = max(primary_emotions, key=primary_emotions.get)
        secondary_emotion_max = max(secondary_emotions, key=secondary_emotions.get)

        # Finally setting values as attributes, if scene = 0 (i.e. whole play)
        if scene < 1:
            self.primary_emotion = primary_emotion_max
            self.secondary_emotion = secondary_emotion_max

        # Prints feedback
        print("# Emotions of {self.name} are {self.primary_emotion} and {self.secondary_emotion}!")

        return {"primary_emotion":primary_emotion_max, "secondary_emotion":secondary_emotion_max}

    @property
    def countWords(self):
        """ Counts the amount of words spoken by a character. """

        # Loops through each speech and makes the sum
        wordCount = sum([speech.countWords for speech in self.speeches])

        return wordCount

    @property
    def countSpeeches(self):
        """ Counts the amount of speeches belonging to a character. """

        return len(self.speeches)
