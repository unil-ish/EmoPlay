# EmoPlay - Extract emotions from TEI-Encoded Theater plays using Senticnet
## Introduction
EmoPlay is an educational object-oriented python project made by students from the University of Lausanne, Switzerland. EmoPlay can parse through TEI-Encoded theater plays and extract speech and speaker data as well as emotional attributes of the speeches it extracts. EmoPlay also offers an additional layer of text processing using a python implementation of Word Sense Disambiguation ([pywsd](https://github.com/alvations/pywsd)). This allows for greater and more accurate emotions extraction as results from disambiguated text often offer richer results when using the senticnet emotion dictionnary.
## Technologies
EmoPlay relies on the following technologies :
* Senticnet Dictionnary
    * This is not the Senticnet python module, but the pre-trained, locally stored, Senticnet word-emotion library. EmoPlay provides an "as-is" Senticnet library, but you can download the latest version [here](https://sentic.net/senticnet.zip) (**Caution** : you may encounter issues if the encoding format has changed since 30.05.2022)
* Natural Language Tool Kit ([NLTK](https://www.nltk.org/)) & [WordNet](https://wordnet.princeton.edu/)
* Python Implementation of Word Sense Disambiguation ([pywsd](https://github.com/alvations/pywsd))
## Install

The following libraries are required to work with EmoPlay:
* [Pandas](https://pandas.pydata.org/)
* [Lxml](https://lxml.de/) as an XML parser for [Beautifoul Soup 4](https://www.crummy.com/software/BeautifulSoup/) (also required)
* [Seaborn](https://seaborn.pydata.org/) for visuals

To install all the required libraries, you can either use `pip install requirements.txt` when running pip from the directory of the cloned git, or use the following commands :

```
pip install pandas
pip install beautifulsoup4
pip install nltk
py -m nltk.downloader 'popular'
pip install pywsd==1.0.2
pip install seaborn
```
## Usage
As of now, EmoPlay can be used by simply running `py main.py`. This will execute data extraction as well emotional extraction of the XML file at the path hard-coded in main.py. We are also implementing a global option to process all XML files included in a specified directory. However, computing times of this program are extremely lengthy and it may not suitable to perform such a task, unless serious computing power is available.

Additionally, you can import classes from EmoPlay in order to use specific methods suiting your needs.
### Example usage:
You can use the Speech() class from speech.py in order to extract emotions from simple sentences. Note that the senticnet class is needed to use the `getEmotions()` method.
```python
import speech
import senticnet

sentic_file = senticnet.Senticnet()
speech1 = speech.Speech('I absolutely love this wonderful test speech', 1, 1)
print(speech1.getEmotions(sentic_file))
```
This code will output :
```p
# Successfully disambiguated speech id 1 in 1.595 s
# Successfully extracted emotions for speech id 1
{'primary_emotion': None, 'secondary_emotion': None}
```
As you can see, not all speeches contain extractable emotional attributes.

You can also use EmoPlay to simply disambiguate any text with the MaxSimilarity algorithm
```python
import speech
speech1 = speech.Speech('I went to the bank to deposit some money', 1, 1)
speech1.disambiguate()
print(speech1.text_disambiguate)
```
This outputs :

```
I travel to the bank to deposit some money
```

Finally you can use the Play class to load a TEI-encoded XML file and extract raw text as well as emotions from the entire play.
```python
    p = play.Play(path)
        for character in p.characters:
            for speech in character.speeches:
                speech.getEmotions(stcnet)
```
Raw text will be extract by the __init__ of the Play class. Emotions are extracted per speech, therefore a loop is needed.
### Exporting and reloading
EmoPlay uses CSV format to export processed data. You can use :
```
p.to_csv() # Exports Play class "p" to CSV file
```
To reload a processed file, you can use :
```
p.from_csv(path/to/file)
```
## Visualisations
EmoPlay uses the Seaborn python library to output graphical plots of the emotional data extracted from the plays. These are the currently supported graphs :
|code|method|description|
|----|------|-----------|
|bps|barPlotSpeech()|Displays what speaker spoke the most (speeches)
|bpw|barPlotWords()|Displays what speaker spoke the most (words)
|ebc|emotionsByCharacter()|Displays emotion across acts for some characters
|eba|emotionsByAct()|Displays the most frequent emotions for each act
### Visualisation usage
Please note that the following example uses a pre-processed file stored in CSV format. In order for emotions plots to compute, you need to process, for each character and each speech, the associated emotions as shown above.
```python
import play
import vizualisation

p = play.Play(path/to/play)
p.from_csv(path/to/pre-process-csv)
plot = vizualisation.Vizualisation(p, "Your Vizualisation Code (ie. 'bps')")
```
## Conclusion
### Scope and Limitations
This program has been developed to work with TEI-Encoded, XML, theater play files. The purpose of this program is to extract speaker's data from the XML file, including every line spoken by every character, as well as the emotional attributes (taken from Senticnet) of every line in the play.
This program can be of use to scholars and enthousiasts looking to perform data analysis on any speaker:speech data combination. Evidently, TEI-Encoded theater plays will work properly from the get-go.
But this program can easily be adapted to work with any type of speaker:speech data combination.
As of right now, this program loops through every line of a play to extract emotional attributes by line.
This design has the inevitable disadvantage of being very computationally heavy, mostly because of the disambiguation that is executed on every speech line. Performance improvements could be made in order to accelerate the text processing of the plays.

### Credits
This project was done by Sinem Kilic, Ellijah Green, Antonin Schnyder and Pedro Tomé under the supervision of Mr. Davide Picca, teacher of object-oriented programming at the University of Lausanne, Switzerland.