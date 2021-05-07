# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 21:01:05 2021

@author: luka5132
Used in my capstone project for hierarchical classification. For more explanation
on this code please look at the explanation notebook called 'class_explanations.ipynb'
https://github.com/luka5132/NLPToS
"""

import numpy as np
import itertools

class HierarchicalData(object):
    """
    This class stores the advice values for the hierarchical classification process
    """
    
    def __init__(self, candidate_treshold = 0.3):
        self.cat_layer = None
        self.cat_candidates = None
        
        self.sub_all_layer = None
        self.sub_all_advice = None
        
        self.sub_layer =None
        self.sub_advice = None
        
        self.val_layer = None
        self.val_advice = None
        
        self.cat_names = None
        self.cat_dictionary = None
        
        self.sub_to_cat_advice = True
        self.val_to_cat_advice = True
        
        self.candidate_treshold = candidate_treshold
        self.parameter_dictionary = None
    
    def set_variables(self, cat_name_list):
        """
        Initiate the class by storing the category names, also creates a 
        dictionary that links the name to the one-hot index
        """
        self.cat_names = cat_name_list
        cat_index_dict = {}
        for i,cat in enumerate(cat_name_list):
            cat_index_dict[cat] = i
        self.cat_dictionary = cat_index_dict
    
    def set_parameters(self, param_dict):
        """
        Loads the parameter dictionary for the suball advices
        """
        self.parameter_dictionary = param_dict
        
    def read_cat_predictions(self, cat_predictions):
        """
        Store the 'base' / 'cat(egory)' predictions
        """
        self.cat_layer = cat_predictions
        cat_shape = cat_predictions.shape
        self.sub_advice = np.zeros(cat_shape)
        self.sub_all_advice = np.zeros(cat_shape)
        self.val_advice = np.zeros(cat_shape)
        
    def read_sub_predictions(self, sub_predictions):
        """
        Store the 'suball' predictions
        """
        self.sub_all_layer = sub_predictions
        
    def define_candidates(self, candidate_treshold):
        self.cat_candidates = self.cat_layer > candidate_treshold
    
    def return_candidate(self, cat_index):
        """
        Returns a list of booleans that define whether a segment is a 'candidate'
        or not
        """
        return self.cat_candidates[:,cat_index]
    
    def return_advice(self, cat_ind, subpredictions, label_treshold, advice_val, seq_advice,neg_advice):
        """
        This funciton takes a cat_ind(ex) and predcitions obtained with that 
        classification model and returns the advice for the respective category
        """
        candidate_list = self.return_candidate(cat_ind)
        found_labels = np.count_nonzero(np.array(subpredictions) > label_treshold, axis = 1)
        
        def advice(x):
            """
            simples advice function
            """
            if x == 0:
                return neg_advice
            else:
                return advice_val  + x * seq_advice
        
        v_advice = np.vectorize(advice)
            
        found_labels = v_advice(found_labels)
        
        n = 0
        outlist = [0] * len(candidate_list)
        for i,j in enumerate(candidate_list): #insert n labels found in the candiate list
            if j:
                outlist[i] = found_labels[n] # only insert an advice when the segmetn was a candidate
                n +=1
        
        return outlist
    
    def return_suball_advice(self, indexdict,predictions):
        """
        returns advice for the suball layer
        """
        
        for cat in indexdict:
            cat_params = self.parameter_dictionary[cat]
            label_treshold = cat_params['label_treshold'][0]
            advice_val = cat_params['advice_val'][0]
            subseq_val = cat_params['subseq_val'][0]
            negative_advice = cat_params['negative_advice'][0]
            
            def advice(x):
                if x == 0:
                    return negative_advice
                else:
                    return advice_val  + x * subseq_val
        
            v_advice = np.vectorize(advice)
        
        
            cat_ind = self.cat_dictionary[cat]
            label_indexes = indexdict[cat]
            sub_predictions = predictions[:,label_indexes]
            found_labels = np.count_nonzero(sub_predictions > label_treshold, axis = 1)
              
            found_labels = v_advice(found_labels)
            
            self.sub_all_advice[:,cat_ind] = found_labels
        
        return self.sub_all_advice
                 
             
    
    def save_advice(self,advice,cat_ind,sub_or_val):  
        """
        takes an array of advices and stores it into the correct column in the
        advice matrix"""
        if sub_or_val == 'sub':
            self.sub_advice[:,cat_ind] = advice
        else:
            self.val_advice[:,cat_ind] = advice
            
    def give_sub_advice(self):
        return self.sub_advice
    
    def give_val_advice(self):
        return self.val_advice
    
    def give_all_sub_advice(self):
        return self.sub_all_advice
    
    def return_predictions(self, sub = True, all_sub = True, val = True):
        """
        return final predcitions with any given combination of layers
        """
        return_predicts = self.cat_layer
        if sub:
            return_predicts = return_predicts + self.sub_advice
        if all_sub:
            return_predicts = return_predicts + self.sub_all_advice
        if val:
            return_predicts = return_predicts + self.val_advice
        
        return return_predicts
    
    def return_predictions_layers(self):
        """
        return combinations for all possible combinations
        """
        all_combinations = [self.cat_layer]
        for i in range(1,4):
            combinations = itertools.combinations([1,2,3], i)
            for combination in combinations:
                sub = 1 in combination
                all_sub = 2 in combination
                val = 3 in combination
                all_combinations.append(self.return_predictions(sub,all_sub,val))
        return all_combinations
            
    def create_gridsearch_advices(self, n_samples, n_params):
        """
        Create the matrix that contains the advices when used in a gridsearch
        n_samples means the number of segments
        n_params stands for the total number of parameters
        """
        advice_lists =[0,0]
        for i in range(n_params):
            if advice_lists[0]:
                advice_lists[0].append(np.zeros((n_samples,10)))
                advice_lists[1].append(np.zeros((n_samples,10)))
            else:
                advice_lists[0] = [np.zeros((n_samples,10))]
                advice_lists[1] = [np.zeros((n_samples,10))]
                
        self.grid_search_advices = advice_lists
        
    def save_gridsearch_advice(self, advice_index = None, advice_vals = None, sub_or_val =None, cat_index=None):
        """
        store a gridsearch advice in the correct place
        advice index stands for which combination of advice layers it is
        the first list of matrices contatins the advices for the 'sub' layers
        the second list of matrices contains the advices for the 'val' layers
        """
        if sub_or_val == 'sub':
            self.grid_search_advices[0][advice_index][:,cat_index] = advice_vals
        else:
            self.grid_search_advices[1][advice_index][:,cat_index] = advice_vals
            
    def return_gridsearch_advice(self):
        return self.grid_search_advices
            