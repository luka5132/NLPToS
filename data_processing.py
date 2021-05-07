# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 21:01:05 2021

@author: luka5132
Used in my capstone project for hierarchical classification. For more explanation
on this code please look at the explanation notebook called 'class_explanations.ipynb'
https://github.com/luka5132/NLPToS
"""
import  ast
import pandas as pd
import os
import numpy as np
from collections import Counter

class Op115OneHots(object):
    
    def __init__(self, adf):
        self.df = adf
        self.categories = None
        self.dicts = None
        self.tuple_list = None
        self.unique_tups = None
        self.unique_atts = None
        self.unique_cats = None
        self.cat_oh = None
        self.subcat_oh = None
        self.subsubcat_oh = None
        self.dictvalues = None
        self.segments = None
        self.segments_vals = None
        
    def getcats(self):
        """Sets self.categories to the respective category per row in the input 
        df (op115-dataset)."""
        self.categories = list(self.df.category_name)
        
    def getdicts(self):
        """Sets self.dicts to the dictionaries that are in the df. When reading the
        df, this value is a string. Using ast we transform it into a proper dictionary"""
        
        self.dicts = []
        str_dicts = list(self.df.attribute_value_pairs)
        for str_dic in str_dicts:
            dic = ast.literal_eval(str_dic)
            self.dicts.append(dic)
            
    def pol_seg(self, tup = True):
        """returns the pol_segments for the corresponding rows, this is used 
        to create the multi label classification"""
        pols = self.df.policy_uid.to_list()
        segs = self.df.segment_id.to_list()
        polsegs = []
        for i in range(len(pols)):
            if tup:
                polseg = (pols[i],segs[i])
                polsegs.append(polseg)
            else:
                polseg = str(pols[i]) + str(segs[i])
                polsegs.append(int(polseg))
                
        return polsegs
    
    def sort_df_polseg(self):
        str_polseg = self.pol_seg()
        self.df['str_polsegs'] = str_polseg
        self.df.sort_values(by=['str_polsegs'], inplace=True)
            
    def tuplist(self,cat,adict):
        """takes a category and a dictionary that contains information one the 
        subcategories. Returns a list of tuples for each value of the subcategory"""
        retlist = []
        endseg_list = []
    
        for key in sorted(list(adict.keys())):
            subdict = adict[key]
            sub_val = subdict['value']
            endseg = subdict['endIndexInSegment']
            endseg_bool = endseg != -1
            tup = (cat,key,sub_val)
            retlist.append(tup)
            endseg_list.append(endseg_bool)
            
        return retlist,endseg_list
        
            
            
    def processtuples(self):
        """Sets the self.tuple_list to the values corresponding per row. Makes it
        so that every row gets a tuple with 3 values: 
            (Category, Subcategory, Subsubcategory / Subcategory value)
        this will be used to create the one hot vectors. Uses the function "tuplist"
        for this.
        
        Also creates the self.unique_tups, these are all the different tuples """
        
        tuple_list = []
        unique_tups = set()
        endseg_l = []
        for i in range(len(self.categories)):
            adict = self.dicts[i]
            cat_name = self.categories[i]
            
            tups,endsegs = self.tuplist(cat_name,adict)
            i = 0
            for tup in tups:
                endseg = endsegs[i]
                if endseg:
                    unique_tups.add(tup)
                i +=1
            tuple_list.append(tups)
            endseg_l.append(endsegs)
        
        self.dictvalues = endseg_l
        self.tuple_list = list(tuple_list)
        self.unique_tups = list(unique_tups)
        
        

    def getsub(self):
        att_set = set()
        cat_set = set()
        for atup in self.unique_tups:
            x,y,z = atup
            subtup = (x,y)
            att_set.add(subtup)
            cat = x
            cat_set.add(cat)
        
        self.unique_atts = list(att_set)
        self.unique_cats = list(cat_set)
        
    def tuplist_per_segment(self):
        """asumes a dataframe that is storted on its policy segments"""
        polsegs = self.pol_seg(False)
        tuplist = self.tuple_list
        texts = self.returntexts()

        prev_polseg = 0
        
        value_list = []
        segment_list = []
        polseg_list = []
        
        vals_per_seg = []
        cur_text = ''
        for i in range(len(tuplist)):
            cur_list = tuplist[i]
            new_polseg = polsegs[i]
            cur_text = texts[i]
            dictval = self.dictvalues[i]
            
            
            if new_polseg != prev_polseg:
                value_list.append(vals_per_seg)
                segment_list.append(cur_text)
                polseg_list.append(prev_polseg)
                
            if new_polseg != prev_polseg:
                vals_per_seg = []
            
            for n in range(len(cur_list)):
                if dictval[n]:
                    vals_per_seg.append(cur_list[n])
            
            prev_polseg = new_polseg
        
        value_list.append(vals_per_seg)
        segment_list.append(cur_text)
        polseg_list.append(prev_polseg)
                
                
        self.segments = segment_list
        self.segments_vals = value_list[1:]
        self.polseg_ids = polseg_list[1:]
                
            
        
    def majority_vote(self):
        text_ids = list(self.df.policy_id)
        seg_ids = list(self.df.segment_id)
        cat_names = list(self.df.category_name)
        ann_ids = list(self.df.annotator_id)
        
        votes = Counter()
        ann_votes = {}
        major_list = []
        id_list = []
        for i in range(len(text_ids)):
            text_id = text_ids[i]
            seg_id = seg_ids[i]
            cat_name = cat_names[i]
            id_tup = (text_id,seg_id,cat_name)
            id_list.append(id_tup)
            ann_id = ann_ids[i]
            
            if ann_id in ann_votes:
                voted = ann_votes[ann_id]
                if id_tup not in voted:
                    votes.update([id_tup])
                    ann_votes[ann_id].append(id_tup)
                else:
                    pass
            else:
                ann_votes[ann_id] = [id_tup]
                votes.update([id_tup])
            

        for aid_tup in id_list:
            majority = votes[aid_tup] > 1
            major_list.append(majority)
        
        self.df = self.df[major_list]
        
    def go2(self, majority = False, class_tup = None):
        if majority:
            self.majority_vote()
        self.sort_df_polseg()  
        self.getcats()
        self.getdicts()
        self.processtuples()
        self.getsub()
        if class_tup:
            self.set_oh_names(class_tup)
        self.tuplist_per_segment()
        
        #self.onehots()
        
        
    def return_ohs(self, oh_name):
        if oh_name == "categories":
            return self.cat_oh
        elif oh_name == "subcategories":
            return self.subcat_oh
        elif oh_name == "subsubcategories":
            return self.subsubcat_oh
        else:
            return (self.cat_oh,self.subcat_oh,self.subsubcat_oh)

    def classtree(self):
        cat_subcat = {}
        subcat_subsubcat = {}
        final_dict = {}
        
 
        for tup in self.unique_tups:
            cat = tup[0]
            subcat = tup[1]
            subsubcat = tup[2]
                
            if cat in cat_subcat:
                cat_subcat[cat].add(subcat)
            else:
                tempset = set()
                tempset.add(subcat)
                cat_subcat[cat] = tempset
            
            catsubcat = (cat, subcat)
            if catsubcat in subcat_subsubcat:
                subcat_subsubcat[catsubcat].append(subsubcat)
            else:
                subcat_subsubcat[catsubcat] = [subsubcat]
        
        n_subcats = 0
        for value in sorted(list(cat_subcat.values())):
            vallist = list(value)
            n = len(vallist)
            n_subcats += n
        
       # print(subcat_subsubcat.values())
        for akey in sorted(list(cat_subcat.keys())):
            subcats = list(cat_subcat[akey])
            nested_dict = {}
            
            for subcat in subcats:
                tup = (akey, subcat)
                #print(subcat)
                subsubcats = subcat_subsubcat[tup]
                #print(subsubcats)
                nested_dict[subcat] = subsubcats
            
            #print(akey,nested_dict)
            
            final_dict[akey] = nested_dict
                
        return final_dict
    
    def indexes(self):
        subsubd = {}
        subd = {}
        d = {}
        
        i = 0
        for atup in self.unique_tups:
            cat = atup[0]
            
            if cat in subsubd:
                subsubd[cat].append(i)
            else:
                subsubd[cat] = [i]
            
            i +=1
        
        j = 0
        for anothertup in self.unique_atts:
            cat2 = anothertup[0]
            
            if cat2 in subd:
                subd[cat2].append(j)
            else:
                subd[cat2] = [j]
            
            j +=1
        
        k = 0
        for acat in self.unique_cats:
            d[acat] = k
            
            k +=1
            
        return (d,subd,subsubd)
    
    
    def returntexts(self):
        return list(self.df.segment_text)
    
    def return_unique_texts(self):
        return list(self.df.segment_text.unique())
    
    def set_onehots(self, oh_list, oh_name):
        if oh_name == 'categories':
            self.unique_cats = oh_list
        elif oh_name == 'subcategories':
            self.unique_atts = oh_list
        else:
            self.unique_tups = oh_list
            
    def return_oh_names(self):
        return((self.unique_cats,self.unique_atts,self.unique_tups))
    
    def set_oh_names(self, class_tup):
        self.unique_cats = class_tup[0]
        self.unique_atts = class_tup[1]
        self.unique_tups = class_tup[2]
    
    def len_onehots(self):
        """for each category this function returns the length of the number of 
        subclasses and value classes in two seperate dictionaries. And it returns a 
        dictionary that maps a tuple to a corresponding index """
        
        class_tree = self.classtree()
        catsub = {}
        catval = {}
        subval = {}
        indexdict = {}
        i = 0 #Tracks number of categories
        jj = 0 #tracks total number of subcategories
        jjj = 0 #tracks total number of values
        for cat in sorted(list(class_tree.keys())):
            subdict = class_tree[cat]
            j=0 #tracks number of subcategories per category
            k=0 #tracks total number of values per category
            
            for subcat in sorted(list(subdict.keys())):
                vals = subdict[subcat]
                catsub_tup = (cat,subcat)
                l = 0 # tracks number of values per subcategory
                
                for val in vals:
                    catsubval_tup = (cat,subcat,val)
                    subval_tup = (catsub_tup,val) # it is important that the subvalue is a subvalue related to the correct category
                    catsubval_all =(i,catsubval_tup)
                    
                    indexdict[catsubval_tup] = k
                    indexdict[catsubval_all] = jjj
                    indexdict[subval_tup] = l
                    k +=1
                    l +=1
                    jjj +=1
                
                subval[catsub_tup] = l
                indexdict[catsub_tup] = j
                catsub_all = (i,cat,subcat)
                indexdict[catsub_all] = jj
                j+=1
                jj += 1
                
                
            catsub[cat] = j
            catval[cat] = k
            indexdict[cat] = i   
            
            i +=1
        
        return (catsub, catval,subval,indexdict)
            

    def new_onehots(self):
        
        #create dictionaries that will contain the texts and one hot vectors for
        #the respective level (e.g: cat -> subcat, 
                                #   cat -> val, 
                                #   subcat -> val)
        cat_to_sub = {} 
        cat_to_val = {}
        sub_to_val = {}
        all_cats = []
        all_subcats = []
        all_vals = []
        all_texts = []
        
        catsub_l,catval_l,subval_l,inds = self.len_onehots()
        
        #iniate cat_to_sub/val dicts by inserting the keys
        for acat in self.unique_cats:
            cat_to_sub[acat] = [-1,[],[]]#each cat has a tuple with two lists one is text other is one hot
            cat_to_val[acat] = [-1,[],[]]
        
        for sub in sorted(list(subval_l.keys())):
            sub_to_val[sub] = [-1,[],[]] #initaite with polseg placeholder, important for recognizing the current segment
        
        
        len_cats = len(self.unique_cats)
        len_subcats = len(self.unique_atts)
        len_vals = len(self.unique_tups)
        
        for i in range(len(self.segments_vals)):
            row = self.segments_vals[i]
            text = self.segments[i]
            cur_polseg = self.polseg_ids[i]
            
            cat_oh = [0] * len_cats
            sub_oh = [0] * len_subcats
            catsubval_oh = [0] * len_vals
            
            for tup in row:
                x,y,z = tup
                cat = x
                catsub = (x,y)
                cat_ind = inds[cat]
                
                catsub_all = (cat_ind, x, y)
                catsubval_all = (cat_ind, tup)
                subval = (catsub,z)
                
                if sub_to_val[catsub][0] != cur_polseg:
                    subval_oh = [0] * subval_l[catsub]
                else:
                    subval_oh = sub_to_val[catsub][2][-1]
                
                if cat_to_sub[cat][0] != cur_polseg:
                    catsub_oh = [0] * catsub_l[cat] #create on hot vectors with the lenghts from the dictionaries
                else:
                    catsub_oh = cat_to_sub[cat][2][-1]
                    
                if cat_to_val[cat][0] != cur_polseg:
                    catval_oh = [0] * catval_l[cat] #create on hot vectors with the lenghts from the dictionaries
                else:
                    catval_oh = cat_to_val[cat][2][-1]
                    
                catsub_ind = inds[catsub]
                catsub_all_ind = inds[catsub_all]
                catsubval_all_ind = inds[catsubval_all]
                subval_ind = inds[subval]
                catval_ind = inds[tup]
                
                cat_oh[cat_ind] = 1
                catsub_oh[catsub_ind] = 1
                sub_oh[catsub_all_ind] = 1 
                subval_oh[subval_ind] = 1
                catval_oh[catval_ind] = 1
                catsubval_oh[catsubval_all_ind] = 1
                
                if sub_to_val[catsub][0] != cur_polseg:
                    sub_to_val[catsub][0] = cur_polseg
                    sub_to_val[catsub][1].append(text) #append the text for the subval pair
                    sub_to_val[catsub][2].append(subval_oh) #append the corresponding one hot vector
                else:
                    if sub_to_val[catsub][2][-1]:
                        sub_to_val[catsub][2][-1] = subval_oh
                    else:
                        sub_to_val[catsub][2] = [subval_oh]
                 
                if cat_to_sub[cat][0] != cur_polseg:
                    cat_to_sub[cat][0] = cur_polseg
                    cat_to_sub[cat][1].append(text)
                    cat_to_sub[cat][2].append(catsub_oh)
                else:
                    if cat_to_sub[cat][2]:
                        cat_to_sub[cat][2][-1] = catsub_oh
                    else:
                        cat_to_sub[cat][2] = [catsub_oh]
                        
                        
                if cat_to_val[cat][0] != cur_polseg:
                    cat_to_val[cat][0] = cur_polseg
                    cat_to_val[cat][1].append(text)
                    cat_to_val[cat][2].append(catval_oh)
                else:
                    if cat_to_val[cat][2]:
                        cat_to_val[cat][2][-1] = catval_oh
                    else:
                        cat_to_val[cat][2] = [catval_oh]
                
            all_cats.append(cat_oh)
            all_subcats.append(sub_oh)
            all_vals.append(catsubval_oh)
            all_texts.append(text)

        return (cat_to_sub,
                cat_to_val,
                sub_to_val,
                all_cats,
                all_subcats,
                all_vals,
                all_texts)
