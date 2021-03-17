# NLPToS
## Optimizng BERT for privacy policy classificatoin
Lukas Busch, AUC Capstone Project

This Github page will contain the code and data used for the AUC Capstone Project. 
As well as serving as the final product I wll continously update here, this way I hope to have everything centralized and clean.


## Current plan:

The Reserach Proposal can be found on this GitHub page under the folder *Documents* 

Current updates beyond Research Proposal:
  1) Using [Google's cloud TPU](https://cloud.google.com/tpu) to run my pre-training model for "PrivBert" as well as optimizng the fine-tuning. This Cloud service not only runs the quickest, but it is also the cleanest Machine Training cloud. 
  2)  Used the [transformers huggingface](https://huggingface.co/transformers/) "bert-base-uncased" model for a classification model. However, I was unable to load a local (smaller) BERT model, which could be easier to train with.
  3)  Have to figure out how feasible it is to create a usable extension.


## Google Cloud API

In the [SciBERT paper](https://arxiv.org/abs/1903.10676) the authors explain how they use a single TPU v3 with 8 cores to train their BERT model for 7 days, using a corpus of 3.3 Bilion tokens.
Using the dataset obtained by [Amos et al. (2020)](https://arxiv.org/abs/2008.09159) I plan to train my BERT model using 661M tokens. 
If we assume linear scaling of the data (which I am not sure of if that is correct) I would have to train my model for only 1/5 of the time, so 7/5= 1.4 days. Which is 1.4 times 24 hours = 33.6 hours. 
The pricing for a TPU v3 with 8 cores is $2.64 per hour. So the total price for pre-training would be 33.6x2.64 = $88.70. 
Google offers $300 as introduction, so I believe it should be able for me to not go over this amount.

## Stuff to figure out still:
1) How exactly does the google cloud TPU work
2) How does the data for BERT scale (could see if I could make this quesiton part of my research)
3) What would my classification model look like exactly (labels / classes)
  3.1) I will for sure try to classify text segnments on one of the 10 major classes
  3.2) Would be interesting to see if sentence classification can be used within these segments to classify the subclasses. This could also be used to verify the main classes (for each main class you have specific subclasses. If I were to train not 1 but 2 models, one that tries to classify texts in segments and one that classifices the sentences for segments, I could use the confidence scores of the two classes combined to see if I can predict a better classification of the main class)

4) How difficult is it to make an application for the model? (maybe too much)
 

