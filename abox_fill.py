import json
import re
import pandas as pd
import rdflib
from rdflib import BNode, Graph, Literal, RDF, URIRef, Namespace

def abox_fill(csv, onto):
    """
        Fills the A-Box with the data in the csv file.

        input:
        ----------
            - A csv file containing the data for each
            speech in a theater play, with their associated
            emotions and values on SenticNet dimensions
            - A owl/rdf/xml file containing the modified
            version of the psy_model.rdf ontology

        
        output:
        -----------
            - A xml file containing the provided ontology
            filled with the data (A-Box) from the csv file
            provided as input.
    """

    from nltk.corpus import stopwords

    # ---
    # (1) Variable definition
    # ---

    # Predicate list for triplets
    w3_person                   = URIRef('http://www.w3.org/ns/ma-ont#Person')
    lemon_word                  = URIRef('http://lemon-model.net/lemon#Word')
    picca_speech                = URIRef('http://github.com/dpicca/ontologies/literary_characters_psychologica_profiles.owl#Speech')
    hasEmotion                  = URIRef('http://arsemotica.di.unito.it/artifacts/#hasEmotion')
    basic_emotion               = URIRef('http://arsemotica.di.unito.it/ontology#')
    property_saidWord           = URIRef('http://stcnet2ocean/property#saidWord')
    property_said               = URIRef('http://github.com/dpicca/ontologies/literary_characters_psychologica_profiles.owl#said')
    property_tokenOf            = URIRef('http://stcnet2ocean.com/property#tokenOf')
    property_hasToken           = URIRef('http://stcnet2ocean.com/property#hasToken')
    property_hasAttitude        = URIRef('http://stcnet2ocean.com/property#hasAttitude')
    property_hasIntrospection   = URIRef('http://stcnet2ocean.com/property#hasIntrospection')
    property_hasSensitivity     = URIRef('http://stcnet2ocean.com/property#hasSensitivity')
    property_hasTemper          = URIRef('http://stcnet2ocean.com/property#hasTemper')
    property_hasPolarity        = URIRef('http://stcnet2ocean.com/property#hasPolarity')
    property_representation     = URIRef('http://www.w3.org/ns/lemon/ontolex#representation')
    stcnet2ocean                = URIRef('http://stcnet2ocean.com/')
    dc_subject                  = URIRef('http://purl.org/dc/terms/subject')
    comment                     = URIRef('http://www.w3.org/2000/01/rdf-schema#comment')
    property_hOv                = URIRef('http://stcnet2ocean.com/property#hasOpennessValue')
    property_hCv                = URIRef('http://stcnet2ocean.com/property#hasConscientiousnessValue')
    property_hEv                = URIRef('http://stcnet2ocean.com/property#hasExtraversionValue')
    property_hAv                = URIRef('http://stcnet2ocean.com/property#hasAgreeablenessValue')
    property_hNv                = URIRef('http://stcnet2ocean.com/property#hasNeuroticismValue')
    property_hXv                = { 'o' : property_hOv, 'c' : property_hCv, 'e' : property_hEv, 'a' : property_hAv, 'n' : property_hNv }

    # Weights for the computation of Big 5 dimensions
    # - = p>.05, * = p<.05, ** = p<.01, *** = p<.001
    ponderation = [0.33, 0.43, 0.5, 1] # -, *, **, ***

    # Correlation values between OCEAN and SencitNet (2020) (based on the point-biserial correlation)
    abreviations = { 'att' : 'attitude', 'int' : 'introspection', 'sen' : 'sensitivity', 'tem' : 'temper', 'pol' : 'polarity'}
    rpb = {
        'att':{
            'o':'-0.057**',
            'c':'0.058**',
            'e':'0.056**',
            'a':'0.124',
            'n':'-0.035'
        },
        'int':{
            'o':'-0.061**',
            'c':'0.069***',
            'e':'0.047*',
            'a':'0.099',
            'n':'-0.081'
        },
        'sen':{
            'o':'0.015',
            'c':'0.048*',
            'e':'-0.013',
            'a':'0.03',
            'n':'-0.063**'
        },
        'tem':{
            'o':'-0.044*',
            'c':'0.095',
            'e':'0.047*',
            'a':'0.105',
            'n':'-0.058**'
        },
        'pol':{
            'o':'-0.058',
            'c':'0.093',
            'e':'0.056**',
            'a':'0.125',
            'n':'-0.083'
        }
    }

    # Stopwords
    stopwords = list(set(stopwords.words('english')))
    punctuation = [',', '.', ':', ';', '(', ')', '[', ']', '!', '?', '+', '-', '*', "'", '"', '/', ' ']

    # ---
    # (2) Import ontology data
    # ---

    # Base ontology, usually psy_model_edit.rdf
    g = Graph()
    g.parse(onto)

    # Data from the csv
    data = pd.read_csv(csv, sep='\t')

    # Find each character of the play
    characters = list(data['speaker'].unique())

    # Other variables used later
    characters_uri = {}
    characters_perso = {}

    # ---
    # (3) Add each character to graph
    # ---
    for char in characters:
        char_name = re.sub(r'[^a-zA-Z0-9]', '_', char.lower())
        uri = stcnet2ocean + char_name

        # Add each character
        g.add((uri, RDF.type, w3_person))

        # Save uri of each character (useful later)
        characters_uri[char_name] = uri

        # Build dict for personality (useful later)
        characters_perso[char_name] = { 'att' : [], 'int' : [], 'sen' : [], 'tem' : [], 'pol' : [] }

    # (4) Add token, speech and their link with the character saying them
    i_speech = 1
    i_token  = 1

    # (4.1) Add each token to the ontology, with associated emotion
    for index, row in data.iterrows():
        # Character's name
        char_name = re.sub(r'[^a-zA-Z0-9]', '_', row['speaker'].lower())

        # Speech's data
        tokens = eval(row['tokenized_text'])
        emotions = eval(row['tokenized_emotions'])

        # Useful for later retrival
        tokens_uri = []

        # Add each token to graph
        for i in range(len(tokens)):
            token = tokens[i]
            token = re.sub(r'[^a-zA-Z0-9]', '_', token.lower()).strip("_").strip()
            emotion = emotions[i]['primary_emotion'] # Seulement l'émotion primaire

            # Ignore stopwords, punctuation and empty words
            if token not in stopwords and token not in punctuation and token:        
                # Unique uri for each token
                uri_mot = URIRef('http://stcnet2ocean.com/token_' + str(i_token) )

                # (1) Create instance for each token
                g.add( ( uri_mot, RDF.type, lemon_word ) )

                # (2) Link graphical representation of each token with the token
                # https://www.dublincore.org/specifications/dublin-core/dcmi-terms/
                lit = token + '@en'
                g.add( ( uri_mot, dc_subject, Literal(lit) ) ) # dc_subject

                # (3) Add emotion associated with the token
                uri_emotion = basic_emotion + emotion.capitalize()
                g.add( ( uri_mot, hasEmotion, uri_emotion ) ) # hasEmotion

                # (4) Add character who said the token
                char = stcnet2ocean + char_name
                g.add( ( char, property_saidWord, uri_mot  ) ) # saidWord

                # Add position of token in speech
                g.add( ( uri_mot, comment, Literal(f'Token index in original Speech was {i}')  ) ) # token index

                # Save uri for later reuse
                tokens_uri.append( uri_mot )

            # ++
            i_token += 1

        # ---
        # (4.1) Add each speech to the ontology, with their associated tokens
        # ---
        uri_speech = URIRef('http://stcnet2ocean.com/') + char_name + '_speech_' + str(i_speech)

        # Add each speech to graph
        g.add( ( uri_speech, RDF.type, picca_speech ) ) # speech

        # Add character who said the speech
        char = characters_uri[char_name]
        g.add( ( char, property_said, uri_speech ) ) # said

        # Add each token linked to the speech
        for token in tokens_uri:
            g.add( ( token, property_tokenOf, uri_speech ) ) # tokenOf

        # ---
        # (4.3) Add SenticNet value on each dimension for the speech
        # ---

        # Attitude
        if row['avg_attitude'] > -2:
            g.add( ( uri_speech, property_hasAttitude, Literal(row['avg_attitude']) ) )
            characters_perso[char_name]['att'].append(row['avg_attitude'])

        # Introspection
        if row['avg_introspection'] > -2:
            g.add( ( uri_speech, property_hasIntrospection, Literal(row['avg_introspection']) ) )
            characters_perso[char_name]['int'].append(row['avg_introspection'])

        # Sensitivity
        if row['avg_sensitivity'] > -2:
            g.add( ( uri_speech, property_hasSensitivity, Literal(row['avg_sensitivity']) ) )
            characters_perso[char_name]['sen'].append(row['avg_sensitivity'])

        # Temper
        if row['avg_temper'] > -2:
            g.add( ( uri_speech, property_hasTemper, Literal(row['avg_temper']) ) )
            characters_perso[char_name]['tem'].append(row['avg_temper'])

        # Polarity
        if row['avg_polarity'] > -2:
            g.add( ( uri_speech, property_hasPolarity, Literal(row['avg_polarity']) ) )
            characters_perso[char_name]['pol'].append(row['avg_polarity'])

        # Act/scene
        g.add( ( uri_speech, comment, Literal(f"Speech was found in scene/act {row['scene']}, with speech position {index}/{len(data)}") ) )

        # ++
        i_speech += 1

    # ---
    # (5.1) Compute mean value on each SenticNet dimension for the whole play
    # ---
    average_personnality = { 'att' : [], 'int' : [], 'sen' : [], 'tem' : [], 'pol' : [] }
    
    # Store each value for each SenticNet dimension for the whole play
    for character in characters_perso:
        for k in characters_perso[character]:
            for v in characters_perso[character][k]:
                average_personnality[k].append(v)
            
    # Compute mean value for each SenticNet dimension for the whole play
    for senticnet_dimension in average_personnality:
        valeurs = average_personnality[senticnet_dimension]
        average_personnality[senticnet_dimension] = round( sum(valeurs) / len(valeurs), 5 )

    # ---
    # (5.2) Compute mean value on each SenticNet dimension for each character
    # ---
    
    # Print outputs to console
    print('character\tO\tC\tE\tA\tN')
    
    for character in characters_perso:
        # Compute mean
        for k in characters_perso[character]:
            valeurs = characters_perso[character][k]
            if valeurs:
            
                # Raw mean
                raw_mean = round( sum(valeurs) / len(valeurs), 4 )
                
                # Adjusted mean
                adjusted_mean = round( raw_mean - average_personnality[k], 4 )
                
                # Store adjusted mean
                characters_perso[character][k] = adjusted_mean

            else:
                characters_perso[character][k] = None

        # Add to graph
        char_uri = stcnet2ocean + character
        for k in characters_perso[character]:
            if characters_perso[character][k]:
                object_property = URIRef( 'http://stcnet2ocean.com/property#has' + abreviations[k].capitalize() )
                g.add( (char_uri, object_property, Literal(characters_perso[character][k])) )

        # Clean data in order to make later comparisons easier
        temp_dim = {}
        for k,v in characters_perso[character].items():
            if v:
                temp_dim[k] = abs(v)
            else:
                temp_dim[k] = 0.0

        # Sort by values
        temp_dim = dict(sorted(temp_dim.items(), key=lambda item: item[1]))

        # Invert list to find most important first
        temp_dim = list(temp_dim)[::-1]

        # Computer OCEAN values on each dimension
        max_dim = 5 # How many dimensions to take in account
        char_ocean_perso = { 'o' : [], 'c' : [], 'e' : [], 'a' : [], 'n' : [] }

        # Loop on max_dim
        for x in range(max_dim):
            dim = temp_dim[x]
            val = characters_perso[character][dim]

            if val: # In some rare cases, val is None. So one must check it before processing further
                # Loop on each OCEAN dimension
                # Formula : dimension_senticnet * valeur_ocean * significativite_p_valeur_ocean
                for k,v in rpb[dim].items():
                    calcul_ponderation = ponderation[v.count("*")]
                    calcul_valeur_senticnet = val
                    calcul_valeur_ocean = float(v.replace('*', ''))

                    # Compute the formula
                    moyenne = round( calcul_valeur_senticnet * calcul_valeur_ocean * calcul_ponderation, 3 )

                    # Add to dict
                    char_ocean_perso[k].append(moyenne)


        big_5_profile = { 'o' : 0, 'c' : 0, 'e' : 0, 'a' : 0, 'n' : 0 }

        # Compute mean on each dimension
        for k,v in char_ocean_perso.items():
            moyenne_moyennes = round( sum(v) / max_dim, 5)
            
            # Replace list of values by mean
            # Raw values won't be used anymore later in the code
            # and are already stored in the ontology
            big_5_profile[k] = moyenne_moyennes

            # Associate each value to the character
            char = stcnet2ocean + character
            g.add( (char, property_hXv[k], Literal(moyenne_moyennes) ) )

        # Print outputs to console
        console_output = character
        for k,v in big_5_profile.items():
            console_output += f'\t{v}'
        print(console_output)
        
    # ---
    # (6) Export to xml
    # ---
    g.serialize(destination="ontology/psy_model_edit_filled.xml", format="xml")

    return

def main():
    """
        Main
    """

    abox_fill('example_csv/Romeo and Juliet - Exported.csv', 'ontology/psy_model_edit.rdf') # csv, ontology

if __name__ == '__main__':
    main()
