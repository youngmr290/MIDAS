# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 10:00:30 2020

Version Control:
Version     Date        Person  Change
1.1         22/02/202   MRY      commented out con2 as it is not needed - don't delete incase we are wrong and it is required.

Known problems:
Fixed   Date    ID by   Problem


@author: young
"""

#python modules
import pandas as pd
import numpy as np
import timeit


#MUDAS modules
import UniversalInputs as uinp
import PropertyInputs as pinp

def rot_params(params):
    ##area
    params['lmu_area'] =  pinp.general['lmu_area'].squeeze().to_dict()
    ###########################
    #rotation phase low bound #
    ###########################
    ##debuging rotaion constraints- create dict for each rotation with 0 as default, then loop through changing each value to 1 (this dict will be used as the min bound)
    phases_df = uinp.structure['phases']
    params['lo_bound'] = dict.fromkeys(phases_df.index, 0)#create default dict, this is the min bound for each rotatoin. Could change 0 to a SAV which is the low bound for every rotation.
    ##alter specific rotation min bounds
    #^still need to determine the best way to do this
    
    #############################
    #rotation phase constraint1 #
    #############################    
    rot_con1 = pd.read_excel('Rotation.xlsx', sheet_name='rotation con1', header= None)#, index_col = [0,1]) #couldn't get it to read in with multiindex for some reason
    params['hist'] =rot_con1.iloc[:,1] # this is a list of each history for each rotation in con1.
    rot_con1 = rot_con1.set_index([0,1])
    params['rot_con1'] =rot_con1.squeeze().to_dict()
    # rot_con2 = pd.read_excel('Rotation.xlsx', sheet_name='rotation con2', header= None)
    # rot_con2 = rot_con2.set_index([0,1])
    # rot_con2 =rot_con2.squeeze().to_dict()



