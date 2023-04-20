"""
    Module Speech
"""

import time
import pywsd
import nltk

from pywsd.similarity import max_similarity as maxsim

# from nltk.corpus import wordnet

# Uncomment this if needed
# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('wordnet')
# nltk.download('omw-1.4')

class Speech:
    """
        Speech class.

        It is used to store the text of each speech spoken
        by a character in the play, and allows the user
        to easily obtain the values they are looking for
        (e.g. the amount of words, the primary/secondary
        emotions of the speech, etc.).
    """

    def __init__(self, text, scene, speech_id):
        self.text = text
        self.text_disambiguate = None
        self.disambiguation_time = -1
        self.pywsd_output = None
        self.tokenized_text = None
        self.tokenized_emotions = None
        self.primary_emotion = None
        self.secondary_emotion = None
        self.polarity = None
        self.scene = scene
        self.id = speech_id
        self.introspection = None
        self.temper = None
        self.attitude = None
        self.sensitivity = None

    def tokenize(self):
        """ Converts a string into a list of words. """

        # Checks if text has already been disambiguated
        if not self.text_disambiguate:
            self.disambiguate()
            print(f'# Successfully disambiguated speech {self.id} in {self.disambiguation_time}s')

        # NLTK tokenization
        self.tokenized_text = nltk.word_tokenize(self.text_disambiguate)

        return self.tokenized_text

    @property
    def countWords(self):
        """ Counts the amount of token/words in the speech. """

        # Tokenizing if needed
        if not self.tokenized_text:
            self.tokenize()

        return len(self.tokenized_text)

    def disambiguate(self):
        """ Disambiguates words in a speech. """

        # Stores start
        disamb_start = time.time()

        # Disambiguates speech
        self.pywsd_output = pywsd.disambiguate(
            self.text,
            algorithm=maxsim,
            similarity_option='wup',
            keepLemmas=True
        )

        # Stores disambiguation time
        self.disambiguation_time = round(time.time() - disamb_start, 3)

        text_disambiguate = ''

        # Builds back the sentence
        for pywsd_tuple in self.pywsd_output:
            # Unpacking tuple of pywsd output
            (word, _, synset) = pywsd_tuple

            if not synset:
                text_disambiguate = text_disambiguate + ' ' + word

            # Using the first lemma's name for simplicity
            if synset:
                text_disambiguate = text_disambiguate + ' ' + synset.lemmas()[0].name()

        # Stores disambiguated speech
        self.text_disambiguate = text_disambiguate.strip()

        return self.text_disambiguate

    def getMaxEmotion(self, emotions):
        """
            Calculates the maximal emotion based on dict
            passed as argument and returns a single emotion.
        """

        # Sets None value to -1 to avoid meaningless results
        emotions[None] = -1

        # Checks if there is at least one emotion to search for
        # different than None
        if len(emotions) > 1:
            # Finds max
            emotion_max_01 = max(emotions, key=emotions.get)
            emotion_max_01_value = emotions[emotion_max_01]

            # Pops out max to see if there is ex-aequo
            emotions[emotion_max_01] = -1

            # Recalculates max
            emotion_max_02 = max(emotions, key=emotions.get)
            emotion_max_02_value = emotions[emotion_max_02]

            # Checks if the first value is different from the other
            if (emotion_max_01_value > emotion_max_02_value):
                return emotion_max_01
            # If the values are the same or if no value seems
            # to be different than the others, returns None
            else:
                return None

        else:
            return None

    def getEmotions(self, stcnet):
        """ Gets primary and secondary emotion for a speech. """

        # Verifes that stcnet is a senticnet dict
        if not stcnet.senticnet:
            return None

        # Various variables
        p_tokenized_emotions = {}
        s_tokenized_emotions = {}

        pol_emotions = []
        int_emotions = []
        tem_emotions = []
        att_emotions = []
        sen_emotions = []

        tokenized_emotions = []

        # If needs to be tokenized
        if not self.tokenized_text:
            self.tokenize()

        # First, determines emotions for each token
        iterator = 0
        for t in self.tokenized_text:
            # Lowering case
            t = t.lower()

            # (1) Verifies if one can find emotions for
            # the token directly in senticnet
            t_emotions = stcnet.emotionsOf(t)

            # Finds polarized emotion (if able)
            pol_emotion = stcnet.polarityOf(t)
            int_emotion = stcnet.introspectionOf(t)
            tem_emotion = stcnet.temperOf(t)
            att_emotion = stcnet.attitudeOf(t)
            sen_emotion = stcnet.sensitivityOf(t)

            # (2) If the emotions are not found, tries to
            # loop through whole synonyms of senticnet to find
            # the average emotion associated with the token
            if not t_emotions["primary_emotion"]:
                # Finds occurences of word in synonyms
                t_synonyms = stcnet.reverseSearch(t)

                # Finds average emotions, if possible
                t_emotions = stcnet.averageEmotionsOf(t_synonyms)

                continue

                # (3) If the emotions are still not found,
                # tries to find them in NLTK
                #if not t_emotions["primary_emotion"]:
                #    emotions_tuple = self.pywsd_output[iterator]
                #    (_, _, synset) = emotions_tuple
                #    if synset:
                #        t_synonyms = [str(lemma.name()) for lemma in synset.lemmas()]
                #        t_emotions = stcnet.averageEmotionsOf(t_synonyms)
            iterator += 1

            # Gets primary/secondary emotion for current word
            pe = t_emotions['primary_emotion']
            se = t_emotions['secondary_emotion']

            # Adds to dict for primary emotions
            if pe in p_tokenized_emotions:
                p_tokenized_emotions[pe] += 1
            else:
                p_tokenized_emotions[pe] = 1

            # Adds to dict for secondary emotions
            if se in s_tokenized_emotions:
                s_tokenized_emotions[se] += 1
            else:
                s_tokenized_emotions[se] = 1

            # Adds to dict for various mesures
            if pol_emotion:
                pol_emotions.append(pol_emotion)

            if int_emotion:
                int_emotions.append(int_emotion)

            if tem_emotion:
                tem_emotions.append(tem_emotion)

            if att_emotion:
                att_emotions.append(att_emotion)

            if sen_emotion:
                sen_emotions.append(sen_emotion)

            # Adds to list
            tokenized_emotions.append(t_emotions)

        # Finds mean for each mesure
        if pol_emotions:
            self.polarity = round(sum(pol_emotions)/len(pol_emotions), 3)

        if int_emotions:
            self.introspection = round(sum(int_emotions)/len(int_emotions), 3)

        if tem_emotions:
            self.temper = round(sum(tem_emotions)/len(tem_emotions), 3)

        if att_emotions:
            self.attitude = round(sum(att_emotions)/len(att_emotions), 3)

        if sen_emotions:
            self.sensitivity = round(sum(sen_emotions)/len(sen_emotions), 3)

        # Stores the result in an attribute of speech
        self.tokenized_emotions = tokenized_emotions

        # Finds mode of the speech and sets as attribute
        self.primary_emotion = self.getMaxEmotion(p_tokenized_emotions)
        self.secondary_emotion = self.getMaxEmotion(s_tokenized_emotions)

        # Success message
        print(f'# Successfully extracted emotions for speech id {self.id} : {self.primary_emotion}, {self.secondary_emotion} with an overall polarity of {self.polarity}.')

        return {"primary_emotion":self.primary_emotion, "secondary_emotion":self.secondary_emotion}
