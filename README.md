# NLPToS
##  Evaluating Privacy Policies and Terms of Services using Machine Learning
Lukas Busch, AUC Capstone Project

This Github page will contain the code and data used for the AUC Capstone Project. 
As well as serving as the final product I wll continously update here, this way I hope to have everything centralized and clean.


## Current plan:

### General idea and contributions:
With this project I hope to make the following contributions:
  1) (Help) create a dataset containing PP(Privacy Policies) and ToS(Terms of Services) of different websites.
  2) Use this to generate a more transparent and fair online environment
  3) Using NLP tools on a new topic
  4) Contribute to the ongoing discussion of internet privacy (?? Not super sure about this, but sounds cool)

### Data
I have found this really cool webiste [ToS;DR](https://tosdr.org/)
They are a non profit organization that aims to make the internet more transparent by making the PP and ToS easier to understand.
People sent in reviews of PPs and ToSs in a JSON.
In my repo is both the **all.json** file and all the seperate **services** that seem to be online and working.
This is taken from the [ToS:DR Github Page](https://github.com/tosdr/tosdr.org) and all of the data belongs to them (although I believe it is pretty open source-ish)

There are about **640** (english) websites reviewed. Usually the reviews are done on 2 different webpages, one on PP and one on ToS. Sometimes the PP is taken apart for different aspects (PP user / PP advertiser / etc ..). **More information on this later, working on it**.
Each JSON file, contains at least the following: *alexa, class, links, points, pointsData, urls*. Where the *links* ocasionaly contain links to the PP and/or ToS. Often this is not the case however. The *pointsData* contains all the points made by the reviewer. It does this by quoting the document it gained the information from (e.q. *Privacy Policy*), quoting the quote itself and then explainig that quote. It ocasionaly also gives a score for such a point. Which then can add up to a total score for a website.


After having figured out exacly how many PPs and ToS are referenced I will try to scrape those. For this I plan to use [trafilatura](https://trafilatura.readthedocs.io/en/latest/installation.html#trafilatura-package), this seems amazing as it can easily get all text visible on a screen with only two simple lines of codes.
To get to those however might be tricky. In some cases a link to the PP or ToS is provided, howver this seems to be the case only 20% of the time. This means I will have to look for the webpages myself. For this I:
  1) First plan to use [Beautiful Soup](https://beautiful-soup-4.readthedocs.io/en/latest/) to get all the links on the main webpage of a website (the url of the main page is always inclued)
  2) I believe it is mandatory to have a link to PP and/or ToS accesable from main page, the correct links should be among the once gathered.
  3) Use the "quoteDoc" datapoint in each JSON file —which says wherefrom the information was taken— to find order the links from most likely to least likely. This can be done in a manner of ways, I will have to find the best:
    3.1) Currently using a very easy Bag Of Words kindoff methods, which simply counts how often the words from the quote appear in a link
    3.2) Using methods explained on [this page](https://dev.to/coderasha/compare-documents-similarity-using-python-nlp-4odp) for example, or different maybe more advanced methods
    3.3) I thought about maybe using a mini machine learning tool with the 145 documents that do provide links
  4) Start by scraping the most likely candidate
  5) After having the scraped text, check if the quotes do appear in the text. If all quotes appear, you are done. If some are missing, keep scraping untill you find all the quotes. Text in which no quotes can be found are thrown away
  **DISCLAIMER: I know that this is time consuming and it might be arbritrary, but I want to assure not having wrong texts or too little texts in my data**
  6) If the end of the links list is reached and there are still quotes remaining, disregard those quotes

After having done this I hope to have a dataset of texts that correspond to a number of quotes containing both textual and numerical (in the form of grades/scores) data.

SIDENOTE: I am currently talking about all the different *.json* files found in the data/services/ folder. There is also an all.json file, this one seems to contain a little bit more reviews. However, also a little bit messier and it would require some more detailed attention. I expect most of the things mentioned above to also apply to this dataset, it might just need a little bit of name change.**Will probably look at that later**

### Machine Learning
With the Data obtained I plan to use a NN strucuture to to one of the following things:
  1) write very small abstracts of the PPs/ToSs using the abstractive explanations of the points made in the dataset
  2) Use the same format as the ToS;DR, meaning I take a quote, intrepret the quote and give it a score. Adding up to a total score

  (1) **Abstracts**
Benefits:
  1) There is more and specific (acadamic) information on abstractive summarization. (Multi-document / Single Sentence ...)
  2) I believe it is more academic to do so. It is a broader subject and therefore can be generalised, perhaps adding more to the ongoing discussion in a way
  
Downsides:
  1) As the data is mostly single sentences it might be difficult to generate a coherent abstract
  2) It's a little bit less interesting as the output is less usefull this way
  
  
  (2) **JSON Format**
Benefits
  1) I find it more interesting
  2) It has the possibility to be used and thereby matter beyond the evaluation and grading of my Capstone
  3) The output could be submitted and thereby peer reviewed, which could be a good model of evaluation
 
 Donwsides:
  1) It might not be acadamic enough to create such a specific output
  2) Time that could be invested in learning more on the NLP process has to be invested in formatting and these kind of things
  

Whichever one it will be (I hope (2) is possible and acadamic enough) the process will look a little bit like this:

As the data I have is rather small I plan to make use of [Transfer Learning](https://www.topbots.com/transfer-learning-in-nlp/) (explanation).
For this the two best choices probably are [ELmo](https://allennlp.org/elmo) and [BERT](https://arxiv.org/pdf/1810.04805.pdf).
These are both language models that can be [finetuned](https://www.analyticsvidhya.com/blog/2020/07/transfer-learning-for-nlp-fine-tuning-bert-for-text-classification/) to fit ones own goal.
BERT seems to be more standard so that is probably what I will use too, [this article](https://towardsdatascience.com/lawbert-towards-a-legal-domain-specific-bert-716886522b49) explains how BERT can be finetuned for a legal domain, which PP and ToS belong to.
I'll have to figure out if a good finetuned BERT already exists and otherwise find a good english law corpora to finetune it.

After having this pretrained model I can use "my own" data to try and to one of the 2 statements above.

For the 1 I could make use of several models out there.
For the 2 I planned to do something like this:
  1) classify all quotes in to groups, using perhaps [scikit](http://scikit-learn.org/stable/modules/clustering.html)
  2) Create an "output" matrix of size n (where n is the number of differnt groups)
  3) Format the data in such a way that each text corresponds to a matrix of size nx2 (nx3 if I want to include scores, etc...), where the first column contains a vector represnation of the quote and the second a vector represenation of the the explananation (third of score, if it has to be the JSON format there need to be a couple more, but I am not sure of those as of yet)
  3) use this combined with the text to further train the model
  4) Hopefully when the program is then fed a text it will return such a matrix and with decoding it can understand the quotes and explanations
  
 

