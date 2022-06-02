"""
    Module Play
"""

import re
import pandas as pd
from bs4 import BeautifulSoup

# Custom classes
import character
import speech

class Play:
    """ Class Play """

    def __init__(self, path):
        """
            Creates an object from a TEI-encoded theater play.

            Various information are also stored in the object,
            such as the title of the play, the author,
            the first publication date, etc.

            The object makes it easy to access characters of
            the play and their respective speeches.
        """

        # Declaring attributes needed to describe the play
        self.path = path
        self.speaker_speech = pd.DataFrame(columns=['speaker', 'speech', 'scene'])
        self.title = '?'
        self.author = '?'
        self.date = '?'
        self.text = '?' # Raw, unstructured text, without speaker
        self.scenes = 0 # Amount of scenes in the play
        self.characters = [] # List of instanciated Character
        self.speech_amount = 0

        # Tries to open the file
        try:
            with open(self.path, 'r', encoding='utf-8') as xml_file:
                xml_file = xml_file.read()

                # Removes all <stage> tags before processing
                xml_file = re.sub(r'<stage>[^<]+?</stage>', ' ', xml_file)

                # Makes a bs object
                soup = BeautifulSoup(xml_file, 'xml')

                # Gets the title of the play
                self.title = re.sub(r'\s+', ' ', soup.find('title').text)

                # Gets the author of the play
                self.author = soup.find('author').text

                # Gets the date of publication
                self.date = soup.find('imprint').find('date').text

                # Finds all the scenes (if any)
                scenes = soup.find_all("div", attrs={"type" : "scene"})

                # Finds all acts (if no scene has been found)
                if len(scenes) < 1:
                    scenes = soup.find_all("div", attrs={"type" : "act"})

                # Finds body if no scene or act are found
                if len(scenes) < 1:
                    scenes = soup.find_all("body")

                # To store speech id
                speech_id = 1

                # Loops through each scene
                for s in scenes:
                    # Increments the number of scenes
                    self.scenes += 1

                    # Finds all "sp" tags in current scene
                    tags_sp = s.find_all('sp')

                    # Gets scene number (if available)
                    try:
                        scene_number = int(s["n"])
                    except:
                        scene_number = 1

                    # Loops through each sp
                    for _, sp in enumerate(tags_sp):
                        # Finding speaker
                        speaker = sp.find('speaker').text

                        # Skipping speakers that have long names
                        # because it happens that the speech gets confused
                        # with the speaker's name during encoding
                        if len(speaker) > 35 or speaker.count(' ') > 5:
                            continue

                        # Finds all other possible speech that
                        # a speaker can have (tags p and l)
                        tags = sp.find_all('p') + sp.find_all('l')

                        # Loops through all tags and adds to dataframe
                        for tag in tags:
                            tag = tag.text.strip()

                            # Stores in dataframe for easy retrieval
                            self.speaker_speech = pd.concat([
                                self.speaker_speech, self.speaker_speech.from_dict({
                                    'speaker':[speaker],
                                    'speech':[
                                        speech.Speech(
                                            tag,
                                            scene_number,
                                            speech_id)
                                        ],
                                    'scene':[scene_number]
                                })
                            ], ignore_index=True)

                            # Adds raw text
                            self.text += ' ' + tag

                            # Increments speech count
                            speech_id += 1

            self.speech_amount = speech_id

            # Once it's done, creates all Character's instance
            self.makeCharacters()

            # Success message
            print(f'''# Play "{self.title}" ({self.author}, {self.date}) with {self.scenes} scene(s), {len(self.characters)} character(s) and {self.speech_amount} speech(es) successfully loaded!''')

        # Returns empty dataframe if the file could not be opened/found
        except IOError:
            print('# Note : The supplied file was not found. Skipping process.')

    def makeCharacters(self):
        """ Creates a list of Characters to handle speeches easily. """

        # Gets a list of unique names for the characters
        characters = self.speaker_speech.speaker.unique()

        # Loops through each name and adds speech to character object
        for char in characters:
            speeches_df   = self.speaker_speech[self.speaker_speech.speaker == char]
            speeches_list = []

            # Skips names appearing once (mistakes while encoding the XML)
            if len(speeches_df) < 2:
                continue

            # Adds each speech object to a temporary list
            for _, row in speeches_df.iterrows():
                speeches_list.append(row.speech)

            # Creates Character instance and links speeches to it
            newCharacter = character.Character(char)
            newCharacter.speeches = speeches_list

            # Stores Character instance in self.characters (list)
            self.characters.append(newCharacter)

    def getCharacters(self):
        """ Displays all characters in the play. """

        # Loops through each character and find their name
        character_names = [character.name for character in self.characters]
        character_names.sort()

        return character_names

    @property
    def speechAmount(self):
        """ Displays the amount of speech in the whole play. """

        return len(self.speaker_speech)

    @property
    def countWords(self):
        """ Displays the length of the play in words. """

        words = 0

        # Loops through each character
        for char in self.characters:
            # Loops through each speech
            for speech in char.speeches:
                # Increment counter
                words += speech.countWords

        return words

    def to_csv(self):
        """ Exports a play to a CSV file. """
    
        # Constructs dataframe
        export_df = pd.DataFrame(columns=[
            'id',
            'speaker',
            'disambiguation_time',
            'pywsd_output',
            'tokens_text',
            'tokens_emotions',
            'scene',
            'primary_emotion',
            'secondary_emotion',
            'text_disambiguate',
            'speech'
        ])

        # Loops through each character
        for c in self.characters:
            # Loops through each speech
            for s in c.speeches:
                export_df = pd.concat([export_df,export_df.from_dict({
                    'id':[s.id],
                    'speaker':[c.name],
                    'disambiguation_time':[s.disambiguation_time],
                    'pywsd_output':[s.pywsd_output],
                    'tokens_text':[s.tokenized_text],
                    'tokens_emotions':[s.tokenized_emotions],
                    'scene':[s.scene],
                    'primary_emotion':[s.primary_emotion],
                    'secondary_emotion':[s.secondary_emotion],
                    'text_disambiguate':[s.text_disambiguate],
                    'speech':[s.text]
                })], ignore_index=True)

        # Saves csv to same folder than the script
        try:
            csv_name = self.title + ' - Exported.csv'
            export_df.to_csv(csv_name, index=False)
            print('# Successfully exported to csv!')

        except IOError:
            print('# An error occured while exporting to csv!')

    def from_csv(self, path):
        """ Loads a play previously exported in a CSV file. """

        try:
            # Loads CSV
            csv = pd.read_csv(path)

            # Empties dataframe
            self.speaker_speech = pd.DataFrame(columns=['speaker', 'speech', 'scene'])
            self.characters = [] # List of instanciated Character

            # Finds all characters in the play and create object for each
            for row in csv.iterrows():
                # Stores variables used later
                text = row[1].speech
                scene = row[1].scene
                speech_id = row[1].id

                # Create new speech object
                s = speech.Speech(text, scene, speech_id)

                # Adds other properties to the object
                s.pywsd_output = row[1].pywsd_output
                s.tokenized_text = row[1].tokens_text
                s.tokenized_emotions = row[1].tokens_emotions
                s.primary_emotion = row[1].primary_emotion
                s.secondary_emotion = row[1].secondary_emotion
                s.text_disambiguate = row[1].text_disambiguate
                s.disambiguation_time = row[1].disambiguation_time

                # Adds to play dataframe
                speaker = row[1].speaker
                self.speaker_speech = pd.concat([self.speaker_speech,self.speaker_speech.from_dict({
                    'speaker':[speaker],
                    'speech':[s],
                    'scene':[scene]
                })], ignore_index=True)

            # Sets max scene value
            self.scene = scene

            # Makes character
            self.makeCharacters()

            # Callback
            print("# Successfully loaded state from CSV file!")

        except TypeError:
            print("# The play state could not be loaded from CSV file!")

    def __str__(self):
        """ Returns the name of the play when printed. """
        return self.title

    def __len__(self):
        """ Returns the amount of words in the play. """
        return self.countWords
