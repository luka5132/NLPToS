# NLPToS
## Building a hierarchical advice system
Lukas Busch, AUC Capstone Project

This Github page will contain the code and data used for the AUC Capstone Project. 
As well as serving as the final product I wll continously update here, this way I hope to have everything centralized and clean.


## Abstract of paper:

Blablabla dida

## Guide through Github

 ### Fine-tuning privbert model
 For fine-tuning my model on the privacy policy corpus I made use of 'Google Cloud/Colab' as one is able to freely leverage their TPU's. This ASIC is the most efficient way to train machine learning models. Although the code used is also available as a notebook on my github under the name: *privbert_training.ipynb* I suggest people who are interested in how that worked to visit the notebook on google colab using this link: https://colab.research.google.com/drive/1jtvEPrQvLT63LaLBCFI5pWKeNEqS4W1O?usp=sharing
 
 ### Building the hierarchical system
 To train the BERT classifcation models I used Kaggle's notebook, here one is able to use a GPU for up to 40 hours a week. Just like *privbert_training.ipynb* is also available here on this github page it was created and is better read on Kaggle. One can find the different codes and datasets that were used on my profile: https://www.kaggle.com/lukasbusch
 
 ### Other notebooks
 The only notebook that cannot be found on either my Kaggle or Google Colab is *sqlite_reading.ipynb*, this notebook was used to read and process the raw privacy policies that were used to create the fine-tuned BERT model.
