# NLPToS
## Building a hierarchical advice system
Lukas Busch, AUC Capstone Project
Supervisor: Kasper Welbers VU

This Github page will contain the code and data used for the AUC Capstone Project. 
As well as serving as the final product I wll continously update here, this way I hope to have everything centralized and clean.


## Abstract of paper:

A website's privacy policy is meant to inform users, however policies are often long and difficult to understand. A growing number of research uses machine learning to address this problem. This paper focuses on privacy policy classification and introduces a so-called 'advice system' which leverages the hierarchical structure the annotated data in the OPP-115 privacy policy corpus. Combining this system with a BERT language model that is trained on a corpus of 340K privacy policies yields results that are on par, or by some metrics slightly better ($\approx$1\%) than the state of the art. It achieves these results by sacrificing some precision for a higher recall. 

## Guide through Github

 ### Fine-tuning privbert model
 For fine-tuning my model on the privacy policy corpus I made use of 'Google Cloud/Colab' as one is able to freely leverage their TPU's. This ASIC is the most efficient way to train machine learning models. Although the code used is also available as a notebook on my github under the name: *privbert_training.ipynb* I suggest people who are interested in how that worked to visit the notebook on google colab using this link: https://colab.research.google.com/drive/1jtvEPrQvLT63LaLBCFI5pWKeNEqS4W1O?usp=sharing
 
 ### Building the hierarchical system
 To train the BERT classifcation models I used Kaggle's notebook, here one is able to use a GPU for up to 40 hours a week. The following notebooks were created and usd on Kaggle:
  *stratify_data.ipynb*, used to create the 5 train,val and test sets for the advice system and used to create the 15 different training seths for both methods of stratification mentioned in the paper: Segment-based and policy-based.
 *privbert.ipynb*, used to train all 18 BERT models and to run tests for the stratification mehtods.
 *privbert_full_model.ipynb*, used to create and apply the advice system
 *privbert_results.ipynb*, used to process and interprete the results obtained in *privbert.ipynb* and *privbert_results.ipynb
  Each notebook has explanations inside. For the .py files, which were created when pieces of code were used more than once, there is an additional notebook called *class_explanations.ipynb* in which these scripts (classes created for this project) are explained/ looked at.
  
 One can find the different codes and datasets that were used for this research on my Kaggle profile also: https://www.kaggle.com/lukasbusch
 
 ### Other notebooks
 The only notebook that cannot be found on either my Kaggle or Google Colab is *sqlite_reading.ipynb*, this notebook was used to read and process the raw privacy policies that were used to create the fine-tuned BERT model.
