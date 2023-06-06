import pandas as pd
import nltk
import pywsd
import time

from pywsd.similarity import max_similarity as maxsim

import senticnet

# from nltk.corpus import wordnet

# Uncomment this if needed
# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('wordnet')
# nltk.download('omw-1.4')

class Essay:
    """
        Class Essay
        
        input:
        ----------
            - A text formatted as a string
            with associated tags (T/F) on
            each OCEAN dimension

        output:
        ----------
            - A csv file with the id of each essay,
            the presence of OCEAN dimension on the
            essay (input data) and the average SenticNet
            value of each essay on each SenticNet dimension
    """

    def __init__(self, essay=None):
        """
            Pre-process data for easy use later
        """

        # Store data for later reuse
        self.id = essay["#AUTHID"]
        self.fe = essay
        self.text = essay["text"]
        self.text_disambiguate = None
        self.tokenized_text = None

        # OCEAN dimensions
        self.agreeableness = True if essay["cAGR"] == 'y' else False
        self.conscientiousness = True if essay["cCON"] == 'y' else False
        self.extroversion = True if essay["cEXT"] == 'y' else False
        self.neuroticism = True if essay["cNEU"] == 'y' else False
        self.openness = True if essay["cOPN"] == 'y' else False

        # SenticNet dimsnsions
        self.attitude = None
        self.introspection = None
        self.sensitivity = None
        self.temper = None
        self.polarity = None

        # Tokenize the essay
        self.tokenize()

    def tokenize(self):
        """ Converts a string into a list of words. """

        # NLTK tokenization
        self.tokenized_text = nltk.word_tokenize(self.text)

        return self.tokenized_text

    def getDimensions(self, stcnet):
        """ Gets values on SenticNet dimensions for a given essay. """

        # Check that stcnet is loaded
        if not stcnet.senticnet:
            return None

        # Variables
        pol_emotions = []
        att_emotions = []
        int_emotions = []
        sen_emotions = []
        tem_emotions = []

        tokenized_emotions = []

        # First, determine emotions for each token
        iterator = 0
        for t in self.tokenized_text:
            # Lower case
            t = t.lower()

            # Find emotion
            pol_emotion = stcnet.polarityOf(t)
            int_emotion = stcnet.introspectionOf(t)
            tem_emotion = stcnet.temperOf(t)
            att_emotion = stcnet.attitudeOf(t)
            sen_emotion = stcnet.sensitivityOf(t)

            # Add to dict for dimensions
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

        # Find mean on each dimension
        if pol_emotions:
            self.polarity = round(sum(pol_emotions)/len(pol_emotions), 5)

        if int_emotions:
            self.introspection = round(sum(int_emotions)/len(int_emotions), 5)

        if tem_emotions:
            self.temper = round(sum(tem_emotions)/len(tem_emotions), 5)

        if att_emotions:
            self.attitude = round(sum(att_emotions)/len(att_emotions), 5)

        if sen_emotions:
            self.sensitivity = round(sum(sen_emotions)/len(sen_emotions), 5)

        # Success message
        print(f'# Successfully extracted dimensions values for essay {self.id}. Polarity : {self.polarity}, Attitude : {self.attitude}, Introspection : {self.introspection}, Sensitivity : {self.sensitivity}, Temper : {self.temper}')

        return

def main():
    """
        Main
    """
    
    # Dataframe format for the output data
    export_df = pd.DataFrame(columns=[
        'id',
        'stcnet_attitude',
        'stcnet_introspection',
        'stcnet_sensitivity',
        'stcnet_temper',
        'stcnet_polarity',
        'ocean_agreeableness',
        'ocean_conscientiousness',
        'ocean_extroversion',
        'ocean_neuroticism',
        'ocean_openness'
    ])
    
    # (1) Load senticnet [mandatory for emotions' search]
    stcnet = senticnet.Senticnet()

    # (2) Find csv containing essays
    paths = ["datasets/essays.csv"]
    
    # List of essays
    essays = []

    # (3) Extract features for each essay
    for path in paths:
        # Reads data to dataframe
        try:
            data = pd.read_csv(path)
        except IOError:
            print('# Could not read file!')
    
        # (4) For each essay, build object
        for index, essay in data.iterrows():
            essay = Essay(essay) # pre-process the data
            essay.getDimensions(stcnet) # find emotions associated to each essay

            # Append to df
            export_df = export_df.append({
                'id':essay.id,
                'stcnet_attitude':essay.attitude,
                'stcnet_introspection':essay.introspection,
                'stcnet_sensitivity':essay.sensitivity,
                'stcnet_temper':essay.temper,
                'stcnet_polarity':essay.polarity,
                'ocean_agreeableness':essay.agreeableness,
                'ocean_conscientiousness':essay.conscientiousness,
                'ocean_extraversion':essay.extroversion,
                'ocean_neuroticism':essay.neuroticism,
                'ocean_openness':essay.openness
            }, ignore_index=True)

    # (5) Export df
    export_df.to_csv('features_extractor.csv')

if __name__ == '__main__':
    main()

