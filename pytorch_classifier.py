# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 21:01:05 2021

@author: luka5132
#Based on:https://towardsdatascience.com/transformers-for-multilabel-classification-71a1a0daf5e1
Used in my capstone project for hierarchical classification. For more explanation
on this code please look at the explanation notebook called 'class_explanations.ipynb'
https://github.com/luka5132/NLPToS
"""


import torch
from torch.utils.data import TensorDataset, DataLoader, SequentialSampler
from transformers import *


class BertClassification(object):
    
    def __init__(self):
        self.labels = None 
        self.segments = None
        self.model_name = None
        self.max_length = None
        self.tokenizer = None
        self.encodings = None
        
        self.num_labels = None
        
        self.optimizer = None

        
    def init_tokenizer(self, model_name, lower_case = True, ret = False):
        """
        Loads the toknenizer, either returns it or saves it in the class
        """
        self.model_name = model_name
        self.tokenizer =  BertTokenizer.from_pretrained(self.model_name, do_lower_case=lower_case)
        if ret:
            return BertTokenizer.from_pretrained(self.model_name, do_lower_case=lower_case) # tokenizer
        
    def encode_texts(self, max_length = 128, trunc = True, ptml = True,stratify = None, batchsize = 32, rs = 2021, valsize = 0.1, with_labels = True):
        """
        Uses the tokenizer to create pytorch bathces
        """
        encodings = self.tokenizer.batch_encode_plus(self.segments,max_length=max_length,pad_to_max_length=ptml, truncation=trunc) # tokenizer's encoding method
        
        input_ids = encodings['input_ids'] # tokenized and encoded sentences
        token_type_ids = encodings['token_type_ids'] # token type ids
        attention_masks = encodings['attention_mask'] # attention masks
        
        if with_labels:
            test_inputs,test_labels,test_token_types,test_masks =self.turn_to_tensor((input_ids, self.labels, token_type_ids,attention_masks))
            test_data = TensorDataset(test_inputs, test_masks, test_labels, test_token_types)
        else:
             test_inputs,test_token_types,test_masks =self.turn_to_tensor((input_ids,token_type_ids,attention_masks), False)
             test_data = TensorDataset(test_inputs, test_masks, test_token_types)
        test_sampler = SequentialSampler(test_data)
        test_dataloader = DataLoader(test_data, sampler=test_sampler, batch_size=batchsize)
        print(type(test_dataloader))
        
        return test_dataloader
        
    def input_texts(self,texts):
        self.segments = texts
        
    def input_labels(self, labels):
        self.labels = labels
        self.num_labels = len(self.labels[0])
        
        
    def turn_to_tensor(self,encoding_tuple, with_labels = True):
        if with_labels:
            inputs = torch.tensor(encoding_tuple[0])
            labels = torch.tensor(encoding_tuple[1])
            masks = torch.tensor(encoding_tuple[2])
            token_types = torch.tensor(encoding_tuple[3])
            return (inputs,labels,masks,token_types)
        else:
            inputs = torch.tensor(encoding_tuple[0])
            masks = torch.tensor(encoding_tuple[1])
            token_types = torch.tensor(encoding_tuple[2])
            return (inputs,masks,token_types)


    def save_optimizer_state(self, save_name):
        return torch.save(self.optimizer.state_dict(), save_name)
        
    def init_optimizer(self, model,lrate = 2e-5,cb = True, ret =True):
        # setting custom optimization parameters. You may implement a scheduler here as well.
        param_optimizer = list(model.named_parameters())
        no_decay = ['bias', 'gamma', 'beta']
        optimizer_grouped_parameters = [
            {'params': [p for n, p in param_optimizer if not any(nd in n for nd in no_decay)],
             'weight_decay_rate': 0.01},
            {'params': [p for n, p in param_optimizer if any(nd in n for nd in no_decay)],
             'weight_decay_rate': 0.0}
        ]
        
        self.optimizer = AdamW(optimizer_grouped_parameters,lr=lrate,correct_bias=cb)
        # optimizer = AdamW(model.parameters(),lr=2e-5)  # Default optimization
        if ret:
            return self.optimizer
        
        
    def init_data(self, texts, labels):
        self.input_texts(texts)
        self.input_labels(labels)
        
        
    def load_test_data(self,test_texts,test_labels):
        self.test = True
        self.init_data(test_texts, test_labels)
        self.encode_texts()
        self.procesdata()
        self.create_batches()
        
        