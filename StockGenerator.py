# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 09:35:18 2020

@author: John


Code structure
1. when reshaping input arrays use the i_len_? values but in the rest of the code use the len_? values.
2. sim params use their own pos and len variables.

Notes
1. Inputs need to be put together. One sheet in property.xl and one in universal.xl (and parameter sheet in universal so basically three sheets total)
2. Find and replace all the sheep input dicts so only the final ones used.


to do:
    check the inputs in structure. and update them



"""






"""
import functions from other modules
"""
# import datetime as dt
# import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
import time
# from numba import jit

import Functions as fun
import Sensitivity as sen
import PropertyInputs as pinp
import StockFunctions as sfun
import UniversalInputs as uinp
import Periods as per
import PlotViewer as pv
import sys,traceback

# np.seterr(all='raise')











# from memory_profiler import profile
# @profile
def generator(params,r_vals,ev,plots = False):
    """
    A function to wrap the generator and post processing that can be called by SheepPyomo.

    Called after the sensitivity variables have been updated.
    It populates the arrays by looping through the time periods
    Globally define arrays are used to transfer results to sheep_parameters()

    Returns
    -------
    None.
    """

    print("starting generator")
    generator_start = time.time()

    ######################
    ##background vars    #
    ######################
    na=np.newaxis
    p_pos = uinp.structure['i_p_pos']
    a1_pos = pinp.sheep['i_a1_pos']
    e1_pos = pinp.sheep['i_e1_pos']
    b1_pos = uinp.parameters['i_b1_pos']
    n_pos = uinp.structure['i_n_pos']
    w_pos = uinp.structure['i_w_pos']
    z_pos = pinp.sheep['i_z_pos']
    i_pos = pinp.sheep['i_i_pos']
    d_pos = uinp.parameters['i_d_pos']
    a0_pos = pinp.sheep['i_a0_pos']
    e0_pos = uinp.structure['i_e0_pos']
    b0_pos = uinp.parameters['i_b0_pos']
    x_pos = uinp.parameters['i_x_pos']
    y_pos = uinp.parameters['i_y_pos']
    # g_pos = 0  #todo (JMY) not used but should it be -1 if it was
    
    ######################
    ##date               #
    ######################
    ## define the periods - default (dams and sires)
    sim_years = uinp.structure['i_age_max']
    # sim_years = 4
    sim_years_offs = min(uinp.structure['i_age_max_offs'], sim_years)
    n_sim_periods, date_start_p, date_end_p, p_index_p, step \
    = sfun.sim_periods(pinp.sheep['i_startyear'], uinp.structure['i_sim_periods_year'], sim_years)
    date_start_pa1e1b1nwzida0e0b0xyg = np.expand_dims(date_start_p, axis = tuple(range(p_pos+1, 0)))
    date_end_pa1e1b1nwzida0e0b0xyg = np.expand_dims(date_end_p, axis = tuple(range(p_pos+1, 0)))
    p_index_pa1e1b1nwzida0e0b0xyg = np.expand_dims(p_index_p, axis = tuple(range(p_pos+1, 0)))
    ## define the periods - offs - these make the p axis customisable for offs which means they can be smaller
    n_sim_periods_offs, offs_date_start_p, offs_date_end_p, p_index_offs_p, step \
    = sfun.sim_periods(pinp.sheep['i_startyear'], uinp.structure['i_sim_periods_year'], sim_years_offs)
    date_start_pa1e1b1nwzida0e0b0xyg3 = np.expand_dims(offs_date_start_p, axis = tuple(range(p_pos+1, 0)))
    date_end_pa1e1b1nwzida0e0b0xyg3 = np.expand_dims(offs_date_end_p, axis = tuple(range(p_pos+1, 0)))
    p_index_pa1e1b1nwzida0e0b0xyg3 = np.expand_dims(p_index_offs_p, axis = tuple(range(p_pos+1, 0)))
    mask_p_offs_p = p_index_p<=(n_sim_periods_offs-1)
    ##day of the year
    doy_pa1e1b1nwzida0e0b0xyg = (date_start_pa1e1b1nwzida0e0b0xyg - date_start_pa1e1b1nwzida0e0b0xyg.astype('datetime64[Y]')).astype(int) + 1 #plus one to include current day eg 7th - 1st = 6 plus 1 = 7th day of year
    ##day length
    dl_pa1e1b1nwzida0e0b0xyg = sfun.f_daylength(doy_pa1e1b1nwzida0e0b0xyg, pinp.sheep['i_latitude'])
    ##days in each period
    days_period_pa1e1b1nwzida0e0b0xyg = date_end_pa1e1b1nwzida0e0b0xyg - date_start_pa1e1b1nwzida0e0b0xyg

    ###################################
    ## calculate masks                #
    ###################################
    ##masks required for initialising arrays
    mask_sire_inc_g0 = np.any(uinp.structure['i_mask_g0g3'] * pinp.sheep['i_g3_inc'], axis =1)
    mask_dams_inc_g1 = np.any(uinp.structure['i_mask_g1g3'] * pinp.sheep['i_g3_inc'], axis =1)
    mask_offs_inc_g3 = np.any(uinp.structure['i_mask_g3g3'] * pinp.sheep['i_g3_inc'], axis =1)
    ##o/d mask - if dob is after the end of the sim then it is masked out -  the mask is created before the date of birth is adjusted to the start of a period however it is adjusted to the start of the next period so the mask wont cut out a birth event that actually would occur, additionally this is the birth of the first however the matrix sees the birth of average animal which is also later therefore if anything the mask will leave in unnecessary o slices
    date_born1st_oa1e1b1nwzida0e0b0xyg2 = sfun.f_g2g(pinp.sheep['i_date_born1st_oig2'],'yatf',i_pos,pinp.sheep['i_i_len'],pinp.sheep['i_o_len'],swap=True,left_pos2=p_pos,right_pos2=i_pos, condition=pinp.sheep['i_mask_i'], axis=i_pos).astype('datetime64[D]') #left2 = e1-1 because e1 needs to be included for the calculation following
    mask_o_dams = np.max(date_born1st_oa1e1b1nwzida0e0b0xyg2<=date_end_p[-1], axis=tuple(range(p_pos+1, 0))) #compare each birth opp with the end date of the sim and make the mask - the mask is of the longest axis (ie to handle situations where say bbb and bbm have birth at different times so one has 6 opp and the other has 5 opp)
    mask_d_offs = np.max(date_born1st_oa1e1b1nwzida0e0b0xyg2<=date_end_p[-1], axis=tuple(range(p_pos+1, 0))) #compare each birth opp with the end date of the sim and make the mask - the mask is of the longest axis (ie to handle situations where say bbb and bbm have birth at different times so one has 6 opp and the other has 5 opp)
    mask_x = pinp.sheep['i_gender_propn_x']>0

    # ###################################
    # ### axis len                      #
    # ###################################
    ## Final length of axis after any masks have been applied, used to initialise arrays and in code below (note: these are not used to reshape input array).
    len_m1 = int(step / np.timedelta64(1, 'D')) #convert timedelta to float by dividing by one day
    len_m2 = uinp.structure['i_lag_wool']
    len_m3 = uinp.structure['i_lag_organs']
    len_q0	 = uinp.sheep['i_eqn_exists_q0q1'].shape[1]
    len_q1	 = len(uinp.sheep['i_eqn_reportvars_q1'])
    len_q2	 = np.max(uinp.sheep['i_eqn_reportvars_q1'])
    len_p = len(date_start_p)
    len_f = len(uinp.structure['sheep_pools'])
    len_c = len(uinp.structure['cashflow_periods'])
    len_p3 = len(offs_date_start_p)
    len_p8 = np.count_nonzero(pinp.sheep['i_mask_p8'])
    len_a1 = np.count_nonzero(pinp.sheep['i_mask_a'])
    len_e1 = np.max(pinp.sheep['i_join_cycles_ig1'])
    len_b1 = len(uinp.structure['i_mask_b0_b1'])
    len_n0 = uinp.structure['i_n0_matrix_len']
    len_n1 = uinp.structure['i_n1_matrix_len']
    len_n2 = uinp.structure['i_n1_matrix_len'] #same as dams
    len_n3 = uinp.structure['i_n3_matrix_len']
    len_w0 = uinp.structure['i_w0_len']
    len_w1 = uinp.structure['i_w1_len']
    len_w2 = uinp.structure['i_w1_len'] #same as dams
    len_w_prog = uinp.structure['i_progeny_w2_len']
    len_w3 = uinp.structure['i_w3_len']
    len_z = np.count_nonzero(pinp.sheep['i_mask_z'])
    len_i = np.count_nonzero(pinp.sheep['i_mask_i'])
    lensire_i = np.count_nonzero(pinp.sheep['i_masksire_i'])
    len_d = np.count_nonzero(mask_d_offs)
    len_o = np.count_nonzero(mask_o_dams)
    len_a0 = np.count_nonzero(pinp.sheep['i_mask_a'])
    len_e0 = np.max(pinp.sheep['i_join_cycles_ig1'])
    len_b0 = np.count_nonzero(uinp.structure['i_mask_b0_b1'])
    len_x = np.count_nonzero(mask_x)
    len_y1 = np.count_nonzero(uinp.parameters['i_mask_y'])
    len_y2 = np.count_nonzero(uinp.parameters['i_mask_y'])
    len_y3 = np.count_nonzero(uinp.parameters['i_mask_y'])
    len_g0 = np.count_nonzero(mask_sire_inc_g0)
    len_g1 = np.count_nonzero(mask_dams_inc_g1)
    len_g2 = np.count_nonzero(mask_dams_inc_g1) #same as dams
    len_g3 = np.count_nonzero(mask_offs_inc_g3)
    len_t1 = pinp.sheep['i_n_dam_sales'] + len_g0
    len_t2 = pinp.sheep['i_t2_len']
    len_t3 = pinp.sheep['i_t3_len']

    ###################################
    ### index arrays                  #
    ###################################
    # index_p = np.arange(300)#asarray(300)
    index_a0e0b0xyg = fun.f_reshape_expand(np.arange(len_a1), a0_pos)
    index_a1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(np.arange(len_a1), a1_pos)
    index_b0xyg = fun.f_reshape_expand(np.arange(len_b0), b0_pos)
    index_b1nwzida0e0b0xyg = fun.f_reshape_expand(np.arange(len_b1), b1_pos)
    index_l = np.arange(uinp.structure['i_len_l']) #gbal
    index_s = np.arange(uinp.structure['i_len_s']) #scan
    index_d = np.arange(len_d)
    index_da0e0b0xyg = fun.f_reshape_expand(index_d, d_pos)
    index_e = np.arange(np.max(pinp.sheep['i_join_cycles_ig1']))
    index_e1b1nwzida0e0b0xyg = fun.f_reshape_expand(index_e, e1_pos)
    index_e0b0xyg = fun.f_reshape_expand(index_e, e0_pos)
    index_g0 = np.arange(len_g0)
    index_g1 = np.arange(len_g1)
    index_g9 = index_g1
    index_g1g = index_g1[:,na]
    index_i = np.arange(len_i)
    index_ida0e0b0xyg = fun.f_reshape_expand(index_i, i_pos)
    index_i9 = index_i
    index_m1 = np.arange(len_m1)
    index_m0 = np.arange(12)*2  #2hourly steps for chill calculations
    index_z = np.arange(len_z)
    index_w0 = np.arange(len_w0)
    index_wzida0e0b0xyg0 = fun.f_reshape_expand(index_w0, w_pos)
    index_w1 = np.arange(len_w1)
    index_wzida0e0b0xyg1 = fun.f_reshape_expand(index_w1, w_pos)
    index_w2 = np.arange(uinp.structure['i_progeny_w2_len'])
    index_w3 = np.arange(len_w3)
    index_wzida0e0b0xyg3 = fun.f_reshape_expand(index_w3, w_pos)
    index_tva1e1b1nw8zida0e0b0xyg1 = fun.f_reshape_expand(np.arange(len_t1), p_pos-1)
    index_tva1e1b1nw8zida0e0b0xyg1w9 = index_tva1e1b1nw8zida0e0b0xyg1[...,na]
    index_t2 = np.arange(len_t2)
    index_tva1e1b1nwzida0e0b0xyg2w9 = fun.f_reshape_expand(index_t2, p_pos-2)
    index_tva1e1b1nw8zida0e0b0xyg3w9 = fun.f_reshape_expand(np.arange(len_t3), p_pos-2)



    prejoin_tup = (a1_pos, b1_pos, e1_pos)
    season_tup = (z_pos)

    ############################
    ### initialise arrays      #
    ############################
    '''only if assigned with a slice'''
    ##unique array shapes required to initialise arrays
    qg0 = (len_q0, len_q1, len_q2, len_p, 1, 1, 1, 1, 1, len_z, lensire_i, 1, 1, 1, 1, 1, 1, len_g0)
    qg1 = (len_q0, len_q1, len_q2, len_p, len_a1, len_e1, len_b1, len_n1, len_w1, len_z, len_i, 1, 1, 1, 1, 1, len_y1, len_g1)
    qg2 = (len_q0, len_q1, len_q2, len_p, len_a1, len_e1, len_b1, len_n2, len_w2, len_z, len_i, 1, 1, 1, 1, len_x, len_y2, len_g1)
    qg3 = (len_q0, len_q1, len_q2, len_p3, 1, 1, 1, len_n3, len_w3, len_z, len_i, len_d, len_a0, len_e0, len_b0, len_x, len_y3, len_g3)
    pg0 = (len_p, 1, 1, 1, 1, 1, len_z, lensire_i, 1, 1, 1, 1, 1, 1, len_g0)
    pg1 = (len_p, len_a1, len_e1, len_b1, len_n1, len_w1, len_z, len_i, 1, 1, 1, 1, 1, len_y1, len_g1)
    pg2 = (len_p, len_a1, len_e1, len_b1, len_n2, len_w2, len_z, len_i, 1, 1, 1, 1, len_x, len_y2, len_g1)
    pg3 = (len_p3, 1, 1, 1, len_n3, len_w3, len_z, len_i, len_d, len_a0, len_e0, len_b0, len_x, len_y3, len_g3)
    m2g0 = (len_m2, 1, 1, 1, 1, 1, len_z, lensire_i, 1, 1, 1, 1, 1, 1, len_g0)
    m2g1 = (len_m2, len_a1, len_e1, len_b1, len_n1, len_w1, len_z, len_i, 1, 1, 1, 1, 1, len_y1, len_g1)
    m2g2 = (len_m2, len_a1, len_e1, len_b1, len_n2, len_w2, len_z, len_i, 1, 1, 1, 1, len_x, len_y2, len_g2)
    m2g3 = (len_m2, 1, 1, 1, len_n3, len_w3, len_z, len_i, len_d, len_a0, len_e0, len_b0, len_x, len_y3, len_g3)
    m3g0 = (len_m3, 1, 1, 1, 1, 1, len_z, lensire_i, 1, 1, 1, 1, 1, 1, len_g0)
    m3g1 = (len_m3, len_a1, len_e1, len_b1, len_n1, len_w1, len_z, len_i, 1, 1, 1, 1, 1, len_y1, len_g1)
    m3g2 = (len_m3, len_a1, len_e1, len_b1, len_n2, len_w2, len_z, len_i, 1, 1, 1, 1, len_x, len_y2, len_g2)
    m3g3 = (len_m3, 1, 1, 1, len_n3, len_w3, len_z, len_i, len_d, len_a0, len_e0, len_b0, len_x, len_y3, len_g3)


    ##output variables for postprocessing & reporting
    dtype='float32' #using 64 was getting slow
    dtypeint='int32' #using 64 was getting slow

    ##sire
    ###array for generator
    omer_history_start_m3g0 = np.zeros(m3g0, dtype = 'float64')
    d_cfw_history_start_m2g0 = np.zeros(m2g0, dtype = 'float64')
    woolvalue_pa1e1b1nwzida0e0b0xyg0 = np.zeros(pg0, dtype =dtype)
    salevalue_pa1e1b1nwzida0e0b0xyg0 = np.zeros(pg0, dtype =dtype)
    ###arrays for postprocessing
    o_numbers_start_psire = np.zeros(pg0, dtype =dtype)
    o_numbers_end_psire = np.zeros(pg0, dtype =dtype)
    o_ffcfw_psire = np.zeros(pg0, dtype =dtype)
    o_ffcfw_condensed_psire = np.zeros(pg0, dtype =dtype)
    o_nw_start_psire = np.zeros(pg0, dtype=dtype)
    o_lw_psire = np.zeros(pg0, dtype =dtype)
    o_pi_psire = np.zeros(pg0, dtype =dtype)
    o_mei_solid_psire = np.zeros(pg0, dtype =dtype)
    o_ch4_total_psire = np.zeros(pg0, dtype =dtype)
    o_cfw_psire = np.zeros(pg0, dtype =dtype)
    o_sl_psire = np.zeros(pg0, dtype =dtype)
    o_ss_psire = np.zeros(pg0, dtype =dtype)
    o_fd_psire = np.zeros(pg0, dtype =dtype)
    o_fd_min_psire = np.zeros(pg0, dtype =dtype)
    o_rc_start_psire = np.zeros(pg0, dtype =dtype)
    o_ebg_psire = np.zeros(pg0, dtype =dtype)
    ###arrays for report variables
    r_compare_q0q1q2psire = np.zeros(qg0, dtype = dtype) #empty arrays to store different return values from the equation systems in the p loop.

    ##dams
    ###array for generator
    omer_history_start_m3g1 = np.zeros(m3g1, dtype = 'float64')
    d_cfw_history_start_m2g1 = np.zeros(m2g1, dtype = 'float64')
    woolvalue_pa1e1b1nwzida0e0b0xyg1 = np.zeros(pg1, dtype =dtype)
    salevalue_pa1e1b1nwzida0e0b0xyg1 = np.zeros(pg1, dtype =dtype)
    ###arrays for postprocessing
    o_numbers_start_pdams = np.zeros(pg1, dtype =dtype)
    o_numbers_join_pdams = np.zeros(pg1, dtype =dtype)
    o_numbers_end_pdams = np.zeros(pg1, dtype =dtype)
    o_ffcfw_pdams = np.zeros(pg1, dtype =dtype)
    o_ffcfw_condensed_pdams = np.zeros(pg1, dtype =dtype)
    o_nw_start_pdams = np.zeros(pg1, dtype = dtype)
    o_lw_pdams = np.zeros(pg1, dtype =dtype)
    o_pi_pdams = np.zeros(pg1, dtype =dtype)
    o_mei_solid_pdams = np.zeros(pg1, dtype =dtype)
    o_ch4_total_pdams = np.zeros(pg1, dtype =dtype)
    o_cfw_pdams = np.zeros(pg1, dtype =dtype)
    # o_gfw_pdams = np.zeros(pg1, dtype =dtype)
    o_sl_pdams = np.zeros(pg1, dtype =dtype)
    o_ss_pdams = np.zeros(pg1, dtype =dtype)
    o_fd_pdams = np.zeros(pg1, dtype =dtype)
    o_fd_min_pdams = np.zeros(pg1, dtype =dtype)
    o_rc_start_pdams = np.zeros(pg1, dtype =dtype)
    o_ebg_pdams = np.zeros(pg1, dtype =dtype)
    o_cfw_ltwadj_pdams = np.zeros(pg1, dtype =dtype)
    o_fd_ltwadj_pdams = np.zeros(pg1, dtype =dtype)
    o_n_sire_pa1e1b1nwzida0e0b0xyg1g0p8 = np.zeros((len_p, 1, 1, 1, 1, 1, len_z, len_i, 1, 1, 1, 1, 1, len_y1, len_g1,len_g0,len_p8), dtype =dtype)
    ###arrays for report variables
    r_compare_q0q1q2pdams = np.zeros(qg1, dtype = dtype) #empty arrays to store different return values from the equation systems in the p loop.
    r_foo_pdams = np.zeros(pg1, dtype = dtype)
    r_dmd_pdams = np.zeros(pg1, dtype = dtype)
    r_evg_pdams = np.zeros(pg1, dtype = dtype)
    r_intake_f_pdams = np.zeros(pg1, dtype = dtype)
    r_md_solid_pdams = np.zeros(pg1, dtype = dtype)
    r_mp2_pdams = np.zeros(pg1, dtype = dtype)
    r_d_cfw_pdams =  np.zeros(pg1, dtype = dtype)

    ##yatf
    ###array for generator
    omer_history_start_m3g2 = np.zeros(m3g2, dtype = 'float64')
    d_cfw_history_start_m2g2 = np.zeros(m2g2, dtype = 'float64')
    ###array for postprocessing
    o_numbers_start_pyatf = np.zeros(pg2, dtype =dtype)
    # o_numbers_end_pyatf = np.zeros(pg2, dtype =dtype)
    o_ffcfw_start_pyatf = np.zeros(pg2, dtype =dtype)
    # o_ffcfw_condensed_pyatf = np.zeros(pg2, dtype =dtype)
    o_pi_pyatf = np.zeros(pg2, dtype =dtype)
    o_mei_solid_pyatf = np.zeros(pg2, dtype =dtype)
    # o_ch4_total_pyatf = np.zeros(pg2, dtype =dtype)
    # o_cfw_pyatf = np.zeros(pg2, dtype =dtype)
    # o_gfw_pyatf = np.zeros(pg2, dtype =dtype)
    # o_sl_pyatf = np.zeros(pg2, dtype =dtype)
    # o_ss_pyatf = np.zeros(pg2, dtype =dtype)
    # o_fd_pyatf = np.zeros(pg2, dtype =dtype)
    # o_fd_min_pyatf = np.zeros(pg2, dtype =dtype)
    o_rc_start_pyatf = np.zeros(pg2, dtype =dtype)
    ###arrays for report variables
    r_compare_q0q1q2pyatf = np.zeros(qg2, dtype = dtype) #empty arrays to store different return values from the equation systems in the p loop.
    r_ebg_pyatf = np.zeros(pg2, dtype = dtype)
    r_evg_pyatf = np.zeros(pg2, dtype = dtype)
    r_mem_pyatf = np.zeros(pg2, dtype = dtype)
    r_mei_pyatf = np.zeros(pg2, dtype = dtype)
    r_mei_solid_pyatf = np.zeros(pg2, dtype = dtype)
    r_propn_solid_pyatf = np.zeros(pg2, dtype = dtype)
    r_pi_pyatf = np.zeros(pg2, dtype = dtype)
    r_kg_pyatf = np.zeros(pg2, dtype = dtype)
    r_mp2_pyatf = np.zeros(pg2, dtype = dtype)
    r_intake_f_pyatf = np.zeros(pg2, dtype = dtype)
    r_nw_start_pyatf = np.zeros(pg2, dtype = dtype)


    ##offs
    ###array for generator
    omer_history_start_m3g3 = np.zeros(m3g3, dtype = 'float64')
    d_cfw_history_start_m2g3 = np.zeros(m2g3, dtype = 'float64')
    woolvalue_tpa1e1b1nwzida0e0b0xyg3 = np.zeros((len_t3,)+pg3, dtype =dtype)
    salevalue_pa1e1b1nwzida0e0b0xyg3 = np.zeros(pg3, dtype =dtype)
    ###array for postprocessing
    o_numbers_start_poffs = np.zeros(pg3, dtype =dtype)
    o_numbers_end_poffs = np.zeros(pg3, dtype =dtype)
    o_ffcfw_poffs = np.zeros(pg3, dtype =dtype)
    o_ffcfw_condensed_poffs = np.zeros(pg3, dtype =dtype)
    o_nw_start_poffs = np.zeros(pg3, dtype=dtype)
    o_lw_poffs = np.zeros(pg3, dtype =dtype)
    o_pi_poffs = np.zeros(pg3, dtype =dtype)
    o_mei_solid_poffs = np.zeros(pg3, dtype =dtype)
    o_ch4_total_poffs = np.zeros(pg3, dtype =dtype)
    o_cfw_poffs = np.zeros(pg3, dtype =dtype)
    # o_gfw_poffs = np.zeros(pg3, dtype =dtype)
    o_sl_poffs = np.zeros(pg3, dtype =dtype)
    o_ss_poffs = np.zeros(pg3, dtype =dtype)
    o_fd_poffs = np.zeros(pg3, dtype =dtype)
    o_fd_min_poffs = np.zeros(pg3, dtype =dtype)
    o_rc_start_poffs = np.zeros(pg3, dtype =dtype)
    o_ebg_poffs = np.zeros(pg3, dtype =dtype)
    ###arrays for report variables
    r_compare_q0q1q2poffs = np.zeros(qg3, dtype = dtype) #empty arrays to store different return values from the equation systems in the p loop.




    ################################################
    #  management, age, date, timing inputs inputs #
    ################################################
    ##gender propn yatf
    gender_propn_xyg = fun.f_reshape_expand(pinp.sheep['i_gender_propn_x'], x_pos, condition=mask_x, axis=0).astype(dtype)
    ##join
    join_cycles_ida0e0b0xyg1 = sfun.f_g2g(pinp.sheep['i_join_cycles_ig1'],'dams',i_pos)[pinp.sheep['i_mask_i'],...]
    ##lamb and lost
    gbal_oa1e1b1nwzida0e0b0xyg1 = sfun.f_g2g(pinp.sheep['i_gbal_og1'],'dams',p_pos, condition=mask_o_dams, axis=p_pos) #need axis up to p so that p association can be applied
    gbal_da0e0b0xyg3 = sfun.f_g2g(pinp.sheep['i_gbal_og1'],'dams',d_pos, condition=mask_d_offs, axis=d_pos) #need axis up to p so that p association can be applied
    ##scanning
    scan_oa1e1b1nwzida0e0b0xyg1 = sfun.f_g2g(pinp.sheep['i_scan_og1'],'dams',p_pos, condition=mask_o_dams, axis=p_pos) #need axis up to p so that p association can be applied
    scan_da0e0b0xyg3 = sfun.f_g2g(pinp.sheep['i_scan_og1'],'dams',d_pos, condition=mask_d_offs, axis=d_pos) #need axis up to p so that p association can be applied
    ##post weaning management
    wean_oa1e1b1nwzida0e0b0xyg1 = sfun.f_g2g(pinp.sheep['i_wean_og1'],'dams',p_pos, condition=mask_o_dams, axis=p_pos) #need axis up to p so that p association can be applied
    ##association between offspring and sire/dam (used to determine the wean age of sire and dams based on the inputted wean age of offs)
    a_g0_g1 = sfun.f_g2g(pinp.sheep['ia_g0_g1'],'dams')
    a_g3_g0 = sfun.f_g2g(pinp.sheep['ia_g3_g0'],'sire')  # the sire association (pure bred B, M & T) are all based on purebred B because there are no pure bred M & T inputs
    a_g3_g1 = sfun.f_g2g(pinp.sheep['ia_g3_g1'],'dams')  # if BMT exist then BBM exist and they will be in slice 1, therefore the association value doesn't need to be adjusted for "prior exclusions"
    ##age weaning- used to calc wean date and also to calc m1 stuff, sire and dams have no active a0 slice therefore just take the first slice
    age_wean1st_a0e0b0xyg3 = sfun.f_g2g(pinp.sheep['i_age_wean_a0g3'],'offs',a0_pos).astype('timedelta64[D]')[pinp.sheep['i_mask_a']]
    age_wean1st_e0b0xyg0 = np.rollaxis(age_wean1st_a0e0b0xyg3[0, ...,a_g3_g0],0,age_wean1st_a0e0b0xyg3.ndim-1) #when you slice one slice of the array and also take multiple slices from another axis the axis with multiple slices jumps to the front therefore need to roll the g axis back to the end
    age_wean1st_e0b0xyg1 = np.rollaxis(age_wean1st_a0e0b0xyg3[0, ...,a_g3_g1],0,age_wean1st_a0e0b0xyg3.ndim-1) #when you slice one slice of the array and also take multiple slices from another axis the axis with multiple slices jumps to the front therefore need to roll the g axis back to the end
    ##date first lamb is born - need to apply i mask to these inputs - make sure animals are born at beginning of gen period
    date_born1st_ida0e0b0xyg0 = sfun.f_g2g(pinp.sheep['i_date_born1st_ig0'],'sire',i_pos, condition=pinp.sheep['i_masksire_i'], axis=i_pos).astype('datetime64[D]')
    date_born1st_ida0e0b0xyg1 = sfun.f_g2g(pinp.sheep['i_date_born1st_ig1'],'dams',i_pos, condition=pinp.sheep['i_mask_i'], axis=i_pos).astype('datetime64[D]')
    date_born1st_oa1e1b1nwzida0e0b0xyg2 = date_born1st_oa1e1b1nwzida0e0b0xyg2[mask_o_dams,...] #input read in in the mask section
    date_born1st_ida0e0b0xyg3 = sfun.f_g2g(pinp.sheep['i_date_born1st_idg3'],'offs',d_pos,pinp.sheep['i_i_len'],uinp.parameters['i_d_len'], condition=pinp.sheep['i_mask_i'], axis=i_pos, condition2=mask_d_offs, axis2=d_pos).astype('datetime64[D]')
    ##mating
    sire_propn_oa1e1b1nwzida0e0b0xyg1 = sfun.f_g2g(pinp.sheep['i_sire_propn_oig1'],'dams',i_pos,pinp.sheep['i_i_len'], pinp.sheep['i_o_len'],swap=True,left_pos2=p_pos,right_pos2=i_pos, condition=pinp.sheep['i_mask_i'], axis=i_pos, condition2=mask_o_dams, axis2=p_pos)
    sire_periods_p8g0 = sfun.f_g2g(pinp.sheep['i_sire_periods_p8g0'], 'sire', condition=pinp.sheep['i_mask_p8'], axis=0)
    sire_periods_g0p8 = np.swapaxes(sire_periods_p8g0, 0, 1) #cant swap in function above because g needs to be in pos-1
    ##Shearing date - set to be on the last day of a sim period
    ###sire
    date_shear_sida0e0b0xyg0 = sfun.f_g2g(pinp.sheep['i_date_shear_sixg0'],'sire',x_pos,pinp.sheep['i_i_len'], pinp.sheep['i_s_len'], pinp.sheep['i_x_len']
                                          ,swap=True,left_pos2=i_pos,right_pos2=x_pos, condition=pinp.sheep['i_masksire_i'], axis=i_pos
                                          )[...,0:1,:,:].astype('datetime64[D]') #slice x axis for only female
    mask_shear_g0 = np.max(date_shear_sida0e0b0xyg0<=date_end_p[-1], axis=tuple(range(i_pos, 0))) #mask out shearing opps that occur after gen is done
    date_shear_sida0e0b0xyg0 = date_shear_sida0e0b0xyg0[mask_shear_g0]
    ###dam
    date_shear_sida0e0b0xyg1 = sfun.f_g2g(pinp.sheep['i_date_shear_sixg1'],'dams',x_pos,pinp.sheep['i_i_len'], pinp.sheep['i_s_len'], pinp.sheep['i_x_len']
                                          ,swap=True,left_pos2=i_pos,right_pos2=x_pos, condition=pinp.sheep['i_mask_i'], axis=i_pos
                                          )[...,1:2,:,:].astype('datetime64[D]') #slice x axis for only female
    mask_shear_g1 = np.max(date_shear_sida0e0b0xyg1<=date_end_p[-1], axis=tuple(range(i_pos, 0))) #mask out shearing opps that occur after gen is done
    date_shear_sida0e0b0xyg1 = date_shear_sida0e0b0xyg1[mask_shear_g1]
    ###off - shearing cant occur as yatf because then need to shear all lambs (ie no scope to not shear the lambs that are going to be fed up and sold) because the offs decision variables for feeding are not linked to the yatf (which are in the dam decision variables)
    date_shear_sida0e0b0xyg3 = sfun.f_g2g(pinp.sheep['i_date_shear_sixg3'],'offs',x_pos,pinp.sheep['i_i_len'], pinp.sheep['i_s_len'], pinp.sheep['i_x_len']
                                          ,swap=True,left_pos2=i_pos,right_pos2=x_pos, condition=pinp.sheep['i_mask_i'], axis=i_pos
                                          , condition2=mask_x, axis2=x_pos).astype('datetime64[D]')
    mask_shear_g3 = np.max(date_shear_sida0e0b0xyg3<=offs_date_end_p[-1], axis=tuple(range(i_pos, 0))) #mask out shearing opps that occur after gen is done
    date_shear_sida0e0b0xyg3 = date_shear_sida0e0b0xyg3[mask_shear_g3]

    ############################
    ### feed supply inputs     #
    ############################
    ##feedsupply
    ###feedsupply option selected
    a_r_zida0e0b0xyg0 = sfun.f_g2g(pinp.sheep['ia_r1_zig0'],'sire',i_pos,pinp.sheep['i_i_len'], pinp.sheep['i_z_len'],swap=True, condition=pinp.sheep['i_masksire_i'], axis=i_pos)
    a_r_zida0e0b0xyg1 = sfun.f_g2g(pinp.sheep['ia_r1_zig1'],'dams',i_pos,pinp.sheep['i_i_len'], pinp.sheep['i_z_len'],swap=True, condition=pinp.sheep['i_mask_i'], axis=i_pos)
    a_r_zida0e0b0xyg3 = sfun.f_g2g(pinp.sheep['ia_r1_zig3'],'offs',i_pos,pinp.sheep['i_i_len'], pinp.sheep['i_z_len'],swap=True, condition=pinp.sheep['i_mask_i'], axis=i_pos)
    ###feed variation for dams
    a_r2_k0e1b1nwzida0e0b0xyg1 = sfun.f_g2g(pinp.sheep['ia_r2_k0ig1'],'dams',i_pos,pinp.sheep['i_i_len'], pinp.sheep['i_k0_len'],swap=True,left_pos2=a1_pos,right_pos2=i_pos, condition=pinp.sheep['i_mask_i'], axis=i_pos)
    a_r2_k1b1nwzida0e0b0xyg1 = sfun.f_g2g(pinp.sheep['ia_r2_k1ig1'],'dams',i_pos,pinp.sheep['i_i_len'], pinp.sheep['i_k1_len'],swap=True,left_pos2=e1_pos,right_pos2=i_pos, condition=pinp.sheep['i_mask_i'], axis=i_pos)
    a_r2_k2nwzida0e0b0xyg1 = sfun.f_g2g(pinp.sheep['ia_r2_k2ig1'],'dams',i_pos,pinp.sheep['i_i_len'], pinp.sheep['i_k2_len'],swap=True,left_pos2=b1_pos,right_pos2=i_pos, condition=pinp.sheep['i_mask_i'], axis=i_pos)  #add axis between g and i and i and b1
    ###feed variation for offs
    a_r2_idk0e0b0xyg3 = sfun.f_g2g(pinp.sheep['ia_r2_ik0g3'],'offs',a0_pos,pinp.sheep['i_i_len'], pinp.sheep['i_k0_len'],left_pos2=i_pos,right_pos2=a0_pos, condition=pinp.sheep['i_mask_i'], axis=i_pos)
    a_r2_ik3a0e0b0xyg3 = sfun.f_g2g(pinp.sheep['ia_r2_ik3g3'],'offs',d_pos,pinp.sheep['i_i_len'], pinp.sheep['i_k3_len'], condition=pinp.sheep['i_mask_i'], axis=i_pos)
    a_r2_ida0e0k4xyg3 = sfun.f_g2g(pinp.sheep['ia_r2_ik4g3'],'offs',b0_pos,pinp.sheep['i_i_len'], pinp.sheep['i_k4_len'],left_pos2=i_pos,right_pos2=b0_pos, condition=pinp.sheep['i_mask_i'], axis=i_pos)  #add axis between g and b0 and b0 and i
    a_r2_ida0e0b0k5yg3 = sfun.f_g2g(pinp.sheep['ia_r2_ik5g3'],'offs',x_pos,pinp.sheep['i_i_len'], pinp.sheep['i_k5_len'],left_pos2=i_pos,right_pos2=x_pos, condition=pinp.sheep['i_mask_i'], axis=i_pos)  #add axis between g and b0 and b0 and i

    ##std feed options
    feedoptions_r1j0p = pinp.feedsupply['i_feedoptions_r1pj0'].reshape(pinp.feedsupply['i_r1_len'],pinp.feedsupply['i_j0_len'],pinp.feedsupply['i_feedoptions_r1pj0'].shape[-1])[...,0:len_p].astype(np.float) #slice off extra p periods so it is the same length as the sim periods
    ##feed variation
    feedoptions_var_r2p = pinp.feedsupply['i_feedoptions_var_r2p'][:,0:len_p].astype(np.float) #slice off extra p periods so it is the same length as the sim periods
    ##an association between the k2 cluster (feed variation) and reproductive management (scanning, gbal & weaning).
    a_k2_mlsb1 = uinp.structure['ia_k2_mlsb1'].reshape(uinp.structure['i_len_m'], uinp.structure['i_len_l'], uinp.structure['i_len_s'], uinp.structure['ia_k2_mlsb1'].shape[-1])

    ############
    #fvp inputs#
    ############
    fvp0_offset_ida0e0b0xyg3 = sfun.f_g2g(pinp.sheep['i_fvp0_offset_ig3'], 'offs', i_pos, condition=pinp.sheep['i_mask_i'], axis=i_pos)
    fvp1_offset_ida0e0b0xyg3 = sfun.f_g2g(pinp.sheep['i_fvp1_offset_ig3'], 'offs', i_pos, condition=pinp.sheep['i_mask_i'], axis=i_pos)
    fvp2_offset_ida0e0b0xyg3 = sfun.f_g2g(pinp.sheep['i_fvp2_offset_ig3'], 'offs', i_pos, condition=pinp.sheep['i_mask_i'], axis=i_pos)

    ###################################
    ###group independent              #  type(pinp.sheep['i_mask_z']).dtype
    ###################################
    ##association between b0 and b1
    a_b0_b1nwzida0e0b0xyg = fun.f_reshape_expand(uinp.structure['ia_b0_b1'], b1_pos)
    ##nfoet expanded
    nfoet_b1nwzida0e0b0xyg = fun.f_reshape_expand(uinp.structure['a_nfoet_b1'], b1_pos)
    ##nyatf expanded to b1 & b0
    nyatf_b1nwzida0e0b0xyg = fun.f_reshape_expand(uinp.structure['a_nyatf_b1'], b1_pos)
    #nyatf_b0xyg = fun.f_reshape_expand(uinp.structure['a_nyatf_b0'], b0_pos)
    ##legume proportion in each period
    legume_p6a1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(pinp.sheep['i_legume_p6z'], z_pos, pinp.sheep['i_p6_len'], pinp.sheep['i_z_len'], left_pos2=p_pos, right_pos2=z_pos, condition = pinp.sheep['i_mask_z'], axis = z_pos) #p6 axis converted to p axis later (association section)
    ##estimated foo and dmd for the midas periods - apply z mask
    paststd_foo_p6a1e1b1j0wzida0e0b0xyg = fun.f_reshape_expand(pinp.sheep['i_paststd_foo_p6zj0'], z_pos, len_ax0=pinp.sheep['i_p6_len'], len_ax1=pinp.sheep['i_z_len'], len_ax2=pinp.feedsupply['i_j0_len'], swap=True, ax1=1, ax2=2, left_pos2=n_pos, right_pos2=z_pos, left_pos3=p_pos, right_pos3=n_pos, condition = pinp.sheep['i_mask_z'], axis = z_pos) #p6 axis converted to p axis later (association section), axis order doesnt matter because sliced when used
    paststd_dmd_p6a1e1b1j0wzida0e0b0xyg = fun.f_reshape_expand(pinp.sheep['i_paststd_dmd_p6zj0'], z_pos, len_ax0=pinp.sheep['i_p6_len'], len_ax1=pinp.sheep['i_z_len'], len_ax2=pinp.feedsupply['i_j0_len'], swap=True, ax1=1, ax2=2, left_pos2=n_pos, right_pos2=z_pos, left_pos3=p_pos, right_pos3=n_pos, condition = pinp.sheep['i_mask_z'], axis = z_pos) #p6 axis converted to p axis later (association section), axis order doesnt matter because sliced when used
    pasture_stage_p6a1e1b1j0wzida0e0b0xyg = fun.f_reshape_expand(pinp.sheep['i_pasture_stage_p6z'], z_pos, len_ax0=pinp.sheep['i_p6_len'], len_ax1=pinp.sheep['i_z_len'], left_pos2=p_pos, right_pos2=z_pos, condition = pinp.sheep['i_mask_z'], axis = z_pos) #p6 axis converted to p axis later (association section)
    ##season type
    i_season_propn_z=np.array([pinp.sheep['i_season_propn_z']]) #convert to np array - this is required if inputs only have one season
    season_propn_zida0e0b0xyg = fun.f_reshape_expand(i_season_propn_z, z_pos, condition = pinp.sheep['i_mask_z'], axis = z_pos) #minimum 1 because p axis needs to be added
    season_propn_zida0e0b0xyg = season_propn_zida0e0b0xyg/sum(i_season_propn_z[pinp.sheep['i_mask_z']]) #adjust probability of each season to account for some seasons being masked out
    ##wind speed
    ws_m4a1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(pinp.sheep['i_ws_m4'], p_pos)
    ##expected stocking density
    density_p6a1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(pinp.sheep['i_density_p6z'], z_pos, pinp.sheep['i_p6_len'], pinp.sheep['i_z_len'], left_pos2=p_pos, right_pos2=z_pos) #p6 axis converted to p axis later (association section)
    ##nutrition adjustment for expected stocking density
    density_nwzida0e0b0xyg1 = fun.f_reshape_expand(uinp.structure['i_density_g1_n'], n_pos)
    density_nwzida0e0b0xyg3 = fun.f_reshape_expand(uinp.structure['i_density_g3_n'], n_pos)
    ##Calculation of rainfall distribution across the week - i_rain_distribution_m4m1 = how much rain falls on each day of the week sorted in order of quantity of rain. SO the most rain falls on the day with the highest rainfall.
    rain_m4a1e1b1nwzida0e0b0xygm1 = fun.f_reshape_expand(pinp.sheep['i_rain_m4'][...,na] * pinp.sheep['i_rain_distribution_m4m1'] * (7/30.4), p_pos-1,right_pos=-1) #-1 because p is -16 when m1 axis is included
    ##Mean daily temperature
    temp_ave_m4a1e1b1nwzida0e0b0xyg= fun.f_reshape_expand(pinp.sheep['i_temp_ave_m4'], p_pos)
    ##Mean daily maximum temperature
    temp_max_m4a1e1b1nwzida0e0b0xyg= fun.f_reshape_expand(pinp.sheep['i_temp_max_m4'], p_pos)
    ##Mean daily minimum temperature
    temp_min_m4a1e1b1nwzida0e0b0xyg= fun.f_reshape_expand(pinp.sheep['i_temp_min_m4'], p_pos)
    ##latitude
    lat_deg = pinp.sheep['i_latitude']
    lat_rad = np.radians(pinp.sheep['i_latitude'])
    ##min numbers
    numbers_min_b1nwzida0e0b0xyg = fun.f_reshape_expand(uinp.structure['i_numbers_min_b1'], b1_pos)

    ############################
    ### sim param arrays       # '''csiro params '''
    ############################
    ##convert input params from c to g
    ###production params
    agedam_propn_da0e0b0xyg0, agedam_propn_da0e0b0xyg1, agedam_propn_da0e0b0xyg2, agedam_propn_da0e0b0xyg03 = sfun.f_c2g(uinp.parameters['i_agedam_propn_std_dc2'], uinp.parameters['i_agedam_propn_y'], uinp.parameters['i_agedam_propn_pos'], condition=mask_o_dams, axis=d_pos) #yatf and off never used
    aw_propn_yg0, aw_propn_yg1, aw_propn_yg2, aw_propn_yg3 = sfun.f_c2g(uinp.parameters['i_aw_propn_wean_c2'], uinp.parameters['i_aw_wean_y'])
    bw_propn_yg0, bw_propn_yg1, bw_propn_yg2, bw_propn_yg3 = sfun.f_c2g(uinp.parameters['i_bw_propn_wean_c2'], uinp.parameters['i_bw_wean_y'])
    cfw_propn_yg0, cfw_propn_yg1, cfw_propn_yg2, cfw_propn_yg3 = sfun.f_c2g(uinp.parameters['i_cfw_propn_c2'], uinp.parameters['i_cfw_propn_y'])
    fl_birth_yg0, fl_birth_yg1, fl_birth_yg2, fl_birth_yg3 = sfun.f_c2g(uinp.parameters['i_fl_birth_c2'], uinp.parameters['i_fl_birth_y'])
    fl_shear_yg0, fl_shear_yg1, fl_shear_yg2, fl_shear_yg3 = sfun.f_c2g(uinp.parameters['i_fl_shear_c2'], uinp.parameters['i_fl_shear_y'])

    scan_std_yg0, scan_std_yg1, scan_std_yg2, scan_std_yg3 = sfun.f_c2g(uinp.parameters['i_scan_std_c2'], uinp.parameters['i_scan_std_y']) #scan_std_yg2/3 not used
    scan_dams_std_yg3 = scan_std_yg1 #offs needs to be the same as dams because scan_std is used to calc starting propn of BTRT which is dependant on dams scanning
    pss_std_yg0, pss_std_yg1, pss_std_yg2, pss_std_yg3 = sfun.f_c2g(uinp.parameters['i_lss_std_c2'], uinp.parameters['i_lss_std_y'])
    pstr_std_yg0, pstr_std_yg1, pstr_std_yg2, pstr_std_yg3 = sfun.f_c2g(uinp.parameters['i_lstr_std_c2'], uinp.parameters['i_lstr_std_y'])
    pstw_std_yg0, pstw_std_yg1, pstw_std_yg2, pstw_std_yg3 = sfun.f_c2g(uinp.parameters['i_lstw_std_c2'], uinp.parameters['i_lstw_std_y'])
    mw_propn_yg0, mw_propn_yg1, mw_propn_yg2, mw_propn_yg3 = sfun.f_c2g(uinp.parameters['i_mw_propn_wean_c2'], uinp.parameters['i_mw_wean_y'])
    sfd_yg0, sfd_yg1, sfd_yg2, sfd_yg3 = sfun.f_c2g(uinp.parameters['i_sfd_c2'], uinp.parameters['i_sfd_y'])
    sfw_yg0, sfw_yg1, sfw_yg2, sfw_yg3 = sfun.f_c2g(uinp.parameters['i_sfw_c2'], uinp.parameters['i_sfw_y'])
    srw_female_yg0, srw_female_yg1, srw_female_yg2, srw_female_yg3 = sfun.f_c2g(uinp.parameters['i_srw_c2'], uinp.parameters['i_srw_y']) #srw of a female of the given genotype (this is the definition of the inputs)

    ###sim params
    ca_sire, ca_dams, ca_yatf, ca_offs = sfun.f_c2g(uinp.parameters['i_ca_c2'], uinp.parameters['i_ca_y'], uinp.parameters['i_ca_pos'], uinp.parameters['i_ca_len'])
    cb0_sire, cb0_dams, cb0_yatf, cb0_offs = sfun.f_c2g(uinp.parameters['i_cb0_c2'], uinp.parameters['i_cb0_y'], uinp.parameters['i_cb0_pos'], uinp.parameters['i_cb0_len'], uinp.parameters['i_cb0_len2'])
    cc_sire, cc_dams, cc_yatf, cc_offs = sfun.f_c2g(uinp.parameters['i_cc_c2'], uinp.parameters['i_cc_y'], uinp.parameters['i_cc_pos'], uinp.parameters['i_cc_len'])
    cd_sire, cd_dams, cd_yatf, cd_offs = sfun.f_c2g(uinp.parameters['i_cd_c2'], uinp.parameters['i_cd_y'], uinp.parameters['i_cd_pos'], uinp.parameters['i_cd_len'])
    ce_sire, ce_dams, ce_yatf, ce_offs = sfun.f_c2g(uinp.parameters['i_ce_c2'], uinp.parameters['i_ce_y'], uinp.parameters['i_ce_pos'], uinp.parameters['i_ce_len'], uinp.parameters['i_ce_len2'], condition=mask_o_dams, axis=d_pos)
    ce_offs = sfun.f_c2g(uinp.parameters['i_ce_c2'], uinp.parameters['i_ce_y'], uinp.parameters['i_ce_pos'], uinp.parameters['i_ce_len'], uinp.parameters['i_ce_len2'], condition=mask_d_offs, axis=d_pos)[3]  #re calc off using off d mask
    cf_sire, cf_dams, cf_yatf, cf_offs = sfun.f_c2g(uinp.parameters['i_cf_c2'], uinp.parameters['i_cf_y'], uinp.parameters['i_cf_pos'], uinp.parameters['i_cf_len'])
    cg_sire, cg_dams, cg_yatf, cg_offs = sfun.f_c2g(uinp.parameters['i_cg_c2'], uinp.parameters['i_cg_y'], uinp.parameters['i_cg_pos'], uinp.parameters['i_cg_len'])
    ch_sire, ch_dams, ch_yatf, ch_offs = sfun.f_c2g(uinp.parameters['i_ch_c2'], uinp.parameters['i_ch_y'], uinp.parameters['i_ch_pos'], uinp.parameters['i_ch_len'])
    ci_sire, ci_dams, ci_yatf, ci_offs = sfun.f_c2g(uinp.parameters['i_ci_c2'], uinp.parameters['i_ci_y'], uinp.parameters['i_ci_pos'], uinp.parameters['i_ci_len'])
    ck_sire, ck_dams, ck_yatf, ck_offs = sfun.f_c2g(uinp.parameters['i_ck_c2'], uinp.parameters['i_ck_y'], uinp.parameters['i_ck_pos'], uinp.parameters['i_ck_len'])
    cl0_sire, cl0_dams, cl0_yatf, cl0_offs = sfun.f_c2g(uinp.parameters['i_cl0_c2'], uinp.parameters['i_cl0_y'], uinp.parameters['i_cl0_pos'], uinp.parameters['i_cl0_len'], uinp.parameters['i_cl0_len2'])
    cl1_sire, cl1_dams, cl1_yatf, cl1_offs = sfun.f_c2g(uinp.parameters['i_cl1_c2'], uinp.parameters['i_cl1_y'], uinp.parameters['i_cl1_pos'], uinp.parameters['i_cl1_len'], uinp.parameters['i_cl1_len2'])
    cl_sire, cl_dams, cl_yatf, cl_offs = sfun.f_c2g(uinp.parameters['i_cl_c2'], uinp.parameters['i_cl_y'], uinp.parameters['i_cl_pos'], uinp.parameters['i_cl_len'])
    cm_sire, cm_dams, cm_yatf, cm_offs = sfun.f_c2g(uinp.parameters['i_cm_c2'], uinp.parameters['i_cm_y'], uinp.parameters['i_cm_pos'], uinp.parameters['i_cm_len'])
    cn_sire, cn_dams, cn_yatf, cn_offs = sfun.f_c2g(uinp.parameters['i_cn_c2'], uinp.parameters['i_cn_y'], uinp.parameters['i_cn_pos'], uinp.parameters['i_cn_len'])
    cp_sire, cp_dams, cp_yatf, cp_offs = sfun.f_c2g(uinp.parameters['i_cp_c2'], uinp.parameters['i_cp_y'], uinp.parameters['i_cp_pos'], uinp.parameters['i_cp_len'])
    cr_sire, cr_dams, cr_yatf, cr_offs = sfun.f_c2g(uinp.parameters['i_cr_c2'], uinp.parameters['i_cr_y'], uinp.parameters['i_cr_pos'], uinp.parameters['i_cr_len'])
    crd_sire, crd_dams, crd_yatf, crd_offs = sfun.f_c2g(uinp.parameters['i_crd_c2'], uinp.parameters['i_crd_y'], uinp.parameters['i_crd_pos'], uinp.parameters['i_crd_len'])
    cu0_sire, cu0_dams, cu0_yatf, cu0_offs = sfun.f_c2g(uinp.parameters['i_cu0_c2'], uinp.parameters['i_cu0_y'], uinp.parameters['i_cu0_pos'], uinp.parameters['i_cu0_len'])
    cu1_sire, cu1_dams, cu1_yatf, cu1_offs = sfun.f_c2g(uinp.parameters['i_cu1_c2'], uinp.parameters['i_cu1_y'], uinp.parameters['i_cu1_pos'], uinp.parameters['i_cu1_len'], uinp.parameters['i_cu1_len2'])
    cu2_sire, cu2_dams, cu2_yatf, cu2_offs = sfun.f_c2g(uinp.parameters['i_cu2_c2'], uinp.parameters['i_cu2_y'], uinp.parameters['i_cu2_pos'], uinp.parameters['i_cu2_len'], uinp.parameters['i_cu2_len2'])
    cw_sire, cw_dams, cw_yatf, cw_offs = sfun.f_c2g(uinp.parameters['i_cw_c2'], uinp.parameters['i_cw_y'], uinp.parameters['i_cw_pos'], uinp.parameters['i_cw_len'])
    cx_sire, cx_dams, cx_yatf, cx_offs = sfun.f_c2g(uinp.parameters['i_cx_c2'], uinp.parameters['i_cx_y'], uinp.parameters['i_cx_pos'], uinp.parameters['i_cx_len'], uinp.parameters['i_cx_len2'])
    ##pasture params
    cu3 = uinp.pastparameters['i_cu3_c4'][...,pinp.sheep['i_pasture_type']].reshape(uinp.pastparameters['i_cu3_len'], uinp.pastparameters['i_cu3_len2']).astype(float)#have to convert from object to float so it doesnt chuck error in np.exp (np.exp cant handle object arrays)
    cu4 = uinp.pastparameters['i_cu4_c4'][...,pinp.sheep['i_pasture_type']].reshape(uinp.pastparameters['i_cu4_len'], uinp.pastparameters['i_cu4_len2']).astype(float)#have to convert from object to float so it doesnt chuck error in np.exp (np.exp cant handle object arrays)
    ##Convert the cl0 & cl1 to cb1 (dams and yatf only need cb1, sires and offs don't have b1 axis)
    cb1_dams = cl0_dams[:,uinp.structure['a_nfoet_b1']] + cl1_dams[:,uinp.structure['a_nyatf_b1']]
    cb1_yatf = cl0_yatf[:,uinp.structure['a_nfoet_b1']] + cl1_yatf[:,uinp.structure['a_nyatf_b1']]
    ###Alter select slices only for yatf (yatf don't have cb0 axis - instead they use cb1 so it aligns with dams)
    ###The b1 parameters that are relevant to the dams relate to either number of foetus (entered as cl0) or number of yatf (entered as cl1). However, because the yatf also use the b1 axis some parameters that change based on the combination of birth type and rear type (BTRT - b0) are needed in the b1 axis for the yatf.
    ###The only role for these parameters is for estimating values for the yatf
    cb1_yatf[12, ...] = np.expand_dims(cb0_yatf[12, uinp.structure['ia_b0_b1']], axis = tuple(range(uinp.parameters['i_cl1_pos']+1,-3))) #add singleton axis between b0 and x so that b0 array aligns with b1
    cb1_yatf[13, ...] = np.expand_dims(cb0_yatf[13, uinp.structure['ia_b0_b1']], axis = tuple(range(uinp.parameters['i_cl1_pos']+1,-3))) #add singleton axis between b0 and x so that b0 array aligns with b1
    cb1_yatf[17, ...] = np.expand_dims(cb0_yatf[17, uinp.structure['ia_b0_b1']], axis = tuple(range(uinp.parameters['i_cl1_pos']+1,-3))) #add singleton axis between b0 and x so that b0 array aligns with b1
    cb1_yatf[18, ...] = np.expand_dims(cb0_yatf[18, uinp.structure['ia_b0_b1']], axis = tuple(range(uinp.parameters['i_cl1_pos']+1,-3))) #add singleton axis between b0 and x so that b0 array aligns with b1

    ########################################
    #adjust input to align with gen periods#
    ########################################
    # 1. Adjust date born (average) = start period
    # 2. Calc date born1st from slice 0 subtract 8 days
    # 3. Calc wean date
    # 4 adjust wean date to occur at start period
    # 5 calc adjusted wean age

    ##calc and adjust date born average of group - convert from date of first lamb born to average date born of all lam
    ###sire
    date_born_ida0e0b0xyg0 = date_born1st_ida0e0b0xyg0 + 0.5 * cf_sire[4, 0:1,:].astype('timedelta64[D]')	 #times by 0.5 to get the average birth date for all lambs because ewes can be conceived anytime within joining cycle
    date_born_idx_ida0e0b0xyg0=sfun.f_next_prev_association(date_start_p, date_born_ida0e0b0xyg0, 0, 'left')
    date_born_ida0e0b0xyg0 = date_start_p[date_born_idx_ida0e0b0xyg0]
    ###dams
    date_born_ida0e0b0xyg1 = date_born1st_ida0e0b0xyg1 + 0.5 * cf_dams[4, 0:1,:].astype('timedelta64[D]')	 #times by 0.5 to get the average birth date for all lambs because ewes can be conceived anytime within joining cycle
    date_born_idx_ida0e0b0xyg1=sfun.f_next_prev_association(date_start_p, date_born_ida0e0b0xyg1, 0, 'left')
    date_born_ida0e0b0xyg1 = date_start_p[date_born_idx_ida0e0b0xyg1]
    ###yatf
    date_born_oa1e1b1nwzida0e0b0xyg2 = date_born1st_oa1e1b1nwzida0e0b0xyg2 + (index_e1b1nwzida0e0b0xyg + 0.5) * cf_yatf[4, 0:1,:].astype('timedelta64[D]')	 #times by 0.5 to get the average birth date for all lambs because ewes can be conceived anytime within joining cycle. e_index is to account for ewe cycles.
    date_born_idx_oa1e1b1nwzida0e0b0xyg2 =sfun.f_next_prev_association(date_start_p, date_born_oa1e1b1nwzida0e0b0xyg2, 0, 'left')
    date_born_oa1e1b1nwzida0e0b0xyg2 = date_start_p[date_born_idx_oa1e1b1nwzida0e0b0xyg2]
    ###offs
    date_born_ida0e0b0xyg3 = date_born1st_ida0e0b0xyg3 + (index_e0b0xyg + 0.5) * cf_offs[4, 0:1,:].astype('timedelta64[D]')	 #times by 0.5 to get the average birth date for all lambs because ewes can be conceived anytime within joining cycle
    date_born_idx_ida0e0b0xyg3=sfun.f_next_prev_association(offs_date_start_p, date_born_ida0e0b0xyg3, 0, 'left')
    date_born_ida0e0b0xyg3 = offs_date_start_p[date_born_idx_ida0e0b0xyg3]
    ##recalc date_born1st
    date_born1st_ida0e0b0xyg0 = date_born_ida0e0b0xyg0 - 0.5 * cf_sire[4, 0:1,:].astype('timedelta64[D]')
    date_born1st_ida0e0b0xyg1 = date_born_ida0e0b0xyg1 - 0.5 * cf_dams[4, 0:1,:].astype('timedelta64[D]')
    date_born1st_oa1e1b1nwzida0e0b0xyg2 = date_born_oa1e1b1nwzida0e0b0xyg2[:,:,0:1,...] - 0.5 * cf_yatf[4, 0:1,:].astype('timedelta64[D]') #take slice 0 of e axis
    date_born1st_ida0e0b0xyg3 = date_born_ida0e0b0xyg3[:,:,:,0:1,...] - 0.5 * cf_offs[4, 0:1,:].astype('timedelta64[D]') #take slice 0 of e axis

    ##calc wean date (weaning input is counting from the date of the first lamb)
    date_weaned_ida0e0b0xyg0 = date_born1st_ida0e0b0xyg0 + age_wean1st_e0b0xyg0
    date_weaned_ida0e0b0xyg1 = date_born1st_ida0e0b0xyg1 + age_wean1st_e0b0xyg1
    date_weaned_oa1e1b1nwzida0e0b0xyg2 = date_born1st_oa1e1b1nwzida0e0b0xyg2 + age_wean1st_a0e0b0xyg3 #use off wean age
    date_weaned_ida0e0b0xyg3 = date_born1st_ida0e0b0xyg3 + age_wean1st_a0e0b0xyg3
    ###adjust weaning to occur at the beginning of generator period and recalc wean age
    ####sire
    date_weaned_idx_ida0e0b0xyg0=sfun.f_next_prev_association(date_start_p, date_weaned_ida0e0b0xyg0, 0, 'left')
    date_weaned_ida0e0b0xyg0 = date_start_p[date_weaned_idx_ida0e0b0xyg0]
    age_wean1st_ida0e0b0xyg0 = date_weaned_ida0e0b0xyg0 - date_born1st_ida0e0b0xyg0
    ####dams
    date_weaned_idx_ida0e0b0xyg1=sfun.f_next_prev_association(date_start_p, date_weaned_ida0e0b0xyg1, 0, 'left')
    date_weaned_ida0e0b0xyg1 = date_start_p[date_weaned_idx_ida0e0b0xyg1]
    age_wean1st_ida0e0b0xyg1 = date_weaned_ida0e0b0xyg1 -date_born1st_ida0e0b0xyg1
    ####yatf - this is the same as offs except without the offs periods (offs potentially have less periods)
    date_weaned_idx_oa1e1b1nwzida0e0b0xyg2=sfun.f_next_prev_association(date_start_p, date_weaned_oa1e1b1nwzida0e0b0xyg2, 0, 'left')
    date_weaned_oa1e1b1nwzida0e0b0xyg2 = date_start_p[date_weaned_idx_oa1e1b1nwzida0e0b0xyg2]
    age_wean1st_oa1e1b1nwzida0e0b0xyg2 = date_weaned_oa1e1b1nwzida0e0b0xyg2 - date_born1st_oa1e1b1nwzida0e0b0xyg2
    ####offs
    date_weaned_idx_ida0e0b0xyg3=sfun.f_next_prev_association(offs_date_start_p, date_weaned_ida0e0b0xyg3, 0, 'left')
    date_weaned_ida0e0b0xyg3 = offs_date_start_p[date_weaned_idx_ida0e0b0xyg3]
    age_wean1st_ida0e0b0xyg3 = date_weaned_ida0e0b0xyg3 - date_born1st_ida0e0b0xyg3

    ##Shearing date - set to be on the last day of a sim period
    ###sire
    idx_sida0e0b0xyg0 = sfun.f_next_prev_association(date_end_p, date_shear_sida0e0b0xyg0,0, 'left')#shearing occurs at the end of the next/current generator period therefore 0 offset
    date_shear_sa1e1b1nwzida0e0b0xyg0 = fun.f_reshape_expand(date_end_p[idx_sida0e0b0xyg0], p_pos, right_pos=i_pos)
    ###dam
    idx_sida0e0b0xyg1 = sfun.f_next_prev_association(date_end_p, date_shear_sida0e0b0xyg1,0, 'left')#shearing occurs at the end of the next/current generator period therefore 0 offset
    date_shear_sa1e1b1nwzida0e0b0xyg1 = fun.f_reshape_expand(date_end_p[idx_sida0e0b0xyg1], p_pos, right_pos=i_pos)
    ###off - shearing cant occur as yatf because then need to shear all lambs (ie no scope to not shear the lambs that are going to be fed up and sold) because the offs decision variables for feeding are not linked to the yatf (which are in the dam decision variables)
    date_shear_sida0e0b0xyg3 = np.maximum(date_born1st_ida0e0b0xyg3 + age_wean1st_ida0e0b0xyg3, date_shear_sida0e0b0xyg3) #shearing must be after weaning.
    idx_sida0e0b0xyg3 = sfun.f_next_prev_association(offs_date_end_p, date_shear_sida0e0b0xyg3,0, 'left')#shearing occurs at the end of the next/current generator period therefore 0 offset
    date_shear_sa1e1b1nwzida0e0b0xyg3 = fun.f_reshape_expand(offs_date_end_p[idx_sida0e0b0xyg3], p_pos, right_pos=i_pos)


    ############################
    ## calc for associations   #
    ############################
    ##date joined (when the rams go in)
    date_joined_oa1e1b1nwzida0e0b0xyg1 = date_born1st_oa1e1b1nwzida0e0b0xyg2 - cp_dams[1,...,0:1,:].astype('timedelta64[D]') #take slice 0 from y axis because cp1 is not affected by genetic merit
    ##expand feed periods over all the years of the sim so that an association between sim period can be made.
    feedperiods_p6 = np.array(pinp.feed_inputs['feed_periods']['date']).astype('datetime64[D]')[:-1] #convert from df to numpy remove last date because that is the end date of the last period (not required)
    feedperiods_p6 = feedperiods_p6 + np.timedelta64(365,'D') * ((date_start_p[0].astype(object).year -1) - feedperiods_p6[0].astype(object).year) #this is to make sure the first sim period date is greater than the first feed period date.
    feedperiods_p6 = np.ravel(feedperiods_p6  + (np.arange(np.ceil(sim_years +1)) * np.timedelta64(365,'D') )[...,na]) #expand then ravel to return 1d array of the feed period dates expanded the length of the sim. +1 because feed periods start and finish mid yr so add one to ensure they go to the end of the sim.


    ## break of season fvp ^the following two lines of code will have to change once season type is included into the feedperiod inputs (the input will have z axis so the reshaping will need to be done in two steps ie pass in pos2 arg) and apply z mask
    #numbers and production redivided at the start of a new season type.
    # breakseason_y = pinp.feed_inputs['feed_periods'].loc[0,'date'].to_datetime64().astype('datetime64[D]') + (np.arange(np.ceil(sim_years)) * np.timedelta64(365,'D'))
    startseason_y = date_start_p[0] + (np.arange(np.ceil(sim_years)) * np.timedelta64(365,'D'))
    seasonstart_ya1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(startseason_y, left_pos=p_pos)
    idx_ya1e1b1nwzida0e0b0xyg = np.searchsorted(date_start_p, seasonstart_ya1e1b1nwzida0e0b0xyg, 'right')-1 #gets the sim period index for the period when season breaks (eg break of season fvp starts at the beginning of the sim period when season breaks), side=right so that if the date is already the start of a period it remains in that period.
    seasonstart_ya1e1b1nwzida0e0b0xyg = date_start_p[idx_ya1e1b1nwzida0e0b0xyg]


    ###################################
    # Feed variation period calcs dams#  ^note if type stuff is used then might need to add a special fvp that is the start of the simulation ie 1/1/19
    ###################################
    ##beginning - first day of generator
    fvp_begin_start_ba1e1b1nwzida0e0b0xyg1 = date_start_pa1e1b1nwzida0e0b0xyg[0:1]
    ##early pregnancy fvp start - The pre-joining accumulation of the dams from the previous reproduction cycle - this date must correspond to the start date of period
    prejoining_approx_oa1e1b1nwzida0e0b0xyg1 = date_joined_oa1e1b1nwzida0e0b0xyg1 - uinp.structure['prejoin_offset'] #approx date of prejoining - adjusted to be the start of a sim period in the next step
    idx = np.searchsorted(date_start_p, prejoining_approx_oa1e1b1nwzida0e0b0xyg1, 'right') - 1 #gets the sim period index for the period that prejoining occurs (eg prejoining fvp starts at the beginning of the sim period when prejoining approx occurs), side=right so that if the date is already the start of a period it remains in that period.
    prejoining_oa1e1b1nwzida0e0b0xyg1 = date_start_p[idx]
    fvp_0_start_oa1e1b1nwzida0e0b0xyg1 = prejoining_oa1e1b1nwzida0e0b0xyg1
    ##late pregnancy fvp start - Scanning if carried out, day 90 from joining (ram in) if not scanned.
    late_preg_oa1e1b1nwzida0e0b0xyg1 = date_joined_oa1e1b1nwzida0e0b0xyg1 + join_cycles_ida0e0b0xyg1 * cf_dams[4, 0:1, :].astype('timedelta64[D]') + pinp.sheep['i_scan_day'][scan_oa1e1b1nwzida0e0b0xyg1].astype('timedelta64[D]')
    idx_oa1e1b1nwzida0e0b0xyg = np.searchsorted(date_start_p, late_preg_oa1e1b1nwzida0e0b0xyg1, 'right')-1 #gets the sim period index for the period when dams in late preg (eg late preg fvp starts at the beginning of the sim period when late preg occurs), side=right so that if the date is already the start of a period it remains in that period.
    fvp_1_start_oa1e1b1nwzida0e0b0xyg1 = date_start_p[idx_oa1e1b1nwzida0e0b0xyg]
    ## lactation fvp start - average date of lambing (with e axis)
    lactation_date_oa1e1b1nwzida0e0b0xyg1 = date_born_oa1e1b1nwzida0e0b0xyg2
    idx_oa1e1b1nwzida0e0b0xyg = np.searchsorted(date_start_p, lactation_date_oa1e1b1nwzida0e0b0xyg1, 'right')-1 #gets the sim period index for the period when lactation starts (eg lactation fvp starts at the beginning of the sim period when lactation occurs), side=right so that if the date is already the start of a period it remains in that period.
    fvp_2_start_oa1e1b1nwzida0e0b0xyg1 = date_start_p[idx_oa1e1b1nwzida0e0b0xyg]

    ##create shape which has max size of each fvp array. Exclude the first dimension because that can be different sizes because only the other dimensions need to be the same for stacking
    shape = np.maximum.reduce([fvp_0_start_oa1e1b1nwzida0e0b0xyg1.shape[1:],fvp_1_start_oa1e1b1nwzida0e0b0xyg1.shape[1:], fvp_2_start_oa1e1b1nwzida0e0b0xyg1.shape[1:], fvp_begin_start_ba1e1b1nwzida0e0b0xyg1.shape[1:]]) #create shape which has the max size, this is used for o array

    ##broadcast the start arrays so that they are all the same size (except axis 0 can be different size)
    fvp_0_start_oa1e1b1nwzida0e0b0xyg1 = np.broadcast_to(fvp_0_start_oa1e1b1nwzida0e0b0xyg1,(fvp_0_start_oa1e1b1nwzida0e0b0xyg1.shape[0],)+tuple(shape))
    fvp_1_start_oa1e1b1nwzida0e0b0xyg1 = np.broadcast_to(fvp_1_start_oa1e1b1nwzida0e0b0xyg1,(fvp_1_start_oa1e1b1nwzida0e0b0xyg1.shape[0],)+tuple(shape))
    fvp_2_start_oa1e1b1nwzida0e0b0xyg1 = np.broadcast_to(fvp_2_start_oa1e1b1nwzida0e0b0xyg1,(fvp_2_start_oa1e1b1nwzida0e0b0xyg1.shape[0],)+tuple(shape))
    fvp_begin_start_ba1e1b1nwzida0e0b0xyg1 = np.broadcast_to(fvp_begin_start_ba1e1b1nwzida0e0b0xyg1,(fvp_begin_start_ba1e1b1nwzida0e0b0xyg1.shape[0],)+tuple(shape))

    ##create fvp type arrays. these are the same shape as the start arrays and are filled with the number corresponding to the fvp number
    fvp_0_type_va1e1b1nwzida0e0b0xyg1 = np.full((fvp_0_start_oa1e1b1nwzida0e0b0xyg1.shape[0],)+tuple(shape),0)
    fvp_1_type_va1e1b1nwzida0e0b0xyg1 = np.full((fvp_1_start_oa1e1b1nwzida0e0b0xyg1.shape[0],)+tuple(shape),1)
    fvp_2_type_va1e1b1nwzida0e0b0xyg1 = np.full((fvp_2_start_oa1e1b1nwzida0e0b0xyg1.shape[0],)+tuple(shape),2)
    fvp_begin_type_va1e1b1nwzida0e0b0xyg1 = np.full((fvp_begin_start_ba1e1b1nwzida0e0b0xyg1.shape[0],)+tuple(shape),2)
    ##stack
    fvp_start_fa1e1b1nwzida0e0b0xyg1 = np.concatenate(([fvp_0_start_oa1e1b1nwzida0e0b0xyg1,fvp_1_start_oa1e1b1nwzida0e0b0xyg1,fvp_2_start_oa1e1b1nwzida0e0b0xyg1,fvp_begin_start_ba1e1b1nwzida0e0b0xyg1]),axis=0)
    fvp_type_fa1e1b1nwzida0e0b0xyg1 = np.concatenate(([fvp_0_type_va1e1b1nwzida0e0b0xyg1,fvp_1_type_va1e1b1nwzida0e0b0xyg1,fvp_2_type_va1e1b1nwzida0e0b0xyg1,fvp_begin_type_va1e1b1nwzida0e0b0xyg1]),axis=0)
    ##sort into date order
    ind=np.argsort(fvp_start_fa1e1b1nwzida0e0b0xyg1, axis=0)
    fvp_date_start_fa1e1b1nwzida0e0b0xyg1 = np.take_along_axis(fvp_start_fa1e1b1nwzida0e0b0xyg1, ind, axis=0)
    fvp_type_fa1e1b1nwzida0e0b0xyg1 = np.take_along_axis(fvp_type_fa1e1b1nwzida0e0b0xyg1, ind, axis=0)
    #proportion of each sim period in each feed period
    # fvp_length_fa1e1b1nwzida0e0b0xyg1 = np.append(fvp_date_start_fa1e1b1nwzida0e0b0xyg1,np.broadcast_to(date_end_pa1e1b1nwzida0e0b0xyg[-1:]+1,(1,)+tuple(fvp_date_start_fa1e1b1nwzida0e0b0xyg1.shape[1:])),axis=0)[1:]-fvp_date_start_fa1e1b1nwzida0e0b0xyg1 #take the last date in the sim and add one day (because end date_p is the date of the last day in the period so add 1 to get the end), broadcast so is it the same shape as fvp. then append it to the end of the fvp dates (basically adding the end date of the last fvp), then subtract the start dates from the end dates to get the length of each period
    # ^might want to swap the f and p axis - decide when this gets used
    # propn_pfa1e1b1nwzida0e0b0xyg1=fun.range_allocation_np(np.append(date_start_pa1e1b1nwzida0e0b0xyg,date_end_pa1e1b1nwzida0e0b0xyg[-1:]+1,axis=0),fvp_date_start_fa1e1b1nwzida0e0b0xyg1,fvp_length_fa1e1b1nwzida0e0b0xyg1) #the function needs the end of the last period so appended that to the start array. +1 so that i get the start of the next period not the last day of the current period

    ####################################
    # Feed variation period calcs offs #
    ####################################
    ##fvp's between weaning and first shearing - there will be 3 fvp's equally spaced between wean and first shearing (unless shearing occurs within 3 periods from weaning - if weaning and shearing are close the extra fvp are masked out in the stacking process below)
    ###0
    fvp_b0_start_ba1e1b1nwzida0e0b0xyg3 = date_start_pa1e1b1nwzida0e0b0xyg3[0:1]
    ###1
    fvp_b1_start_ba1e1b1nwzida0e0b0xyg3 = date_weaned_ida0e0b0xyg3 + (date_shear_sa1e1b1nwzida0e0b0xyg3[0:1] - date_weaned_ida0e0b0xyg3)/3
    idx_oa1e1b1nwzida0e0b0xyg = np.searchsorted(offs_date_start_p, fvp_b1_start_ba1e1b1nwzida0e0b0xyg3, side='right')-1 #makes sure fvp starts on the same date as sim period. (-1 get the start date of current period)
    fvp_b1_start_ba1e1b1nwzida0e0b0xyg3 = offs_date_start_p[idx_oa1e1b1nwzida0e0b0xyg]
    ###2
    fvp_b2_start_ba1e1b1nwzida0e0b0xyg3 = date_weaned_ida0e0b0xyg3 + 2*(date_shear_sa1e1b1nwzida0e0b0xyg3[0:1] - date_weaned_ida0e0b0xyg3)/3
    idx_oa1e1b1nwzida0e0b0xyg = np.searchsorted(offs_date_start_p, fvp_b2_start_ba1e1b1nwzida0e0b0xyg3,side='right')-1 #makes sure fvp starts on the same date as sim period. (-1 get the start date of current period)
    fvp_b2_start_ba1e1b1nwzida0e0b0xyg3 = offs_date_start_p[idx_oa1e1b1nwzida0e0b0xyg]
    ##fvp0 - date shearing plus 1 day because shearing is the last day of period
    fvp_0_start_oa1e1b1nwzida0e0b0xyg3 = date_shear_sa1e1b1nwzida0e0b0xyg3 + np.maximum(1, fvp0_offset_ida0e0b0xyg3) #plus 1 at least 1 because shearing is the last day of the period and the fvp should start after shearing
    idx_oa1e1b1nwzida0e0b0xyg = np.searchsorted(offs_date_start_p, fvp_0_start_oa1e1b1nwzida0e0b0xyg3, 'right')-1 #makes sure fvp starts on the same date as sim period. side=right so that if the date is already the start of a period it remains in that period.
    fvp_0_start_oa1e1b1nwzida0e0b0xyg3 = offs_date_start_p[idx_oa1e1b1nwzida0e0b0xyg]
    ##fvp1 - date shearing (this is the first day of sim period)
    fvp_1_start_oa1e1b1nwzida0e0b0xyg3 = date_shear_sa1e1b1nwzida0e0b0xyg3 + fvp1_offset_ida0e0b0xyg3
    idx_oa1e1b1nwzida0e0b0xyg = np.searchsorted(offs_date_start_p, fvp_1_start_oa1e1b1nwzida0e0b0xyg3, 'right')-1 #makes sure fvp starts on the same date as sim period, side=right so that if the date is already the start of a period it remains in that period.
    fvp_1_start_oa1e1b1nwzida0e0b0xyg3 = offs_date_start_p[idx_oa1e1b1nwzida0e0b0xyg]
    ##fvp2 - date shearing (this is the first day of sim period)
    fvp_2_start_oa1e1b1nwzida0e0b0xyg3 = date_shear_sa1e1b1nwzida0e0b0xyg3 + fvp2_offset_ida0e0b0xyg3
    idx_oa1e1b1nwzida0e0b0xyg = np.searchsorted(offs_date_start_p, fvp_2_start_oa1e1b1nwzida0e0b0xyg3, 'right')-1 #makes sure fvp starts on the same date as sim period, side=right so that if the date is already the start of a period it remains in that period.
    fvp_2_start_oa1e1b1nwzida0e0b0xyg3 = offs_date_start_p[idx_oa1e1b1nwzida0e0b0xyg]

    ##create shape which has max size of each fvp array. Exclude the first dimension because that can be different sizes because only the other dimensions need to be the same for stacking
    shape = np.maximum.reduce([fvp_b0_start_ba1e1b1nwzida0e0b0xyg3.shape[1:], fvp_b1_start_ba1e1b1nwzida0e0b0xyg3.shape[1:], fvp_b2_start_ba1e1b1nwzida0e0b0xyg3.shape[1:]
                               ,fvp_0_start_oa1e1b1nwzida0e0b0xyg3.shape[1:], fvp_1_start_oa1e1b1nwzida0e0b0xyg3.shape[1:], fvp_2_start_oa1e1b1nwzida0e0b0xyg3.shape[1:]]) #create shape which has the max size, this is used for o array
    ##broadcast the start arrays so that they are all the same size (except axis 0 can be different size)
    fvp_b0_start_ba1e1b1nwzida0e0b0xyg3 = np.broadcast_to(fvp_b0_start_ba1e1b1nwzida0e0b0xyg3,(fvp_b0_start_ba1e1b1nwzida0e0b0xyg3.shape[0],)+tuple(shape))
    fvp_b1_start_ba1e1b1nwzida0e0b0xyg3 = np.broadcast_to(fvp_b1_start_ba1e1b1nwzida0e0b0xyg3,(fvp_b1_start_ba1e1b1nwzida0e0b0xyg3.shape[0],)+tuple(shape))
    fvp_b2_start_ba1e1b1nwzida0e0b0xyg3 = np.broadcast_to(fvp_b2_start_ba1e1b1nwzida0e0b0xyg3,(fvp_b2_start_ba1e1b1nwzida0e0b0xyg3.shape[0],)+tuple(shape))
    fvp_0_start_oa1e1b1nwzida0e0b0xyg3 = np.broadcast_to(fvp_0_start_oa1e1b1nwzida0e0b0xyg3,(fvp_0_start_oa1e1b1nwzida0e0b0xyg3.shape[0],)+tuple(shape))
    fvp_1_start_oa1e1b1nwzida0e0b0xyg3 = np.broadcast_to(fvp_1_start_oa1e1b1nwzida0e0b0xyg3,(fvp_1_start_oa1e1b1nwzida0e0b0xyg3.shape[0],)+tuple(shape))
    fvp_2_start_oa1e1b1nwzida0e0b0xyg3 = np.broadcast_to(fvp_2_start_oa1e1b1nwzida0e0b0xyg3,(fvp_2_start_oa1e1b1nwzida0e0b0xyg3.shape[0],)+tuple(shape))

    fvp_b0_type_va1e1b1nwzida0e0b0xyg3 = np.full((fvp_b0_start_ba1e1b1nwzida0e0b0xyg3.shape[0],)+tuple(shape),0)
    fvp_b1_type_va1e1b1nwzida0e0b0xyg3 = np.full((fvp_b1_start_ba1e1b1nwzida0e0b0xyg3.shape[0],)+tuple(shape),1)
    fvp_b2_type_va1e1b1nwzida0e0b0xyg3 = np.full((fvp_b2_start_ba1e1b1nwzida0e0b0xyg3.shape[0],)+tuple(shape),2)
    fvp_0_type_va1e1b1nwzida0e0b0xyg3 = np.full((fvp_0_start_oa1e1b1nwzida0e0b0xyg3.shape[0],)+tuple(shape),0)
    fvp_1_type_va1e1b1nwzida0e0b0xyg3 = np.full((fvp_1_start_oa1e1b1nwzida0e0b0xyg3.shape[0],)+tuple(shape),1)
    fvp_2_type_va1e1b1nwzida0e0b0xyg3 = np.full((fvp_2_start_oa1e1b1nwzida0e0b0xyg3.shape[0],)+tuple(shape),2)

    ##stack - extra fvp only included if shearing occurs more than 3 periods after weaning)
    mask = (date_shear_sa1e1b1nwzida0e0b0xyg3[0:1] - date_weaned_ida0e0b0xyg3) < ((step.astype('timedelta64[D]')+1)*3)  #true if not enough gap between weaning and shearing for extra dvps.
    fvp_start_fa1e1b1nwzida0e0b0xyg3 = np.concatenate(([fvp_b0_start_ba1e1b1nwzida0e0b0xyg3, fvp_b1_start_ba1e1b1nwzida0e0b0xyg3, fvp_b2_start_ba1e1b1nwzida0e0b0xyg3,
                                                        fvp_0_start_oa1e1b1nwzida0e0b0xyg3,fvp_1_start_oa1e1b1nwzida0e0b0xyg3,fvp_2_start_oa1e1b1nwzida0e0b0xyg3]),axis=0)
    fvp_type_fa1e1b1nwzida0e0b0xyg3 = np.concatenate(([fvp_b0_type_va1e1b1nwzida0e0b0xyg3, fvp_b1_type_va1e1b1nwzida0e0b0xyg3, fvp_b2_type_va1e1b1nwzida0e0b0xyg3,
                                                        fvp_0_type_va1e1b1nwzida0e0b0xyg3,fvp_1_type_va1e1b1nwzida0e0b0xyg3,fvp_2_type_va1e1b1nwzida0e0b0xyg3]),axis=0)
    ###if shearing is less than 3 sim periods after weaning then set the break fvp dates to the first date of the sim (so they arent used)
    mask, fvp_start_fa1e1b1nwzida0e0b0xyg3 = np.broadcast_arrays(mask, fvp_start_fa1e1b1nwzida0e0b0xyg3)
    mask = mask.copy()
    mask[3:, ...] = False #only a mask for the 3 extra dvps at the beginning (all the others will not be altered hence set mask to false)
    fvp_start_fa1e1b1nwzida0e0b0xyg3 = fvp_start_fa1e1b1nwzida0e0b0xyg3.copy() #have to create copy because can't assign to broadcasted array or something
    fvp_start_fa1e1b1nwzida0e0b0xyg3[mask] = offs_date_start_p[0]
    fvp_type_fa1e1b1nwzida0e0b0xyg3[mask] = 0
    ##sort into date order
    ind=np.argsort(fvp_start_fa1e1b1nwzida0e0b0xyg3, axis=0)
    fvp_start_fa1e1b1nwzida0e0b0xyg3 = np.take_along_axis(fvp_start_fa1e1b1nwzida0e0b0xyg3, ind, axis=0)
    fvp_type_fa1e1b1nwzida0e0b0xyg3 = np.take_along_axis(fvp_type_fa1e1b1nwzida0e0b0xyg3, ind, axis=0)


    ############################
    ### associations           #
    ############################
    ### Aim is to create an association array that points from period to opportunity
    ## The date_p array will be the start date for each period.
    ## A pointer (association) is required that points from the period to the previous or next lambing opportunity
    ## The Lambing opportunity is defined by the joining_date array (which has an 'o' axis)
    ## The previous lambing opportunity is the latest joining date that is less than the date at the end of the period (ie previous/current opportunity)
    ## # ('end of the period' so that if joining occurs during the period it is the previous
    ## The next lambing opportunity is the earliest joining date that is greater than or equal to the end date at the end of the period
    ##prev is just next - 1




    ##joining opportunity association
    a_nextprejoining_o_pa1e1b1nwzida0e0b0xyg1 = np.apply_along_axis(sfun.f_next_prev_association, 0, prejoining_oa1e1b1nwzida0e0b0xyg1, date_start_p, 0,'left')
    a_prevprejoining_o_pa1e1b1nwzida0e0b0xyg1 = np.apply_along_axis(sfun.f_next_prev_association, 0, prejoining_oa1e1b1nwzida0e0b0xyg1, date_end_p, 1,'right')
    a_prevjoining_o_pa1e1b1nwzida0e0b0xyg1 = np.apply_along_axis(sfun.f_next_prev_association, 0, date_joined_oa1e1b1nwzida0e0b0xyg1, date_end_p, 1,'right')
    a_prevbirth_o_pa1e1b1nwzida0e0b0xyg2 = np.apply_along_axis(sfun.f_next_prev_association, 0, date_born_oa1e1b1nwzida0e0b0xyg2, date_end_p, 1,'right')
    ##dam age association, note this is the same as birth opp (just using a new variable name to avoid confusion in the rest of the code)
    a_prevbirth_d_pa1e1b1nwzida0e0b0xyg2 = a_prevbirth_o_pa1e1b1nwzida0e0b0xyg2
    ##start of season
    a_seasonstart_pa1e1b1nwzida0e0b0xyg = np.apply_along_axis(sfun.f_next_prev_association, 0, seasonstart_ya1e1b1nwzida0e0b0xyg, date_end_p, 1,'right')
    ##MIDAS feed period for each sim period
    a_p6_p = sfun.f_next_prev_association(feedperiods_p6, date_end_p, 1,'right') % (len(pinp.feed_inputs['feed_periods'])-1) #% 10 required to convert association back to only the number of feed periods, -1 because the end feed period date is included

    ##shearing opp (previous/current)
    a_prev_s_pa1e1b1nwzida0e0b0xyg0 = np.apply_along_axis(sfun.f_next_prev_association, 0, date_shear_sa1e1b1nwzida0e0b0xyg0, date_end_p, 1,'right')
    a_prev_s_pa1e1b1nwzida0e0b0xyg1 = np.apply_along_axis(sfun.f_next_prev_association, 0, date_shear_sa1e1b1nwzida0e0b0xyg1, date_end_p, 1,'right')
    a_prev_s_pa1e1b1nwzida0e0b0xyg3 = np.apply_along_axis(sfun.f_next_prev_association, 0, date_shear_sa1e1b1nwzida0e0b0xyg3, offs_date_end_p, 1,'right')
    ##shearing opp (next/current) - points at the next shearing period unless shearing is the current period in which case it points at the current period
    a_next_s_pa1e1b1nwzida0e0b0xyg0 = np.apply_along_axis(sfun.f_next_prev_association, 0, date_shear_sa1e1b1nwzida0e0b0xyg0, date_start_p, 0,'left')
    a_next_s_pa1e1b1nwzida0e0b0xyg1 = np.apply_along_axis(sfun.f_next_prev_association, 0, date_shear_sa1e1b1nwzida0e0b0xyg1, date_start_p, 0,'left')
    a_next_s_pa1e1b1nwzida0e0b0xyg3 = np.apply_along_axis(sfun.f_next_prev_association, 0, date_shear_sa1e1b1nwzida0e0b0xyg3, offs_date_start_p, 0,'left')
    ##p7 to p association - used for equation systems
    a_g0_p7_p = np.apply_along_axis(sfun.f_next_prev_association, 0, pinp.sheep['i_eqn_date_g0_p7'].astype('datetime64[D]'), date_end_p, 1,'right')
    a_g1_p7_p = np.apply_along_axis(sfun.f_next_prev_association, 0, pinp.sheep['i_eqn_date_g1_p7'].astype('datetime64[D]'), date_end_p, 1,'right')
    a_g2_p7_p = np.apply_along_axis(sfun.f_next_prev_association, 0, pinp.sheep['i_eqn_date_g2_p7'].astype('datetime64[D]'), date_end_p, 1,'right')
    a_g3_p7_p = np.apply_along_axis(sfun.f_next_prev_association, 0, pinp.sheep['i_eqn_date_g3_p7'].astype('datetime64[D]'), date_end_p, 1,'right')
    ##month of each period (0 - 11 not 1 -12 because this is association array)
    a_m4_p = date_start_p.astype('datetime64[M]').astype(int) % 12
    ##feed variation period
    a_fvp_pa1e1b1nwzida0e0b0xyg1 = np.apply_along_axis(sfun.f_next_prev_association, 0, fvp_date_start_fa1e1b1nwzida0e0b0xyg1, date_end_p, 1,'right')
    a_fvp_pa1e1b1nwzida0e0b0xyg3 = np.apply_along_axis(sfun.f_next_prev_association, 0, fvp_start_fa1e1b1nwzida0e0b0xyg3, offs_date_end_p, 1,'right')


    ############################
    ### apply associations     #
    ############################
    '''
    The association applied determines when the increment to the next opportunity will occur:
        eg if you use a_prev_joining the date in the p slice will increment at joining each time.
    
    '''
    ###shearing
    date_shear_pa1e1b1nwzida0e0b0xyg0=np.take_along_axis(date_shear_sa1e1b1nwzida0e0b0xyg0,a_prev_s_pa1e1b1nwzida0e0b0xyg0,0) #np.takealong uses the number in the second array as the index for the first array. and returns a same shaped array
    date_shear_pa1e1b1nwzida0e0b0xyg1=np.take_along_axis(date_shear_sa1e1b1nwzida0e0b0xyg1,a_prev_s_pa1e1b1nwzida0e0b0xyg1,0) #np.takealong uses the number in the second array as the index for the first array. and returns a same shaped array
    date_shear_pa1e1b1nwzida0e0b0xyg3=np.take_along_axis(date_shear_sa1e1b1nwzida0e0b0xyg3,a_prev_s_pa1e1b1nwzida0e0b0xyg3,0) #np.takealong uses the number in the second array as the index for the first array. and returns a same shaped array
    date_nextshear_pa1e1b1nwzida0e0b0xyg0=np.take_along_axis(date_shear_sa1e1b1nwzida0e0b0xyg0,a_next_s_pa1e1b1nwzida0e0b0xyg0,0) #np.takealong uses the number in the second array as the index for the first array. and returns a same shaped array
    date_nextshear_pa1e1b1nwzida0e0b0xyg1=np.take_along_axis(date_shear_sa1e1b1nwzida0e0b0xyg1,a_next_s_pa1e1b1nwzida0e0b0xyg1,0) #np.takealong uses the number in the second array as the index for the first array. and returns a same shaped array
    date_nextshear_pa1e1b1nwzida0e0b0xyg3=np.take_along_axis(date_shear_sa1e1b1nwzida0e0b0xyg3,a_next_s_pa1e1b1nwzida0e0b0xyg3,0) #np.takealong uses the number in the second array as the index for the first array. and returns a same shaped array
    ###management for weaning, gbal and scan options
    wean_pa1e1b1nwzida0e0b0xyg1=np.take_along_axis(wean_oa1e1b1nwzida0e0b0xyg1,a_prevbirth_o_pa1e1b1nwzida0e0b0xyg2,0) #np.takealong uses the number in the second array as the index for the first array. and returns a same shaped array
    gbal_pa1e1b1nwzida0e0b0xyg1=np.take_along_axis(gbal_oa1e1b1nwzida0e0b0xyg1,a_prevbirth_o_pa1e1b1nwzida0e0b0xyg2,0) #np.takealong uses the number in the second array as the index for the first array. and returns a same shaped array
    scan_pa1e1b1nwzida0e0b0xyg1=np.take_along_axis(scan_oa1e1b1nwzida0e0b0xyg1,a_prevprejoining_o_pa1e1b1nwzida0e0b0xyg1,0) #np.takealong uses the number in the second array as the index for the first array. and returns a same shaped array
    ###date, age, timing
    date_born1st_pa1e1b1nwzida0e0b0xyg2=np.take_along_axis(date_born1st_oa1e1b1nwzida0e0b0xyg2,a_prevbirth_o_pa1e1b1nwzida0e0b0xyg2,0)
    date_born_pa1e1b1nwzida0e0b0xyg2=np.take_along_axis(date_born_oa1e1b1nwzida0e0b0xyg2,a_prevbirth_o_pa1e1b1nwzida0e0b0xyg2,0)
    # ####convert from date of first lamb born to average date born of all lambs and adjust date born1st (so that birth happens on start of p)
    # date_born_pa1e1b1nwzida0e0b0xyg2 = date_born1st_pa1e1b1nwzida0e0b0xyg2 + (index_e1b1nwzida0e0b0xyg + 0.5) * cf_yatf[4, 0:1,:].astype('timedelta64[D]')	 #times by 0.5 to get the average birth date for all lambs because ewes can be conceived anytime within joining cycle. e_index is to account for ewe cycles.
    # date_born_idx_pa1e1b1nwzida0e0b0xyg2 =sfun.f_next_prev_association(date_start_p, date_born_pa1e1b1nwzida0e0b0xyg2, 0)
    # date_born_pa1e1b1nwzida0e0b0xyg2 = date_start_p[date_born_idx_pa1e1b1nwzida0e0b0xyg2]
    # date_born1st_pa1e1b1nwzida0e0b0xyg2 = date_born_pa1e1b1nwzida0e0b0xyg2[:,:,0:1,...] - 0.5 * cf_yatf[4, 0:1,:].astype('timedelta64[D]') #take slice 0 of e axis

    date_born1st2_pa1e1b1nwzida0e0b0xyg2=np.take_along_axis(date_born1st_oa1e1b1nwzida0e0b0xyg2,a_prevprejoining_o_pa1e1b1nwzida0e0b0xyg1,0) #increments at prejoining
    date_prejoin_next_pa1e1b1nwzida0e0b0xyg1=np.take_along_axis(prejoining_oa1e1b1nwzida0e0b0xyg1,a_nextprejoining_o_pa1e1b1nwzida0e0b0xyg1,0)
    date_prejoin_pa1e1b1nwzida0e0b0xyg1=np.take_along_axis(prejoining_oa1e1b1nwzida0e0b0xyg1,a_prevprejoining_o_pa1e1b1nwzida0e0b0xyg1,0)
    date_joined_pa1e1b1nwzida0e0b0xyg1=np.take_along_axis(date_joined_oa1e1b1nwzida0e0b0xyg1,a_prevjoining_o_pa1e1b1nwzida0e0b0xyg1,0)
    date_joined2_pa1e1b1nwzida0e0b0xyg1=np.take_along_axis(date_joined_oa1e1b1nwzida0e0b0xyg1,a_prevprejoining_o_pa1e1b1nwzida0e0b0xyg1,0) #increments at prejoining
    ####create age wean yatf
    age_wean1st_oa1e1b1nwzida0e0b0xyg2 = np.swapaxes(age_wean1st_oa1e1b1nwzida0e0b0xyg2, a0_pos, a1_pos) #swap a0 and a1 because yatf have to be same shape as dams
    age_wean1st_oa1e1b1nwzida0e0b0xyg2 = np.swapaxes(age_wean1st_oa1e1b1nwzida0e0b0xyg2, e0_pos, e1_pos) #swap e0 and e1 because yatf have to be same shape as dams
    age_wean1st_pa1e1b1nwzida0e0b0xyg2=np.take_along_axis(age_wean1st_oa1e1b1nwzida0e0b0xyg2,a_prevbirth_o_pa1e1b1nwzida0e0b0xyg2,0)#use off wean age - may vary by d axis therefore have to convert to a p array
    age_wean1st2_pa1e1b1nwzida0e0b0xyg2=np.take_along_axis(age_wean1st_oa1e1b1nwzida0e0b0xyg2,a_prevprejoining_o_pa1e1b1nwzida0e0b0xyg1,0) #increments at prejoining
    ##yatf sim params - turn d to p axis
    ce_yatf = np.expand_dims(ce_yatf, axis = tuple(range(p_pos,d_pos)))
    ce_yatf = np.take_along_axis(ce_yatf,a_prevbirth_d_pa1e1b1nwzida0e0b0xyg2[na,...],d_pos)
    ##feed period
    legume_pa1e1b1nwzida0e0b0xyg = legume_p6a1e1b1nwzida0e0b0xyg[a_p6_p,...]
    ##expected stocking density
    density_pa1e1b1nwzida0e0b0xyg = density_p6a1e1b1nwzida0e0b0xyg[a_p6_p,...]
    ##select which equation is used for the sheep sim functions for each period
    eqn_used_g0_q1p = uinp.sheep['i_eqn_used_g0_q1p7'][:, a_g0_p7_p]
    eqn_used_g1_q1p = uinp.sheep['i_eqn_used_g1_q1p7'][:, a_g1_p7_p]
    eqn_used_g2_q1p = uinp.sheep['i_eqn_used_g2_q1p7'][:, a_g2_p7_p]
    eqn_used_g3_q1p = uinp.sheep['i_eqn_used_g3_q1p7'][:, a_g3_p7_p]
    ##convert foo and dmd for each feed period to each sim period
    paststd_foo_pa1e1b1j0wzida0e0b0xyg = paststd_foo_p6a1e1b1j0wzida0e0b0xyg[a_p6_p,...]
    paststd_dmd_pa1e1b1j0wzida0e0b0xyg = paststd_dmd_p6a1e1b1j0wzida0e0b0xyg[a_p6_p,...]
    pasture_stage_pa1e1b1j0wzida0e0b0xyg = pasture_stage_p6a1e1b1j0wzida0e0b0xyg[a_p6_p,...]
    ##mating
    sire_propn_pa1e1b1nwzida0e0b0xyg1=np.take_along_axis(sire_propn_oa1e1b1nwzida0e0b0xyg1,a_prevjoining_o_pa1e1b1nwzida0e0b0xyg1,0) #np.take_along uses the number in the second array as the index for the first array. and returns a same shaped array
    sire_include_idx = np.arange(len(mask_sire_inc_g0))[mask_sire_inc_g0]
    sire_propn_pa1e1b1nwzida0e0b0xyg1g0=sire_propn_pa1e1b1nwzida0e0b0xyg1[..., na] * (a_g0_g1[:,na] == sire_include_idx)
 #add g0 axis
    ##weather
    ws_pa1e1b1nwzida0e0b0xyg = ws_m4a1e1b1nwzida0e0b0xyg[a_m4_p]
    rain_pa1e1b1nwzida0e0b0xygm1 = rain_m4a1e1b1nwzida0e0b0xygm1[a_m4_p]
    temp_ave_pa1e1b1nwzida0e0b0xyg= temp_ave_m4a1e1b1nwzida0e0b0xyg[a_m4_p]
    temp_max_pa1e1b1nwzida0e0b0xyg= temp_max_m4a1e1b1nwzida0e0b0xyg[a_m4_p]
    temp_min_pa1e1b1nwzida0e0b0xyg= temp_min_m4a1e1b1nwzida0e0b0xyg[a_m4_p]
    ##feed variation
    fvp_type_pa1e1b1nwzida0e0b0xyg1 = np.take_along_axis(fvp_type_fa1e1b1nwzida0e0b0xyg1,a_fvp_pa1e1b1nwzida0e0b0xyg1,0)
    fvp_type_pa1e1b1nwzida0e0b0xyg3 = np.take_along_axis(fvp_type_fa1e1b1nwzida0e0b0xyg3,a_fvp_pa1e1b1nwzida0e0b0xyg3,0)
    fvp_date_start_pa1e1b1nwzida0e0b0xyg1 = np.take_along_axis(fvp_date_start_fa1e1b1nwzida0e0b0xyg1,a_fvp_pa1e1b1nwzida0e0b0xyg1,0)
    fvp_date_start_pa1e1b1nwzida0e0b0xyg3 = np.take_along_axis(fvp_start_fa1e1b1nwzida0e0b0xyg3,a_fvp_pa1e1b1nwzida0e0b0xyg3,0)
    ##break of season
    date_prev_seasonstart_pa1e1b1nwzida0e0b0xyg=np.take_along_axis(seasonstart_ya1e1b1nwzida0e0b0xyg,a_seasonstart_pa1e1b1nwzida0e0b0xyg,0)

    ##create association between n and w - code has to be after fvp_type has had association applied
    ###sire ^not required yet because only 1 fvp and n slice for sire
    # n_fs_g0 = uinp.structure['i_n0_len']
    # n_fvp_periods_g0=uinp.structure['i_n_fvp_period0']
    # a_n_pa1e1b1nwzida0e0b0xyg0 = (np.trunc(index_wzida0e0b0xyg0 / (n_fs_g0 ** ((n_fvp_periods_g0-1) - fvp_type_pa1e1b1nwzida0e0b0xyg0))) % n_fs_g0).astype(int) #needs to be int so it can be an indice
    ###dams
    n_fs_g1 = uinp.structure['i_n1_len']
    n_fvp_periods_g1=uinp.structure['i_n_fvp_period1']
    a_n_pa1e1b1nwzida0e0b0xyg1 = (np.trunc(index_wzida0e0b0xyg1 / (n_fs_g1 ** ((n_fvp_periods_g1-1) - fvp_type_pa1e1b1nwzida0e0b0xyg1*(a_fvp_pa1e1b1nwzida0e0b0xyg1>0)))) % n_fs_g1).astype(int) #mul fvp be bool to convert the first fvp type from 2 to 0 (we want the type to be 0 so the feed supply is clustered) #needs to be int so it can be an indice
    ###offs
    n_fs_g3 = uinp.structure['i_n3_len']
    n_fvp_periods_g3=uinp.structure['i_n_fvp_period3']
    a_n_pa1e1b1nwzida0e0b0xyg3 = (np.trunc(index_wzida0e0b0xyg3 / (n_fs_g3 ** ((n_fvp_periods_g3-1) - fvp_type_pa1e1b1nwzida0e0b0xyg3))) % n_fs_g3).astype(int) #needs to be int so it can be an indice


    ###########################
    ##genotype calculations   #
    ###########################
    ##calc proportion of dry, singles, twin and triplets
    dstwtr_l0yg0 = np.moveaxis(sfun.f_DSTw(scan_std_yg0), -1, 0)
    dstwtr_l0yg1 = np.moveaxis(sfun.f_DSTw(scan_std_yg1), -1, 0)
    dstwtr_l0yg3 = np.moveaxis(sfun.f_DSTw(scan_dams_std_yg3), -1, 0)

    ##Std scanning & survival: propn of progeny in each BTRT b0 category - 11, 22, 33, 21, 32, 31 and lambs surviving birth per ewe joined (standard weaning percentage)
    btrt_propn_b0xyg0, npw_std_xyg0 = sfun.f_btrt0(dstwtr_l0yg0,pss_std_yg0,pstw_std_yg0,pstr_std_yg0)
    btrt_propn_b0xyg1, npw_std_xyg1 = sfun.f_btrt0(dstwtr_l0yg1,pss_std_yg1,pstw_std_yg1,pstr_std_yg1)
    btrt_propn_b0xyg3, npw_std_xyg3 = sfun.f_btrt0(dstwtr_l0yg3,pss_std_yg3,pstw_std_yg3,pstr_std_yg3)

    # ##Std scanning & survival: proportion of dams in each BTRT b1 category - NM, 00, 11, 22, 33, 21, 32, 31, 10, 20, 30
    # btrt_b1nwzida0e0b0xy0 = f_btrt1(dstwtr_l0yg0,pss_std_yg0,pstw_std_yg0,pstr_std_yg0)
    # btrt_b1nwzida0e0b0xy1 = f_btrt1(dstwtr_l0yg1,pss_std_yg1,pstw_std_yg1,pstr_std_yg1)
    # btrt_b1nwzida0e0b0xy2 = f_btrt1(dstwtr_l0yg2,pss_std_yg2,pstw_std_yg2,pstr_std_yg2)
    # btrt_b1nwzida0e0b0xy3 = f_btrt1(dstwtr_l0yg3,pss_std_yg3,pstw_std_yg3,pstr_std_yg3)

    ###calc adjustments sfw
    adja_sfw_d_a0e0b0xyg0 = np.sum(ce_sire[12, ...] * agedam_propn_da0e0b0xyg0, axis = 0)
    adja_sfw_d_a0e0b0xyg1 = np.sum(ce_dams[12, ...] * agedam_propn_da0e0b0xyg1, axis = 0)
    adja_sfw_d_pa1e1b1nwzida0e0b0xyg2 = ce_yatf[12,...]
    adja_sfw_d_da0e0b0xyg3 = ce_offs[12, ...]
    adja_sfw_b0_xyg0 = np.sum(cb0_sire[12, ...] * btrt_propn_b0xyg0, axis = 0)
    adja_sfw_b0_xyg1 = np.sum(cb0_dams[12, ...] * btrt_propn_b0xyg1, axis = 0)
    adja_sfw_b0_b1nwzida0e0b0xyg2 = cb1_yatf[12, ...]
    adja_sfw_b0_b0xyg3 = cb0_offs[12, ...]
    ###apply adjustments sfw
    sfw_a0e0b0xyg0 = sfw_yg0 + adja_sfw_d_a0e0b0xyg0 + adja_sfw_b0_xyg0
    sfw_a0e0b0xyg1 = sfw_yg1 + adja_sfw_d_a0e0b0xyg1 + adja_sfw_b0_xyg1
    sfw_pa1e1b1nwzida0e0b0xyg2 = sfw_yg2 + adja_sfw_d_pa1e1b1nwzida0e0b0xyg2 + adja_sfw_b0_b1nwzida0e0b0xyg2
    sfw_da0e0b0xyg3 = sfw_yg3 + adja_sfw_d_da0e0b0xyg3 + adja_sfw_b0_b0xyg3
    ###calc adjustments sfd
    adja_sfd_d_a0e0b0xyg0 = np.sum(ce_sire[13, ...] * agedam_propn_da0e0b0xyg0, axis = 0)
    adja_sfd_d_a0e0b0xyg1 = np.sum(ce_dams[13, ...] * agedam_propn_da0e0b0xyg1, axis = 0)
    adja_sfd_d_pa1e1b1nwzida0e0b0xyg2 = ce_yatf[13, ...]
    adja_sfd_d_da0e0b0xyg3 = ce_offs[13, ...]
    adja_sfd_b0_xyg0 = np.sum(cb0_sire[13, ...] * btrt_propn_b0xyg0, axis = 0)
    adja_sfd_b0_xyg1 = np.sum(cb0_dams[13, ...] * btrt_propn_b0xyg1, axis = 0)
    adja_sfd_b0_b0xyg2 = cb1_yatf[13, ...]
    adja_sfd_b0_b0xyg3 = cb0_offs[13, ...]
    ###apply adjustments sfd
    sfd_a0e0b0xyg0 = sfd_yg0 + adja_sfd_d_a0e0b0xyg0 + adja_sfd_b0_xyg0
    sfd_a0e0b0xyg1 = sfd_yg1 + adja_sfd_d_a0e0b0xyg1 + adja_sfd_b0_xyg1
    sfd_pa1e1b1nwzida0e0b0xyg2 = sfd_yg2 + adja_sfd_d_pa1e1b1nwzida0e0b0xyg2 + adja_sfd_b0_b0xyg2
    sfd_da0e0b0xyg3 = sfd_yg3 + adja_sfd_d_da0e0b0xyg3 + adja_sfd_b0_b0xyg3

    ###gender adjustment for srw
    srw_xyg0 = srw_female_yg0 * cx_sire[11, 0:1, ...]  #11 is the srw parameter, 0:1 is the sire gender slice (retaining the axis).
    srw_xyg1 = srw_female_yg1 * cx_dams[11, 1:2, ...]
    srw_xyg2 = srw_female_yg2 * cx_yatf[11, mask_x,...] #all gender slices
    srw_xyg3 = srw_female_yg3 * cx_offs[11, mask_x,...] #all gender slices

    ##Standard birth weight -
    w_b_std_b0xyg0 = srw_female_yg0 * np.sum(cb0_sire[15, ...] * btrt_propn_b0xyg0, axis = b0_pos, keepdims=True) * cx_sire[15, 0:1, ...]
    w_b_std_b0xyg1 = srw_female_yg1 * np.sum(cb0_dams[15, ...] * btrt_propn_b0xyg1, axis = b0_pos, keepdims=True) * cx_dams[15, 1:2, ...]
    w_b_std_b0xyg3 = srw_female_yg3 * cb0_offs[15, ...] * cx_offs[15, mask_x,...]
    ##fetal param - normal birthweight young - used as target birthweight during pregnancy if sheep fed well. Therefore average gender effect.
    w_b_std_y_b1nwzida0e0b0xyg1 = srw_female_yg2 * cb1_yatf[15, ...] #gender not considers until actual birth therefore no cx
    ##wool growth efficiency (sfw same for all animals)
    wge_a0e0b0xyg0 = sfw_a0e0b0xyg0 / (srw_xyg0 / cx_sire[11, 0:1, ...]) #wge is sfw divided by srw of a ewe of given genotype therefore convert srw_sire back to dam by dividing by cx
    wge_a0e0b0xyg1 = sfw_a0e0b0xyg1 / srw_xyg1
    wge_pa1e1b1nwzida0e0b0xyg2 = sfw_pa1e1b1nwzida0e0b0xyg2 / srw_xyg2[1:2, ...] #take female slice of srw
    wge_da0e0b0xyg3 = sfw_da0e0b0xyg3 / srw_xyg3[1:2, ...] #take female slice of srw

    ##Legume impact on efficiency
    lgf_eff_pa1e1b1nwzida0e0b0xyg0 = 1 + ck_sire[14,...] * legume_pa1e1b1nwzida0e0b0xyg
    lgf_eff_pa1e1b1nwzida0e0b0xyg1 = 1 + ck_dams[14,...] * legume_pa1e1b1nwzida0e0b0xyg
    lgf_eff_pa1e1b1nwzida0e0b0xyg2 = 1 + ck_yatf[14,...] * legume_pa1e1b1nwzida0e0b0xyg
    lgf_eff_pa1e1b1nwzida0e0b0xyg3 = 1 + ck_offs[14,...] * legume_pa1e1b1nwzida0e0b0xyg

    ##Day length factor on wool
    dlf_wool_pa1e1b1nwzida0e0b0xyg0 = 1 + cw_sire[6,...] * (dl_pa1e1b1nwzida0e0b0xyg - 12)
    dlf_wool_pa1e1b1nwzida0e0b0xyg1 = 1 + cw_dams[6,...] * (dl_pa1e1b1nwzida0e0b0xyg - 12)
    dlf_wool_pa1e1b1nwzida0e0b0xyg2 = 1 + cw_yatf[6,...] * (dl_pa1e1b1nwzida0e0b0xyg - 12)
    dlf_wool_pa1e1b1nwzida0e0b0xyg3 = 1 + cw_offs[6,...] * (dl_pa1e1b1nwzida0e0b0xyg[mask_p_offs_p] - 12)

    ##Efficiency for wool
    kw_yg0 = ck_sire[17,...]
    kw_yg1 = ck_dams[17,...]
    kw_yg2 = ck_yatf[17,...]
    kw_yg3 = ck_offs[17,...]

    ##Efficiency for conceptus
    kc_yg1 = ck_dams[8,...]


    ####################
    #initial conditions#
    ####################
    ##convert i_adjp to adjp - add necessary axes for 'a' and 'w'
    adjp_lw_initial_a0e0b0xyg = fun.f_reshape_expand(pinp.sheep['i_adjp_lw_initial_a'], a0_pos, condition=pinp.sheep['i_mask_a'], axis=a0_pos)
    adjp_lw_initial_wzida0e0b0xyg0 = fun.f_reshape_expand(uinp.structure['i_adjp_lw_initial_w0'], w_pos)
    adjp_lw_initial_wzida0e0b0xyg1 = fun.f_reshape_expand(uinp.structure['i_adjp_lw_initial_w1'], w_pos)
    adjp_lw_initial_wzida0e0b0xyg3 = fun.f_reshape_expand(uinp.structure['i_adjp_lw_initial_w3'], w_pos)
    adjp_cfw_initial_a0e0b0xyg = fun.f_reshape_expand(pinp.sheep['i_adjp_cfw_initial_a'], a0_pos, condition=pinp.sheep['i_mask_a'], axis=a0_pos)
    adjp_cfw_initial_wzida0e0b0xyg0 = fun.f_reshape_expand(uinp.structure['i_adjp_cfw_initial_w0'], w_pos)
    adjp_cfw_initial_wzida0e0b0xyg1 = fun.f_reshape_expand(uinp.structure['i_adjp_cfw_initial_w1'], w_pos)
    adjp_cfw_initial_wzida0e0b0xyg3 = fun.f_reshape_expand(uinp.structure['i_adjp_cfw_initial_w3'], w_pos)
    adjp_fd_initial_a0e0b0xyg = fun.f_reshape_expand(pinp.sheep['i_adjp_fd_initial_a'], a0_pos, condition=pinp.sheep['i_mask_a'], axis=a0_pos)
    adjp_fd_initial_wzida0e0b0xyg0 = fun.f_reshape_expand(uinp.structure['i_adjp_fd_initial_w0'], w_pos)
    adjp_fd_initial_wzida0e0b0xyg1 = fun.f_reshape_expand(uinp.structure['i_adjp_fd_initial_w1'], w_pos)
    adjp_fd_initial_wzida0e0b0xyg3 = fun.f_reshape_expand(uinp.structure['i_adjp_fd_initial_w3'], w_pos)
    adjp_fl_initial_a0e0b0xyg = fun.f_reshape_expand(pinp.sheep['i_adjp_fl_initial_a'], a0_pos, condition=pinp.sheep['i_mask_a'], axis=a0_pos)
    adjp_fl_initial_wzida0e0b0xyg0 = fun.f_reshape_expand(uinp.structure['i_adjp_fl_initial_w0'], w_pos)
    adjp_fl_initial_wzida0e0b0xyg1 = fun.f_reshape_expand(uinp.structure['i_adjp_fl_initial_w1'], w_pos)
    adjp_fl_initial_wzida0e0b0xyg3 = fun.f_reshape_expand(uinp.structure['i_adjp_fl_initial_w3'], w_pos)


    ##convert variable from c2 to g (yatf is not used, only here because it is return from the function) then adjust by initial lw pattern
    lw_initial_yg0, lw_initial_yg1, lw_initial_yatf, lw_initial_yg3 = sfun.f_c2g(uinp.parameters['i_lw_initial_c2'], uinp.parameters['i_lw_initial_y'])
    lw_initial_wzida0e0b0xyg0 = lw_initial_yg0 * (1 + adjp_lw_initial_wzida0e0b0xyg0)
    lw_initial_wzida0e0b0xyg1 = lw_initial_yg1 * (1 + adjp_lw_initial_wzida0e0b0xyg1)
    lw_initial_wzida0e0b0xyg3 = lw_initial_yg3 * (1 + adjp_lw_initial_wzida0e0b0xyg3)
    cfw_initial_yg0, cfw_initial_yg1, cfw_initial_yatf, cfw_initial_yg3 = sfun.f_c2g(uinp.parameters['i_cfw_initial_c2'], uinp.parameters['i_cfw_initial_y'])
    cfw_initial_wzida0e0b0xyg0 = cfw_initial_yg0 * (1 + adjp_cfw_initial_wzida0e0b0xyg0)
    cfw_initial_wzida0e0b0xyg1 = cfw_initial_yg1 * (1 + adjp_cfw_initial_wzida0e0b0xyg1)
    cfw_initial_wzida0e0b0xyg3 = cfw_initial_yg3 * (1 + adjp_cfw_initial_wzida0e0b0xyg3)
    fd_initial_yg0, fd_initial_yg1, fd_initial_yatf, fd_initial_yg3 = sfun.f_c2g(uinp.parameters['i_fd_initial_c2'], uinp.parameters['i_fd_initial_y'])
    fd_initial_wzida0e0b0xyg0 = fd_initial_yg0 * (1 + adjp_fd_initial_wzida0e0b0xyg0)
    fd_initial_wzida0e0b0xyg1 = fd_initial_yg1 * (1 + adjp_fd_initial_wzida0e0b0xyg1)
    fd_initial_wzida0e0b0xyg3 = fd_initial_yg3 * (1 + adjp_fd_initial_wzida0e0b0xyg3)
    fl_initial_yg0, fl_initial_yg1, fl_initial_yatf, fl_initial_yg3 = sfun.f_c2g(uinp.parameters['i_fl_initial_c2'], uinp.parameters['i_fl_initial_y'])
    fl_initial_wzida0e0b0xyg0 = fl_initial_yg0 * (1 + adjp_fl_initial_wzida0e0b0xyg0)
    fl_initial_wzida0e0b0xyg1 = fl_initial_yg1 * (1 + adjp_fl_initial_wzida0e0b0xyg1)
    fl_initial_wzida0e0b0xyg3 = fl_initial_yg3 * (1 + adjp_fl_initial_wzida0e0b0xyg3)

    ##adjustment for weaning age
    adjp_lw_initial_a_a0e0b0xyg0 = adjp_lw_initial_a0e0b0xyg[0:1,...]
    adjp_lw_initial_a_a0e0b0xyg1 = adjp_lw_initial_a0e0b0xyg[0:1,...]
    adjp_lw_initial_a_a0e0b0xyg3 = adjp_lw_initial_a0e0b0xyg
    adjp_cfw_initial_a_a0e0b0xyg0 = adjp_cfw_initial_a0e0b0xyg[0:1,...]
    adjp_cfw_initial_a_a0e0b0xyg1 = adjp_cfw_initial_a0e0b0xyg[0:1,...]
    adjp_cfw_initial_a_a0e0b0xyg3 = adjp_cfw_initial_a0e0b0xyg
    adjp_fd_initial_a_a0e0b0xyg0 = adjp_fd_initial_a0e0b0xyg[0:1,...]
    adjp_fd_initial_a_a0e0b0xyg1 = adjp_fd_initial_a0e0b0xyg[0:1,...]
    adjp_fd_initial_a_a0e0b0xyg3 = adjp_fd_initial_a0e0b0xyg
    adjp_fl_initial_a_a0e0b0xyg0 = adjp_fl_initial_a0e0b0xyg[0:1,...]
    adjp_fl_initial_a_a0e0b0xyg1 = adjp_fl_initial_a0e0b0xyg[0:1,...]
    adjp_fl_initial_a_a0e0b0xyg3 = adjp_fl_initial_a0e0b0xyg
    ##adjustment for gender. Note cfw changes throughout the year therefore the adjustment factor will not be the same all yr hence divide by std_fw (same for fl) eg the impact of gender on cfw will be much less after only a small time (the parameter is a yearly factor eg male sheep have 0.02 kg more wool each yr)
    adja_lw_initial_x_xyg0 = cx_sire[17, 0:1, ...] #17 is the weaning wt parameter, 0:1 is the sire gender slice (retaining the axis).
    adja_lw_initial_x_xyg1 = cx_dams[17, 1:2, ...]
    adja_lw_initial_x_xyg3 = cx_offs[17, mask_x, ...]
    adja_cfw_initial_x_wzida0e0b0xyg0 = cx_sire[12, 0:1, ...] * cfw_initial_wzida0e0b0xyg0 / sfw_a0e0b0xyg0
    adja_cfw_initial_x_wzida0e0b0xyg1 = cx_dams[12, 1:2, ...] * cfw_initial_wzida0e0b0xyg1 / sfw_a0e0b0xyg1
    adja_cfw_initial_x_wzida0e0b0xyg3 = cx_offs[12, mask_x, ...] * cfw_initial_wzida0e0b0xyg3 / sfw_da0e0b0xyg3
    adja_fd_initial_x_xyg0 = cx_sire[13, 0:1, ...]
    adja_fd_initial_x_xyg1 = cx_dams[13, 1:2, ...]
    adja_fd_initial_x_xyg3 = cx_offs[13, mask_x, ...]
    adja_fl_initial_x_wzida0e0b0xyg0 = cx_sire[12, 0:1, ...] * fl_initial_wzida0e0b0xyg0 / sfw_a0e0b0xyg0 #Should be fl_initial / sfw  So more understandable to think of the eqn as being fl_initial * cx[0] (cfw adj due to gender) / sfw
    adja_fl_initial_x_wzida0e0b0xyg1 = cx_dams[12, 1:2, ...] * fl_initial_wzida0e0b0xyg1 / sfw_a0e0b0xyg1
    adja_fl_initial_x_wzida0e0b0xyg3 = cx_offs[12, mask_x, ...] * fl_initial_wzida0e0b0xyg3 / sfw_da0e0b0xyg3
    ##adjust for dam age. Note cfw changes throughout the year therefore the adjustment factor will not be the same all yr hence divide by std_fw (same for fl) eg the impact of gender on cfw will be much less after only a small time (the parameter is a yearly factor eg male sheep have 0.02 kg more wool each yr)
    adja_lw_initial_d_a0e0b0xyg0 = np.sum(ce_sire[17, ...] * agedam_propn_da0e0b0xyg0, axis=0) #d axis lost when summing
    adja_lw_initial_d_a0e0b0xyg1 = np.sum(ce_dams[17, ...] * agedam_propn_da0e0b0xyg1, axis=0)
    adja_lw_initial_d_da0e0b0xyg3 = ce_offs[17, ...]
    adja_cfw_initial_d_wzida0e0b0xyg0 = np.sum(ce_sire[12, ...] * cfw_initial_wzida0e0b0xyg0 / sfw_a0e0b0xyg0 * agedam_propn_da0e0b0xyg0, axis=d_pos, keepdims=True)
    adja_cfw_initial_d_wzida0e0b0xyg1 = np.sum(ce_dams[12, ...] * cfw_initial_wzida0e0b0xyg1 / sfw_a0e0b0xyg1 * agedam_propn_da0e0b0xyg1, axis=d_pos, keepdims=True)
    adja_cfw_initial_d_wzida0e0b0xyg3 = ce_offs[12, ...] * cfw_initial_wzida0e0b0xyg3 / sfw_da0e0b0xyg3
    adja_fd_initial_d_a0e0b0xyg0 = np.sum(ce_sire[13, ...] * agedam_propn_da0e0b0xyg0, axis=0) #d axis lost when summing
    adja_fd_initial_d_a0e0b0xyg1 = np.sum(ce_dams[13, ...] * agedam_propn_da0e0b0xyg1, axis=0)
    adja_fd_initial_d_da0e0b0xyg3 = ce_offs[13, ...]
    adja_fl_initial_d_wzida0e0b0xyg0 = np.sum(ce_sire[12, ...] * fl_initial_wzida0e0b0xyg0 / sfw_a0e0b0xyg0 * agedam_propn_da0e0b0xyg0, axis=d_pos, keepdims=True) #Should be fl_initial / sfw  So more understandable to think of the eqn as being fl_initial * cx[0] (cfw adj due to gender) / sfw
    adja_fl_initial_d_wzida0e0b0xyg1 = np.sum(ce_dams[12, ...] * fl_initial_wzida0e0b0xyg1 / sfw_a0e0b0xyg1 * agedam_propn_da0e0b0xyg1, axis=d_pos, keepdims=True)
    adja_fl_initial_d_wzida0e0b0xyg3 = ce_offs[12, ...] * fl_initial_wzida0e0b0xyg3 / sfw_da0e0b0xyg3
    ##adjust for btrt. Note cfw changes throughout the year therefore the adjustment factor will not be the same all yr hence divide by std_fw (same for fl) eg the impact of gender on cfw will be much less after only a small time (the parameter is a yearly factor eg male sheep have 0.02 kg more wool each yr)
    adja_lw_initial_b0_xyg0 = np.sum(cb0_sire[17, ...] * btrt_propn_b0xyg0, axis=0) #d axis lost when summing
    adja_lw_initial_b0_xyg1 = np.sum(cb0_dams[17, ...] * btrt_propn_b0xyg1, axis=0)
    adja_lw_initial_b0_b0xyg3 = cb0_offs[17, ...]
    adja_cfw_initial_b0_wzida0e0b0xyg0 = np.sum(cb0_sire[12, ...] * cfw_initial_wzida0e0b0xyg0 / sfw_a0e0b0xyg0 * btrt_propn_b0xyg0, axis=b0_pos, keepdims=True)
    adja_cfw_initial_b0_wzida0e0b0xyg1 = np.sum(cb0_dams[12, ...] * cfw_initial_wzida0e0b0xyg1 / sfw_a0e0b0xyg1 * btrt_propn_b0xyg1, axis=b0_pos, keepdims=True)
    adja_cfw_initial_b0_wzida0e0b0xyg3 = cb0_offs[12, ...] * cfw_initial_wzida0e0b0xyg3 / sfw_da0e0b0xyg3
    adja_fd_initial_b0_xyg0 = np.sum(cb0_sire[13, ...] * btrt_propn_b0xyg0, axis=0) #d axis lost when summing
    adja_fd_initial_b0_xyg1 = np.sum(cb0_dams[13, ...] * btrt_propn_b0xyg1, axis=0)
    adja_fd_initial_b0_b0xyg3 = cb0_offs[13, ...]
    adja_fl_initial_b0_wzida0e0b0xyg0 = np.sum(cb0_sire[12, ...] * fl_initial_wzida0e0b0xyg0 / sfw_a0e0b0xyg0 * btrt_propn_b0xyg0, axis=b0_pos, keepdims=True) #Should be fl_initial / sfw  So more understandable to think of the eqn as being fl_initial * cx[0] (cfw adj due to gender) / sfw
    adja_fl_initial_b0_wzida0e0b0xyg1 = np.sum(cb0_dams[12, ...] * fl_initial_wzida0e0b0xyg1 / sfw_a0e0b0xyg1 * btrt_propn_b0xyg1, axis=b0_pos, keepdims=True)
    adja_fl_initial_b0_wzida0e0b0xyg3 = cb0_offs[12, ...] * fl_initial_wzida0e0b0xyg3 / sfw_da0e0b0xyg3
    ##apply adjustments to initial variables
    lw_initial_wzida0e0b0xyg0 = lw_initial_wzida0e0b0xyg0 * (1 + adjp_lw_initial_a_a0e0b0xyg0) + adja_lw_initial_x_xyg0 + adja_lw_initial_d_a0e0b0xyg0 + adja_lw_initial_b0_xyg0
    lw_initial_wzida0e0b0xyg1 = lw_initial_wzida0e0b0xyg1 * (1 + adjp_lw_initial_a_a0e0b0xyg1) + adja_lw_initial_x_xyg1 + adja_lw_initial_d_a0e0b0xyg1 + adja_lw_initial_b0_xyg1
    lw_initial_wzida0e0b0xyg3 = lw_initial_wzida0e0b0xyg3 * (1 + adjp_lw_initial_a_a0e0b0xyg3) + adja_lw_initial_x_xyg3 + adja_lw_initial_d_da0e0b0xyg3 + adja_lw_initial_b0_b0xyg3
    cfw_initial_wzida0e0b0xyg0 = cfw_initial_wzida0e0b0xyg0 * (1 + adjp_cfw_initial_a_a0e0b0xyg0) + adja_cfw_initial_x_wzida0e0b0xyg0 + adja_cfw_initial_d_wzida0e0b0xyg0 + adja_cfw_initial_b0_wzida0e0b0xyg0
    cfw_initial_wzida0e0b0xyg1 = cfw_initial_wzida0e0b0xyg1 * (1 + adjp_cfw_initial_a_a0e0b0xyg1) + adja_cfw_initial_x_wzida0e0b0xyg1 + adja_cfw_initial_d_wzida0e0b0xyg1 + adja_cfw_initial_b0_wzida0e0b0xyg1
    cfw_initial_wzida0e0b0xyg3 = cfw_initial_wzida0e0b0xyg3 * (1 + adjp_cfw_initial_a_a0e0b0xyg3) + adja_cfw_initial_x_wzida0e0b0xyg3 + adja_cfw_initial_d_wzida0e0b0xyg3 + adja_cfw_initial_b0_wzida0e0b0xyg3
    fd_initial_wzida0e0b0xyg0 = fd_initial_wzida0e0b0xyg0 * (1 + adjp_fd_initial_a_a0e0b0xyg0) + adja_fd_initial_x_xyg0 + adja_fd_initial_d_a0e0b0xyg0 + adja_fd_initial_b0_xyg0
    fd_initial_wzida0e0b0xyg1 = fd_initial_wzida0e0b0xyg1 * (1 + adjp_fd_initial_a_a0e0b0xyg1) + adja_fd_initial_x_xyg1 + adja_fd_initial_d_a0e0b0xyg1 + adja_fd_initial_b0_xyg1
    fd_initial_wzida0e0b0xyg3 = fd_initial_wzida0e0b0xyg3 * (1 + adjp_fd_initial_a_a0e0b0xyg3) + adja_fd_initial_x_xyg3 + adja_fd_initial_d_da0e0b0xyg3 + adja_fd_initial_b0_b0xyg3
    fl_initial_wzida0e0b0xyg0 = fl_initial_wzida0e0b0xyg0 * (1 + adjp_fl_initial_a_a0e0b0xyg0) + adja_fl_initial_x_wzida0e0b0xyg0 + adja_fl_initial_d_wzida0e0b0xyg0 + adja_fl_initial_b0_wzida0e0b0xyg0
    fl_initial_wzida0e0b0xyg1 = fl_initial_wzida0e0b0xyg1 * (1 + adjp_fl_initial_a_a0e0b0xyg1) + adja_fl_initial_x_wzida0e0b0xyg1 + adja_fl_initial_d_wzida0e0b0xyg1 + adja_fl_initial_b0_wzida0e0b0xyg1
    fl_initial_wzida0e0b0xyg3 = fl_initial_wzida0e0b0xyg3 * (1 + adjp_fl_initial_a_a0e0b0xyg3) + adja_fl_initial_x_wzida0e0b0xyg3 + adja_fl_initial_d_wzida0e0b0xyg3 + adja_fl_initial_b0_wzida0e0b0xyg3
    ##calc aw, bw and mw (adipose, bone and muscle weight)
    aw_initial_wzida0e0b0xyg0 = lw_initial_wzida0e0b0xyg0 * aw_propn_yg0
    aw_initial_wzida0e0b0xyg1 = lw_initial_wzida0e0b0xyg1 * aw_propn_yg1
    aw_initial_wzida0e0b0xyg3 = lw_initial_wzida0e0b0xyg3 * aw_propn_yg3
    bw_initial_wzida0e0b0xyg0 = lw_initial_wzida0e0b0xyg0 * bw_propn_yg0
    bw_initial_wzida0e0b0xyg1 = lw_initial_wzida0e0b0xyg1 * bw_propn_yg1
    bw_initial_wzida0e0b0xyg3 = lw_initial_wzida0e0b0xyg3 * bw_propn_yg3
    mw_initial_wzida0e0b0xyg0 = lw_initial_wzida0e0b0xyg0 * mw_propn_yg0
    mw_initial_wzida0e0b0xyg1 = lw_initial_wzida0e0b0xyg1 * mw_propn_yg1
    mw_initial_wzida0e0b0xyg3 = lw_initial_wzida0e0b0xyg3 * mw_propn_yg3
    ##numbers
    ###Distribution of initial numbers across the a1 axis
    initial_a1 = pinp.sheep['i_initial_a1'][pinp.sheep['i_mask_a']] / np.sum(pinp.sheep['i_initial_a1'][pinp.sheep['i_mask_a']])
    initial_a1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(initial_a1, a1_pos)
    ###Distribution of initial numbers across the b1 axis
    initial_b1nwzida0e0b0xyg = fun.f_reshape_expand(uinp.structure['i_initial_b1'], b1_pos)
    ###Distribution of initial numbers across the y axis
    initial_yg0 = fun.f_reshape_expand(uinp.parameters['i_initial_y0'], y_pos, condition = uinp.parameters['i_mask_y0'], axis = y_pos)
    initial_yg1 = fun.f_reshape_expand(uinp.parameters['i_initial_y1'], y_pos, condition = uinp.parameters['i_mask_y1'], axis = y_pos)
    initial_yg3 = fun.f_reshape_expand(uinp.parameters['i_initial_y3'], y_pos, condition = uinp.parameters['i_mask_y3'], axis = y_pos)
    ###Distribution of initial numbers across the e1 axis
    initial_e1 = np.zeros(len_e1)
    initial_e1[0]=1
    initial_e1b1nwzida0e0b0xyg = fun.f_reshape_expand(initial_e1, e1_pos)
    ###distribution of numbers on the e0 axis
    propn_e_ida0e0b0xyg = fun.f_reshape_expand(pinp.sheep['i_propn_e_i'], i_pos, condition=pinp.sheep['i_mask_i'], axis=i_pos)
    ###If 70% of ewes that are not pregnant get pregnant in a cycle then
    ###first cycle 70% pregnant (30% not pregnant)
    ###2nd cycle 70% of the 30% get pregnant = 21% (9 % not pregnant)
    ###3rd cycle 70% of the 9% = 6.3% (2.7% not pregnant)
    ###Proportion conceiving in each cycle from the view of the proportion of dams conceiving in each cycle
    e0_propn_ida0e0b0xyg = (1 - propn_e_ida0e0b0xyg) ** index_e0b0xyg * propn_e_ida0e0b0xyg
    #propn of the off born in each cycle (propn of dams conceived in each cycle / total number conceiving during the mating period)
    e0_propn_ida0e0b0xyg = e0_propn_ida0e0b0xyg / np.sum(e0_propn_ida0e0b0xyg, axis = e0_pos, keepdims=True)
    ###sire
    numbers_initial_zida0e0b0xyg0 = season_propn_zida0e0b0xyg * initial_yg0
    ###dams
    numbers_initial_propn_repro_a1e1b1nwzida0e0b0xyg1 = initial_a1e1b1nwzida0e0b0xyg * initial_e1b1nwzida0e0b0xyg * initial_b1nwzida0e0b0xyg
    numbers_initial_a1e1b1nwzida0e0b0xyg1 = numbers_initial_propn_repro_a1e1b1nwzida0e0b0xyg1 * season_propn_zida0e0b0xyg * initial_yg1
    ###offs
    ####Initial proportion of offspring if clustered.
    ####These proportions are used if the offspring are clustered
    numbers_initial_cluster_ida0e0b0xyg3 = btrt_propn_b0xyg3 * e0_propn_ida0e0b0xyg
    ####initial offs numbers
    numbers_initial_zida0e0b0xyg3 = season_propn_zida0e0b0xyg * initial_yg3 * numbers_initial_cluster_ida0e0b0xyg3

    #######################
    ##Age, date, timing 1 #
    #######################

    ## date mated (when the ewe actually conceives)
    date_mated_pa1e1b1nwzida0e0b0xyg1 = date_joined_pa1e1b1nwzida0e0b0xyg1.astype('datetime64[D]') + (cf_dams[4, ..., 0:1, :] * (index_e1b1nwzida0e0b0xyg + 0.5)).astype('timedelta64[D]')
    ##Age of dam when first lamb is born
    agedam_lamb1st_a1e1b1nwzida0e0b0xyg3 = np.swapaxes(date_born1st_oa1e1b1nwzida0e0b0xyg2 - date_born1st_ida0e0b0xyg1,0,d_pos)[0,...] #replace the d axis with the o axis then remove the d axis by taking slice 0 (note the d axis was not active)
    if np.count_nonzero(pinp.sheep['i_mask_i']) > 1: #complicated by the fact that sire tol is not necessarily the same as dams and off
        agedam_lamb1st_a1e1b1nwzida0e0b0xyg0 = np.compress(pinp.sheep['i_masksire_i'], agedam_lamb1st_a1e1b1nwzida0e0b0xyg3[...,a_g3_g0], i_pos) #don't mask if both tol are included
    else:
        agedam_lamb1st_a1e1b1nwzida0e0b0xyg0 = np.compress(pinp.sheep['i_masksire_i'][pinp.sheep['i_masksire_i']], agedam_lamb1st_a1e1b1nwzida0e0b0xyg3[...,a_g3_g0], i_pos) #have to mask masksire_i  because it needs to be the same length as i
    agedam_lamb1st_a1e1b1nwzida0e0b0xyg1 = agedam_lamb1st_a1e1b1nwzida0e0b0xyg3[...,a_g3_g1]
    agedam_lamb1st_a1e1b1nwzida0e0b0xyg3 = np.compress(mask_d_offs, agedam_lamb1st_a1e1b1nwzida0e0b0xyg3, d_pos) #mask d axis (compress function masks a specific axis)

    ##wean date (weaning input is counting from the date of the first lamb (not the date of the average lamb in the first cycle))
    date_weaned_pa1e1b1nwzida0e0b0xyg2 = date_born1st_pa1e1b1nwzida0e0b0xyg2 + age_wean1st_pa1e1b1nwzida0e0b0xyg2 #use offs wean age input and has the same birth day (offset by a yr) therefore it will automatically align with a period start

    ##age start open (not capped at weaning or before birth) used to calc m1 stuff
    age_start_open_pa1e1b1nwzida0e0b0xyg0 = date_start_pa1e1b1nwzida0e0b0xyg - date_born_ida0e0b0xyg0
    age_start_open_pa1e1b1nwzida0e0b0xyg1 = date_start_pa1e1b1nwzida0e0b0xyg - date_born_ida0e0b0xyg1
    age_start_open_pa1e1b1nwzida0e0b0xyg3 = date_start_pa1e1b1nwzida0e0b0xyg3 - date_born_ida0e0b0xyg3
    age_start_open_pa1e1b1nwzida0e0b0xyg2 = date_start_pa1e1b1nwzida0e0b0xyg - date_born_pa1e1b1nwzida0e0b0xyg2
    ##age start
    age_start_pa1e1b1nwzida0e0b0xyg0 = (np.maximum(date_start_pa1e1b1nwzida0e0b0xyg, date_weaned_ida0e0b0xyg0) - date_born_ida0e0b0xyg0).astype(int) #use date weaned because the simulation for these animals is starting at weaning.
    age_start_pa1e1b1nwzida0e0b0xyg1 = (np.maximum(date_start_pa1e1b1nwzida0e0b0xyg, date_weaned_ida0e0b0xyg1) - date_born_ida0e0b0xyg1).astype(int) #use date weaned because the simulation for these animals is starting at weaning.
    age_start_pa1e1b1nwzida0e0b0xyg3 = (np.maximum(date_start_pa1e1b1nwzida0e0b0xyg, date_weaned_ida0e0b0xyg3) - date_born_ida0e0b0xyg3).astype(int) #use date weaned because the simulation for these animals is starting at weaning.
    age_start_pa1e1b1nwzida0e0b0xyg2 = (np.maximum(np.array([0]).astype('timedelta64[D]'),np.minimum(date_start_pa1e1b1nwzida0e0b0xyg, date_weaned_pa1e1b1nwzida0e0b0xyg2) - date_born_pa1e1b1nwzida0e0b0xyg2)).astype(int) #use min and max so that the min age is 0 and the max age is the age at weaning
    ##Age_end: age at the beginning of the last day of the given period
    ##age end, minus one to allow the plus one in the next step when period date is less than weaning date (the minus one ensures that when the p_date is less than weaning the animal gets 0 days in the given period)
    age_end_pa1e1b1nwzida0e0b0xyg0 = (np.maximum(date_end_pa1e1b1nwzida0e0b0xyg, date_weaned_ida0e0b0xyg0 -1) - date_born_ida0e0b0xyg0).astype(int) #use date weaned because the simulation for these animals is starting at weaning.
    age_end_pa1e1b1nwzida0e0b0xyg1 = (np.maximum(date_end_pa1e1b1nwzida0e0b0xyg, date_weaned_ida0e0b0xyg1 -1) - date_born_ida0e0b0xyg1).astype(int) #use date weaned because the simulation for these animals is starting at weaning.
    age_end_pa1e1b1nwzida0e0b0xyg3 = (np.maximum(date_end_pa1e1b1nwzida0e0b0xyg, date_weaned_ida0e0b0xyg3 -1) - date_born_ida0e0b0xyg3).astype(int) #use date weaned because the simulation for these animals is starting at weaning.
    age_end_pa1e1b1nwzida0e0b0xyg2 = (np.maximum(np.array([-1]).astype('timedelta64[D]'),np.minimum(date_end_pa1e1b1nwzida0e0b0xyg, date_weaned_pa1e1b1nwzida0e0b0xyg2 -1) - date_born_pa1e1b1nwzida0e0b0xyg2)).astype(int)  #use min and max so that the min age is 0 and the max age is the age at weaning

    ##age mid period , plus one to get the age at the end of the last day of the period ie needed to get the full len of period.
    age_pa1e1b1nwzida0e0b0xyg0 = (age_start_pa1e1b1nwzida0e0b0xyg0 + age_end_pa1e1b1nwzida0e0b0xyg0 +1) /2
    age_pa1e1b1nwzida0e0b0xyg1 = (age_start_pa1e1b1nwzida0e0b0xyg1 + age_end_pa1e1b1nwzida0e0b0xyg1 +1) /2
    age_pa1e1b1nwzida0e0b0xyg2 = (age_start_pa1e1b1nwzida0e0b0xyg2 + age_end_pa1e1b1nwzida0e0b0xyg2 +1) /2
    age_pa1e1b1nwzida0e0b0xyg3 = (age_start_pa1e1b1nwzida0e0b0xyg3 + age_end_pa1e1b1nwzida0e0b0xyg3 +1) /2

    ##days in each period for each animal
    days_period_pa1e1b1nwzida0e0b0xyg0 = age_end_pa1e1b1nwzida0e0b0xyg0 +1 - age_start_pa1e1b1nwzida0e0b0xyg0
    days_period_pa1e1b1nwzida0e0b0xyg1 = age_end_pa1e1b1nwzida0e0b0xyg1 +1 - age_start_pa1e1b1nwzida0e0b0xyg1
    days_period_pa1e1b1nwzida0e0b0xyg2 = age_end_pa1e1b1nwzida0e0b0xyg2 +1 - age_start_pa1e1b1nwzida0e0b0xyg2
    days_period_pa1e1b1nwzida0e0b0xyg3 = (age_end_pa1e1b1nwzida0e0b0xyg3 +1 - age_start_pa1e1b1nwzida0e0b0xyg3
                                          ) * (p_index_pa1e1b1nwzida0e0b0xyg<np.count_nonzero(mask_p_offs_p)-1) #make days per period zero if period is not required for offs. -1 because we want days per period to be 0 in the period before the mask turns to false because there are some spots where p+1 is used as the index
    days_period_cut_pa1e1b1nwzida0e0b0xyg3 = days_period_pa1e1b1nwzida0e0b0xyg3[mask_p_offs_p] #masked version of p axis

    ##Age of foetus (start of period, end of period and mid period - days)
    age_f_start_open_pa1e1b1nwzida0e0b0xyg1 = date_start_pa1e1b1nwzida0e0b0xyg - date_mated_pa1e1b1nwzida0e0b0xyg1
    age_f_start_pa1e1b1nwzida0e0b0xyg1 = np.maximum(np.array([0]).astype('timedelta64[D]'), np.minimum(cp_dams[1, 0:1, :].astype('timedelta64[D]'), date_start_pa1e1b1nwzida0e0b0xyg - date_mated_pa1e1b1nwzida0e0b0xyg1))
    age_f_end_pa1e1b1nwzida0e0b0xyg1 = np.minimum(cp_dams[1, 0:1, :].astype('timedelta64[D]') - 1, date_end_pa1e1b1nwzida0e0b0xyg - date_mated_pa1e1b1nwzida0e0b0xyg1) #open at bottom capped at top, cp -1 so that the period_days formula below is correct when p_date - date_mated is greater than cp (because plus 1)


    ############################
    ### Daily steps            #
    ############################
    ##definition for this is that the action eg weaning occurs at 12am on the given date. therefore is weaning occurs on day 150 the lambs are counted as weaned lambs on that day.
    ##This info determines the side with > or >=


    ##add m1 axis
    date_start_pa1e1b1nwzida0e0b0xygm1 = date_start_pa1e1b1nwzida0e0b0xyg[...,na] + index_m1
    doy_pa1e1b1nwzida0e0b0xygm1= doy_pa1e1b1nwzida0e0b0xyg[...,na] + index_m1
    ##age open ie not capped at weaning
    age_m1_pa1e1b1nwzida0e0b0xyg0m1 = (age_start_open_pa1e1b1nwzida0e0b0xyg0[..., na] + index_m1) /np.timedelta64(1, 'D') #divide by 1 day to get int. need int so that i can put np.nan into array
    age_m1_pa1e1b1nwzida0e0b0xyg1m1 = (age_start_open_pa1e1b1nwzida0e0b0xyg1[..., na] + index_m1) /np.timedelta64(1, 'D') #divide by 1 day to get int. need int so that i can put np.nan into array
    age_m1_pa1e1b1nwzida0e0b0xyg2m1 = (age_start_open_pa1e1b1nwzida0e0b0xyg2[..., na] + index_m1) /np.timedelta64(1, 'D') #divide by 1 day to get int. need int so that i can put np.nan into array
    age_m1_pa1e1b1nwzida0e0b0xyg3m1 = (age_start_open_pa1e1b1nwzida0e0b0xyg3[..., na] + index_m1) /np.timedelta64(1, 'D') #divide by 1 day to get int. need int so that i can put np.nan into array
    ##calc m1 weights - if age<=weaning it has 0 weighting (ie false) else weighting = 1 (ie true) - need so that the values are not included in the mean calculations below which determine the average production for a given m1 period.
    age_m1_weights_pa1e1b1nwzida0e0b0xyg0m1 = age_m1_pa1e1b1nwzida0e0b0xyg0m1>=(date_weaned_ida0e0b0xyg0 - date_born_ida0e0b0xyg0)[..., na].astype(int) #use date_wean - date born because that results in the average weaning age of all animal (age_weaned variable is just the age of the first animal)
    age_m1_weights_pa1e1b1nwzida0e0b0xyg1m1 = age_m1_pa1e1b1nwzida0e0b0xyg1m1>=(date_weaned_ida0e0b0xyg1 - date_born_ida0e0b0xyg1)[..., na].astype(int) #use date_wean - date born because that results in the average weaning age of all animal (age_weaned variable is just the age of the first animal)
    age_m1_weights_pa1e1b1nwzida0e0b0xyg3m1 = age_m1_pa1e1b1nwzida0e0b0xyg3m1>=(date_weaned_ida0e0b0xyg3 - date_born_ida0e0b0xyg3)[..., na].astype(int) #use date_wean - date born because that results in the average weaning age of all animal (age_weaned variable is just the age of the first animal)
    ##calc yatf m1 weighting - if age is greater than weaning or less than 0 it will have 0 weighting in the m1 means calculated below else it will have weighting 1
    age_m1_weights_pa1e1b1nwzida0e0b0xyg2m1 = np.logical_and(age_m1_pa1e1b1nwzida0e0b0xyg2m1>=0, age_m1_pa1e1b1nwzida0e0b0xyg2m1<(date_weaned_pa1e1b1nwzida0e0b0xyg2 - date_born_pa1e1b1nwzida0e0b0xyg2)[..., na].astype(int)) #use date_wean - date born because that results in the average weaning age of all animal (age_weaned variable is just the age of the first animal)
    ##Age of foetus with minor axis (days)
    age_f_m1_pa1e1b1nwzida0e0b0xyg1m1 = (age_f_start_open_pa1e1b1nwzida0e0b0xyg1[...,na] + index_m1) /np.timedelta64(1, 'D') #divide by 1 day to get int. need int so that i can put np.nan into array
    ##calc foetus m1 weighting - if age is greater than birth or less than 0 it will have 0 weighting in the m1 means calculated below else it will have weighting 1
    age_f_m1_weights_pa1e1b1nwzida0e0b0xyg1m1 = np.logical_and(age_f_m1_pa1e1b1nwzida0e0b0xyg1m1>=0, age_f_m1_pa1e1b1nwzida0e0b0xyg1m1<cp_dams[1, 0, :, na])
    #age_f_m1_pa1e1b1nwzida0e0b0xyg1m1[age_f_m1_pa1e1b1nwzida0e0b0xyg1m1 <= 0] = np.nan
    #age_f_m1_pa1e1b1nwzida0e0b0xyg1m1[age_f_m1_pa1e1b1nwzida0e0b0xyg1m1 > cp_dams[1, 0, :, na]] = np.nan
    ##adjusted age of young (adjusted by intake factor - basically the factor of how age of young effect dam intake, the adjustment factor basically alters the age of the young to influence intake.)
    age_y_adj_pa1e1b1nwzida0e0b0xyg1m1 = age_m1_pa1e1b1nwzida0e0b0xyg2m1 + np.maximum(0, (date_start_pa1e1b1nwzida0e0b0xygm1 - date_weaned_pa1e1b1nwzida0e0b0xyg2[..., na]) /np.timedelta64(1, 'D')) * (ci_dams[21, ..., na] - 1) #minus 1 because the ci factor is applied to the age post weaning but using the open date means it has already been included once ie we want x + y *ci but using date open gives  x  + y + y*ci, x = age to weaning, y = age between period and weaning, therefore minus 1 x  + y + y*(ci-1)
    ##calc young m1 weighting - if age is less than 0 it will have 0 weighting in the m1 means calculated below else it will have weighting 1
    age_y_adj_weights_pa1e1b1nwzida0e0b0xyg1m1 = age_y_adj_pa1e1b1nwzida0e0b0xyg1m1 > 0  #no max cap (ie represents age young would be if never weaned off mum)
    ##Foetal age relative to parturition with minor axis
    relage_f_pa1e1b1nwzida0e0b0xyg1m1 = np.maximum(0,age_f_m1_pa1e1b1nwzida0e0b0xyg1m1 / cp_dams[1, 0, :, na])
    ##Age of lamb relative to peak intake-with minor function
    pimi_pa1e1b1nwzida0e0b0xyg1m1 = age_y_adj_pa1e1b1nwzida0e0b0xyg1m1 / ci_dams[8, ..., na]
    ##Age of lamb relative to peak lactation-with minor axis
    lmm_pa1e1b1nwzida0e0b0xyg1m1 = (age_m1_pa1e1b1nwzida0e0b0xyg2m1 + cl_dams[1, ..., na]) / cl_dams[2, ..., na]
    ##Chill index for lamb survival
    chill_index_pa1e1b1nwzida0e0b0xygm1 = (481 + (11.7 + 3.1 * ws_pa1e1b1nwzida0e0b0xyg[..., na] ** 0.5) * (40 - temp_ave_pa1e1b1nwzida0e0b0xyg[..., na]) + 418 * (1-np.exp(-0.04 * rain_pa1e1b1nwzida0e0b0xygm1)))

    ##Proportion of SRW with age
    srw_age_pa1e1b1nwzida0e0b0xyg0 = fun.f_weighted_average(np.exp(-cn_sire[1, ..., na] * age_m1_pa1e1b1nwzida0e0b0xyg0m1 / srw_xyg0[..., na] ** cn_sire[2, ..., na]), weights=age_m1_weights_pa1e1b1nwzida0e0b0xyg0m1, axis = -1)
    srw_age_pa1e1b1nwzida0e0b0xyg1 = fun.f_weighted_average(np.exp(-cn_dams[1, ..., na] * age_m1_pa1e1b1nwzida0e0b0xyg1m1 / srw_xyg1[..., na] ** cn_dams[2, ..., na]), weights=age_m1_weights_pa1e1b1nwzida0e0b0xyg1m1, axis = -1)
    srw_age_pa1e1b1nwzida0e0b0xyg2 = fun.f_weighted_average(np.exp(-cn_yatf[1, ..., na] * age_m1_pa1e1b1nwzida0e0b0xyg2m1 / srw_xyg2[..., na] ** cn_yatf[2, ..., na]), weights=age_m1_weights_pa1e1b1nwzida0e0b0xyg2m1, axis = -1)
    srw_age_pa1e1b1nwzida0e0b0xyg3 = fun.f_weighted_average(np.exp(-cn_offs[1, ..., na] * age_m1_pa1e1b1nwzida0e0b0xyg3m1 / srw_xyg3[..., na] ** cn_offs[2, ..., na]), weights=age_m1_weights_pa1e1b1nwzida0e0b0xyg3m1, axis = -1)

    #srw_age_pa1e1b1nwzida0e0b0xyg0 = np.nanmean(np.exp(-cn_sire[1, ..., na] * age_m1_pa1e1b1nwzida0e0b0xyg0m1 / srw_xyg0[..., na] ** cn_sire[2, ..., na]), axis = -1)
    #srw_age_pa1e1b1nwzida0e0b0xyg1 = np.nanmean(np.exp(-cn_dams[1, ..., na] * age_m1_pa1e1b1nwzida0e0b0xyg1m1 / srw_xyg1[..., na] ** cn_dams[2, ..., na]), axis = -1)
    #srw_age_pa1e1b1nwzida0e0b0xyg2 = np.nanmean(np.exp(-cn_yatf[1, ..., na] * age_m1_pa1e1b1nwzida0e0b0xyg2m1 / srw_xyg2[..., na] ** cn_yatf[2, ..., na]), axis = -1)
    #srw_age_pa1e1b1nwzida0e0b0xyg3 = np.nanmean(np.exp(-cn_offs[1, ..., na] * age_m1_pa1e1b1nwzida0e0b0xyg3m1 / srw_xyg3[..., na] ** cn_offs[2, ..., na]), axis = -1)

    ##age factor wool
    af_wool_pa1e1b1nwzida0e0b0xyg0 = fun.f_weighted_average(cw_sire[5, ..., na] + (1 - cw_sire[5, ..., na])*(1-np.exp(-cw_sire[12, ..., na] * age_m1_pa1e1b1nwzida0e0b0xyg0m1)), weights=age_m1_weights_pa1e1b1nwzida0e0b0xyg0m1, axis = -1)
    af_wool_pa1e1b1nwzida0e0b0xyg1 = fun.f_weighted_average(cw_dams[5, ..., na] + (1 - cw_dams[5, ..., na])*(1-np.exp(-cw_dams[12, ..., na] * age_m1_pa1e1b1nwzida0e0b0xyg1m1)), weights=age_m1_weights_pa1e1b1nwzida0e0b0xyg1m1, axis = -1)
    af_wool_pa1e1b1nwzida0e0b0xyg2 = fun.f_weighted_average(cw_yatf[5, ..., na] + (1 - cw_yatf[5, ..., na])*(1-np.exp(-cw_yatf[12, ..., na] * age_m1_pa1e1b1nwzida0e0b0xyg2m1)), weights=age_m1_weights_pa1e1b1nwzida0e0b0xyg2m1, axis = -1)
    af_wool_pa1e1b1nwzida0e0b0xyg3 = fun.f_weighted_average(cw_offs[5, ..., na] + (1 - cw_offs[5, ..., na])*(1-np.exp(-cw_offs[12, ..., na] * age_m1_pa1e1b1nwzida0e0b0xyg3m1)), weights=age_m1_weights_pa1e1b1nwzida0e0b0xyg3m1, axis = -1)
    ##Day length factor on efficiency
    dlf_eff_pa1e1b1nwzida0e0b0xyg = np.average(lat_deg / 40 * np.sin(2 * np.pi * doy_pa1e1b1nwzida0e0b0xygm1 / 365), axis = -1)
    ##Pattern of maintenance with age
    mr_age_pa1e1b1nwzida0e0b0xyg0 = fun.f_weighted_average(np.maximum(cm_sire[4, ..., na], np.exp(-cm_sire[3, ..., na] * age_m1_pa1e1b1nwzida0e0b0xyg0m1)), weights=age_m1_weights_pa1e1b1nwzida0e0b0xyg0m1, axis = -1)
    mr_age_pa1e1b1nwzida0e0b0xyg1 = fun.f_weighted_average(np.maximum(cm_dams[4, ..., na], np.exp(-cm_dams[3, ..., na] * age_m1_pa1e1b1nwzida0e0b0xyg1m1)), weights=age_m1_weights_pa1e1b1nwzida0e0b0xyg1m1, axis = -1)
    mr_age_pa1e1b1nwzida0e0b0xyg2 = fun.f_weighted_average(np.maximum(cm_offs[4, ..., na], np.exp(-cm_offs[3, ..., na] * age_m1_pa1e1b1nwzida0e0b0xyg2m1)), weights=age_m1_weights_pa1e1b1nwzida0e0b0xyg2m1, axis = -1)
    mr_age_pa1e1b1nwzida0e0b0xyg3 = fun.f_weighted_average(np.maximum(cm_yatf[4, ..., na], np.exp(-cm_yatf[3, ..., na] * age_m1_pa1e1b1nwzida0e0b0xyg3m1)), weights=age_m1_weights_pa1e1b1nwzida0e0b0xyg3m1, axis = -1)
    ##Impact of rainfall on 'cold' intake increment
    rain_intake_pa1e1b1nwzida0e0b0xyg0 = fun.f_weighted_average(np.maximum(0, 1 - rain_pa1e1b1nwzida0e0b0xygm1 / ci_sire[18, ..., na]),  weights=age_m1_weights_pa1e1b1nwzida0e0b0xyg0m1, axis = -1)
    rain_intake_pa1e1b1nwzida0e0b0xyg1 = fun.f_weighted_average(np.maximum(0, 1 - rain_pa1e1b1nwzida0e0b0xygm1 / ci_dams[18, ..., na]),  weights=age_m1_weights_pa1e1b1nwzida0e0b0xyg1m1, axis = -1)
    rain_intake_pa1e1b1nwzida0e0b0xyg2 = fun.f_weighted_average(np.maximum(0, 1 - rain_pa1e1b1nwzida0e0b0xygm1 / ci_offs[18, ..., na]),  weights=age_m1_weights_pa1e1b1nwzida0e0b0xyg2m1, axis = -1)
    rain_intake_pa1e1b1nwzida0e0b0xyg3 = fun.f_weighted_average(np.maximum(0, 1 - rain_pa1e1b1nwzida0e0b0xygm1[mask_p_offs_p] / ci_yatf[18, ..., na]),  weights=age_m1_weights_pa1e1b1nwzida0e0b0xyg3m1, axis = -1)
    ##Proportion of peak intake due to time from birth
    pi_age_y_pa1e1b1nwzida0e0b0xyg1 = fun.f_weighted_average(cb1_dams[19, ..., na] * np.maximum(0,pimi_pa1e1b1nwzida0e0b0xyg1m1) ** ci_dams[9, ..., na] * np.exp(ci_dams[9, ..., na] * (1 - pimi_pa1e1b1nwzida0e0b0xyg1m1)), weights=age_y_adj_weights_pa1e1b1nwzida0e0b0xyg1m1, axis = -1) #maximum to stop error in power (not sure why the negatives were causing a problem)
    ##Peak milk production pattern (time from birth)
    mp_age_y_pa1e1b1nwzida0e0b0xyg1 = fun.f_weighted_average(cb1_dams[0, ..., na] * lmm_pa1e1b1nwzida0e0b0xyg1m1 ** cl_dams[3, ..., na] * np.exp(cl_dams[3, ..., na]* (1 - lmm_pa1e1b1nwzida0e0b0xyg1m1)), weights=age_m1_weights_pa1e1b1nwzida0e0b0xyg2m1, axis = -1)
    ##Suckling volume pattern
    mp2_age_y_pa1e1b1nwzida0e0b0xyg1 = fun.f_weighted_average(nyatf_b1nwzida0e0b0xyg[...,na] * cl_dams[6, ..., na] * ( cl_dams[12, ..., na] + cl_dams[13, ..., na] * np.exp(-cl_dams[14, ..., na] * age_m1_pa1e1b1nwzida0e0b0xyg2m1)), weights=age_m1_weights_pa1e1b1nwzida0e0b0xyg2m1, axis = -1)
    ##Pattern of conception efficiency (doy)
    crg_doy_pa1e1b1nwzida0e0b0xyg1 = np.average(np.maximum(0,1 - cb1_dams[1, ..., na] * (1 - np.sin(2 * np.pi * (doy_pa1e1b1nwzida0e0b0xygm1 + 10) / 365) * np.sin(lat_rad) / -0.57)), axis = -1)
    ##Rumen development factor on PI - yatf
    piyf_pa1e1b1nwzida0e0b0xyg2 = fun.f_weighted_average(1/(1 + np.exp(-ci_yatf[3, ..., na] * (age_m1_pa1e1b1nwzida0e0b0xyg2m1 - ci_yatf[4, ..., na]))), weights=age_m1_weights_pa1e1b1nwzida0e0b0xyg2m1, axis = -1)
    ##Foetal normal weight pattern (mid period)
    nwf_age_f_pa1e1b1nwzida0e0b0xyg1 = fun.f_weighted_average(np.exp(cp_dams[2, ..., na] * (1 - np.exp(cp_dams[3, ..., na] * (1 - relage_f_pa1e1b1nwzida0e0b0xyg1m1)))), weights=age_f_m1_weights_pa1e1b1nwzida0e0b0xyg1m1, axis = -1)
    ##Conceptus weight pattern (mid period)
    guw_age_f_pa1e1b1nwzida0e0b0xyg1 = fun.f_weighted_average(np.exp(cp_dams[6, ..., na] * (1 - np.exp(cp_dams[7, ..., na] * (1 - relage_f_pa1e1b1nwzida0e0b0xyg1m1)))), weights=age_f_m1_weights_pa1e1b1nwzida0e0b0xyg1m1, axis = -1)
    ##Conceptus energy pattern (end of period)
    # ce_age_f_pa1e1b1nwzida0e0b0xyg1 = fun.f_weighted_average(np.exp(cp_dams[9, ..., na] * (1 - np.exp(cp_dams[10, ..., na] * (1 - relage_f_pa1e1b1nwzida0e0b0xyg1m1)))), weights=age_f_m1_weights_pa1e1b1nwzida0e0b0xyg1m1, axis = -1)
    ##Conceptus energy pattern (d_nec)
    dce_age_f_pa1e1b1nwzida0e0b0xyg1 = fun.f_weighted_average((cp_dams[9, ..., na] - cp_dams[10, ..., na]) / cp_dams[1, 0, ..., na] * np.exp(cp_dams[10, ..., na] * (1 - relage_f_pa1e1b1nwzida0e0b0xyg1m1) + cp_dams[9, ..., na] * (1 - np.exp(cp_dams[10, ..., na] * (1 - relage_f_pa1e1b1nwzida0e0b0xyg1m1)))), weights=age_f_m1_weights_pa1e1b1nwzida0e0b0xyg1m1, axis = -1)

    ##genotype calc that requires af_wool. ME for minimum wool growth (with no intake, relsize = 1)
    mew_min_pa1e1b1nwzida0e0b0xyg0 =cw_sire[14, ...] * sfw_a0e0b0xyg0[0, ...] / cw_sire[3,...] / 365 * af_wool_pa1e1b1nwzida0e0b0xyg0 * dlf_wool_pa1e1b1nwzida0e0b0xyg0 * cw_sire[1, ...] / kw_yg0
    mew_min_pa1e1b1nwzida0e0b0xyg1 =cw_dams[14, ...] * sfw_a0e0b0xyg1[0, ...] / cw_dams[3,...] / 365 * af_wool_pa1e1b1nwzida0e0b0xyg1 * dlf_wool_pa1e1b1nwzida0e0b0xyg1 * cw_dams[1, ...] / kw_yg1
    mew_min_pa1e1b1nwzida0e0b0xyg2 =cw_yatf[14, ...] * sfw_pa1e1b1nwzida0e0b0xyg2[0, ...] / cw_yatf[3,...] / 365 * af_wool_pa1e1b1nwzida0e0b0xyg2 * dlf_wool_pa1e1b1nwzida0e0b0xyg2 * cw_yatf[1, ...] / kw_yg2
    mew_min_pa1e1b1nwzida0e0b0xyg3 =cw_offs[14, ...] * sfw_da0e0b0xyg3[0, ...] / cw_offs[3,...] / 365 * af_wool_pa1e1b1nwzida0e0b0xyg3 * dlf_wool_pa1e1b1nwzida0e0b0xyg3 * cw_offs[1, ...] / kw_yg3

    ##plot above x axis is p
    # array = srw_age_pa1e1b1nwzida0e0b0xyg2
    # array = dce_age_f_pa1e1b1nwzida0e0b0xyg1
    # array = guw_age_f_pa1e1b1nwzida0e0b0xyg1
    # array = nwf_age_f_pa1e1b1nwzida0e0b0xyg1
    # array = mp2_age_y_pa1e1b1nwzida0e0b0xyg1
    # array = mp_age_y_pa1e1b1nwzida0e0b0xyg1
    # array = piyf_pa1e1b1nwzida0e0b0xyg2
    # array = af_wool_pa1e1b1nwzida0e0b0xyg2
    # array = mr_age_pa1e1b1nwzida0e0b0xyg2
    # shape=array.shape
    # for a1 in range(shape[-14]):
    #     for e1 in range(shape[-13]):
    #         for b1 in range(shape[-12]):
    #             for n in range(shape[-11]):
    #                 for w in range(shape[-10]):
    #                     for z in range(shape[-9]):
    #                         for i in range(shape[-8]):
    #                             for d in range(shape[-7]):
    #                                 for a0 in range(shape[-6]):
    #                                     for e0 in range(shape[-5]):
    #                                         for b0 in range(shape[-4]):
    #                                             for x in range(shape[-3]):
    #                                                 for y in range(shape[-2]):
    #                                                     for g in range(shape[-1]):
    #                                                         plt.plot(array[:100, a1-1, e1-1, b1-1, n-1, w-1, z-1, i-1, d-1, a0-1, e0-1, b0-1, x-1, y-1, g-1])
    # plt.show()



    #######################
    ##Age, date, timing 2 #
    #######################
    ##Days per period in the simulation - foetus
    days_period_f_pa1e1b1nwzida0e0b0xyg1 = np.maximum(0,(age_f_end_pa1e1b1nwzida0e0b0xyg1 +1 - age_f_start_pa1e1b1nwzida0e0b0xyg1).astype(int))

    ##proportion of days gestating during the period
    gest_propn_pa1e1b1nwzida0e0b0xyg1 = days_period_f_pa1e1b1nwzida0e0b0xyg1 / np.maximum(1, days_period_pa1e1b1nwzida0e0b0xyg1) #use max to stop div/0 error (when dams days per period =0 then days_f will also be zero)

    ##proportion of days of lactating during the period
    lact_propn_pa1e1b1nwzida0e0b0xyg1 = days_period_pa1e1b1nwzida0e0b0xyg2 / np.maximum(1, days_period_pa1e1b1nwzida0e0b0xyg1) #use max to stop div/0 error (when dams days per period =0 then days_f will also be zero)

    ##Is nutrition effecting lactation
    lact_nut_effect_pa1e1b1nwzida0e0b0xyg1 = (age_pa1e1b1nwzida0e0b0xyg2  > (cl_dams[16, ...] * cl_dams[2, ...]))

    ##Average daily CFW
    d_cfw_ave_pa1e1b1nwzida0e0b0xyg0 = sfw_a0e0b0xyg0 * af_wool_pa1e1b1nwzida0e0b0xyg0 / 365
    d_cfw_ave_pa1e1b1nwzida0e0b0xyg1 = sfw_a0e0b0xyg1 * af_wool_pa1e1b1nwzida0e0b0xyg1 / 365
    d_cfw_ave_pa1e1b1nwzida0e0b0xyg2 = sfw_pa1e1b1nwzida0e0b0xyg2 * af_wool_pa1e1b1nwzida0e0b0xyg2 / 365
    d_cfw_ave_pa1e1b1nwzida0e0b0xyg3 = sfw_da0e0b0xyg3 * af_wool_pa1e1b1nwzida0e0b0xyg3 / 365

    ##Expected relative size
    relsize_exp_a1e1b1nwzida0e0b0xyg0  = (srw_xyg0 - (srw_xyg0 - w_b_std_b0xyg0) * np.exp(-cn_sire[1, ...] * (agedam_lamb1st_a1e1b1nwzida0e0b0xyg0 /np.timedelta64(1, 'D')) / (srw_xyg0**cn_sire[2, ...]))) / srw_xyg0
    relsize_exp_a1e1b1nwzida0e0b0xyg1  = (srw_xyg1 - (srw_xyg1 - w_b_std_b0xyg1) * np.exp(-cn_dams[1, ...] * (agedam_lamb1st_a1e1b1nwzida0e0b0xyg1/np.timedelta64(1, 'D')) / (srw_xyg1**cn_dams[2, ...]))) / srw_xyg1
    relsize_exp_a1e1b1nwzida0e0b0xyg3  = (srw_xyg3 - (srw_xyg3 - w_b_std_b0xyg3) * np.exp(-cn_offs[1, ...] * (agedam_lamb1st_a1e1b1nwzida0e0b0xyg3/np.timedelta64(1, 'D')) / (srw_xyg3**cn_offs[2, ...]))) / srw_xyg3

    ##adjust ce sim param (^ ce12 &13 should be scaled by relsize (similar to ce15)) -  (^instead of setting ce with relsize adjustment then adjusting birth weight could just adjust birthweight directly with relsize factor - to avoid doing this code below)
    shape = (ce_sire.shape[0],) + relsize_exp_a1e1b1nwzida0e0b0xyg0.shape #get shape of the new ce array
    ce_ca1e1b1nwzida0e0b0xyg0 = np.zeros(shape) #make a new array - same a ce with an active i axis
    ce_ca1e1b1nwzida0e0b0xyg0[...] = fun.f_reshape_expand(ce_sire, p_pos, right_pos=uinp.parameters['i_ce_pos'])
    ce_ca1e1b1nwzida0e0b0xyg0[15, ...] = 1 - cp_sire[4, ...] * (1 - relsize_exp_a1e1b1nwzida0e0b0xyg0) #alter ce15 param, relsize has active i axis hence this is not a  simple assignment.
    ce_sire = ce_ca1e1b1nwzida0e0b0xyg0 #rename to keep consistent

    shape = (ce_dams.shape[0],) + relsize_exp_a1e1b1nwzida0e0b0xyg1.shape #get shape of the new ce array - required because assigning relsize which is diff size
    ce_ca1e1b1nwzida0e0b0xyg1 = np.zeros(shape) #make a new array - same a ce with an active i axis
    ce_ca1e1b1nwzida0e0b0xyg1[...] = fun.f_reshape_expand(ce_dams, p_pos, right_pos=uinp.parameters['i_ce_pos'])
    ce_ca1e1b1nwzida0e0b0xyg1[15, ...] = 1 - cp_dams[4, ...] * (1 - relsize_exp_a1e1b1nwzida0e0b0xyg1) #alter ce15 param, relsize has active i axis hence this is not a  simple assignment.
    ce_dams = ce_ca1e1b1nwzida0e0b0xyg1 #rename to keep consistent

    shape = (ce_offs.shape[0],) + relsize_exp_a1e1b1nwzida0e0b0xyg3.shape #get shape of the new ce array - required because assigning relsize which is diff size
    ce_ca1e1b1nwzida0e0b0xyg3 = np.zeros(shape) #make a new array - same a ce with an active i axis
    ce_ca1e1b1nwzida0e0b0xyg3[...] = fun.f_reshape_expand(ce_offs, p_pos, right_pos=uinp.parameters['i_ce_pos'])
    ce_ca1e1b1nwzida0e0b0xyg3[15, ...] = 1 - cp_offs[4, ...] * (1 - relsize_exp_a1e1b1nwzida0e0b0xyg3) #alter ce15 param, relsize has active i axis hence this is not a  simple assignment.
    ce_offs = ce_ca1e1b1nwzida0e0b0xyg3 #rename to keep consistent

    ##birth weight expected - includes relsize factor
    w_b_exp_a1e1b1nwzida0e0b0xyg0 = w_b_std_b0xyg0 * np.sum(ce_sire[15, ...] * agedam_propn_da0e0b0xyg0, axis = d_pos, keepdims = True)
    w_b_exp_a1e1b1nwzida0e0b0xyg1 = w_b_std_b0xyg1 * np.sum(ce_dams[15, ...] * agedam_propn_da0e0b0xyg1, axis = d_pos, keepdims = True)
    w_b_exp_a1e1b1nwzida0e0b0xyg3 = w_b_std_b0xyg3 * ce_offs[15, ...]

    ##Normal weight max (if animal is well fed)
    nw_max_pa1e1b1nwzida0e0b0xyg0 = srw_xyg0 * (1 - srw_age_pa1e1b1nwzida0e0b0xyg0) + w_b_exp_a1e1b1nwzida0e0b0xyg0 * srw_age_pa1e1b1nwzida0e0b0xyg0
    nw_max_pa1e1b1nwzida0e0b0xyg1 = srw_xyg1 * (1 - srw_age_pa1e1b1nwzida0e0b0xyg1) + w_b_exp_a1e1b1nwzida0e0b0xyg1 * srw_age_pa1e1b1nwzida0e0b0xyg1
    nw_max_pa1e1b1nwzida0e0b0xyg3 = srw_xyg3 * (1 - srw_age_pa1e1b1nwzida0e0b0xyg3) + w_b_exp_a1e1b1nwzida0e0b0xyg3 * srw_age_pa1e1b1nwzida0e0b0xyg3

    ##Change in normal weight max - the last period will be 0 by default but this is okay because nw hits an asymptote so change in will be 0 in the last period.
    d_nw_max_pa1e1b1nwzida0e0b0xyg0 = np.zeros_like(nw_max_pa1e1b1nwzida0e0b0xyg0)
    d_nw_max_pa1e1b1nwzida0e0b0xyg0[0:-1, ...] = (nw_max_pa1e1b1nwzida0e0b0xyg0[1:, ...] - nw_max_pa1e1b1nwzida0e0b0xyg0[0:-1, ...]) / np.maximum(1,days_period_pa1e1b1nwzida0e0b0xyg0[0:-1, ...]) #np max to stop div/0
    d_nw_max_pa1e1b1nwzida0e0b0xyg1 = np.zeros_like(nw_max_pa1e1b1nwzida0e0b0xyg1)
    d_nw_max_pa1e1b1nwzida0e0b0xyg1[0:-1, ...] = (nw_max_pa1e1b1nwzida0e0b0xyg1[1:, ...] - nw_max_pa1e1b1nwzida0e0b0xyg1[0:-1, ...]) / np.maximum(1,days_period_pa1e1b1nwzida0e0b0xyg1[0:-1, ...]) #np max to stop div/0
    d_nw_max_pa1e1b1nwzida0e0b0xyg3 = np.zeros_like(nw_max_pa1e1b1nwzida0e0b0xyg3)
    d_nw_max_pa1e1b1nwzida0e0b0xyg3[0:-1, ...] = (nw_max_pa1e1b1nwzida0e0b0xyg3[1:, ...] - nw_max_pa1e1b1nwzida0e0b0xyg3[0:-1, ...]) / np.maximum(1,days_period_cut_pa1e1b1nwzida0e0b0xyg3[0:-1, ...]) #np max to stop div/0


    #########################
    # management calc       #
    #########################
    ##scan
    date_scan_pa1e1b1nwzida0e0b0xyg1 = date_joined2_pa1e1b1nwzida0e0b0xyg1 + join_cycles_ida0e0b0xyg1 * cf_dams[4, 0:1, :].astype('timedelta64[D]') + pinp.sheep['i_scan_day'][scan_pa1e1b1nwzida0e0b0xyg1].astype('timedelta64[D]')
    # retain_scan_b1nwzida0e0b0xyg = np.max(pinp.sheep['i_drysretained_scan'], np.min(1, nfoet_b1nwzida0e0b0xyg))
    # retain_birth_b1nwzida0e0b0xyg = np.max(pinp.sheep['i_drysretained_birth'], np.min(1, nyatf_b1nwzida0e0b0xyg))
    ##Expected stocking density
    density_pa1e1b1nwzida0e0b0xyg0 = density_pa1e1b1nwzida0e0b0xyg
    density_pa1e1b1nwzida0e0b0xyg1 = density_pa1e1b1nwzida0e0b0xyg * density_nwzida0e0b0xyg1
    density_pa1e1b1nwzida0e0b0xyg3 = density_pa1e1b1nwzida0e0b0xyg[mask_p_offs_p] * density_nwzida0e0b0xyg3
    ###convert density from active n to active w axis
    densityw_pa1e1b1nwzida0e0b0xyg0 = density_pa1e1b1nwzida0e0b0xyg0#^don't need following association until multiple n levels sire. np.take_along_axis(density_pa1e1b1nwzida0e0b0xyg0,a_n_pa1e1b1nwzida0e0b0xyg0,axis=n_pos)
    densityw_pa1e1b1nwzida0e0b0xyg1 = np.take_along_axis(density_pa1e1b1nwzida0e0b0xyg1,a_n_pa1e1b1nwzida0e0b0xyg1,axis=n_pos)
    densityw_pa1e1b1nwzida0e0b0xyg2 = densityw_pa1e1b1nwzida0e0b0xyg1  #yes this is meant to be the same as dams
    densityw_pa1e1b1nwzida0e0b0xyg3 = np.take_along_axis(density_pa1e1b1nwzida0e0b0xyg3,a_n_pa1e1b1nwzida0e0b0xyg3,axis=n_pos)



    #########################
    # period is ...         #
    #########################
    period_between_prejoinscan_pa1e1b1nwzida0e0b0xyg1 = sfun.f_period_is_('period_is_between', date_prejoin_pa1e1b1nwzida0e0b0xyg1, date_start_pa1e1b1nwzida0e0b0xyg, date_scan_pa1e1b1nwzida0e0b0xyg1, date_end_pa1e1b1nwzida0e0b0xyg)
    period_between_joinscan_pa1e1b1nwzida0e0b0xyg1 = sfun.f_period_is_('period_is_between', date_joined_pa1e1b1nwzida0e0b0xyg1, date_start_pa1e1b1nwzida0e0b0xyg, date_scan_pa1e1b1nwzida0e0b0xyg1, date_end_pa1e1b1nwzida0e0b0xyg)
    date_born2_pa1e1b1nwzida0e0b0xyg2 = date_born1st2_pa1e1b1nwzida0e0b0xyg2 + (index_e1b1nwzida0e0b0xyg + 0.5) * cf_yatf[4, 0:1,:].astype('timedelta64[D]')	 #increments at prejoining #times by 0.5 to get the average birth date for all lambs because ewes can be conceived anytime within joining cycle. e_index is to account for ewe cycles.
    period_between_scanbirth_pa1e1b1nwzida0e0b0xyg1 = sfun.f_period_is_('period_is_between', date_scan_pa1e1b1nwzida0e0b0xyg1, date_start_pa1e1b1nwzida0e0b0xyg, date_born2_pa1e1b1nwzida0e0b0xyg2, date_end_pa1e1b1nwzida0e0b0xyg) #use date born that increments at joining
    period_between_birthwean_pa1e1b1nwzida0e0b0xyg1 = sfun.f_period_is_('period_is_between', date_born_pa1e1b1nwzida0e0b0xyg2, date_start_pa1e1b1nwzida0e0b0xyg, date_weaned_pa1e1b1nwzida0e0b0xyg2, date_end_pa1e1b1nwzida0e0b0xyg)
    date_weaned2_pa1e1b1nwzida0e0b0xyg2 = date_born1st2_pa1e1b1nwzida0e0b0xyg2 + age_wean1st2_pa1e1b1nwzida0e0b0xyg2 #this needs to increment at prejoining for period between weaning and prejoining, so that it is false after prejoining and before weaning.
    period_between_weanprejoin_pa1e1b1nwzida0e0b0xyg1 = sfun.f_period_is_('period_is_between', date_weaned2_pa1e1b1nwzida0e0b0xyg2, date_start_pa1e1b1nwzida0e0b0xyg, date_prejoin_next_pa1e1b1nwzida0e0b0xyg1, date_end_pa1e1b1nwzida0e0b0xyg)
    period_is_scan_pa1e1b1nwzida0e0b0xyg1 = sfun.f_period_is_('period_is', date_scan_pa1e1b1nwzida0e0b0xyg1, date_start_pa1e1b1nwzida0e0b0xyg, date_end_p = date_end_pa1e1b1nwzida0e0b0xyg) #g2 date born is the equivalent of date lambed g1
    period_is_birth_pa1e1b1nwzida0e0b0xyg1 = sfun.f_period_is_('period_is', date_born_pa1e1b1nwzida0e0b0xyg2, date_start_pa1e1b1nwzida0e0b0xyg, date_end_p = date_end_pa1e1b1nwzida0e0b0xyg) #g2 date born is the equivalent of date lambed g1
    period_is_wean_pa1e1b1nwzida0e0b0xyg2 = sfun.f_period_is_('period_is', date_weaned_pa1e1b1nwzida0e0b0xyg2, date_start_pa1e1b1nwzida0e0b0xyg, date_end_p = date_end_pa1e1b1nwzida0e0b0xyg) #g2 date born is the equivalent of date lambed g1
    period_is_wean_pa1e1b1nwzida0e0b0xyg1 = period_is_wean_pa1e1b1nwzida0e0b0xyg2
    # prev_period_is_birth_pa1e1b1nwzida0e0b0xyg1 = np.roll(period_is_birth_pa1e1b1nwzida0e0b0xyg1,1,axis=p_pos)
    period_is_mating_pa1e1b1nwzida0e0b0xyg1 = sfun.f_period_is_('period_is', date_mated_pa1e1b1nwzida0e0b0xyg1, date_start_pa1e1b1nwzida0e0b0xyg, date_end_p = date_end_pa1e1b1nwzida0e0b0xyg) #g2 date born is the equivalent of date lambed g1
    period_between_birth6wks_pa1e1b1nwzida0e0b0xyg1 = sfun.f_period_is_('period_is_between', date_born_pa1e1b1nwzida0e0b0xyg2, date_start_pa1e1b1nwzida0e0b0xyg, date_born_pa1e1b1nwzida0e0b0xyg2+np.array([(6*7)]).astype('timedelta64[D]'), date_end_pa1e1b1nwzida0e0b0xyg) #This is within 6 weeks of the Birth period
    ##start of fvp0 for both offs and dams the production is clustered -
    period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1 =  np.logical_and(fvp_type_pa1e1b1nwzida0e0b0xyg1 == 0, np.roll(fvp_type_pa1e1b1nwzida0e0b0xyg1,1, axis=0)!=0)  #is this sim period the first period in type 0 of fvp's
    period_is_startfvp0_pa1e1b1nwzida0e0b0xyg3 =  np.logical_and(fvp_type_pa1e1b1nwzida0e0b0xyg3 == 0, np.roll(fvp_type_pa1e1b1nwzida0e0b0xyg3,1, axis=0)!=0)  #is this sim period the first period in type 0 of fvp's
    ###shearing
    period_is_shearing_pa1e1b1nwzida0e0b0xyg0 = sfun.f_period_is_('period_is', date_shear_pa1e1b1nwzida0e0b0xyg0, date_start_pa1e1b1nwzida0e0b0xyg, date_end_p = date_end_pa1e1b1nwzida0e0b0xyg)
    period_is_shearing_pa1e1b1nwzida0e0b0xyg1 = sfun.f_period_is_('period_is', date_shear_pa1e1b1nwzida0e0b0xyg1, date_start_pa1e1b1nwzida0e0b0xyg, date_end_p = date_end_pa1e1b1nwzida0e0b0xyg)
    period_is_shearing_pa1e1b1nwzida0e0b0xyg3 = sfun.f_period_is_('period_is', date_shear_pa1e1b1nwzida0e0b0xyg3, date_start_pa1e1b1nwzida0e0b0xyg3, date_end_p = date_end_pa1e1b1nwzida0e0b0xyg3)
    period_is_startseason_pa1e1b1nwzida0e0b0xyg = sfun.f_period_is_('period_is', date_prev_seasonstart_pa1e1b1nwzida0e0b0xyg, date_start_pa1e1b1nwzida0e0b0xyg, date_end_p = date_end_pa1e1b1nwzida0e0b0xyg)
    period_is_prejoin_pa1e1b1nwzida0e0b0xyg1 = sfun.f_period_is_('period_is', date_prejoin_pa1e1b1nwzida0e0b0xyg1, date_start_pa1e1b1nwzida0e0b0xyg, date_end_p = date_end_pa1e1b1nwzida0e0b0xyg) #g2 date born is the equivalent of date lambed g1
    period_is_join_pa1e1b1nwzida0e0b0xyg1 = sfun.f_period_is_('period_is', date_joined_pa1e1b1nwzida0e0b0xyg1, date_start_pa1e1b1nwzida0e0b0xyg, date_end_p = date_end_pa1e1b1nwzida0e0b0xyg) #g2 date born is the equivalent of date lambed g1
    # period_is_startfvp_pa1e1b1nwzida0e0b0xyg1 = sfun.f_period_is_('period_is', fvp_date_start_pa1e1b1nwzida0e0b0xyg1, date_start_pa1e1b1nwzida0e0b0xyg, date_end_p = date_end_pa1e1b1nwzida0e0b0xyg)
    # period_is_startfvp_pa1e1b1nwzida0e0b0xyg3 = sfun.f_period_is_('period_is', fvp_date_start_pa1e1b1nwzida0e0b0xyg3, date_start_pa1e1b1nwzida0e0b0xyg3, date_end_p = date_end_pa1e1b1nwzida0e0b0xyg)
    # period_is_startfvp_pa1e1b1nwzida0e0b0xyg1 =  fvp_type_pa1e1b1nwzida0e0b0xyg1 != np.roll(fvp_type_pa1e1b1nwzida0e0b0xyg1,1, axis=0)  #all periods except the first will be the same type is the array is rolled once   #old method

    ##This is the end of the Mating period. (no active e axis - end of mating inclusive of all e slices)
    period_is_matingend_pa1e1b1nwzida0e0b0xyg1 = np.any(np.logical_and(period_is_mating_pa1e1b1nwzida0e0b0xyg1, index_e1b1nwzida0e0b0xyg == np.max(pinp.sheep['i_join_cycles_ig1']) - 1), axis=e1_pos,keepdims=True)




    ############################
    ### feed supply calcs      # ^need to add something about break of season..? and need to add e variation
    ############################
    ##1)	Compile the standard pattern from the inputs
    ###sire
    t_feedsupply_pj0zida0e0b0xyg0 = np.moveaxis(np.moveaxis(feedoptions_r1j0p[a_r_zida0e0b0xyg0],-1,0),-1,1) #had to rollaxis twice once for p and once for j0 (couldn't find a way to do both at the same time)
    t_feedsupply_pa1e1b1j0wzida0e0b0xyg0 = fun.f_reshape_expand(t_feedsupply_pj0zida0e0b0xyg0, left_pos=n_pos, right_pos=z_pos, left_pos2=p_pos,right_pos2=n_pos) #add  a1,e1,b1,w axis. Note n and j are the same thing (as far a position goes)

    ###dams
    t_feedsupply_pj0zida0e0b0xyg1 = np.moveaxis(np.moveaxis(feedoptions_r1j0p[a_r_zida0e0b0xyg1],-1,0),-1,1) #had to rollaxis twice once for p and once for j0 (couldn't find a way to do both at the same time)
    t_feedsupply_pa1e1b1j0wzida0e0b0xyg1 = fun.f_reshape_expand(t_feedsupply_pj0zida0e0b0xyg1, left_pos=n_pos, right_pos=z_pos, left_pos2=p_pos,right_pos2=n_pos) #add  a1,e1,b1,w axis. Note n and j are the same thing (as far a position goes)

    ###offs
    t_feedsupply_pj0zida0e0b0xyg3 = np.moveaxis(np.moveaxis(feedoptions_r1j0p[a_r_zida0e0b0xyg3],-1,0),-1,1) #had to rollaxis twice once for p and once for j0 (couldn't find a way to do both at the same time)
    t_feedsupply_pa1e1b1j0wzida0e0b0xyg3 = fun.f_reshape_expand(t_feedsupply_pj0zida0e0b0xyg3, left_pos=n_pos, right_pos=z_pos, left_pos2=p_pos,right_pos2=n_pos, condition=mask_p_offs_p, axis=0) #add  a1,e1,b1,w axis. Note n and j are the same thing (as far a position goes), mask p axis for offs

    ##2) calculate the feedsupply variation for each sheep class
    t_fs_ageweaned_pk0k1k2j0wzida0e0b0xyg1 = np.rollaxis(feedoptions_var_r2p[a_r2_k0e1b1nwzida0e0b0xyg1],-1,0)
    t_fs_cycle_pk0k1k2j0wzida0e0b0xyg1 = np.expand_dims(np.rollaxis(feedoptions_var_r2p[a_r2_k1b1nwzida0e0b0xyg1],-1,0), axis = tuple(range(p_pos+1,e1_pos))) #add k0
    t_fs_lsln_pk0k1k2j0wzida0e0b0xyg1 = np.expand_dims(np.rollaxis(feedoptions_var_r2p[a_r2_k2nwzida0e0b0xyg1],-1,0), axis = tuple(range(p_pos+1,b1_pos))) #add k0,k1
    t_fs_agedam_pa1e1b1j0wzik3a0e0b0xyg3 = np.expand_dims(np.rollaxis(feedoptions_var_r2p[a_r2_ik3a0e0b0xyg3],-1,0), axis = tuple(range(p_pos+1,i_pos))) #add from i to p
    t_fs_ageweaned_pa1e1b1j0wzidk0e0b0xyg3 = np.expand_dims(np.rollaxis(feedoptions_var_r2p[a_r2_idk0e0b0xyg3],-1,0), axis = tuple(range(p_pos+1,i_pos))) #add from i to p
    t_fs_btrt_a1e1b1j0wzida0e0k4xyg3 = np.expand_dims(np.rollaxis(feedoptions_var_r2p[a_r2_ida0e0k4xyg3],-1,0), axis = tuple(range(p_pos+1,i_pos))) #add from i to p
    t_fs_gender_pa1e1b1j0wzida0e0b0k5yg3 = np.expand_dims(np.rollaxis(feedoptions_var_r2p[a_r2_ida0e0b0k5yg3],-1,0), axis = tuple(range(p_pos+1,i_pos))) #add from i to p


    ##3)Based on the animal management selected (scan, gbal and wean) and whether the animals are differentially managed in this trial
    ###a) weaning age variation
    a_k0_pa1e1b1nwzida0e0b0xyg1 = period_between_weanprejoin_pa1e1b1nwzida0e0b0xyg1 * pinp.sheep['i_dam_wean_diffman'] * fun.f_reshape_expand(np.arange(len_a1)+1, a1_pos) #len_a+1 because that is the association between k0 and a1
    t_fs_ageweaned_pa1e1b1j0wzida0e0b0xyg1 = np.take_along_axis(t_fs_ageweaned_pk0k1k2j0wzida0e0b0xyg1, a_k0_pa1e1b1nwzida0e0b0xyg1, 1)

    ###b)b.	Dams Cluster k1 – oestrus cycle (e1): The association required is
    #^Have decided to drop this out of version 1. Will require multiple nutrition patterns in order to test value of scanning for foetal age

    ###c)Dams Cluster k2 – BTRT (b1)
    ####have to create a_t array so that it is maximum size of the arrays that are used it mask it. Then use broadcasting function to allow a smaller mask to be applied.
    shape = np.maximum.reduce([period_between_prejoinscan_pa1e1b1nwzida0e0b0xyg1.shape,period_between_scanbirth_pa1e1b1nwzida0e0b0xyg1.shape,period_between_birthwean_pa1e1b1nwzida0e0b0xyg1.shape]) #create shape which has the max size
    a_t_pa1e1b1nwzida0e0b0xyg1 = np.zeros(shape)
    period_between_prejoinscan_mask = np.broadcast_arrays(a_t_pa1e1b1nwzida0e0b0xyg1, period_between_prejoinscan_pa1e1b1nwzida0e0b0xyg1)[1] #mask must be manually broadcasted then applied - for some reason numpy doesnt automatically broadcast them.
    period_between_scanbirth_mask = np.broadcast_arrays(a_t_pa1e1b1nwzida0e0b0xyg1, period_between_scanbirth_pa1e1b1nwzida0e0b0xyg1)[1]
    period_between_birthwean_mask = np.broadcast_arrays(a_t_pa1e1b1nwzida0e0b0xyg1, period_between_birthwean_pa1e1b1nwzida0e0b0xyg1)[1]
    ####order matters because post wean does not have a cap ie it is over written by others
    a_t_pa1e1b1nwzida0e0b0xyg1[...] = 3 #t = 0 is prescan, 1 is postscan, 2 is lactation, 3 not used in V1 but would be is post wean
    a_t_pa1e1b1nwzida0e0b0xyg1[period_between_prejoinscan_mask] = 0 #t = 0 is prescan, 1 is postscan, 2 is lactation, 3 is not used in V1 but would be post wean
    a_t_pa1e1b1nwzida0e0b0xyg1[period_between_scanbirth_mask] = 1 #t = 0 is prescan, 1 is postscan, 2 is lactation, 3 is not used in V1 but would be post wean
    a_t_pa1e1b1nwzida0e0b0xyg1[period_between_birthwean_mask] = 2 #t = 0 is prescan, 1 is postscan, 2 is lactation, 3 is not used in V1 but would be post wean

    # a_t_pa1e1b1nwzida0e0b0xyg1[period_is_postscan_pa1e1b1nwzida0e0b0xyg1] = 1 #t = 0 is prescan, 1 is postscan, 2 is lactation, 3 is post wean
    # a_t_pa1e1b1nwzida0e0b0xyg1[period_is_postlactation_pa1e1b1nwzida0e0b0xyg1] = 2 #t = 0 is prescan, 1 is postscan, 2 is lactation, 3 is post wean
    # a_t_pa1e1b1nwzida0e0b0xyg1[period_is_postwean_pa1e1b1nwzida0e0b0xyg1] = 3 #t = 0 is prescan, 1 is postscan, 2 is lactation, 3 is post wean
    # a_t_pa1e1b1nwzida0e0b0xyg1[period_is_prescan_pa1e1b1nwzida0e0b0xyg1] = 0 #t = 0 is prescan, 1 is postscan, 2 is lactation, 3 is post wean


    ####dams management in each period
    scan_pa1e1b1nwzida0e0b0xyg1 = (scan_pa1e1b1nwzida0e0b0xyg1) * (a_t_pa1e1b1nwzida0e0b0xyg1 >= 1) * pinp.sheep['i_dam_lsln_diffman_t'][1]
    gbal_pa1e1b1nwzida0e0b0xyg1 = (gbal_pa1e1b1nwzida0e0b0xyg1 -1 ) * (a_t_pa1e1b1nwzida0e0b0xyg1 >= 2) * pinp.sheep['i_dam_lsln_diffman_t'][2] + 1  #minus 1 then plus 1 ensures that the wean option before lactation is 1
    wean_pa1e1b1nwzida0e0b0xyg1 = (wean_pa1e1b1nwzida0e0b0xyg1 -1 ) * (a_t_pa1e1b1nwzida0e0b0xyg1 >= 3) * pinp.sheep['i_dam_lsln_diffman_t'][3] + 1  #minus 1 then plus 1 ensures that the wean option before weaning is 1
    ####a_k2_mlsb1 states the feed variation slice for different management. In this step we slice a_k2_mlsb1 for the selected management in each period.
    a_k2_pa1e1b1nwzida0e0b0xyg1 = np.rollaxis(a_k2_mlsb1[wean_pa1e1b1nwzida0e0b0xyg1[:,:,:,0,...], gbal_pa1e1b1nwzida0e0b0xyg1[:,:,:,0,...], scan_pa1e1b1nwzida0e0b0xyg1[:,:,:,0,...], ...],-1,3) #remove the singleton b1 axis from the association arrays because a populated b1 axis comes from a_k2_mlsb1
    ####select feed variation pattern
    t_fs_lsln_pa1e1b1j0wzida0e0b0xyg1 = np.take_along_axis(t_fs_lsln_pk0k1k2j0wzida0e0b0xyg1, a_k2_pa1e1b1nwzida0e0b0xyg1, b1_pos)

    ###d) ^come back to offs (remember gender needs to be masked)
    # t_fs_agedam_pj0zida0e0b0xg3 = t_fs_agedam_pj0zik3k0k4k5g3
    # t_fs_ageweaned_pj0zida0e0b0xg3 = t_fs_ageweaned_pj0zik3k0k4k5g3
    # t_fs_btrt_pj0zida0e0b0xg3 = t_fs_btrt_pj0zik3k0k4k5g3
    # t_fs_gender_pj0zida0e0b0xg3 = t_fs_gender_pj0zik3k0k4k5g3

    ##4) add variation to std pattern
    t_feedsupply_pa1e1b1j0wzida0e0b0xyg1 = (t_feedsupply_pa1e1b1j0wzida0e0b0xyg1 + t_fs_ageweaned_pa1e1b1j0wzida0e0b0xyg1 + t_fs_lsln_pa1e1b1j0wzida0e0b0xyg1) #cant use += for some reason



    ##6)Convert the ‘j0’ axis to an ‘n’ axis
    ###a- create a ‘j0’ by ‘n’ array that is the multipliers that weight each ‘j0’ for that level of ‘n’
    nut_mult_g0_j0n = np.empty((3,uinp.structure['i_nut_spread_n0'].shape[0]))
    nut_mult_g0_j0n[0, ...] = 1 - np.abs(uinp.structure['i_nut_spread_n0'])
    nut_mult_g0_j0n[1, ...] = 1-(1 - np.abs(np.minimum(0, uinp.structure['i_nut_spread_n0'])))
    nut_mult_g0_j0n[2, ...] = 1-(1 - np.maximum(0, uinp.structure['i_nut_spread_n0']))
    nut_mult_g1_j0n = np.empty((3,uinp.structure['i_nut_spread_n1'].shape[0]))
    nut_mult_g1_j0n[0, ...] = 1 - np.abs(uinp.structure['i_nut_spread_n1'])
    nut_mult_g1_j0n[1, ...] = 1-(1 - np.abs(np.minimum(0, uinp.structure['i_nut_spread_n1'])))
    nut_mult_g1_j0n[2, ...] = 1-(1 - np.maximum(0, uinp.structure['i_nut_spread_n1']))
    nut_mult_g3_j0n = np.empty((3,uinp.structure['i_nut_spread_n3'].shape[0]))
    nut_mult_g3_j0n[0, ...] = 1 - np.abs(uinp.structure['i_nut_spread_n3'])
    nut_mult_g3_j0n[1, ...] = 1-(1 - np.abs(np.minimum(0, uinp.structure['i_nut_spread_n3'])))
    nut_mult_g3_j0n[2, ...] = 1-(1 - np.maximum(0, uinp.structure['i_nut_spread_n3']))

    ###b- create add array if there is a confinement or feedlot pattern (i_nut_spread_n >=3)
    nut_spread_g0_n = uinp.structure['i_nut_spread_n0']
    nut_add_g0_n = np.zeros_like(nut_spread_g0_n)
    nut_add_g0_n[nut_spread_g0_n >=3] = nut_spread_g0_n[nut_spread_g0_n >=3]
    nut_mult_g0_j0n[:,nut_spread_g0_n >=3] = 0 #if nut_add exists then nut_mult=0

    nut_spread_g1_n = uinp.structure['i_nut_spread_n1']
    nut_add_g1_n = np.zeros_like(nut_spread_g1_n)
    nut_add_g1_n[nut_spread_g1_n >=3] = nut_spread_g1_n[nut_spread_g1_n >=3]
    nut_mult_g1_j0n[:,nut_spread_g1_n >=3] = 0 #if nut_add exists then nut_mult=0

    nut_spread_g3_n = uinp.structure['i_nut_spread_n3']
    nut_add_g3_n = np.zeros_like(nut_spread_g3_n)
    nut_add_g3_n[nut_spread_g3_n >=3] = nut_spread_g3_n[nut_spread_g3_n >=3]
    nut_mult_g3_j0n[:,nut_spread_g3_n >=3] = 0 #if nut_add exists then nut_mult=0

    ###c - feedsupply_std with n axis (instead of j axis).
    nut_mult_g0_pk0k1k2j0nwzida0e0b0xyg = np.expand_dims(nut_mult_g0_j0n[na,na,na,na,...], axis = tuple(range(n_pos+1,0))) #expand axis to line up with feedsupply, add axis from g to n and j0 to p
    nut_add_g0_pk0k1k2nwzida0e0b0xyg = np.expand_dims(nut_add_g0_n, axis = (tuple(range(p_pos,n_pos)) + tuple(range(n_pos+1,0)))) #add axis from p to n and n to g
    t_feedsupply_pa1e1b1j0nwzida0e0b0xyg0 = np.expand_dims(t_feedsupply_pa1e1b1j0wzida0e0b0xyg0, axis = n_pos) #add n axis
    feedsupply_std_pa1e1b1nwzida0e0b0xyg0 = np.sum(t_feedsupply_pa1e1b1j0nwzida0e0b0xyg0 * nut_mult_g0_pk0k1k2j0nwzida0e0b0xyg, axis = n_pos-1 ) + nut_add_g0_pk0k1k2nwzida0e0b0xyg #minus 1 because n axis was added therefore shifting j0 position (it was originally in the same place). Sum across j0 axis and leave just the n axis

    nut_mult_g1_pk0k1k2j0nwzida0e0b0xyg = np.expand_dims(nut_mult_g1_j0n[na,na,na,na,...], axis = tuple(range(n_pos+1,0))) #expand axis to line up with feedsupply, add axis from g to n and j0 to p
    nut_add_g1_pk0k1k2nwzida0e0b0xyg = np.expand_dims(nut_add_g1_n, axis = (tuple(range(p_pos,n_pos)) + tuple(range(n_pos+1,0)))) #add axis from p to n and n to g
    t_feedsupply_pa1e1b1j0nwzida0e0b0xyg1 = np.expand_dims(t_feedsupply_pa1e1b1j0wzida0e0b0xyg1, axis = n_pos) #add n axis
    feedsupply_std_pa1e1b1nwzida0e0b0xyg1 = np.sum(t_feedsupply_pa1e1b1j0nwzida0e0b0xyg1 * nut_mult_g1_pk0k1k2j0nwzida0e0b0xyg, axis = n_pos-1 ) + nut_add_g1_pk0k1k2nwzida0e0b0xyg #minus 1 because n axis was added therefore shifting j0 position (it was originally in the same place). Sum across j0 axis and leave just the n axis

    nut_mult_g3_pk0k1k2j0nwzida0e0b0xyg = np.expand_dims(nut_mult_g3_j0n[na,na,na,na,...], axis = tuple(range(n_pos+1,0))) #expand axis to line up with feedsupply, add axis from g to n and j0 to p
    nut_add_g3_pk0k1k2nwzida0e0b0xyg = np.expand_dims(nut_add_g3_n, axis = (tuple(range(p_pos,n_pos)) + tuple(range(n_pos+1,0)))) #add axis from p to n and n to g
    t_feedsupply_pa1e1b1j0nwzida0e0b0xyg3 = np.expand_dims(t_feedsupply_pa1e1b1j0wzida0e0b0xyg3, axis = n_pos) #add n axis
    feedsupply_std_pa1e1b1nwzida0e0b0xyg3 = np.sum(t_feedsupply_pa1e1b1j0nwzida0e0b0xyg3 * nut_mult_g3_pk0k1k2j0nwzida0e0b0xyg, axis = n_pos-1 ) + nut_add_g3_pk0k1k2nwzida0e0b0xyg #minus 1 because n axis was added therefore shifting j0 position (it was originally in the same place). Sum across j0 axis and leave just the n axis

    ##7)Ensure that no feed supplies are outside the range 0 to 4
    feedsupply_std_pa1e1b1nwzida0e0b0xyg0 = np.maximum(0, feedsupply_std_pa1e1b1nwzida0e0b0xyg0)
    feedsupply_std_pa1e1b1nwzida0e0b0xyg0 = np.minimum(4, feedsupply_std_pa1e1b1nwzida0e0b0xyg0)
    feedsupply_std_pa1e1b1nwzida0e0b0xyg1 = np.maximum(0, feedsupply_std_pa1e1b1nwzida0e0b0xyg1)
    feedsupply_std_pa1e1b1nwzida0e0b0xyg1 = np.minimum(4, feedsupply_std_pa1e1b1nwzida0e0b0xyg1)
    feedsupply_std_pa1e1b1nwzida0e0b0xyg3 = np.maximum(0, feedsupply_std_pa1e1b1nwzida0e0b0xyg3)
    feedsupply_std_pa1e1b1nwzida0e0b0xyg3 = np.minimum(4, feedsupply_std_pa1e1b1nwzida0e0b0xyg3)


    #####################################
    ##expand feedsupply for all w slices#  see google doc for more info
    #####################################
    ###appply association - give feedsupply singleton n axis and 81 slices in w axis
    feedsupplyw_pa1e1b1nwzida0e0b0xyg0 = feedsupply_std_pa1e1b1nwzida0e0b0xyg0 #^only one n slice so doesnt need following code yet: np.take_along_axis(feedsupply_std_pa1e1b1nwzida0e0b0xyg0,a_n_pa1e1b1nwzida0e0b0xyg0,axis=n_pos)
    feedsupplyw_pa1e1b1nwzida0e0b0xyg1 = np.take_along_axis(feedsupply_std_pa1e1b1nwzida0e0b0xyg1,a_n_pa1e1b1nwzida0e0b0xyg1,axis=n_pos)
    feedsupplyw_pa1e1b1nwzida0e0b0xyg3 = np.take_along_axis(feedsupply_std_pa1e1b1nwzida0e0b0xyg3,a_n_pa1e1b1nwzida0e0b0xyg3,axis=n_pos)



    ##Start the LTW loop here so that the arrays are reinitialised from the inputs
    ### set the LTW adjustments to zero for the first loop. Sires do not have a LTW adjust because they are born off farm
    sfw_ltwadj_g0 = 1
    sfd_ltwadj_g0 = 0
    sfw_ltwadj_pa1e1b1nwzida0e0b0xyg1 = np.ones(pg1)
    sfd_ltwadj_pa1e1b1nwzida0e0b0xyg1 = np.zeros(pg1)
    sfw_ltwadj_g2 = 1
    sfd_ltwadj_g2 = 0
    sfw_ltwadj_a1e1b1nwzida0e0b0xyg3 = np.ones(pg3)[0, ...]  # slice the p axis to remove
    sfd_ltwadj_a1e1b1nwzida0e0b0xyg3 = np.zeros(pg3)[0, ...]  # slice the p axis to remove

    for loop_ltw in range(2):

        ####################################
        ### initialise arrays for sim loop  # axis names not always track from now on because they change between p=0 and p=1
        ####################################

        ##all groups
        eqn_compare = uinp.sheep['i_eqn_compare']
        ##sire
        ffcfw_start_sire = lw_initial_wzida0e0b0xyg0 - cfw_initial_wzida0e0b0xyg0 / cw_sire[3, ...]
        ffcfw_max_start_sire = ffcfw_start_sire
        omer_history_start_m3g0[...] = np.nan
        d_cfw_history_start_m2g0[...] = np.nan
        cfw_start_sire = cfw_initial_wzida0e0b0xyg0
        fd_start_sire = fd_initial_wzida0e0b0xyg0
        fl_start_sire = fl_initial_wzida0e0b0xyg0
        fd_min_start_sire = fd_initial_wzida0e0b0xyg0
        aw_start_sire = aw_initial_wzida0e0b0xyg0
        mw_start_sire = mw_initial_wzida0e0b0xyg0
        bw_start_sire = bw_initial_wzida0e0b0xyg0
        nw_start_sire = 0 #no dimensions to start
        temp_lc_sire = np.array([0]) #this is calculated in the chill function but it is required for the intake function so it is set to 0 for the first period.
        numbers_start_sire = numbers_initial_zida0e0b0xyg0
        numbers_start_fvp0_sire = numbers_initial_zida0e0b0xyg0 #just need a default because this is processed using update function.
        # ebg_start_sire=0

        ##dams
        t_numbers_start_prejoin = 0
        numbers_join_dams = 0
        ldr_start_dams = np.array([1.0])
        lb_start_dams = np.array([1.0])
        w_f_start_dams = np.array([0.0])
        nw_f_start_dams = np.array([0.0])
        nec_cum_start_dams = np.array([0.0])
        cf_w_b_start_dams = np.array([0.0])
        cfw_ltwadj_start_dams = np.array([0.0])
        cf_cfwltw_start_dams = np.array([0.0])
        fd_ltwadj_start_dams = np.array([0.0])
        cf_fdltw_start_dams = np.array([0.0])
        cf_w_w_start_dams = np.array([0.0])
        cf_w_w_dams = 0 #this is required as default when mu wean function is not being called (it is required in the start production function)
        cf_conception_start_dams = np.array([0.0])
        conception_dams = 0.0 #initialise so it can be added to (conception += conception)
        guw_start_dams = np.array([0.0])
        rc_birth_start_dams = np.array([1.0])
        ffcfw_start_dams = fun.f_reshape_expand(lw_initial_wzida0e0b0xyg1 - cfw_initial_wzida0e0b0xyg1 / cw_dams[3, ...], p_pos, right_pos=w_pos) #add axis w to a1 because e and b axis are sliced before they are added via calculation
        ffcfw_max_start_dams = ffcfw_start_dams
        ffcfw_mating_dams = 0.0
        # ffcfw_birth_dams = 0.0
        # ffcfw_weaning_dams = 0.0
        omer_history_start_m3g1[...] = np.nan
        d_cfw_history_start_m2g1[...] = np.nan
        cfw_start_dams = cfw_initial_wzida0e0b0xyg1
        fd_start_dams = fd_initial_wzida0e0b0xyg1
        fl_start_dams = fl_initial_wzida0e0b0xyg1
        fd_min_start_dams = fd_initial_wzida0e0b0xyg1
        aw_start_dams = aw_initial_wzida0e0b0xyg1
        mw_start_dams = mw_initial_wzida0e0b0xyg1
        bw_start_dams = bw_initial_wzida0e0b0xyg1
        nw_start_dams = np.array([0.0])
        temp_lc_dams = np.array([0.0]) #this is calculated in the chill function but it is required for the intake function so it is set to 0 for the first period.
        numbers_start_dams = numbers_initial_a1e1b1nwzida0e0b0xyg1
        numbers_start_fvp0_dams = numbers_initial_a1e1b1nwzida0e0b0xyg1 #just need a default because this is processed using update function.
        scanning = 0 #variable is used only for reporting
        # ebg_start_dams=0

        ##yatf
        omer_history_start_m3g2[...] = np.nan
        d_cfw_history_start_m2g2[...] = np.nan
        nw_start_yatf = 0.0
        rc_start_yatf = 0.0
        ffcfw_start_yatf = w_b_std_y_b1nwzida0e0b0xyg1 #this is just an estimate, it is updated with the real weight at birth - needed to calc milk production in birth period because milk prod is calculated before yatf weight is updated)
        ffcfw_max_start_yatf = ffcfw_start_yatf
        mortality_birth_yatf=0.0 #required for dam numbers before progeny born
        cfw_start_yatf = 0.0
        temp_lc_yatf = np.array([0.0]) #this is calculated in the chill function but it is required for the intake function so it is set to 0 for the first period.
        numbers_start_yatf = 0.0
        numbers_start_fvp0_yatf = 0.0 #just need a default because this is processed using update function.
        numbers_end_yatf = 0.0 #need a default because this is required in f_start[p+1] prior to being assigned.
        # ebg_start_yatf=0
        ebg_yatf = 0.0 #need a default because used in call to WWt of yatf
        fl_start_yatf=fl_birth_yg2 #cant use fl_initial because that is at weaning
        fd_start_yatf=0.0
        fd_min_start_yatf = 1000.0
        w_b_start_yatf = 0.0
        w_b_ltw_std_yatf = 0.0
        w_w_start_yatf = 0.0
        w_w_yatf = 0.0
        foo_lact_ave_start = 0.0
        foo_lact_ave = 0.0
        aw_start_yatf = 0.0
        bw_start_yatf = 0.0
        mw_start_yatf = 0.0

        ##offs
        ffcfw_start_offs = lw_initial_wzida0e0b0xyg3 - cfw_initial_wzida0e0b0xyg3 / cw_offs[3, ...]
        ffcfw_max_start_offs = ffcfw_start_offs
        omer_history_start_m3g3[...] = np.nan
        d_cfw_history_start_m2g3[...] = np.nan
        cfw_start_offs = cfw_initial_wzida0e0b0xyg3
        fd_start_offs = fd_initial_wzida0e0b0xyg3
        fl_start_offs = fl_initial_wzida0e0b0xyg3
        fd_min_start_offs = fd_initial_wzida0e0b0xyg3
        aw_start_offs = aw_initial_wzida0e0b0xyg3
        mw_start_offs = mw_initial_wzida0e0b0xyg3
        bw_start_offs = bw_initial_wzida0e0b0xyg3
        nw_start_offs = 0.0
        temp_lc_offs = np.array([0.0]) #this is calculated in the chill function but it is required for the intake function so it is set to 0 for the first period.
        numbers_start_offs = numbers_initial_zida0e0b0xyg3
        numbers_start_fvp0_offs = numbers_initial_zida0e0b0xyg3 #just need a default because this is processed using update function.
        # ebg_start_offs=0


        ######################
        ### sim engine       #
        ######################

        ## Loop through each week of the simulation (p) for ewes
        for p in range(n_sim_periods-1):   #-1 because assigns to [p+1] for start values
            # print(p)
            # if np.any(period_is_birth_pa1e1b1nwzida0e0b0xyg1[p]):
            #     print("period is lactation: ", period_is_birth_pa1e1b1nwzida0e0b0xyg1[p])
            # if np.any(period_is_wean_pa1e1b1nwzida0e0b0xyg1[p]):
            #     print("period is weaning: ", period_is_wean_pa1e1b1nwzida0e0b0xyg1[p])
            # if np.any(period_is_mating_pa1e1b1nwzida0e0b0xyg1[p]):
            #     print("period is gest: ", period_is_mating_pa1e1b1nwzida0e0b0xyg1[p])
            # if np.any(period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p]):
            #     print("period is fvp0 dams: ", period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p])
            # if np.any(period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p]):
            #     print("period is fvp0 offs: ", period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p])



            ###################################################################################
            #reset variables if period is beginning of a reproduction cycle or shearing cycle #
            ###################################################################################
            ##sire
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg0[p,...] >0):
                ###cfw
                cfw_start_sire = fun.f_update(cfw_start_sire, 0, period_is_shearing_pa1e1b1nwzida0e0b0xyg0[p-1]) #reset if previous period is shearing (shearing occurs at the end of a period)
                ###fl
                fl_start_sire = fun.f_update(fl_start_sire, fl_shear_yg0, period_is_shearing_pa1e1b1nwzida0e0b0xyg0[p-1]) #reset if previous period is shearing (shearing occurs at the end of a period)
                ###min fd
                fd_min_start_sire = fun.f_update(fd_min_start_sire, 1000, period_is_shearing_pa1e1b1nwzida0e0b0xyg0[p-1]) #reset if previous period is shearing (shearing occurs at the end of a period)

            ##dams
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
            ##Reproduction
                ###Lagged DR (lactation deficit)
                ldr_start_dams = fun.f_update(ldr_start_dams, 1, period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p])
                ###Loss of potential milk due to consistent under production
                lb_start_dams = fun.f_update(lb_start_dams, 1, period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p])
                ###Weight of foetus (start)
                w_f_start_dams = fun.f_update(w_f_start_dams, 0, period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p])
                ###Weight of gravid uterus (start)
                guw_start_dams = fun.f_update(guw_start_dams, 0, period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p])
                ###Normal weight of foetus (start)
                nw_f_start_dams = fun.f_update(nw_f_start_dams, 0, period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p])
                ###Birth weight carryover (running tally of foetal weight diff)
                cf_w_b_start_dams = fun.f_update(cf_w_b_start_dams, 0, period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p])
                ###Weaning weight carryover (running tally of foetal weight diff)
                cf_w_w_start_dams = fun.f_update(cf_w_w_start_dams, 0, period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p])
                ###Carry forward conception
                cf_conception_start_dams = fun.f_update(cf_conception_start_dams, 0, period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p])
                ###LTW CFW adjustment carryover (running tally of LTW progeny CFW)
                cfw_ltwadj_start_dams = fun.f_update(cfw_ltwadj_start_dams, 0, period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p])
                cf_cfwltw_start_dams = fun.f_update(cf_cfwltw_start_dams, 0, period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p])
                ###LTW FD adjustment carryover (running tally of LTW progeny FD)
                fd_ltwadj_start_dams = fun.f_update(fd_ltwadj_start_dams, 0, period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p])
                cf_fdltw_start_dams = fun.f_update(cf_fdltw_start_dams, 0, period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p])

            ##Wool Production
                ###cfw
                cfw_start_dams = fun.f_update(cfw_start_dams, 0, period_is_shearing_pa1e1b1nwzida0e0b0xyg1[p-1]) #reset if previous period is shearing (shearing occurs at the end of a period)
                ###fl
                fl_start_dams = fun.f_update(fl_start_dams, fl_shear_yg1, period_is_shearing_pa1e1b1nwzida0e0b0xyg1[p-1]) #reset if previous period is shearing (shearing occurs at the end of a period)
                ###min fd
                fd_min_start_dams = fun.f_update(fd_min_start_dams, 1000, period_is_shearing_pa1e1b1nwzida0e0b0xyg1[p-1]) #reset if previous period is shearing (shearing occurs at the end of a period)

            ##offs
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg3[p,...] >0):
                ###cfw
                cfw_start_offs = fun.f_update(cfw_start_offs, 0, period_is_shearing_pa1e1b1nwzida0e0b0xyg3[p-1]) #reset if previous period is shearing (shearing occurs at the end of a period)
                ###fl
                fl_start_offs = fun.f_update(fl_start_offs, fl_shear_yg3, period_is_shearing_pa1e1b1nwzida0e0b0xyg3[p-1]) #reset if previous period is shearing (shearing occurs at the end of a period)
                ###min fd
                fd_min_start_offs = fun.f_update(fd_min_start_offs, 1000, period_is_shearing_pa1e1b1nwzida0e0b0xyg3[p-1]) #reset if previous period is shearing (shearing occurs at the end of a period)



            ###################
            ##dependent start #
            ###################
            ##note: yatf calculated later in the code
            ##sire
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg0[p, ...] > 0):
                ###GFW (start)
                gfw_start_sire = cfw_start_sire / cw_sire[3, ...]
                ###LW (start -with fleece & conceptus)
                lw_start_sire = ffcfw_start_sire + gfw_start_sire
                ###Normal weight (start)
                nw_start_sire = np.minimum(nw_max_pa1e1b1nwzida0e0b0xyg0[p], np.maximum(nw_start_sire, ffcfw_start_sire + cn_sire[3, ...] * (nw_max_pa1e1b1nwzida0e0b0xyg0[p]  - ffcfw_start_sire)))
                ###Relative condition (start)
                rc_start_sire = ffcfw_start_sire / nw_start_sire
                ##Condition score at  start of p
                cs_start_sire = sfun.f_condition_score(rc_start_sire, cu0_sire)
                ###staple length
                sl_start_sire = fl_start_sire * cw_sire[15,...]
                ###Relative size (start) - dams & sires
                relsize_start_sire = np.minimum(1, nw_start_sire / srw_xyg0)
                ###Relative size for LWG (start). Capped by current LW
                relsize1_start_sire = np.minimum(ffcfw_max_start_sire, nw_max_pa1e1b1nwzida0e0b0xyg0[p]) / srw_xyg0
                ###PI Size factor (for cattle)
                zf_sire = np.maximum(1, 1 + cr_sire[7, ...] - relsize_start_sire)
                ###EVG Size factor (decreases steadily - some uncertainty about the sign on cg[4])
                z1f_sire = 1 / (1 + np.exp(+cg_sire[4, ...] * (relsize1_start_sire - cg_sire[5, ...])))
                ###EVG Size factor (increases at maturity)
                z2f_sire = np.clip((relsize1_start_sire - cg_sire[6, ...]) / (cg_sire[7, ...] - cg_sire[6, ...]), 0 ,1)

            ##dams
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p, ...] > 0):
                ###GFW (start)
                gfw_start_dams = cfw_start_dams / cw_dams[3, ...]
                ###LW (start -with fleece & conceptus)
                lw_start_dams = ffcfw_start_dams + guw_start_dams + gfw_start_dams
                ###Normal weight (start)
                nw_start_dams = np.minimum(nw_max_pa1e1b1nwzida0e0b0xyg1[p], np.maximum(nw_start_dams, ffcfw_start_dams + cn_dams[3, ...] * (nw_max_pa1e1b1nwzida0e0b0xyg1[p]  - ffcfw_start_dams)))
                ###Relative condition (start)
                rc_start_dams = ffcfw_start_dams / nw_start_dams
                ##Condition score of the dam at  start of p
                cs_start_dams = sfun.f_condition_score(rc_start_dams, cu0_dams)
                ###Relative condition of dam at parturition - needs to be remembered between loops (milk production) - Loss of potential milk due to consistent under production
                rc_birth_dams = fun.f_update(rc_birth_start_dams, rc_start_dams, period_is_birth_pa1e1b1nwzida0e0b0xyg1[p])
                ###staple length
                sl_start_dams = fl_start_dams * cw_dams[15,...]
                ###Relative size (start) - dams & sires
                relsize_start_dams = np.minimum(1, nw_start_dams / srw_xyg1)
                ###Relative size for LWG (start). Capped by current LW
                relsize1_start_dams = np.minimum(ffcfw_max_start_dams, nw_max_pa1e1b1nwzida0e0b0xyg1[p]) / srw_xyg1
                ###PI Size factor (for cattle)
                zf_dams = np.maximum(1, 1 + cr_dams[7, ...] - relsize_start_dams)
                ###EVG Size factor (decreases steadily - some uncertainty about the sign on cg[4])
                z1f_dams = 1 / (1 + np.exp(+cg_dams[4, ...] * (relsize1_start_dams - cg_dams[5, ...])))
                ###EVG Size factor (increases at maturity)
                z2f_dams = np.clip((relsize1_start_dams - cg_dams[6, ...]) / (cg_dams[7, ...] - cg_dams[6, ...]), 0 ,1)
                ##sires for mating
                n_sire_a1e1b1nwzida0e0b0xyg1g0p8 = sfun.f_sire_req(sire_propn_pa1e1b1nwzida0e0b0xyg1g0[p], sire_periods_g0p8, pinp.sheep['i_sire_recovery'],
                                                                   pinp.sheep['i_startyear'], date_end_pa1e1b1nwzida0e0b0xyg[p], period_is_join_pa1e1b1nwzida0e0b0xyg1[p])


        ##offs
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg3[p, ...] > 0):
                ###GFW (start)
                gfw_start_offs = cfw_start_offs / cw_offs[3, ...]
                ###LW (start -with fleece & conceptus)
                lw_start_offs = ffcfw_start_offs + gfw_start_offs
                ###Normal weight (start)
                nw_start_offs = np.minimum(nw_max_pa1e1b1nwzida0e0b0xyg3[p], np.maximum(nw_start_offs, ffcfw_start_offs + cn_offs[3, ...] * (nw_max_pa1e1b1nwzida0e0b0xyg3[p]  - ffcfw_start_offs)))
                ###Relative condition (start)
                rc_start_offs = ffcfw_start_offs / nw_start_offs
                ##Condition score at  start of p
                cs_start_offs = sfun.f_condition_score(rc_start_offs, cu0_offs)
                ###staple length
                sl_start_offs = fl_start_offs * cw_offs[15,...]
                ###Relative size (start) - dams & sires
                relsize_start_offs = np.minimum(1, nw_start_offs / srw_xyg3)
                ###Relative size for LWG (start). Capped by current LW
                relsize1_start_offs = np.minimum(ffcfw_max_start_offs, nw_max_pa1e1b1nwzida0e0b0xyg3[p]) / srw_xyg3
                ###PI Size factor (for cattle)
                zf_offs = np.maximum(1, 1 + cr_offs[7, ...] - relsize_start_offs)
                ###EVG Size factor (decreases steadily - some uncertainty about the sign on cg[4])
                z1f_offs = 1 / (1 + np.exp(+cg_offs[4, ...] * (relsize1_start_offs - cg_offs[5, ...])))
                ###EVG Size factor (increases at maturity)
                z2f_offs = np.clip((relsize1_start_offs - cg_offs[6, ...]) / (cg_offs[7, ...] - cg_offs[6, ...]), 0 ,1)








            ##feed supply loop
            ##this loop is only required if a LW target is specified for the animals
            ##if there is a target then the loop needs to continue until
            ##the feed supply has converged on a value that generates a liveweight
            ##change close to the target
            ##The loop needs to execute at least once, then repeat if there
            ##is a target and the result is not close enough to the target

            ###initial info ^this will need to be hooked up with correct inputs, if they are the same for each period they don't need to be initialised below
            target_lwc = None
            epsilon = 0
            n_max_itn = uinp.structure['i_feedsupply_itn_max']
            attempts = 0 #initial

            for itn in range(n_max_itn):
                ##potential intake
                eqn_group = 4
                eqn_system = 0 # CSIRO = 0
                if uinp.sheep['i_eqn_exists_q0q1'][eqn_group, eqn_system]:  # proceed with call & assignment if this system exists for this group
                    ###sire
                    eqn_used = (eqn_used_g0_q1p[eqn_group, p] == eqn_system)
                    if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg0[p,...] >0):
                        temp0 = sfun.f_potential_intake_cs(ci_sire, cl_sire, srw_xyg0, relsize_start_sire, rc_start_sire, temp_lc_sire, temp_ave_pa1e1b1nwzida0e0b0xyg[p], temp_max_pa1e1b1nwzida0e0b0xyg[p]
                                                           , temp_min_pa1e1b1nwzida0e0b0xyg[p], rain_intake_pa1e1b1nwzida0e0b0xyg0[p])
                        if eqn_used:
                            pi_sire = temp0
                        if eqn_compare:
                            r_compare_q0q1q2psire[eqn_system, eqn_group, 0, p, ...] = temp0
                    ###dams
                    eqn_used = (eqn_used_g1_q1p[eqn_group, p] == eqn_system)
                    if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                        temp0 = sfun.f_potential_intake_cs(ci_dams, cl_dams, srw_xyg1, relsize_start_dams, rc_start_dams, temp_lc_dams, temp_ave_pa1e1b1nwzida0e0b0xyg[p], temp_max_pa1e1b1nwzida0e0b0xyg[p]
                                                          , temp_min_pa1e1b1nwzida0e0b0xyg[p], rain_intake_pa1e1b1nwzida0e0b0xyg1[p], rc_birth_start = rc_birth_dams, pi_age_y = pi_age_y_pa1e1b1nwzida0e0b0xyg1[p]
                                                          , lb_start = lb_start_dams)
                        if eqn_used:
                            pi_dams = temp0
                        if eqn_compare:
                            r_compare_q0q1q2pdams[eqn_system, eqn_group, 0, p, ...] = temp0
                    ###offs
                    eqn_used = (eqn_used_g3_q1p[eqn_group, p] == eqn_system)
                    if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg3[p,...] >0):
                        temp0 = sfun.f_potential_intake_cs(ci_offs, cl_offs, srw_xyg3, relsize_start_offs, rc_start_offs, temp_lc_offs, temp_ave_pa1e1b1nwzida0e0b0xyg[p], temp_max_pa1e1b1nwzida0e0b0xyg[p]
                                                            , temp_min_pa1e1b1nwzida0e0b0xyg[p], rain_intake_pa1e1b1nwzida0e0b0xyg3[p])
                        if eqn_used:
                            pi_offs = temp0
                        if eqn_compare:
                            r_compare_q0q1q2poffs[eqn_system, eqn_group, 0, p, ...] = temp0

                ###murdoch #todo function doesnt exist yet, add args when it is built
                eqn_system = 1 # mu = 1
                if uinp.sheep['i_eqn_exists_q0q1'][eqn_group, eqn_system]:  # proceed with call & assignment if this system exists for this group
                    ###sire
                    eqn_used = (eqn_used_g0_q1p[eqn_group, p] == eqn_system)
                    if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg0[p,...] >0):
                        temp0 = sfun.f_potential_intake_mu(srw_xyg0)
                        if eqn_used:
                            pi_sire = temp0
                        if eqn_compare:
                            r_compare_q0q1q2psire[eqn_system, eqn_group, 0, p, ...] = temp0
                    ###dams
                    eqn_used = (eqn_used_g1_q1p[eqn_group, p] == eqn_system)
                    if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                        temp0 = sfun.f_potential_intake_mu(srw_xyg1)
                        if eqn_used:
                            pi_dams = temp0
                        if eqn_compare:
                            r_compare_q0q1q2pdams[eqn_system, eqn_group, 0, p, ...] = temp0
                    ###offs
                    eqn_used = (eqn_used_g3_q1p[eqn_group, p] == eqn_system)
                    if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg3[p,...] >0):
                        temp0 = sfun.f_potential_intake_mu(srw_xyg3)
                        if eqn_used:
                            pi_offs = temp0
                        if eqn_compare:
                            r_compare_q0q1q2poffs[eqn_system, eqn_group, 0, p, ...] = temp0

                ##feedsupply - calculated after pi because pi required for intake_s
                if np.any(days_period_pa1e1b1nwzida0e0b0xyg0[p,...] >0):
                    foo_sire, hf_sire, dmd_sire, intake_s_sire, md_herb_sire = sfun.f_feedsupply(cu3, cu4, cr_sire, feedsupply_std_pa1e1b1nwzida0e0b0xyg0[p], paststd_foo_pa1e1b1j0wzida0e0b0xyg[p], paststd_dmd_pa1e1b1j0wzida0e0b0xyg[p], legume_pa1e1b1nwzida0e0b0xyg[p], pi_sire, pasture_stage_pa1e1b1j0wzida0e0b0xyg[p], pinp.sheep['i_hr_scalar'], pinp.sheep['i_region'], uinp.pastparameters['i_n_pasture_stage'], uinp.pastparameters['i_hd_std'])
                if np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                    foo_dams, hf_dams, dmd_dams, intake_s_dams, md_herb_dams = sfun.f_feedsupply(cu3, cu4, cr_dams, feedsupplyw_pa1e1b1nwzida0e0b0xyg1[p], paststd_foo_pa1e1b1j0wzida0e0b0xyg[p], paststd_dmd_pa1e1b1j0wzida0e0b0xyg[p], legume_pa1e1b1nwzida0e0b0xyg[p], pi_dams, pasture_stage_pa1e1b1j0wzida0e0b0xyg[p], pinp.sheep['i_hr_scalar'], pinp.sheep['i_region'], uinp.pastparameters['i_n_pasture_stage'], uinp.pastparameters['i_hd_std'])
                if np.any(days_period_pa1e1b1nwzida0e0b0xyg3[p,...] >0):
                    foo_offs, hf_offs, dmd_offs, intake_s_offs, md_herb_offs = sfun.f_feedsupply(cu3, cu4, cr_offs, feedsupplyw_pa1e1b1nwzida0e0b0xyg3[p], paststd_foo_pa1e1b1j0wzida0e0b0xyg[p], paststd_dmd_pa1e1b1j0wzida0e0b0xyg[p], legume_pa1e1b1nwzida0e0b0xyg[p], pi_offs, pasture_stage_pa1e1b1j0wzida0e0b0xyg[p], pinp.sheep['i_hr_scalar'], pinp.sheep['i_region'], uinp.pastparameters['i_n_pasture_stage'], uinp.pastparameters['i_hd_std'])

                ##relative availability
                eqn_group = 5
                eqn_system = 0 # CSIRO = 0
                if uinp.sheep['i_eqn_exists_q0q1'][eqn_group, eqn_system]:  # proceed with call & assignment if this system exists for this group
                    ###sire
                    eqn_used = (eqn_used_g0_q1p[eqn_group, p] == eqn_system)
                    if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg0[p,...] >0):
                        temp0 = sfun.f_ra_cs(foo_sire, hf_sire, cr_sire, zf_sire)
                        if eqn_used:
                            ra_sire = temp0
                        if eqn_compare:
                            r_compare_q0q1q2psire[eqn_system, eqn_group, 0, p, ...] = temp0
                    ###dams
                    eqn_used = (eqn_used_g1_q1p[eqn_group, p] == eqn_system)
                    if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                        temp0 = sfun.f_ra_cs(foo_dams, hf_dams, cr_dams, zf_dams)
                        if eqn_used:
                            ra_dams = temp0
                        if eqn_compare:
                            r_compare_q0q1q2pdams[eqn_system, eqn_group, 0, p, ...] = temp0
                    ###offs
                    eqn_used = (eqn_used_g3_q1p[eqn_group, p] == eqn_system)
                    if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg3[p,...] >0):
                        temp0 = sfun.f_ra_cs(foo_offs, hf_offs, cr_offs, zf_offs)
                        if eqn_used:
                            ra_offs = temp0
                        if eqn_compare:
                            r_compare_q0q1q2poffs[eqn_system, eqn_group, 0, p, ...] = temp0

                eqn_system = 1 # Murdoch = 1
                if uinp.sheep['i_eqn_exists_q0q1'][eqn_group, eqn_system]:  # proceed with call & assignment if this system exists for this group
                    ###sire
                    eqn_used = (eqn_used_g0_q1p[eqn_group, p] == eqn_system)
                    if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg0[p,...] >0):
                        temp0 = sfun.f_ra_mu(cu0_sire, foo_sire, hf_sire, zf_sire)
                        if eqn_used:
                            ra_sire = temp0
                        if eqn_compare:
                            r_compare_q0q1q2psire[eqn_system, eqn_group, 0, p, ...] = temp0
                    ###dams
                    eqn_used = (eqn_used_g1_q1p[eqn_group, p] == eqn_system)
                    if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                        temp0 = sfun.f_ra_mu(cu0_dams, foo_dams, hf_dams, zf_dams)
                        if eqn_used:
                            ra_dams = temp0
                        if eqn_compare:
                            r_compare_q0q1q2pdams[eqn_system, eqn_group, 0, p, ...] = temp0
                    ###offs
                    eqn_used = (eqn_used_g3_q1p[eqn_group, p] == eqn_system)
                    if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg3[p,...] >0):
                        temp0 = sfun.f_ra_mu(cu0_offs, foo_offs, hf_offs, zf_offs)
                        if eqn_used:
                            ra_offs = temp0
                        if eqn_compare:
                            r_compare_q0q1q2poffs[eqn_system, eqn_group, 0, p, ...] = temp0


                ##relative ingestibility (quality)
                eqn_group = 6
                eqn_system = 0 # CSIRO = 0
                if uinp.sheep['i_eqn_exists_q0q1'][eqn_group, eqn_system]:  # proceed with call & assignment if this system exists for this group
                    ###sire
                    eqn_used = (eqn_used_g0_q1p[eqn_group, p] == eqn_system)
                    if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg0[p,...] >0):
                        temp0 = sfun.f_rq_cs(dmd_sire, legume_pa1e1b1nwzida0e0b0xyg[p], cr_sire, pinp.sheep['i_sf'])
                        if eqn_used:
                            rq_sire = temp0
                        if eqn_compare:
                            r_compare_q0q1q2psire[eqn_system, eqn_group, 0, p, ...] = temp0
                    ###dams
                    eqn_used = (eqn_used_g1_q1p[eqn_group, p] == eqn_system)
                    if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                        temp0 = sfun.f_rq_cs(dmd_dams, legume_pa1e1b1nwzida0e0b0xyg[p], cr_dams, pinp.sheep['i_sf'])
                        if eqn_used:
                            rq_dams = temp0
                        if eqn_compare:
                            r_compare_q0q1q2pdams[eqn_system, eqn_group, 0, p, ...] = temp0
                    ###offs
                    eqn_used = (eqn_used_g3_q1p[eqn_group, p] == eqn_system)
                    if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg3[p,...] >0):
                        temp0 = sfun.f_rq_cs(dmd_offs, legume_pa1e1b1nwzida0e0b0xyg[p], cr_offs, pinp.sheep['i_sf'])
                        if eqn_used:
                            rq_offs = temp0
                        if eqn_compare:
                            r_compare_q0q1q2poffs[eqn_system, eqn_group, 0, p, ...] = temp0

                ##intake
                if np.any(days_period_pa1e1b1nwzida0e0b0xyg0[p,...] >0):
                    mei_sire, mei_solid_sire, intake_f_sire, md_solid_sire, mei_propn_milk_sire, mei_propn_herb_sire, mei_propn_supp_sire \
                            = sfun.f_intake(cr_sire, pi_sire, ra_sire, rq_sire,  md_herb_sire, feedsupply_std_pa1e1b1nwzida0e0b0xyg0[p]
                                            , intake_s_sire, pinp.sheep['i_md_supp'], legume_pa1e1b1nwzida0e0b0xyg[p])
                if np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                    mei_dams, mei_solid_dams, intake_f_dams, md_solid_dams, mei_propn_milk_dams, mei_propn_herb_dams, mei_propn_supp_dams  \
                            = sfun.f_intake(cr_dams, pi_dams, ra_dams, rq_dams,  md_herb_dams, feedsupplyw_pa1e1b1nwzida0e0b0xyg1[p]
                                            , intake_s_dams, pinp.sheep['i_md_supp'], legume_pa1e1b1nwzida0e0b0xyg[p])
                if np.any(days_period_pa1e1b1nwzida0e0b0xyg3[p,...] >0):
                    mei_offs, mei_solid_offs, intake_f_offs, md_solid_offs, mei_propn_milk_offs, mei_propn_herb_offs, mei_propn_supp_offs  \
                            = sfun.f_intake(cr_offs, pi_offs, ra_offs, rq_offs,  md_herb_offs, feedsupplyw_pa1e1b1nwzida0e0b0xyg3[p]
                                            , intake_s_offs, pinp.sheep['i_md_supp'], legume_pa1e1b1nwzida0e0b0xyg[p])


                ##energy
                eqn_group = 7
                eqn_system = 0 # CSIRO = 0
                if uinp.sheep['i_eqn_exists_q0q1'][eqn_group, eqn_system]:  # proceed with call & assignment if this system exists for this group
                    ###sire
                    eqn_used = (eqn_used_g0_q1p[eqn_group, p] == eqn_system)
                    if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg0[p,...] >0):
                        temp0, temp1, temp2, temp3, temp4, temp5 = sfun.f_energy_cs(ck_sire, cx_sire[:,0:1,...], cm_sire, lw_start_sire, ffcfw_start_sire
                                                                    , mr_age_pa1e1b1nwzida0e0b0xyg0[p], mei_sire, omer_history_start_m3g0
                                                                    , days_period_pa1e1b1nwzida0e0b0xyg0[p], md_solid_sire, pinp.sheep['i_md_supp']
                                                                    , md_herb_sire, lgf_eff_pa1e1b1nwzida0e0b0xyg0[p, ...]
                                                                    , dlf_eff_pa1e1b1nwzida0e0b0xyg[p,...], pinp.sheep['i_steepness']
                                                                    , densityw_pa1e1b1nwzida0e0b0xyg0[p], foo_sire, feedsupply_std_pa1e1b1nwzida0e0b0xyg0[p]
                                                                    , intake_f_sire, dmd_sire)
                        ## these variables need to be stored even if the equation system is not used so that the equations can be compared
                        omer_history_sire = temp1
                        if eqn_used:
                            meme_sire = temp0
                            km_sire = temp2
                            kg_fodd_sire = temp3
                            kg_supp_sire = temp4  # temp5 is not used for sires
                        if eqn_compare:
                            r_compare_q0q1q2psire[eqn_system, eqn_group, 0, p, ...] = temp0  # more of the return variable could be retained
                    ###dams
                    eqn_used = (eqn_used_g1_q1p[eqn_group, p] == eqn_system)
                    if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                        temp0, temp1, temp2, temp3, temp4, temp5 = sfun.f_energy_cs(ck_dams, cx_dams[:,1:2,...], cm_dams, lw_start_dams, ffcfw_start_dams
                                                                    , mr_age_pa1e1b1nwzida0e0b0xyg1[p], mei_dams, omer_history_start_m3g1
                                                                    , days_period_pa1e1b1nwzida0e0b0xyg1[p], md_solid_dams, pinp.sheep['i_md_supp']
                                                                    , md_herb_dams, lgf_eff_pa1e1b1nwzida0e0b0xyg1[p, ...]
                                                                    , dlf_eff_pa1e1b1nwzida0e0b0xyg[p,...], pinp.sheep['i_steepness']
                                                                    , densityw_pa1e1b1nwzida0e0b0xyg1[p], foo_dams, feedsupplyw_pa1e1b1nwzida0e0b0xyg1[p]
                                                                    , intake_f_dams, dmd_dams)
                        ## these variables need to be stored even if the equation system is not used so that the equations can be compared
                        omer_history_dams = temp1
                        if eqn_used:
                            meme_dams = temp0
                            km_dams = temp2
                            kg_fodd_dams = temp3
                            kg_supp_dams = temp4
                            kl_dams = temp5
                        if eqn_compare:
                            r_compare_q0q1q2pdams[eqn_system, eqn_group, 0, p, ...] = temp0  # more of the return variable could be retained
                    ###offs
                    eqn_used = (eqn_used_g3_q1p[eqn_group, p] == eqn_system)
                    if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg3[p,...] >0):
                        temp0, temp1, temp2, temp3, temp4, temp5 = sfun.f_energy_cs(ck_offs, cx_offs[:,mask_x,...], cm_offs, lw_start_offs, ffcfw_start_offs
                                                                    , mr_age_pa1e1b1nwzida0e0b0xyg3[p], mei_offs, omer_history_start_m3g3
                                                                    , days_period_pa1e1b1nwzida0e0b0xyg3[p], md_solid_offs, pinp.sheep['i_md_supp']
                                                                    , md_herb_offs, lgf_eff_pa1e1b1nwzida0e0b0xyg3[p, ...]
                                                                    , dlf_eff_pa1e1b1nwzida0e0b0xyg[p,...], pinp.sheep['i_steepness']
                                                                    , densityw_pa1e1b1nwzida0e0b0xyg3[p], foo_offs, feedsupplyw_pa1e1b1nwzida0e0b0xyg3[p]
                                                                    , intake_f_offs, dmd_offs)
                        ## these variables need to be stored even if the equation system is not used so that the equations can be compared
                        omer_history_offs = temp1
                        if eqn_used:
                            meme_offs = temp0
                            km_offs = temp2
                            kg_fodd_offs = temp3
                            kg_supp_offs = temp4 # temp5 is not used for offspring
                        if eqn_compare:
                            r_compare_q0q1q2poffs[eqn_system, eqn_group, 0, p, ...] = temp0  # more of the return variable could be retained






                ##foetal growth - dams
                eqn_group = 9
                eqn_system = 0 # CSIRO = 0
                if uinp.sheep['i_eqn_exists_q0q1'][eqn_group, eqn_system]:  # proceed with call & assignment if this system exists for this group
                    eqn_used = (eqn_used_g0_q1p[eqn_group, p] == eqn_system)
                    if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                        ##first method is using the nec_cum method
                        temp0, temp1, temp2, temp3, temp4, temp5 = sfun.f_foetus_cs(cp_dams, cb1_dams, kc_yg1, nfoet_b1nwzida0e0b0xyg, relsize_start_dams
                                        , rc_start_dams, w_b_std_y_b1nwzida0e0b0xyg1, w_f_start_dams, nw_f_start_dams, nwf_age_f_pa1e1b1nwzida0e0b0xyg1[p]
                                        , guw_age_f_pa1e1b1nwzida0e0b0xyg1[p], dce_age_f_pa1e1b1nwzida0e0b0xyg1[p])
                        ## these variables need to be stored even if the equation system is not used so that the equations can be compared
                        w_f_dams = temp0
                        nw_f_dams = temp4
                        if eqn_used:
                            mec_dams = temp1
                            nec_dams = temp2
                            w_b_exp_y_dams = temp3
                            guw_dams = temp5
                        if eqn_compare:
                            r_compare_q0q1q2pdams[eqn_system, eqn_group, 0, p, ...] = temp0
                            # r_compare_q0q1q2pdams[eqn_system, eqn_group, 1, p, ...] = temp1



                ##milk production
                if np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                    ###Expected ffcfw of yatf with m1 axis - each period
                    ffcfw_exp_a1e1b1nwzida0e0b0xyg2m1 = (ffcfw_start_yatf[..., na] + (index_m1 * cn_yatf[7, ...][...,na])) * (
                                index_m1 < days_period_pa1e1b1nwzida0e0b0xyg2[...,na][p])
                    ###Expected average metabolic LW of yatf during period
                    ffcfw75_exp_yatf = np.sum(ffcfw_exp_a1e1b1nwzida0e0b0xyg2m1 ** 0.75, axis=-1) / np.maximum(1, days_period_pa1e1b1nwzida0e0b0xyg2[p, ...])

                    mp2_dams, mel_dams, nel_dams, ldr_dams, lb_dams \
                        = sfun.f_milk(cl_dams, srw_xyg1, relsize_start_dams, rc_birth_dams, mei_dams, meme_dams, mew_min_pa1e1b1nwzida0e0b0xyg1[p]
                            , rc_start_dams, ffcfw75_exp_yatf, lb_start_dams, ldr_start_dams, age_pa1e1b1nwzida0e0b0xyg2[p]
                            , mp_age_y_pa1e1b1nwzida0e0b0xyg1[p], mp2_age_y_pa1e1b1nwzida0e0b0xyg1[p], x_pos
                            , days_period_pa1e1b1nwzida0e0b0xyg2[p], kl_dams, lact_nut_effect_pa1e1b1nwzida0e0b0xyg1[p])
                    mp2_yatf = fun.f_divide(mp2_dams, nyatf_b1nwzida0e0b0xyg) # 0 if given slice of b1 axis has no yatf

                ##wool production
                if np.any(days_period_pa1e1b1nwzida0e0b0xyg0[p,...] >0):
                    d_cfw_sire, d_fd_sire, d_fl_sire, d_cfw_history_sire_m2, mew_sire, new_sire  \
                        = sfun.f_fibre(cw_sire, cc_sire, ffcfw_start_sire, relsize_start_sire, d_cfw_history_start_m2g0,
                                       mei_sire, mew_min_pa1e1b1nwzida0e0b0xyg0[p],
                                       d_cfw_ave_pa1e1b1nwzida0e0b0xyg0[p, ...],  sfd_a0e0b0xyg0, wge_a0e0b0xyg0,
                                       af_wool_pa1e1b1nwzida0e0b0xyg0[p, ...], dlf_wool_pa1e1b1nwzida0e0b0xyg0[p, ...],
                                       kw_yg0, days_period_pa1e1b1nwzida0e0b0xyg0[p], sfw_ltwadj_g0, sfd_ltwadj_g0)
                if np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                    d_cfw_dams, d_fd_dams, d_fl_dams, d_cfw_history_dams_m2, mew_dams, new_dams  \
                        = sfun.f_fibre(cw_dams, cc_dams, ffcfw_start_dams, relsize_start_dams, d_cfw_history_start_m2g1,
                                       mei_dams, mew_min_pa1e1b1nwzida0e0b0xyg1[p],
                                       d_cfw_ave_pa1e1b1nwzida0e0b0xyg1[p, ...], sfd_a0e0b0xyg1, wge_a0e0b0xyg1,
                                       af_wool_pa1e1b1nwzida0e0b0xyg1[p, ...], dlf_wool_pa1e1b1nwzida0e0b0xyg1[p, ...],
                                       kw_yg1, days_period_pa1e1b1nwzida0e0b0xyg1[p],
                                       sfw_ltwadj_pa1e1b1nwzida0e0b0xyg1[p, ...],
                                       sfd_ltwadj_pa1e1b1nwzida0e0b0xyg1[p, ...], mec_dams, mel_dams,
                                       gest_propn_pa1e1b1nwzida0e0b0xyg1[p], lact_propn_pa1e1b1nwzida0e0b0xyg1[p])
                if np.any(days_period_pa1e1b1nwzida0e0b0xyg3[p,...] >0):
                    d_cfw_offs, d_fd_offs, d_fl_offs, d_cfw_history_offs_m2, mew_offs, new_offs  \
                        = sfun.f_fibre(cw_offs, cc_offs, ffcfw_start_offs, relsize_start_offs, d_cfw_history_start_m2g3,
                                       mei_offs, mew_min_pa1e1b1nwzida0e0b0xyg3[p],
                                       d_cfw_ave_pa1e1b1nwzida0e0b0xyg3[p, ...], sfd_da0e0b0xyg3, wge_da0e0b0xyg3,
                                       af_wool_pa1e1b1nwzida0e0b0xyg3[p, ...], dlf_wool_pa1e1b1nwzida0e0b0xyg3[p, ...],
                                       kw_yg3, days_period_pa1e1b1nwzida0e0b0xyg3[p], sfw_ltwadj_a1e1b1nwzida0e0b0xyg3,
                                       sfd_ltwadj_a1e1b1nwzida0e0b0xyg3)

                ##energy to offset chilling
                if np.any(days_period_pa1e1b1nwzida0e0b0xyg0[p,...] >0):
                    mem_sire, temp_lc_sire, kg_sire = sfun.f_chill_cs(cc_sire, ck_sire, ffcfw_start_sire, rc_start_sire, sl_start_sire, mei_sire
                                                            , meme_sire, mew_sire, new_sire, km_sire, kg_supp_sire, kg_fodd_sire, mei_propn_supp_sire
                                                            , mei_propn_herb_sire, temp_ave_pa1e1b1nwzida0e0b0xyg[p], temp_max_pa1e1b1nwzida0e0b0xyg[p]
                                                            , temp_min_pa1e1b1nwzida0e0b0xyg[p], ws_pa1e1b1nwzida0e0b0xyg[p], rain_pa1e1b1nwzida0e0b0xygm1[p]
                                                            , index_m0)
                if np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                    mem_dams, temp_lc_dams, kg_dams = sfun.f_chill_cs(cc_dams, ck_dams, ffcfw_start_dams, rc_start_dams, sl_start_dams, mei_dams
                                                            , meme_dams, mew_dams, new_dams, km_dams, kg_supp_dams, kg_fodd_dams, mei_propn_supp_dams
                                                            , mei_propn_herb_dams, temp_ave_pa1e1b1nwzida0e0b0xyg[p], temp_max_pa1e1b1nwzida0e0b0xyg[p]
                                                            , temp_min_pa1e1b1nwzida0e0b0xyg[p], ws_pa1e1b1nwzida0e0b0xyg[p], rain_pa1e1b1nwzida0e0b0xygm1[p]
                                                            , index_m0, guw = guw_dams, kl = kl_dams, mei_propn_milk = mei_propn_milk_dams, mec = mec_dams
                                                            , mel = mel_dams, nec = nec_dams, nel = nel_dams, gest_propn = gest_propn_pa1e1b1nwzida0e0b0xyg1[p]
                                                            , lact_propn = lact_propn_pa1e1b1nwzida0e0b0xyg1[p])
                if np.any(days_period_pa1e1b1nwzida0e0b0xyg3[p,...] >0):
                    mem_offs, temp_lc_offs, kg_offs = sfun.f_chill_cs(cc_offs, ck_offs, ffcfw_start_offs, rc_start_offs, sl_start_offs, mei_offs
                                                            , meme_offs, mew_offs, new_offs, km_offs, kg_supp_offs, kg_fodd_offs, mei_propn_supp_offs
                                                            , mei_propn_herb_offs, temp_ave_pa1e1b1nwzida0e0b0xyg[p], temp_max_pa1e1b1nwzida0e0b0xyg[p]
                                                            , temp_min_pa1e1b1nwzida0e0b0xyg[p], ws_pa1e1b1nwzida0e0b0xyg[p], rain_pa1e1b1nwzida0e0b0xygm1[p]
                                                            , index_m0)

                ##calc lwc
                eqn_group = 8
                eqn_system = 0 # CSIRO = 0
                if uinp.sheep['i_eqn_exists_q0q1'][eqn_group, eqn_system]:  # proceed with call & assignment if this system exists for this group
                    ###sire
                    eqn_used = (eqn_used_g0_q1p[eqn_group, p] == eqn_system)
                    if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg0[p,...] >0):
                        temp0, temp1, temp2, temp3, temp4 = sfun.f_lwc_cs(cg_sire, rc_start_sire, mei_sire, mem_sire, mew_sire
                                                                , z1f_sire, z2f_sire, kg_sire)
                        if eqn_used:
                            ebg_sire = temp0
                            evg_sire = temp1
                            pg_sire = temp2
                            fg_sire = temp3
                            level_sire = temp4
                        if eqn_compare:
                            r_compare_q0q1q2psire[eqn_system, eqn_group, 0, p, ...] = temp0
                            r_compare_q0q1q2psire[eqn_system, eqn_group, 1, p, ...] = temp1
                    ###dams
                    eqn_used = (eqn_used_g1_q1p[eqn_group, p] == eqn_system)
                    if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                        temp0, temp1, temp2, temp3, temp4 = sfun.f_lwc_cs(cg_dams, rc_start_dams, mei_dams, mem_dams, mew_dams
                                                                , z1f_dams, z2f_dams, kg_dams, mec_dams, mel_dams
                                                                , gest_propn_pa1e1b1nwzida0e0b0xyg1[p], lact_propn_pa1e1b1nwzida0e0b0xyg1[p])
                        if eqn_used:
                            ebg_dams = temp0
                            evg_dams = temp1
                            pg_dams = temp2
                            fg_dams = temp3
                            level_dams = temp4
                        if eqn_compare:
                            r_compare_q0q1q2pdams[eqn_system, eqn_group, 0, p, ...] = temp0
                            r_compare_q0q1q2pdams[eqn_system, eqn_group, 1, p, ...] = temp1
                    ###offs
                    eqn_used = (eqn_used_g3_q1p[eqn_group, p] == eqn_system)
                    if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg3[p,...] >0):
                        temp0, temp1, temp2, temp3, temp4 = sfun.f_lwc_cs(cg_offs, rc_start_offs, mei_offs, mem_offs, mew_offs
                                                                , z1f_offs, z2f_offs, kg_offs)
                        if eqn_used:
                            ebg_offs = temp0
                            evg_offs = temp1
                            pg_offs = temp2
                            fg_offs = temp3
                            level_offs = temp4
                        if eqn_compare:
                            r_compare_q0q1q2poffs[eqn_system, eqn_group, 0, p, ...] = temp0
                            r_compare_q0q1q2poffs[eqn_system, eqn_group, 1, p, ...] = temp1




                ###if there is a target then adjust feedsupply, if not break out of feedsupply loop
                if target_lwc == None:
                    break
                ###calc error
                error = (ebg_dams * cg_dams) - target_lwc
                ###store in attempts array - build new array assign old array and then add current itn results - done like this to handle the shape changing and because we don't know what shape feedsupply and error are before this loop starts
                shape = tuple(np.maximum.reduce([feedsupplyw_pa1e1b1nwzida0e0b0xyg1.shape, error.shape]))+(n_max_itn,)+(2,)
                attempts2= np.zeros(shape)
                attempts2[...] = attempts
                attempts2[...,itn,0] = feedsupplyw_pa1e1b1nwzida0e0b0xyg1
                attempts2[...,itn,1] = error
                attempts = attempts2
                ###is error within tolerance
                if np.all(np.abs(error) <= epsilon):
                    break
                ###max attempts reached
                elif itn == n_max_itn-1: #minus 1 because range() and hence itn starts from 0
                    ####select best feed supply option
                    feedsupply = attempts[...,attempts[...,1]==np.nanmin(np.abs(attempts[...,1]),axis=-1),0] #create boolean index using error array then index feedsupply array
                    break
                feedsupply = sfun.f_feedsupply_adjust(attempts,feedsupply,itn)
                itn+=1

            ##dam weight at a given time during period - used for special events like birth.
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                ##Dam weight at mating - to estimate the weight at mating we are wanting to use the growth rate of the dams that are not yet pregnant
                ffcfw_e1b1sliced = sfun.f_dynamic_slice(ffcfw_start_dams, e1_pos, 0, 1, b1_pos, 0, 1) #slice e1 & b1 axis
                ebg_e1b1sliced = sfun.f_dynamic_slice(ebg_dams, e1_pos, 0, 1, b1_pos, 0, 1) #slice e1 & b1 axis
                gest_propn_b1sliced = sfun.f_dynamic_slice(gest_propn_pa1e1b1nwzida0e0b0xyg1[p], b1_pos, 2, 3) #slice b1 axis
                days_period_b1sliced = sfun.f_dynamic_slice(days_period_pa1e1b1nwzida0e0b0xyg1[p], b1_pos, 2, 3) #slice b1 axis

                t_w_mating = np.sum((ffcfw_e1b1sliced + ebg_e1b1sliced * cg_dams[18, ...] * days_period_b1sliced * (1-gest_propn_b1sliced)) \
                             * period_is_mating_pa1e1b1nwzida0e0b0xyg1[p], axis=e1_pos, keepdims=True)#Temporary variable for mating weight
                ffcfw_mating_dams = fun.f_update(ffcfw_mating_dams, t_w_mating, period_is_mating_pa1e1b1nwzida0e0b0xyg1[p])
                ##Relative condition of the dam at mating - required to determine milk production
                rc_mating_dams = ffcfw_mating_dams / nw_start_dams
                ##Condition score of the dam at  mating
                cs_mating_dams = sfun.f_condition_score(rc_mating_dams, cu0_dams)
                ##Relative size of the dame at mating
                relsize_mating_dams = relsize_start_dams

                ##Dam weight at birth ^probs don't need this since birth is first day of period - just need to pass in ffcfw_start to function
                # t_w_birth = ffcfw_start_dams + ebg_dams * cg_dams[18, ...] * days_period_pa1e1b1nwzida0e0b0xyg1[p] * gest_propn_pa1e1b1nwzida0e0b0xyg1[p]
                # ffcfw_birth_dams = fun.f_update(ffcfw_birth_dams, t_w_birth, period_is_birth_pa1e1b1nwzida0e0b0xyg1[p])
                ##Relative condition of the dam at most recent birth
                # rc_birth_dams = ffcfw_birth_dams / nw_start_dams

                ##Dam weight at weaning
                # t_w_weaning = ffcfw_start_dams + ebg_dams * cg_dams[18, ...] * days_period_pa1e1b1nwzida0e0b0xyg1[p] * lact_propn_pa1e1b1nwzida0e0b0xyg1[p]
                # ffcfw_weaning_dams = fun.f_update(ffcfw_weaning_dams, t_w_weaning, period_is_wean_pa1e1b1nwzida0e0b0xyg1[p])


            ##birth weight yatf - calculated when dams days per period > 0  - calced for start of period (ebg is mul by gest propn so not included for period when birth happens)
            eqn_group = 10
            eqn_system = 0 # CSIRO = 0
            if uinp.sheep['i_eqn_exists_q0q1'][eqn_group, eqn_system]:  # proceed with call & assignment if this system exists for this group
                eqn_used = (eqn_used_g2_q1p[eqn_group, p] == eqn_system)
                if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                    temp0 = sfun.f_birthweight_cs(cx_yatf[:,mask_x,...], w_b_start_yatf, w_f_start_dams, period_is_birth_pa1e1b1nwzida0e0b0xyg1[p]) #pass in wf_start because animal is born on first day of period
                    if eqn_used:
                        w_b_yatf = temp0
                        # cf_w_b_dams = 0 #this is only returned by mu function but variable needs to be defined so it doesnt give error in start function - default is 0
                    if eqn_compare:
                        r_compare_q0q1q2pyatf[eqn_system, eqn_group, 0, p, ...] = temp0
            eqn_system = 1 # Mu = 1
            if uinp.sheep['i_eqn_exists_q0q1'][eqn_group, eqn_system]:  # proceed with call & assignment if this system exists for this group
                eqn_used = (eqn_used_g2_q1p[eqn_group, p] == eqn_system)
                if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                    temp0, temp1 = sfun.f_birthweight_mu(cu1_yatf, cb1_yatf, cx_yatf[:,mask_x,...], ce_yatf[:,p-1,...], w_b_start_yatf
                                                         , cf_w_b_start_dams, ffcfw_start_dams , ebg_dams, days_period_pa1e1b1nwzida0e0b0xyg1[p]
                                                         , gest_propn_pa1e1b1nwzida0e0b0xyg1[p],  period_between_joinscan_pa1e1b1nwzida0e0b0xyg1[p]
                                                         , period_between_scanbirth_pa1e1b1nwzida0e0b0xyg1[p], period_is_birth_pa1e1b1nwzida0e0b0xyg1[p]) #have to use yatf days per period if using prejoinng to scanning
                    ## these variables need to be stored even if the equation system is not used so that the equations can be compared
                    cf_w_b_dams = temp1
                    if eqn_used:
                        w_b_yatf = temp0
                    if eqn_compare:
                        r_compare_q0q1q2pyatf[eqn_system, eqn_group, 0, p, ...] = temp0

            ##progeny fleece prodn adjustment due to dam profile (LTW adjustment)
            eqn_group = 13
            eqn_system = 0 # CSIRO = 0 - doesn't exist for LTW impacts on progeny
            if uinp.sheep['i_eqn_exists_q0q1'][eqn_group, eqn_system]:  # proceed with call & assignment if this system exists for this group
                eqn_used = (eqn_used_g1_q1p[eqn_group, p] == eqn_system)
                # if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                #     temp0 = sfun.f_progenycfw_cs(cx_yatf[:,mask_x,...], w_b_start_yatf, w_f_start_dams, period_is_birth_pa1e1b1nwzida0e0b0xyg1[p]) #pass in wf_start because animal is born on first day of period
                #     if eqn_used:
                #         cfw_ltwadj_dams = temp0
                #         fdltw = temp1
                #         cf_cfwltw_dams = 0 #this is only returned by mu function but variable needs to be defined so it doesnt give error in start function - default is 0
                #         cf_fdltw_dams = 0  #this is only returned by mu function but variable needs to be defined so it doesnt give error in start function - default is 0
                #     if eqn_compare:
                #         r_compare_q0q1q2pyatf[eqn_system, eqn_group, 0, p, ...] = temp0
                #         r_compare_q0q1q2pyatf[eqn_system, eqn_group, 1, p, ...] = temp1
            eqn_system = 1 # MU = 1
            if uinp.sheep['i_eqn_exists_q0q1'][eqn_group, eqn_system]:  # proceed with call & assignment if this system exists for this group
                eqn_used = (eqn_used_g1_q1p[eqn_group, p] == eqn_system)
                if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                    temp0, temp1 = sfun.f_progenycfw_mu(cu1_yatf, cfw_ltwadj_start_dams, cf_cfwltw_start_dams, ffcfw_start_dams
                                        , nw_start_dams, ebg_dams, days_period_pa1e1b1nwzida0e0b0xyg1[p], gest_propn_pa1e1b1nwzida0e0b0xyg1[p]
                                        ,  period_between_joinscan_pa1e1b1nwzida0e0b0xyg1[p], period_between_scanbirth_pa1e1b1nwzida0e0b0xyg1[p]
                                        , period_is_birth_pa1e1b1nwzida0e0b0xyg1[p]) #have to use yatf days per period if using prejoinng to scanning
                    temp2, temp3 = sfun.f_progenyfd_mu(cu1_yatf, fd_ltwadj_start_dams, cf_fdltw_start_dams, ffcfw_start_dams
                                        , nw_start_dams, ebg_dams, days_period_pa1e1b1nwzida0e0b0xyg1[p], gest_propn_pa1e1b1nwzida0e0b0xyg1[p]
                                        ,  period_between_joinscan_pa1e1b1nwzida0e0b0xyg1[p], period_between_scanbirth_pa1e1b1nwzida0e0b0xyg1[p]
                                        , period_is_birth_pa1e1b1nwzida0e0b0xyg1[p]) #have to use yatf days per period if using prejoinng to scanning
                    #if eqn_used:
                    ## these variables all need to be stored even if the equation system is not used so that the equations can be compared
                    cfw_ltwadj_dams = temp0
                    cf_cfwltw_dams = temp1
                    fd_ltwadj_dams = temp2
                    cf_fdltw_dams = temp3
                    if eqn_compare:
                        r_compare_q0q1q2pyatf[eqn_system, eqn_group, 0, p, ...] = temp0
                        r_compare_q0q1q2pyatf[eqn_system, eqn_group, 1, p, ...] = temp2

            ##yatf resets
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg2[p,...] >0):
                ##reset start variables if period is birth
                ###ffcf weight of yatf
                ffcfw_start_yatf = fun.f_update(ffcfw_start_yatf, w_b_yatf, period_is_birth_pa1e1b1nwzida0e0b0xyg1[p, ...])
                ###normal weight of yatf
                nw_start_yatf	= fun.f_update(nw_start_yatf, w_b_yatf, period_is_birth_pa1e1b1nwzida0e0b0xyg1[p, ...])
                ###adipose weight of yatf
                aw_start_yatf	= fun.f_update(aw_start_yatf, w_b_yatf * aw_propn_yg2, period_is_birth_pa1e1b1nwzida0e0b0xyg1[p, ...])
                ###muscle weight of yatf
                mw_start_yatf	= fun.f_update(mw_start_yatf, w_b_yatf * mw_propn_yg2, period_is_birth_pa1e1b1nwzida0e0b0xyg1[p, ...])
                ###bone weight of the yatf
                bw_start_yatf	= fun.f_update(bw_start_yatf, w_b_yatf * bw_propn_yg2, period_is_birth_pa1e1b1nwzida0e0b0xyg1[p, ...])
                ###clean fleece weight of yatf
                cfw_start_yatf	= fun.f_update(cfw_start_yatf, 0, period_is_birth_pa1e1b1nwzida0e0b0xyg1[p, ...])
                ###fibre diameter of yatf
                fd_start_yatf	= fun.f_update(fd_start_yatf, 0, period_is_birth_pa1e1b1nwzida0e0b0xyg1[p, ...])
                ###fibre length of yatf
                fl_start_yatf	= fun.f_update(fl_start_yatf, fl_birth_yg2, period_is_birth_pa1e1b1nwzida0e0b0xyg1[p, ...])
                ###minimum fibre diameter of yatf
                fd_min_start_yatf	= fun.f_update(fd_min_start_yatf, 1000, period_is_birth_pa1e1b1nwzida0e0b0xyg1[p, ...])

                ##Yatf dependent start values
                ###Normal weight max (if animal is well fed) - yatf
                nw_max_yatf	= srw_xyg2 * (1 - srw_age_pa1e1b1nwzida0e0b0xyg2[p]) + w_b_yatf * srw_age_pa1e1b1nwzida0e0b0xyg2[p]
                ##Dependent start: Change in normal weight max - yatf
                d_nw_max_yatf = fun.f_divide(srw_age_pa1e1b1nwzida0e0b0xyg2[p-1, ...] - srw_age_pa1e1b1nwzida0e0b0xyg2[p, ...] * (srw_xyg2 - w_b_yatf)
                                             , days_period_pa1e1b1nwzida0e0b0xyg2[p]) #nw_max = srw - (srw - bw) * srw_age[p] so d_nw_max = (srw - (srw-bw) * srw_age[p]) - (srw - (srw - bw) * srw_age[p-1]) and that simplifies to d_nw_max = (srw_age[p-1] - srw_age[p]) * (srw-bw)
                ###GFW (start)
                gfw_start_yatf = cfw_start_yatf / cw_yatf[3, ...]
                ###LW (start -with fleece & conceptus)
                lw_start_yatf = ffcfw_start_yatf + gfw_start_yatf
                ###Normal weight (start)
                nw_start_yatf = np.minimum(nw_max_yatf, np.maximum(nw_start_yatf, ffcfw_start_yatf + cn_yatf[3, ...] * (nw_max_yatf  - ffcfw_start_yatf)))
                ###Relative condition (start) - use update function so that when 0 days/period we keep the rc of the last period because it is used to calc sale value which is period_is_weaning which has 0 days because sold at beginning.
                temp_rc_start_yatf = ffcfw_start_yatf / nw_start_yatf
                rc_start_yatf = fun.f_update(rc_start_yatf, temp_rc_start_yatf, days_period_pa1e1b1nwzida0e0b0xyg2[p,...] >0)
                ##Condition score of the dam at  start of p
                cs_start_yatf = sfun.f_condition_score(rc_start_yatf, cu0_yatf)
                ###staple length
                sl_start_yatf = fl_start_yatf * cw_yatf[15,...]
                ###Relative size (start) - dams & sires
                relsize_start_yatf = np.minimum(1, nw_start_yatf / srw_xyg2)
                ###Relative size for LWG (start). Capped by current LW
                relsize1_start_yatf = np.minimum(ffcfw_max_start_yatf, nw_max_yatf) / srw_xyg2
                ###PI Size factor (for cattle)
                zf_yatf = np.maximum(1, 1 + cr_yatf[7, ...] - relsize_start_yatf)
                ###EVG Size factor (decreases steadily - some uncertainty about the sign on cg[4])
                z1f_yatf = 1 / (1 + np.exp(+cg_yatf[4, ...] * (relsize1_start_yatf - cg_yatf[5, ...])))
                ###EVG Size factor (increases at maturity)
                z2f_yatf = np.clip((relsize1_start_yatf - cg_yatf[6, ...]) / (cg_yatf[7, ...] - cg_yatf[6, ...]), 0 ,1)


            ##potential intake - yatf
            eqn_group = 4
            eqn_system = 0 # CSIRO = 0
            if uinp.sheep['i_eqn_exists_q0q1'][eqn_group, eqn_system]:  # proceed with call & assignment if this system exists for this group
                eqn_used = (eqn_used_g2_q1p[eqn_group, p] == eqn_system)
                if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg2[p,...] >0):
                    temp0 = sfun.f_potential_intake_cs(ci_yatf, cl_yatf, srw_xyg2, relsize_start_yatf, rc_start_yatf, temp_lc_yatf, temp_ave_pa1e1b1nwzida0e0b0xyg[p]
                                                       , temp_max_pa1e1b1nwzida0e0b0xyg[p], temp_min_pa1e1b1nwzida0e0b0xyg[p], rain_intake_pa1e1b1nwzida0e0b0xyg2[p]
                                                       , mp2 = mp2_yatf, piyf = piyf_pa1e1b1nwzida0e0b0xyg2[p]
                                                       , period_between_birthwean = period_between_birthwean_pa1e1b1nwzida0e0b0xyg1[p])
                    if eqn_used:
                        pi_yatf = temp0
                    if eqn_compare:
                        r_compare_q0q1q2pyatf[eqn_system, eqn_group, 0, p, ...] = temp0

            ##feedsupply
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg2[p,...] >0):
                foo_yatf, hf_yatf, dmd_yatf, intake_s_yatf, md_herb_yatf = sfun.f_feedsupply(cu3, cu4, cr_yatf, feedsupplyw_pa1e1b1nwzida0e0b0xyg1[p], paststd_foo_pa1e1b1j0wzida0e0b0xyg[p], paststd_dmd_pa1e1b1j0wzida0e0b0xyg[p], legume_pa1e1b1nwzida0e0b0xyg[p], pi_yatf, pasture_stage_pa1e1b1j0wzida0e0b0xyg[p], pinp.sheep['i_hr_scalar'], pinp.sheep['i_region'], uinp.pastparameters['i_n_pasture_stage'], uinp.pastparameters['i_hd_std']) #yatf use dam feedsupply_std


            ##relative availability - yatf
            eqn_group = 5
            eqn_system = 0 # CSIRO = 0
            if uinp.sheep['i_eqn_exists_q0q1'][eqn_group, eqn_system]:  # proceed with call & assignment if this system exists for this group
                eqn_used = (eqn_used_g2_q1p[eqn_group, p] == eqn_system)
                if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg2[p,...] >0):
                    temp0 = sfun.f_ra_cs(foo_yatf, hf_yatf, cr_yatf, zf_yatf)
                    if eqn_used:
                        ra_yatf = temp0
                    if eqn_compare:
                        r_compare_q0q1q2pyatf[eqn_system, eqn_group, 0, p, ...] = temp0
            eqn_system = 1 # Mu = 1
            if uinp.sheep['i_eqn_exists_q0q1'][eqn_group, eqn_system]:  # proceed with call & assignment if this system exists for this group
                eqn_used = (eqn_used_g2_q1p[eqn_group, p] == eqn_system)
                if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg2[p,...] >0):
                    temp0 = sfun.f_ra_mu(cu0_yatf, foo_yatf, hf_yatf, zf_yatf)
                    if eqn_used:
                        ra_yatf = temp0
                    if eqn_compare:
                        r_compare_q0q1q2pyatf[eqn_system, eqn_group, 0, p, ...] = temp0


            ##relative ingestibility (quality) - yatf
            eqn_group = 6
            eqn_system = 0 # CSIRO = 0
            if uinp.sheep['i_eqn_exists_q0q1'][eqn_group, eqn_system]:  # proceed with call & assignment if this system exists for this group
                ###sire
                eqn_used = (eqn_used_g2_q1p[eqn_group, p] == eqn_system)
                if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg2[p,...] >0):
                    temp0 = sfun.f_rq_cs(dmd_yatf, legume_pa1e1b1nwzida0e0b0xyg[p], cr_yatf, pinp.sheep['i_sf'])
                    if eqn_used:
                        rq_yatf = temp0
                    if eqn_compare:
                        r_compare_q0q1q2pyatf[eqn_system, eqn_group, 0, p, ...] = temp0


            ##intake - yatf
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg2[p,...] >0):
                mei_yatf, mei_solid_yatf, intake_f_yatf, md_solid_yatf, mei_propn_milk_yatf, mei_propn_herb_yatf, mei_propn_supp_yatf = \
                        sfun.f_intake(cr_yatf, pi_yatf, ra_yatf, rq_yatf,  md_herb_yatf, feedsupplyw_pa1e1b1nwzida0e0b0xyg1[p]
                                        , intake_s_yatf, pinp.sheep['i_md_supp'], legume_pa1e1b1nwzida0e0b0xyg[p], mp2_yatf)   #same feedsupply as dams

            ##energy - yatf
            eqn_group = 7
            eqn_system = 0 # CSIRO = 0
            if uinp.sheep['i_eqn_exists_q0q1'][eqn_group, eqn_system]:  # proceed with call & assignment if this system exists for this group
                eqn_used = (eqn_used_g2_q1p[eqn_group, p] == eqn_system)
                if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg2[p,...] >0):
                    temp0, temp1, temp2, temp3, temp4, temp5 = sfun.f_energy_cs(ck_yatf, cx_yatf[:,mask_x,...], cm_yatf, lw_start_yatf
                                                                , ffcfw_start_yatf, mr_age_pa1e1b1nwzida0e0b0xyg2[p], mei_yatf
                                                                , omer_history_start_m3g2, days_period_pa1e1b1nwzida0e0b0xyg2[p]
                                                                , md_solid_yatf, pinp.sheep['i_md_supp'], md_herb_yatf
                                                                , lgf_eff_pa1e1b1nwzida0e0b0xyg2[p], dlf_eff_pa1e1b1nwzida0e0b0xyg[p]
                                                                , pinp.sheep['i_steepness'], densityw_pa1e1b1nwzida0e0b0xyg2[p]
                                                                , foo_yatf, feedsupplyw_pa1e1b1nwzida0e0b0xyg1[p], intake_f_yatf
                                                                , dmd_yatf, mei_propn_milk_yatf)  #same feedsupply as dams
                    ## these variables need to be stored even if the equation system is not used so that the equations can be compared
                    omer_history_yatf = temp1
                    if eqn_used:
                        meme_yatf = temp0
                        km_yatf = temp2
                        kg_fodd_yatf = temp3
                        kg_supp_yatf = temp4  # temp5 is not used for yatf
                    if eqn_compare:
                        r_compare_q0q1q2pyatf[eqn_system, eqn_group, 0, p, ...] = temp0  # more of the return variable could be retained


            ##wool production - yatf
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg2[p,...] >0):
                d_cfw_yatf, d_fd_yatf, d_fl_yatf, d_cfw_history_yatf_m2, mew_yatf, new_yatf  \
                    = sfun.f_fibre(cw_yatf, cc_yatf, ffcfw_start_yatf, relsize_start_yatf, d_cfw_history_start_m2g2,
                                   mei_yatf, mew_min_pa1e1b1nwzida0e0b0xyg2[p],
                                   d_cfw_ave_pa1e1b1nwzida0e0b0xyg2[p, ...], sfd_pa1e1b1nwzida0e0b0xyg2[p],
                                   wge_pa1e1b1nwzida0e0b0xyg2[p], af_wool_pa1e1b1nwzida0e0b0xyg2[p, ...],
                                   dlf_wool_pa1e1b1nwzida0e0b0xyg2[p, ...], kw_yg2,
                                   days_period_pa1e1b1nwzida0e0b0xyg2[p], sfw_ltwadj_g2, sfd_ltwadj_g2)


            ##energy to offset chilling - yatf
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg2[p,...] >0):
                mem_yatf, temp_lc_yatf, kg_yatf = sfun.f_chill_cs(cc_yatf, ck_yatf, ffcfw_start_yatf, rc_start_yatf, sl_start_yatf, mei_yatf,
                                                                  meme_yatf, mew_yatf, new_yatf, km_yatf, kg_supp_yatf, kg_fodd_yatf, mei_propn_supp_yatf,
                                                                  mei_propn_herb_yatf, temp_ave_pa1e1b1nwzida0e0b0xyg[p], temp_max_pa1e1b1nwzida0e0b0xyg[p],
                                                                  temp_min_pa1e1b1nwzida0e0b0xyg[p], ws_pa1e1b1nwzida0e0b0xyg[p], rain_pa1e1b1nwzida0e0b0xygm1[p],
                                                                  index_m0,  mei_propn_milk=mei_propn_milk_yatf)



            ##calc lwc - yatf
            eqn_group = 8
            eqn_system = 0 # CSIRO = 0
            if uinp.sheep['i_eqn_exists_q0q1'][eqn_group, eqn_system]:  # proceed with call & assignment if this system exists for this group
                eqn_used = (eqn_used_g2_q1p[eqn_group, p] == eqn_system)
                if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg2[p,...] >0):
                    temp0, temp1, temp2, temp3, temp4 = sfun.f_lwc_cs(cg_yatf, rc_start_yatf, mei_yatf, mem_yatf, mew_yatf, z1f_yatf, z2f_yatf, kg_yatf)
                    if eqn_used:
                        ebg_yatf = temp0
                        evg_yatf = temp1
                        pg_yatf = temp2
                        fg_yatf = temp3
                        level_yatf = temp4
                    if eqn_compare:
                        r_compare_q0q1q2pyatf[eqn_system, eqn_group, 0, p, ...] = temp0
                        r_compare_q0q1q2pyatf[eqn_system, eqn_group, 1, p, ...] = temp1

            ##weaning weight yatf - called when dams days per period greater than 0 - calculates the weight at the start of the period
            eqn_group = 11
            eqn_system = 0 # CSIRO = 0
            if uinp.sheep['i_eqn_exists_q0q1'][eqn_group, eqn_system]:  # proceed with call & assignment if this system exists for this group
                eqn_used = (eqn_used_g2_q1p[eqn_group, p] == eqn_system)
                ##based on days_period_dams because weaning occurs at start of period so days_period_yatf==0
                if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                    temp0 = sfun.f_weanweight_cs(w_w_start_yatf, ffcfw_start_yatf, ebg_yatf, days_period_pa1e1b1nwzida0e0b0xyg2[p]
                                                 , period_is_wean_pa1e1b1nwzida0e0b0xyg1[p])  #it is okay to use ebg of current period because it is mul by lact propn
                    if eqn_used:
                        w_w_yatf = temp0
                    #    cf_w_w_dams = 0 #this is only returned by mu function but variable needs to be defined so it doesnt give error in start function - default is 0
                    if eqn_compare:
                        r_compare_q0q1q2pyatf[eqn_system, eqn_group, 0, p, ...] = temp0
            eqn_system = 1 # Mu = 1   #it is okay to use ebg of current period because it is mul by lact propn
            if uinp.sheep['i_eqn_exists_q0q1'][eqn_group, eqn_system]:  # proceed with call & assignment if this system exists for this group
                eqn_used = (eqn_used_g2_q1p[eqn_group, p] == eqn_system)
                ##based on days_period_dams because weaning occurs at start of period so days_period_yatf==0
                if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                    temp0, temp1, temp2 = sfun.f_weanweight_mu(cu1_yatf, cb1_yatf, cx_yatf[:,mask_x,...], ce_yatf[:,p-1,...]
                                            , nyatf_b1nwzida0e0b0xyg, w_w_start_yatf, cf_w_w_start_dams, ffcfw_start_dams
                                            , ebg_dams, foo_dams ,foo_lact_ave_start, days_period_pa1e1b1nwzida0e0b0xyg2[p]
                                            , age_start_pa1e1b1nwzida0e0b0xyg2[p], period_between_joinscan_pa1e1b1nwzida0e0b0xyg1[p]
                                            , period_between_scanbirth_pa1e1b1nwzida0e0b0xyg1[p], period_between_birthwean_pa1e1b1nwzida0e0b0xyg1[p]
                                            , period_is_wean_pa1e1b1nwzida0e0b0xyg1[p]) #have to use yatf days per period if using prejoining to scanning
                    ## these variables need to be stored even if the equation system is not used so that the equations can be compared
                    cf_w_w_dams = temp1
                    foo_lact_ave = temp2
                    if eqn_used:
                        w_w_yatf = temp0
                    if eqn_compare:
                        r_compare_q0q1q2pyatf[eqn_system, eqn_group, 0, p, ...] = temp0



            ##emissions
            eqn_group = 12
            eqn_system = 0 # Baxter and Clapperton = 0
            if uinp.sheep['i_eqn_exists_q0q1'][eqn_group, eqn_system]:  # proceed with call & assignment if this system exists for this group
                ###sire
                eqn_used = (eqn_used_g0_q1p[eqn_group, p] == eqn_system)
                if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg0[p,...] >0):
                    temp0, temp1 = sfun.f_emissions_bc(ch_sire, intake_f_sire, intake_s_sire, md_solid_sire, level_sire)
                    if eqn_used:
                        ch4_total_sire = temp0
                        ch4_animal_sire = temp1
                    if eqn_compare:
                        r_compare_q0q1q2psire[eqn_system, eqn_group, 0, p, ...] = temp0
                ###dams
                eqn_used = (eqn_used_g1_q1p[eqn_group, p] == eqn_system)
                if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                    temp0, temp1 = sfun.f_emissions_bc(ch_dams, intake_f_dams, intake_s_dams, md_solid_dams, level_dams)
                    if eqn_used:
                        ch4_total_dams = temp0
                        ch4_animal_dams = temp1
                    if eqn_compare:
                        r_compare_q0q1q2pdams[eqn_system, eqn_group, 0, p, ...] = temp0
                ###yatf
                eqn_used = (eqn_used_g2_q1p[eqn_group, p] == eqn_system)
                if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg2[p,...] >0):
                    temp0, temp1 = sfun.f_emissions_bc(ch_yatf, intake_f_yatf, intake_s_yatf, md_solid_yatf, level_yatf)
                    if eqn_used:
                        ch4_total_yatf = temp0
                        ch4_animal_yatf = temp1
                    if eqn_compare:
                        r_compare_q0q1q2pyatf[eqn_system, eqn_group, 0, p, ...] = temp0
                ###offs
                eqn_used = (eqn_used_g3_q1p[eqn_group, p] == eqn_system)
                if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg3[p,...] >0):
                    temp0, temp1 = sfun.f_emissions_bc(ch_offs, intake_f_offs, intake_s_offs, md_solid_offs, level_offs)
                    if eqn_used:
                        ch4_total_offs = temp0
                        ch4_animal_offs = temp1
                    if eqn_compare:
                        r_compare_q0q1q2poffs[eqn_system, eqn_group, 0, p, ...] = temp0

            ##conception Dams
            eqn_group = 0
            eqn_system = 0 # CSIRO = 0
            if uinp.sheep['i_eqn_exists_q0q1'][eqn_group, eqn_system]:  # proceed with call & assignment if this system exists for this group
                eqn_used = (eqn_used_g1_q1p[eqn_group, p] == eqn_system)
                if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                    temp0 = sfun.f_conception_cs(cf_dams, cb1_dams, relsize_mating_dams, rc_mating_dams, crg_doy_pa1e1b1nwzida0e0b0xyg1[p]
                                                 , nfoet_b1nwzida0e0b0xyg, nyatf_b1nwzida0e0b0xyg, period_is_mating_pa1e1b1nwzida0e0b0xyg1[p]
                                                 , index_e1b1nwzida0e0b0xyg)
                    if eqn_used:
                        conception_dams =  temp0
                        # cf_conception_dams = 0 #default set to 0 because required in start production function (only used in lmat conception function)
                    if eqn_compare:
                        r_compare_q0q1q2pdams[eqn_system, eqn_group, 0, p, ...] = temp0
            eqn_system = 1 # MU LTW = 0
            if uinp.sheep['i_eqn_exists_q0q1'][eqn_group, eqn_system]:  # proceed with call & assignment if this system exists for this group
                eqn_used = (eqn_used_g1_q1p[eqn_group, p] == eqn_system)
                if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                    temp0 = sfun.f_conception_ltw(cf_dams, cu0_dams, relsize_mating_dams, cs_mating_dams, scan_std_yg1, doy_pa1e1b1nwzida0e0b0xyg[p]
                                                  , nfoet_b1nwzida0e0b0xyg, nyatf_b1nwzida0e0b0xyg, period_is_mating_pa1e1b1nwzida0e0b0xyg1[p]
                                                  , index_e1b1nwzida0e0b0xyg)
                    ## these variables need to be stored even if the equation system is not used so that the equations can be compared
                    cf_conception_dams = 0  #default set to 0 because required in start production function (only used in lmat conception function)
                    if eqn_used:
                        conception_dams = temp0
                    if eqn_compare:
                        r_compare_q0q1q2pdams[eqn_system, eqn_group, 0, p, ...] = temp0

            ##Scanning percentage per ewe scanned (if scanning) -  report variable only
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                t_scanning = np.sum(numbers_start_dams * nfoet_b1nwzida0e0b0xyg, axis=prejoin_tup, keepdims=True) / np.sum(numbers_start_dams, axis=prejoin_tup, keepdims=True) * period_is_scan_pa1e1b1nwzida0e0b0xyg1[p]
                ##Scanning percentage per ewe scanned (if scanning)
                scanning = fun.f_update(scanning, t_scanning, period_is_scan_pa1e1b1nwzida0e0b0xyg1[p])


            ## base mortality
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg0[p,...] >0):
                mortality_sire = sfun.f_mortality_base(cd_sire, cg_sire, rc_start_sire, ebg_sire, d_nw_max_pa1e1b1nwzida0e0b0xyg0[p], days_period_pa1e1b1nwzida0e0b0xyg0[p])
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                mortality_dams = sfun.f_mortality_base(cd_dams, cg_dams, rc_start_dams, ebg_dams, d_nw_max_pa1e1b1nwzida0e0b0xyg1[p], days_period_pa1e1b1nwzida0e0b0xyg1[p])
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg2[p,...] >0):
                mortality_yatf = sfun.f_mortality_base(cd_yatf, cg_yatf, rc_start_yatf, ebg_yatf, d_nw_max_yatf, days_period_pa1e1b1nwzida0e0b0xyg2[p])
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg3[p,...] >0):
                mortality_offs = sfun.f_mortality_base(cd_offs, cg_offs, rc_start_offs, ebg_offs, d_nw_max_pa1e1b1nwzida0e0b0xyg3[p], days_period_pa1e1b1nwzida0e0b0xyg3[p])

            ## weaner mortality
            eqn_group = 2
            eqn_system = 0 # CSIRO = 0
            ####sire
            if uinp.sheep['i_eqn_exists_q0q1'][eqn_group, eqn_system]:  # proceed with call & assignment if this system exists for this group
                eqn_used = (eqn_used_g0_q1p[eqn_group, p] == eqn_system)
                if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg0[p,...] >0):
                    temp0 = sfun.f_mortality_weaner_cs(cd_sire, cg_sire, age_pa1e1b1nwzida0e0b0xyg0[p], ebg_sire
                                        , d_nw_max_pa1e1b1nwzida0e0b0xyg0[p], days_period_pa1e1b1nwzida0e0b0xyg0[p])
                    if eqn_used:
                        mortality_sire += temp0
                    if eqn_compare:
                        r_compare_q0q1q2psire[eqn_system, eqn_group, 0, p, ...] = temp0
            ####dams
            if uinp.sheep['i_eqn_exists_q0q1'][eqn_group, eqn_system]:  # proceed with call & assignment if this system exists for this group
                eqn_used = (eqn_used_g1_q1p[eqn_group, p] == eqn_system)
                if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                    temp0 = sfun.f_mortality_weaner_cs(cd_dams, cg_dams, age_pa1e1b1nwzida0e0b0xyg1[p], ebg_dams
                                        , d_nw_max_pa1e1b1nwzida0e0b0xyg1[p], days_period_pa1e1b1nwzida0e0b0xyg1[p])
                    if eqn_used:
                        mortality_dams += temp0
                    if eqn_compare:
                        r_compare_q0q1q2pdams[eqn_system, eqn_group, 0, p, ...] = temp0
            ####offs
            if uinp.sheep['i_eqn_exists_q0q1'][eqn_group, eqn_system]:  # proceed with call & assignment if this system exists for this group
                eqn_used = (eqn_used_g3_q1p[eqn_group, p] == eqn_system)
                if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg3[p,...] >0):
                    temp0 = sfun.f_mortality_weaner_cs(cd_offs, cg_offs, age_pa1e1b1nwzida0e0b0xyg3[p], ebg_offs
                                        , d_nw_max_pa1e1b1nwzida0e0b0xyg3[p], days_period_pa1e1b1nwzida0e0b0xyg3[p])
                    if eqn_used:
                        mortality_offs += temp0
                    if eqn_compare:
                        r_compare_q0q1q2poffs[eqn_system, eqn_group, 0, p, ...] = temp0

            ## dam mortality - Peri-natal Dam mortality
            eqn_group = 3
            eqn_system = 0 # CSIRO = 0
            if uinp.sheep['i_eqn_exists_q0q1'][eqn_group, eqn_system]:  # proceed with call & assignment if this system exists for this group
                eqn_used = (eqn_used_g1_q1p[eqn_group, p] == eqn_system)
                if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                    temp0 = sfun.f_mortality_dam_cs(cb1_dams, cg_dams, nw_start_dams, ebg_dams, days_period_pa1e1b1nwzida0e0b0xyg1[p]
                                                    , period_between_birth6wks_pa1e1b1nwzida0e0b0xyg1[p], gest_propn_pa1e1b1nwzida0e0b0xyg1[p]
                                                    , sen.sar['mortalitye'])
                    if eqn_used:
                        mortality_dams += temp0
                    if eqn_compare:
                        r_compare_q0q1q2pdams[eqn_system, eqn_group, 0, p, ...] = temp0
            eqn_system = 1 # mu = 1
            if uinp.sheep['i_eqn_exists_q0q1'][eqn_group, eqn_system]:  # proceed with call & assignment if this system exists for this group
                eqn_used = (eqn_used_g1_q1p[eqn_group, p] == eqn_system)
                if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                    temp0 = sfun.f_mortality_dam_mu(cu2_dams, cs_start_dams, period_is_birth_pa1e1b1nwzida0e0b0xyg1[p]
                                                    , days_period_pa1e1b1nwzida0e0b0xyg1[p], sen.sar['mortalitye'])
                    if eqn_used:
                        mortality_dams += temp0
                    if eqn_compare:
                        r_compare_q0q1q2pdams[eqn_system, eqn_group, 0, p, ...] = temp0

            ### Peri-natal progeny mortality (progeny survival)
            eqn_group = 1
            eqn_system = 0 # CSIRO = 0
            if uinp.sheep['i_eqn_exists_q0q1'][eqn_group, eqn_system]:  # proceed with call & assignment if this system exists for this group
                eqn_used = (eqn_used_g2_q1p[eqn_group, p] == eqn_system)
                if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg2[p,...] >0):
                    temp0, temp1, temp2 = sfun.f_mortality_progeny_cs(cd_yatf, cb1_yatf, w_b_yatf, rc_start_dams, w_b_exp_y_dams, period_is_birth_pa1e1b1nwzida0e0b0xyg1[p], chill_index_pa1e1b1nwzida0e0b0xygm1[p], nfoet_b1nwzida0e0b0xyg,sen.sar['mortalityp'])
                    if eqn_used:
                        mortality_birth_yatf = temp1 #mortalityd, assign first because it has x axis
                        mortality_birth_yatf += temp0 #mortalityx
                        mortality_dams += temp2 #mortalityd_dams
                    if eqn_compare:
                        r_compare_q0q1q2pyatf[eqn_system, eqn_group, 0, p, ...] = temp0
                        r_compare_q0q1q2pyatf[eqn_system, eqn_group, 1, p, ...] = temp1
            eqn_system = 1 # MU = 1
            if uinp.sheep['i_eqn_exists_q0q1'][eqn_group, eqn_system]:  # proceed with call & assignment if this system exists for this group
                eqn_used = (eqn_used_g2_q1p[eqn_group, p] == eqn_system)
                if (eqn_used or eqn_compare) and np.any(days_period_pa1e1b1nwzida0e0b0xyg2[p,...] >0):
                    ##calculate the standard BW which is used in the paddock level scaling
                    w_b_ltw_std_yatf, t_cf = sfun.f_birthweight_mu(cu1_yatf, cb1_yatf, cx_yatf[:,mask_x,...], ce_yatf[:,p-1,...], w_b_ltw_std_yatf
                                                         , 0, nw_start_dams , 0, days_period_pa1e1b1nwzida0e0b0xyg1[p]
                                                         , gest_propn_pa1e1b1nwzida0e0b0xyg1[p],  period_between_joinscan_pa1e1b1nwzida0e0b0xyg1[p]
                                                         , period_between_scanbirth_pa1e1b1nwzida0e0b0xyg1[p], period_is_birth_pa1e1b1nwzida0e0b0xyg1[p])
                    temp0 = sfun.f_mortality_progeny_mu(cu2_yatf, cb1_yatf, cx_yatf[:,mask_x,...], ce_yatf[:,p,...], w_b_yatf, w_b_ltw_std_yatf
                                                        , foo_yatf, chill_index_pa1e1b1nwzida0e0b0xygm1[p], period_is_birth_pa1e1b1nwzida0e0b0xyg1[p]
                                                        , sen.sar['mortalityp'])
                    if eqn_used:
                        mortality_birth_yatf = temp0 #mortalityx
                    if eqn_compare:
                        r_compare_q0q1q2pyatf[eqn_system, eqn_group, 0, p, ...] = temp0


            ##end numbers - accounts for mortality and other activity during the period - this is the number in the different classes as at the end of the period
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg0[p,...] >0):
                numbers_end_sire, pp_numbers_end_sire = sfun.f_period_end_nums(numbers_start_sire, mortality_sire, numbers_min_b1nwzida0e0b0xyg, group=0)
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                numbers_end_dams, pp_numbers_end_dams = sfun.f_period_end_nums(numbers_start_dams, mortality_dams, numbers_min_b1nwzida0e0b0xyg, mortality_yatf=mortality_birth_yatf, nfoet_b1=nfoet_b1nwzida0e0b0xyg,
                                                     nyatf_b1=nyatf_b1nwzida0e0b0xyg, group=1, conception=conception_dams, scan= scan_pa1e1b1nwzida0e0b0xyg1[p],
                                                     gbal = gbal_pa1e1b1nwzida0e0b0xyg1[p], gender_propn_x=gender_propn_xyg, period_is_mating = period_is_mating_pa1e1b1nwzida0e0b0xyg1[p],
                                                     period_is_matingend=period_is_matingend_pa1e1b1nwzida0e0b0xyg1[p],
                                                     period_is_birth = period_is_birth_pa1e1b1nwzida0e0b0xyg1[p], period_is_scan=period_is_scan_pa1e1b1nwzida0e0b0xyg1[p])
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg2[p,...] >0):
                numbers_end_yatf, pp_numbers_end_yatf = sfun.f_period_end_nums(numbers_start_yatf, mortality_yatf, numbers_min_b1nwzida0e0b0xyg, group=2)
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg3[p,...] >0):
                numbers_end_offs, pp_numbers_end_offs = sfun.f_period_end_nums(numbers_start_offs, mortality_offs, numbers_min_b1nwzida0e0b0xyg, group=3)

            ##############
            ##end values #
            ##############
            ###sire
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg0[p,...] >0):
                ##FFCFW (end - fleece free conceptus free)
                ffcfw_sire = np.maximum(0,ffcfw_start_sire + cg_sire[18, ...] * ebg_sire * days_period_pa1e1b1nwzida0e0b0xyg0[p])
                ##FFCFW maximum to date
                ffcfw_max_sire = np.maximum(ffcfw_sire, ffcfw_max_start_sire)
                ##Weight of fat adipose (end)
                aw_sire = aw_start_sire + fg_sire / cg_sire[20, ...] * days_period_pa1e1b1nwzida0e0b0xyg0[p]
                ##Weight of muscle (end)
                mw_sire = mw_start_sire + pg_sire / cg_sire[19, ...] * days_period_pa1e1b1nwzida0e0b0xyg0[p]
                ##Weight of bone (end)	bw ^formula needs finishing
                bw_sire = bw_start_sire
                ##Weight of water (end - if above are dry matter)
                ww_sire = mw_sire * (1 - cg_sire[19, ...]) + aw_sire * (1 - cg_sire[20, ...])
                ##Weight of gutfill (end)
                gw_sire = ffcfw_sire* (1 - 1 / cg_sire[18, ...])
                ##Clean fleece weight (end)
                cfw_sire = cfw_start_sire + d_cfw_sire * days_period_pa1e1b1nwzida0e0b0xyg0[p] * cfw_propn_yg0
                ##Greasy fleece weight (end)
                gfw_sire = cfw_sire / cw_sire[3, ...]
                ##LW with conceptus and fleece (end)
                lw_sire = ffcfw_sire + gfw_sire
                ##Fibre length since shearing (end)
                fl_sire = fl_start_sire + d_fl_sire * days_period_pa1e1b1nwzida0e0b0xyg0[p]
                ##Average FD since shearing (end)
                fd_sire = (fl_start_sire * fd_start_sire + d_fl_sire * days_period_pa1e1b1nwzida0e0b0xyg0[p] * d_fd_sire) / fl_sire
                ##Minimum FD since shearing (end)
                fd_min_sire = np.minimum(fd_min_start_sire, d_fd_sire)
                ##Staple length if shorn(end)
                sl_sire = (fl_sire - fl_shear_yg0) / cw_sire[15, ...]
                ##Staple strength if shorn(end)
                ss_sire = fd_min_sire**2 / fd_sire **2 * cw_sire[16, ...]



        ###dams
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                ##FFCFW (end - fleece free conceptus free)
                ffcfw_dams = np.maximum(0,ffcfw_start_dams + cg_dams[18, ...] * ebg_dams * days_period_pa1e1b1nwzida0e0b0xyg1[p])
                ##FFCFW maximum to date
                ffcfw_max_dams = np.maximum(ffcfw_dams, ffcfw_max_start_dams)
                ##Weight of fat adipose (end)
                aw_dams = aw_start_dams + fg_dams / cg_dams[20, ...] * days_period_pa1e1b1nwzida0e0b0xyg1[p]
                ##Weight of muscle (end)
                mw_dams = mw_start_dams + pg_dams / cg_dams[19, ...] * days_period_pa1e1b1nwzida0e0b0xyg1[p]
                ##Weight of bone (end)	bw ^formula needs finishing
                bw_dams = bw_start_dams
                ##Weight of water (end - if above are dry matter)
                ww_dams = mw_dams * (1 - cg_dams[19, ...]) + aw_dams * (1 - cg_dams[20, ...])
                ##Weight of gutfill (end)
                gw_dams = ffcfw_dams* (1 - 1 / cg_dams[18, ...])
                ##Clean fleece weight (end)
                cfw_dams = cfw_start_dams + d_cfw_dams * days_period_pa1e1b1nwzida0e0b0xyg1[p] * cfw_propn_yg1
                ##Greasy fleece weight (end)
                gfw_dams = cfw_dams / cw_dams[3, ...]
                ##LW with conceptus and fleece (end)
                lw_dams = ffcfw_dams + guw_dams + gfw_dams
                ##Fibre length since shearing (end)
                fl_dams = fl_start_dams + d_fl_dams * days_period_pa1e1b1nwzida0e0b0xyg1[p]
                ##Average FD since shearing (end)
                fd_dams = (fl_start_dams * fd_start_dams + d_fl_dams * days_period_pa1e1b1nwzida0e0b0xyg1[p] * d_fd_dams) / fl_dams
                ##Minimum FD since shearing (end)
                fd_min_dams = np.minimum(fd_min_start_dams, d_fd_dams)
                ##Staple length if shorn(end)
                sl_dams = (fl_dams - fl_shear_yg0) / cw_dams[15, ...]
                ##Staple strength if shorn(end)
                ss_dams = fd_min_dams ** 2 / fd_dams ** 2 * cw_dams[16, ...]


        ###yatf
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg2[p,...] >0):
                ##FFCFW (end - fleece free conceptus free)
                ffcfw_yatf = np.maximum(0,ffcfw_start_yatf + cg_yatf[18, ...] * ebg_yatf * days_period_pa1e1b1nwzida0e0b0xyg2[p])
                ##FFCFW maximum to date
                ffcfw_max_yatf = np.maximum(ffcfw_yatf, ffcfw_max_start_yatf)
                ##Weight of fat adipose (end)
                aw_yatf = aw_start_yatf + fg_yatf / cg_yatf[20, ...] * days_period_pa1e1b1nwzida0e0b0xyg2[p]
                ##Weight of muscle (end)
                mw_yatf = mw_start_yatf + pg_yatf / cg_yatf[19, ...] * days_period_pa1e1b1nwzida0e0b0xyg2[p]
                ##Weight of bone (end)	bw ^formula needs finishing
                bw_yatf = bw_start_yatf
                ##Weight of water (end - if above are dry matter)
                ww_yatf = mw_yatf * (1 - cg_yatf[19, ...]) + aw_yatf * (1 - cg_yatf[20, ...])
                ##Weight of gutfill (end)
                gw_yatf = ffcfw_yatf* (1 - 1 / cg_yatf[18, ...])
                ##Clean fleece weight (end)
                cfw_yatf = cfw_start_yatf + d_cfw_yatf * days_period_pa1e1b1nwzida0e0b0xyg2[p] * cfw_propn_yg2
                ##Greasy fleece weight (end)
                gfw_yatf = cfw_yatf / cw_yatf[3, ...]
                ##LW with conceptus and fleece (end)
                lw_yatf = ffcfw_yatf + gfw_yatf
                ##Fibre length since shearing (end)
                fl_yatf = fl_start_yatf + d_fl_yatf * days_period_pa1e1b1nwzida0e0b0xyg2[p]
                ##Average FD since shearing (end)
                fd_yatf = (fl_start_yatf * fd_start_yatf + d_fl_yatf * days_period_pa1e1b1nwzida0e0b0xyg2[p] * d_fd_yatf) / fl_yatf #d_fd is actually the fd of the weeks growth. Not the change in fd.
                ##Minimum FD since shearing (end)
                fd_min_yatf = np.minimum(fd_min_start_yatf, d_fd_yatf) #d_fd is actually the fd of the weeks growth. Not the change in fd.
                ##Staple length if shorn(end)
                sl_yatf = (fl_yatf - fl_shear_yg0) / cw_yatf[15, ...]
                ##Staple strength if shorn(end)
                ss_yatf = fun.f_divide(fd_min_yatf ** 2 , fd_yatf ** 2 * cw_yatf[16, ...])

            ###offs
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg3[p,...] >0):
                ##FFCFW (end - fleece free conceptus free)
                ffcfw_offs = np.maximum(0,ffcfw_start_offs + cg_offs[18, ...] * ebg_offs * days_period_pa1e1b1nwzida0e0b0xyg3[p])
                ##FFCFW maximum to date
                ffcfw_max_offs = np.maximum(ffcfw_offs, ffcfw_max_start_offs)
                ##Weight of fat adipose (end)
                aw_offs = aw_start_offs + fg_offs / cg_offs[20, ...] * days_period_pa1e1b1nwzida0e0b0xyg3[p]
                ##Weight of muscle (end)
                mw_offs = mw_start_offs + pg_offs / cg_offs[19, ...] * days_period_pa1e1b1nwzida0e0b0xyg3[p]
                ##Weight of bone (end)	bw ^formula needs finishing
                bw_offs = bw_start_offs
                ##Weight of water (end - if above are dry matter)
                ww_offs = mw_offs * (1 - cg_offs[19, ...]) + aw_offs * (1 - cg_offs[20, ...])
                ##Weight of gutfill (end)
                gw_offs = ffcfw_offs* (1 - 1 / cg_offs[18, ...])
                ##Clean fleece weight (end)
                cfw_offs = cfw_start_offs + d_cfw_offs * days_period_pa1e1b1nwzida0e0b0xyg3[p] * cfw_propn_yg3
                ##Greasy fleece weight (end)
                gfw_offs = cfw_offs / cw_offs[3, ...]
                ##LW with conceptus and fleece (end)
                lw_offs = ffcfw_offs + gfw_offs
                ##Fibre length since shearing (end)
                fl_offs = fl_start_offs + d_fl_offs * days_period_pa1e1b1nwzida0e0b0xyg3[p]
                ##Average FD since shearing (end)
                fd_offs = (fl_start_offs * fd_start_offs + d_fl_offs * days_period_pa1e1b1nwzida0e0b0xyg3[p] * d_fd_offs) / fl_offs
                ##Minimum FD since shearing (end)
                fd_min_offs = np.minimum(fd_min_start_offs, d_fd_offs)
                ##Staple length if shorn(end)
                sl_offs = (fl_offs - fl_shear_yg0) / cw_offs[15, ...]
                ##Staple strength if shorn(end)
                ss_offs = fd_min_offs ** 2 / fd_offs ** 2 * cw_offs[16, ...]

            ######################################
            #store postprocessing and report vars#
            ######################################
            ###sire
            o_numbers_start_psire[p] = numbers_start_sire  # needed outside if so that dvp0 (p0) has start numbers
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg0[p, ...] > 0):
                ###store output variables for the post processing
                o_numbers_end_psire[p] = pp_numbers_end_sire
                o_ffcfw_psire[p] = ffcfw_sire
                o_lw_psire[p] = lw_sire
                o_pi_psire[p] = pi_sire
                o_mei_solid_psire[p] = mei_solid_sire
                o_ch4_total_psire[p] = ch4_total_sire
                o_cfw_psire[p] = cfw_sire
                o_sl_psire[p] = sl_sire
                o_fd_psire[p] = fd_sire
                o_fd_min_psire[p] = fd_min_sire
                o_ss_psire[p] = ss_sire
                o_rc_start_psire[p] = rc_start_sire
                o_ebg_psire[p] = ebg_sire

                ###store report variables for dams - individual variables can be deleted if not needed - store in report dictionary in the report section at end of this module
                o_nw_start_psire[p] = nw_start_sire

        ###dams
            o_numbers_start_pdams[p] = numbers_start_dams #needed outside if so that dvp0 (p0) has start numbers
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                ###store output variables for the post processing
                o_numbers_end_pdams[p] = pp_numbers_end_dams
                ###store the start numbers at prejoining - used to scale numbers when back dating from mating to prejoining
                if np.any(period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p]):
                    t_numbers_start_prejoin = fun.f_update(t_numbers_start_prejoin, numbers_start_dams, period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p])
                if np.any(period_is_mating_pa1e1b1nwzida0e0b0xyg1[p]): #need to back date the numbers from conception to prejoining because otherwise in the matrix there is not a dvp between prejoining and mating therefore this is require so that other slices have energy etc requirement
                    ###period is between prejoining and the end of current period (testing this for each p slice)
                    between_prejoinnow = sfun.f_period_is_('period_is_between', date_prejoin_pa1e1b1nwzida0e0b0xyg1[p], date_start_pa1e1b1nwzida0e0b0xyg, date_end_pa1e1b1nwzida0e0b0xyg[p], date_end_pa1e1b1nwzida0e0b0xyg)
                    ###if period is mating back date the end number after mating to all the periods since prejoining
                    o_numbers_end_pdams = fun.f_update(o_numbers_end_pdams, pp_numbers_end_dams.astype(dtype), (period_is_matingend_pa1e1b1nwzida0e0b0xyg1[p] * between_prejoinnow))
                    ###scale end numbers (to account for mortality) before back dating to the start (only start numbers need scaling because end numbers don't need to be correct at the start of the dvp)
                    t_scaled_numbers = pp_numbers_end_dams * (np.sum(t_numbers_start_prejoin, axis=(e1_pos,b1_pos)) / np.sum(pp_numbers_end_dams, axis=(e1_pos,b1_pos)))
                    o_numbers_start_pdams = fun.f_update(o_numbers_start_pdams, t_scaled_numbers.astype(dtype), (period_is_matingend_pa1e1b1nwzida0e0b0xyg1[p] * between_prejoinnow))
                o_ffcfw_pdams[p] = ffcfw_dams
                o_ffcfw_condensed_pdams[p] = sfun.f_condensed(numbers_end_dams, ffcfw_dams, prejoin_tup, season_tup, uinp.structure['i_n1_len'], uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_dams,
                                    period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1])  #condensed lw at the end of the period before fvp0
                o_nw_start_pdams[p] = nw_start_dams
                numbers_join_dams = fun.f_update(numbers_join_dams, numbers_start_dams, period_is_join_pa1e1b1nwzida0e0b0xyg1[p])
                o_numbers_join_pdams[p] = numbers_join_dams #store the numbers at joining until next
                o_lw_pdams[p] = lw_dams
                o_pi_pdams[p] = pi_dams
                o_mei_solid_pdams[p] = mei_solid_dams
                o_ch4_total_pdams[p] = ch4_total_dams
                o_cfw_pdams[p] = cfw_dams
                # o_gfw_pdams[p] = gfw_dams
                o_sl_pdams[p] = sl_dams
                o_fd_pdams[p] = fd_dams
                o_fd_min_pdams[p] = fd_min_dams
                o_ss_pdams[p] = ss_dams
                o_n_sire_pa1e1b1nwzida0e0b0xyg1g0p8[p] = n_sire_a1e1b1nwzida0e0b0xyg1g0p8
                o_rc_start_pdams[p] = rc_start_dams
                o_ebg_pdams[p] = ebg_dams
                o_cfw_ltwadj_pdams[p] = cfw_ltwadj_dams
                o_fd_ltwadj_pdams[p] = fd_ltwadj_dams

                ###store report variables for dams - individual variables can be deleted if not needed - store in report dictionary in the report section at end of this module
                r_intake_f_pdams[p] = intake_f_dams
                r_md_solid_pdams[p] = md_solid_dams
                r_foo_pdams[p] = foo_dams
                r_dmd_pdams[p] = dmd_dams
                r_evg_pdams[p] = evg_dams
                r_mp2_pdams[p] = mp2_dams
                r_d_cfw_pdams[p] = d_cfw_dams


            ###yatf
            o_ffcfw_start_pyatf[p] = ffcfw_start_yatf #use ffcfw_start because weaning start of period, has to be outside of the 'if' because days per period = 0 when weaning occurs because weaning is first day of period. But we need to know the start ffcfw.
            o_numbers_start_pyatf[p] = numbers_start_yatf #used for npw calculation - use numbers start because weaning is start of period - has to be out of the 'if' because there is 0 days in the period when weaning occurs but we still want to store the start weight
            o_rc_start_pyatf[p] = rc_start_yatf #outside because used for sale value which is weaning which has 0 days per period because weaning is first day (this means the rc at weaning is actually the rc at the start of the previous period because it doesnt recalculate once days per period goes to 0)
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg2[p,...] >0):
                ###store output variables for the post processing
                # o_numbers_end_pyatf[p] = pp_numbers_end_yatf
                o_pi_pyatf[p] = pi_yatf
                o_mei_solid_pyatf[p] = mei_solid_yatf
                # o_ch4_total_pyatf[p] = ch4_total_yatf
                # o_cfw_pyatf[p] = cfw_yatf
                # o_gfw_pyatf[p] = gfw_yatf
                # o_sl_pyatf[p] = sl_yatf
                # o_fd_pyatf[p] = fd_yatf
                # o_fd_min_pyatf[p] = fd_min_yatf
                # o_ss_pyatf[p] = ss_yatf

                ###store report variables - individual variables can be deleted if not needed - store in report dictionary in the report section at end of this module
                r_ebg_pyatf[p] = ebg_yatf
                r_evg_pyatf[p] = evg_yatf
                r_mp2_pyatf[p] = mp2_yatf
                r_mem_pyatf[p] = mem_yatf
                r_mei_pyatf[p] = mei_yatf
                r_mei_solid_pyatf[p] = mei_solid_yatf
                r_propn_solid_pyatf[p] = mei_propn_herb_yatf
                r_pi_pyatf[p] = pi_yatf
                r_kg_pyatf[p] = kg_yatf
                r_intake_f_pyatf[p] = intake_f_yatf
                r_nw_start_pyatf[p] = nw_start_yatf



        ###offs
            try:
                o_numbers_start_poffs[p] = numbers_start_offs  # needed outside if so that dvp0 (p0) has start numbers. this will raise exception when p is greater that len offs p
            except IndexError:
                pass
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg3[p,...] >0):
                ###store output variables for the post processing
                o_numbers_end_poffs[p] = numbers_end_offs
                o_ffcfw_poffs[p] = ffcfw_offs
                o_ffcfw_condensed_poffs[p] = sfun.f_condensed(numbers_end_offs, ffcfw_offs, prejoin_tup, season_tup, uinp.structure['i_n3_len'], uinp.structure['i_w3_len'], uinp.structure['i_n_fvp_period3'], numbers_start_fvp0_offs,
                                                             period_is_startfvp0_pa1e1b1nwzida0e0b0xyg3[p+1])  #condensed lw at the end of the period before fvp0
                o_lw_poffs[p] = lw_offs
                o_pi_poffs[p] = pi_offs
                o_mei_solid_poffs[p] = mei_solid_offs
                o_ch4_total_poffs[p] = ch4_total_offs
                o_cfw_poffs[p] = cfw_offs
                # o_gfw_poffs[p] = gfw_offs
                o_sl_poffs[p] = sl_offs
                o_fd_poffs[p] = fd_offs
                o_fd_min_poffs[p] = fd_min_offs
                o_ss_poffs[p] = ss_offs
                o_rc_start_poffs[p] = rc_start_offs
                o_ebg_poffs[p] = ebg_offs

                ###store report variables - individual variables can be deleted if not needed - store in report dictionary in the report section at end of this module
                o_nw_start_poffs[p] = nw_start_offs

            ###########################
            #stuff for next period    #
            ###########################

            ##start production
            ###sire
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg0[p,...] >0):
                ###FFCFW (start - fleece free conceptus free)
                ffcfw_start_sire = sfun.f_period_start_prod(numbers_end_sire, ffcfw_sire, prejoin_tup, season_tup, uinp.structure['i_n0_len']
                                        , uinp.structure['i_w0_len'], uinp.structure['i_n_fvp_period0'], numbers_start_fvp0_sire
                                        , False, period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])  #increment the p slice, note this doesnt impact the p loop - this is required for the next section because we are calculating the production and numbers for the start of the next period.
                ###FFCFW (start - fleece free conceptus free)	- yes this is meant to be updated from nw_start
                nw_start_sire = sfun.f_period_start_prod(numbers_end_sire, nw_start_sire, prejoin_tup, season_tup, uinp.structure['i_n0_len']
                                        , uinp.structure['i_w0_len'], uinp.structure['i_n_fvp_period0'], numbers_start_fvp0_sire
                                        , False, period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])  #increment the p slice, note this doesnt impact the p loop - this is required for the next section because we are calculating the production and numbers for the start of the next period.
                ###FFCFW maximum to date
                ffcfw_max_start_sire = sfun.f_period_start_prod(numbers_end_sire, ffcfw_max_sire, prejoin_tup, season_tup, uinp.structure['i_n0_len']
                                        , uinp.structure['i_w0_len'], uinp.structure['i_n_fvp_period0'], numbers_start_fvp0_sire
                                        , False, period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])  #increment the p slice, note this doesnt impact the p loop - this is required for the next section because we are calculating the production and numbers for the start of the next period.
                ###Weight of adipose (start)
                aw_start_sire = sfun.f_period_start_prod(numbers_end_sire, aw_sire, prejoin_tup, season_tup, uinp.structure['i_n0_len']
                                        , uinp.structure['i_w0_len'], uinp.structure['i_n_fvp_period0'], numbers_start_fvp0_sire
                                        , False, period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])  #increment the p slice, note this doesnt impact the p loop - this is required for the next section because we are calculating the production and numbers for the start of the next period.
                ###Weight of muscle (start)
                mw_start_sire = sfun.f_period_start_prod(numbers_end_sire, mw_sire, prejoin_tup, season_tup, uinp.structure['i_n0_len']
                                        , uinp.structure['i_w0_len'], uinp.structure['i_n_fvp_period0'], numbers_start_fvp0_sire
                                        , False, period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])  #increment the p slice, note this doesnt impact the p loop - this is required for the next section because we are calculating the production and numbers for the start of the next period.
                ###Weight of bone (start)
                bw_start_sire = sfun.f_period_start_prod(numbers_end_sire, bw_sire, prejoin_tup, season_tup, uinp.structure['i_n0_len']
                                        , uinp.structure['i_w0_len'], uinp.structure['i_n_fvp_period0'], numbers_start_fvp0_sire
                                        , False, period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])  #increment the p slice, note this doesnt impact the p loop - this is required for the next section because we are calculating the production and numbers for the start of the next period.
                ###Organ energy requirement (start)
                omer_history_start_m3g0 = sfun.f_period_start_prod(numbers_end_sire, omer_history_sire, prejoin_tup, season_tup, uinp.structure['i_n0_len']
                                        , uinp.structure['i_w0_len'], uinp.structure['i_n_fvp_period0'], numbers_start_fvp0_sire
                                        , False, period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])  #increment the p slice, note this doesnt impact the p loop - this is required for the next section because we are calculating the production and numbers for the start of the next period.
                ###Clean fleece weight (start)
                cfw_start_sire = sfun.f_period_start_prod(numbers_end_sire, cfw_sire, prejoin_tup, season_tup, uinp.structure['i_n0_len']
                                        , uinp.structure['i_w0_len'], uinp.structure['i_n_fvp_period0'], numbers_start_fvp0_sire
                                        , False, period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])  #increment the p slice, note this doesnt impact the p loop - this is required for the next section because we are calculating the production and numbers for the start of the next period.
                ###Clean fleece weight (start)
                d_cfw_history_start_m2g0 = sfun.f_period_start_prod(numbers_end_sire, d_cfw_history_sire_m2, prejoin_tup, season_tup, uinp.structure['i_n0_len']
                                        , uinp.structure['i_w0_len'], uinp.structure['i_n_fvp_period0'], numbers_start_fvp0_sire
                                        , False, period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])  #increment the p slice, note this doesnt impact the p loop - this is required for the next section because we are calculating the production and numbers for the start of the next period.
                ###Fibre length since shearing (start)
                fl_start_sire = sfun.f_period_start_prod(numbers_end_sire, fl_sire, prejoin_tup, season_tup, uinp.structure['i_n0_len']
                                        , uinp.structure['i_w0_len'], uinp.structure['i_n_fvp_period0'], numbers_start_fvp0_sire
                                        , False, period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])  #increment the p slice, note this doesnt impact the p loop - this is required for the next section because we are calculating the production and numbers for the start of the next period.
                ###Average FD since shearing (start)
                fd_start_sire = sfun.f_period_start_prod(numbers_end_sire, fd_sire, prejoin_tup, season_tup, uinp.structure['i_n0_len']
                                        , uinp.structure['i_w0_len'], uinp.structure['i_n_fvp_period0'], numbers_start_fvp0_sire
                                        , False, period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])  #increment the p slice, note this doesnt impact the p loop - this is required for the next section because we are calculating the production and numbers for the start of the next period.
                ###Minimum FD since shearing (start)
                fd_min_start_sire = sfun.f_period_start_prod(numbers_end_sire, fd_min_sire, prejoin_tup, season_tup, uinp.structure['i_n0_len']
                                        , uinp.structure['i_w0_len'], uinp.structure['i_n_fvp_period0'], numbers_start_fvp0_sire
                                        , False, period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])  #increment the p slice, note this doesnt impact the p loop - this is required for the next section because we are calculating the production and numbers for the start of the next period.

            ###dams
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                ###FFCFW (start - fleece free conceptus free)
                ffcfw_start_dams = sfun.f_period_start_prod(numbers_end_dams, ffcfw_dams, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                        , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_dams
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1]
                                        , period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p+1], group=1)
                ###normal weight	- yes this is meant to be updated from nw_start
                nw_start_dams = sfun.f_period_start_prod(numbers_end_dams, nw_start_dams, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                        , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_dams
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1]
                                        , period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p+1], group=1)
                ###FFCFW maximum to date
                ffcfw_max_start_dams = sfun.f_period_start_prod(numbers_end_dams, ffcfw_max_dams, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                        , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_dams
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1]
                                        , period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p+1], group=1)
                ###Weight of adipose (start)
                aw_start_dams = sfun.f_period_start_prod(numbers_end_dams, aw_dams, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                        , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_dams
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1]
                                        , period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p+1], group=1)
                ###Weight of muscle (start)
                mw_start_dams = sfun.f_period_start_prod(numbers_end_dams, mw_dams, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                        , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_dams
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1]
                                        , period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p+1], group=1)
                ###Weight of bone (start)
                bw_start_dams = sfun.f_period_start_prod(numbers_end_dams, bw_dams, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                        , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_dams
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1]
                                        , period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p+1], group=1)
                ###Organ energy requirement (start)
                omer_history_start_m3g1 = sfun.f_period_start_prod(numbers_end_dams, omer_history_dams, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                            , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_dams
                                            , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1]
                                            , period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p+1], group=1)
                ###Clean fleece weight (start)
                cfw_start_dams = sfun.f_period_start_prod(numbers_end_dams, cfw_dams, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                        , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_dams
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1]
                                        , period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p+1], group=1)
                ###Clean fleece weight (start)
                d_cfw_history_start_m2g1 = sfun.f_period_start_prod(numbers_end_dams, d_cfw_history_dams_m2, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                            , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_dams
                                            , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1]
                                            , period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p+1], group=1)
                ###Fibre length since shearing (start)
                fl_start_dams = sfun.f_period_start_prod(numbers_end_dams, fl_dams, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                        , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_dams
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1]
                                        , period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p+1], group=1)
                ###Average FD since shearing (start)
                fd_start_dams = sfun.f_period_start_prod(numbers_end_dams, fd_dams, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                        , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_dams
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1]
                                        , period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p+1], group=1)
                ###Minimum FD since shearing (start)
                fd_min_start_dams = sfun.f_period_start_prod(numbers_end_dams, fd_min_dams, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                        , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_dams
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1]
                                        , period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p+1], group=1)
                ###Lagged DR (lactation deficit)
                ldr_start_dams = sfun.f_period_start_prod(numbers_end_dams, ldr_dams, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                        , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_dams
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1]
                                        , period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p+1], group=1)
                ###Loss of potential milk due to consistent under production
                lb_start_dams = sfun.f_period_start_prod(numbers_end_dams, lb_dams, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                        , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_dams
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1]
                                        , period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p+1], group=1)
                ###Loss of potential milk due to consistent under production
                rc_birth_start_dams = sfun.f_period_start_prod(numbers_end_dams, rc_birth_dams, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                        , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_dams
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1]
                                        , period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p+1], group=1)
                ###Weight of foetus (start)
                w_f_start_dams = sfun.f_period_start_prod(numbers_end_dams, w_f_dams, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                        , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_dams
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1]
                                        , period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p+1], group=1)
                ###Cumulative energy in conceptus (start)- not required with new method calculating change in ce age rather than just
                # nec_cum_start_dams = sfun.f_period_start_prod(numbers_end_dams, nec_cum_dams, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                #                       , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_dams
                #                       , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1]
                #                       , period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p+1], group=1)
                ###Weight of gravid uterus (start)
                guw_start_dams = sfun.f_period_start_prod(numbers_end_dams, guw_dams, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                        , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_dams
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1]
                                        , period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p+1], group=1)
                ###Normal weight of foetus (start)
                nw_f_start_dams = sfun.f_period_start_prod(numbers_end_dams, nw_f_dams, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                        , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_dams
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1]
                                        , period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p+1], group=1)
                ###Birth weight carryover (running tally of foetal weight diff)
                cf_w_b_start_dams = sfun.f_period_start_prod(numbers_end_dams, cf_w_b_dams, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                        , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_dams
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1]
                                        , period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p+1], group=1)
                ###LTW CFW carryover (running tally of CFW diff)
                cf_cfwltw_start_dams = sfun.f_period_start_prod(numbers_end_dams, cf_cfwltw_dams, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                        , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_dams
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1]
                                        , period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p+1], group=1)
                ###LTW FD carryover (running tally of FD diff)
                cf_fdltw_start_dams = sfun.f_period_start_prod(numbers_end_dams, cf_fdltw_dams, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                        , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_dams
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1]
                                        , period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p+1], group=1)
                ##dams LTW CFW (total adjustment, calculated at birth)
                cfw_ltwadj_start_dams = sfun.f_period_start_prod(numbers_end_dams, cfw_ltwadj_dams, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                        , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_dams
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1]
                                        , period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p+1], group=1)
                ##dams LTW FD (total adjustment, calculated at birth)
                fd_ltwadj_start_dams = sfun.f_period_start_prod(numbers_end_dams, fd_ltwadj_dams, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                        , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_dams
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1]
                                        , period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p+1], group=1)

                ###Carry forward conception
                cf_conception_start_dams = sfun.f_period_start_prod(numbers_end_dams, cf_conception_dams, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                                , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_dams
                                                , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1]
                                                , period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p+1], group=1)
                ###Weaning weight carryover (running tally of foetal weight diff)
                cf_w_w_start_dams = sfun.f_period_start_prod(numbers_end_dams, cf_w_w_dams, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                        , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_dams
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1]
                                        , period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p+1], group=1)
                ###Average FOO during lactation (for weaning weight calculation)
                foo_lact_ave_start = sfun.f_period_start_prod(numbers_end_dams, foo_lact_ave, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                        , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_dams
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p + 1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p + 1]
                                        , period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p + 1], group=1)

            ###yatf
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg2[p,...] >0):
                ###FFCFW (start - fleece free conceptus free)
                ffcfw_start_yatf = sfun.f_period_start_prod(numbers_end_yatf, ffcfw_yatf, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                    , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_yatf
                                    , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])
                ###normal weight	- yes this is meant to be updated from nw_start
                nw_start_yatf = sfun.f_period_start_prod(numbers_end_yatf, nw_start_yatf, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                    , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_yatf
                                    , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])
                ###FFCFW maximum to date
                ffcfw_max_start_yatf = sfun.f_period_start_prod(numbers_end_yatf, ffcfw_max_yatf, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                        , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_yatf
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])
                ###Weight of adipose (start)
                aw_start_yatf = sfun.f_period_start_prod(numbers_end_yatf, aw_yatf, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                        , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_yatf
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])
                ###Weight of muscle (start)
                mw_start_yatf = sfun.f_period_start_prod(numbers_end_yatf, mw_yatf, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                    , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_yatf
                                    , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])
                ###Weight of bone (start)
                bw_start_yatf = sfun.f_period_start_prod(numbers_end_yatf, bw_yatf, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                    , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_yatf
                                    , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])
                ###Organ energy requirement (start)
                omer_history_start_m3g2 = sfun.f_period_start_prod(numbers_end_yatf, omer_history_yatf, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                            , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_yatf
                                            , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])
                ###Clean fleece weight (start)
                cfw_start_yatf = sfun.f_period_start_prod(numbers_end_yatf, cfw_yatf, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                    , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_yatf
                                    , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])
                ###Clean fleece weight (start)
                d_cfw_history_start_m2g2 = sfun.f_period_start_prod(numbers_end_yatf, d_cfw_history_yatf_m2, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                            , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_yatf
                                            , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])
                ###Fibre length since shearing (start)
                fl_start_yatf = sfun.f_period_start_prod(numbers_end_yatf, fl_yatf, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                    , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_yatf
                                    , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])
                ###Average FD since shearing (start)
                fd_start_yatf = sfun.f_period_start_prod(numbers_end_yatf, fd_yatf, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                    , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_yatf
                                    , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])
                ###Minimum FD since shearing (start)
                fd_min_start_yatf = sfun.f_period_start_prod(numbers_end_yatf, fd_min_yatf, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                        , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_yatf
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])
                ##yatf birth weight
                w_b_start_yatf = sfun.f_period_start_prod(numbers_end_yatf, w_b_yatf, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                    , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_yatf
                                    , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])
                ##yatf wean weight
                w_w_start_yatf = sfun.f_period_start_prod(numbers_end_yatf, w_w_yatf, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                    , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_yatf
                                    , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])
            ###offs
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg3[p,...] >0):
                ###FFCFW (start - fleece free conceptus free)
                ffcfw_start_offs = sfun.f_period_start_prod(numbers_end_offs, ffcfw_offs, prejoin_tup, season_tup, uinp.structure['i_n3_len']
                                    , uinp.structure['i_w3_len'], uinp.structure['i_n_fvp_period3'], numbers_start_fvp0_offs
                                    , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg3[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])
                ###normal weight	- yes this is meant to be updated from nw_start
                nw_start_offs = sfun.f_period_start_prod(numbers_end_offs, nw_start_offs, prejoin_tup, season_tup, uinp.structure['i_n3_len']
                                    , uinp.structure['i_w3_len'], uinp.structure['i_n_fvp_period3'], numbers_start_fvp0_offs
                                    , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg3[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])
                ###FFCFW maximum to date
                ffcfw_max_start_offs = sfun.f_period_start_prod(numbers_end_offs, ffcfw_max_offs, prejoin_tup, season_tup, uinp.structure['i_n3_len']
                                        , uinp.structure['i_w3_len'], uinp.structure['i_n_fvp_period3'], numbers_start_fvp0_offs
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg3[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])
                ###Weight of adipose (start)
                aw_start_offs = sfun.f_period_start_prod(numbers_end_offs, aw_offs, prejoin_tup, season_tup, uinp.structure['i_n3_len']
                                    , uinp.structure['i_w3_len'], uinp.structure['i_n_fvp_period3'], numbers_start_fvp0_offs
                                    , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg3[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])
                ###Weight of muscle (start)
                mw_start_offs = sfun.f_period_start_prod(numbers_end_offs, mw_offs, prejoin_tup, season_tup, uinp.structure['i_n3_len']
                                    , uinp.structure['i_w3_len'], uinp.structure['i_n_fvp_period3'], numbers_start_fvp0_offs
                                    , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg3[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])
                ###Weight of bone (start)
                bw_start_offs = sfun.f_period_start_prod(numbers_end_offs, bw_offs, prejoin_tup, season_tup, uinp.structure['i_n3_len']
                                    , uinp.structure['i_w3_len'], uinp.structure['i_n_fvp_period3'], numbers_start_fvp0_offs
                                    , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg3[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])
                ###Organ energy requirement (start)
                omer_history_start_m3g3 = sfun.f_period_start_prod(numbers_end_offs, omer_history_offs, prejoin_tup, season_tup, uinp.structure['i_n3_len']
                                            , uinp.structure['i_w3_len'], uinp.structure['i_n_fvp_period3'], numbers_start_fvp0_offs
                                            , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg3[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])
                ###Clean fleece weight (start)
                cfw_start_offs = sfun.f_period_start_prod(numbers_end_offs, cfw_offs, prejoin_tup, season_tup, uinp.structure['i_n3_len']
                                    , uinp.structure['i_w3_len'], uinp.structure['i_n_fvp_period3'], numbers_start_fvp0_offs
                                    , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg3[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])
                ###Clean fleece weight (start)
                d_cfw_history_start_m2g3 = sfun.f_period_start_prod(numbers_end_offs, d_cfw_history_offs_m2, prejoin_tup, season_tup, uinp.structure['i_n3_len']
                                            , uinp.structure['i_w3_len'], uinp.structure['i_n_fvp_period3'], numbers_start_fvp0_offs
                                            , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg3[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])
                ###Fibre length since shearing (start)
                fl_start_offs = sfun.f_period_start_prod(numbers_end_offs, fl_offs, prejoin_tup, season_tup, uinp.structure['i_n3_len']
                                    , uinp.structure['i_w3_len'], uinp.structure['i_n_fvp_period3'], numbers_start_fvp0_offs
                                    , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg3[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])
                ###Average FD since shearing (start)
                fd_start_offs = sfun.f_period_start_prod(numbers_end_offs, fd_offs, prejoin_tup, season_tup, uinp.structure['i_n3_len']
                                    , uinp.structure['i_w3_len'], uinp.structure['i_n_fvp_period3'], numbers_start_fvp0_offs
                                    , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg3[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])
                ###Minimum FD since shearing (start)
                fd_min_start_offs = sfun.f_period_start_prod(numbers_end_offs, fd_min_offs, prejoin_tup, season_tup, uinp.structure['i_n3_len']
                                        , uinp.structure['i_w3_len'], uinp.structure['i_n_fvp_period3'], numbers_start_fvp0_offs
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg3[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1])




            ##start numbers - has to be after production because the numbers are being calced for the current period and are used in the start production function
            if np.any(days_period_pa1e1b1nwzida0e0b0xyg0[p,...] >0):
                numbers_start_sire = sfun.f_period_start_nums(numbers_end_sire, prejoin_tup, season_tup, uinp.structure['i_n0_len']
                                            , uinp.structure['i_w0_len'], uinp.structure['i_n_fvp_period0'], numbers_start_fvp0_sire
                                            , False, period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1], season_propn_zida0e0b0xyg, group=0)
                ###numbers at the beginning of fvp 0 (used to calc mort for the lw patterns to determine the lowest feasible level - used in the start prod func)
                numbers_start_fvp0_sire = fun.f_update(numbers_start_fvp0_sire, numbers_start_sire, False) #currently sire don't have any fvp

            if np.any(days_period_pa1e1b1nwzida0e0b0xyg1[p,...] >0):
                numbers_start_dams = sfun.f_period_start_nums(numbers_end_dams, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                        , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_dams
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p]
                                        , season_propn_zida0e0b0xyg, group=1, numbers_initial_repro=numbers_initial_propn_repro_a1e1b1nwzida0e0b0xyg1
                                        , period_is_prejoin=period_is_prejoin_pa1e1b1nwzida0e0b0xyg1[p+1])
                ###numbers at the beginning of fvp 0 (used to calc mort for the lw patterns to determine the lowest feasible level - used in the start prod func)
                numbers_start_fvp0_dams = fun.f_update(numbers_start_fvp0_dams, numbers_start_dams, period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p + 1])

            if np.any(days_period_pa1e1b1nwzida0e0b0xyg2[p+1,...] >0):  #Look at days next period so that period_is_birth is triggered in f_period_start_nums
                numbers_start_yatf = sfun.f_period_start_nums(numbers_end_yatf, prejoin_tup, season_tup, uinp.structure['i_n1_len']
                                        , uinp.structure['i_w1_len'], uinp.structure['i_n_fvp_period1'], numbers_start_fvp0_yatf
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1]
                                        , season_propn_zida0e0b0xyg, nyatf_b1=nyatf_b1nwzida0e0b0xyg, gender_propn_x=gender_propn_xyg
                                        , period_is_birth=period_is_birth_pa1e1b1nwzida0e0b0xyg1[p+1], group=2)
                ###numbers at the beginning of fvp 0 (used to calc mort for the lw patterns to determine the lowest feasible level - used in the start prod func)
                numbers_start_fvp0_yatf = fun.f_update(numbers_start_fvp0_yatf, numbers_start_yatf, period_is_startfvp0_pa1e1b1nwzida0e0b0xyg1[p + 1])

            if np.any(days_period_pa1e1b1nwzida0e0b0xyg3[p,...] >0):
                numbers_start_offs = sfun.f_period_start_nums(numbers_end_offs, prejoin_tup, season_tup, uinp.structure['i_n3_len']
                                        , uinp.structure['i_w3_len'], uinp.structure['i_n_fvp_period3'], numbers_start_fvp0_offs
                                        , period_is_startfvp0_pa1e1b1nwzida0e0b0xyg3[p+1], period_is_startseason_pa1e1b1nwzida0e0b0xyg[p+1]
                                        , season_propn_zida0e0b0xyg, group=3)
                ###numbers at the beginning of fvp 0 (used to calc mort for the lw patterns to determine the lowest feasible level - used in the start prod func)
                numbers_start_fvp0_offs = fun.f_update(numbers_start_fvp0_offs, numbers_start_offs, period_is_startfvp0_pa1e1b1nwzida0e0b0xyg3[p + 1])

        ## Calculate LTW sfw multiplier & sfd addition then repeat the generator loops with updated LTW adjuster
        ### sires don't have an adjuster calculated because they are born off-farm & unrelated to the dam nutrition profile
        ### yatf don't have an adjuster because the LTW project did not show a consistent effect of dam profile on the wool shorn at the lamb shearing.

        ## The LTW adjuster for a period within the range pre-joining to next_period_is_prejoining, is the value from that lambing
        ### The LTW adjuster is retained in the variable through until period_is_prejoining, so it can be accessed when next_period_is_prejoining
        ### Create the association between nextperiod_is_prejoin and the current period
        a_nextisprejoin_pa1e1b1nwzida0e0b0xyg1 = sfun.f_next_prev_association(date_end_p, date_prejoin_next_pa1e1b1nwzida0e0b0xyg1, 1, 'right').astype(dtypeint) #p indx of period before prejoining - when nextperiod is prejoining this returns the current period

        ## the dam lifetime adjustment (for the p, e1, b1 & w axes) are based on the LW profile of the dams themselves and scaled by the number of progeny they rear as a proportion of the total number weaned.
        o_cfw_ltwadj_pdams = np.take_along_axis(o_cfw_ltwadj_pdams, a_nextisprejoin_pa1e1b1nwzida0e0b0xyg1, axis=0) #adjust p axis so it is the cfw in the period before prejoining
        sfw_ltwadj_pa1e1b1nwzida0e0b0xyg1 = 1 + (o_cfw_ltwadj_pdams * nyatf_b1nwzida0e0b0xyg
                                                 / npw_std_xyg1 / sfw_a0e0b0xyg1)
        o_fd_ltwadj_pdams = np.take_along_axis(o_fd_ltwadj_pdams, a_nextisprejoin_pa1e1b1nwzida0e0b0xyg1, axis=0) #adjust p axis so it is the fd in the period before prejoining
        sfd_ltwadj_pa1e1b1nwzida0e0b0xyg1 = o_fd_ltwadj_pdams * nyatf_b1nwzida0e0b0xyg / npw_std_xyg1


        ## the offspring lifetime adjustment is based on LW pattern 0
        ###want the p slice from nextisprejoin (or period_is_lambing) to be in the d axis using a_prevjoining_o_pa1e1b1nwzida0e0b0xyg1
        ###         e1 axis in the position of e0
        ###         b1 axis in the position of b0 and simplified using a_b0_b1
        ###         w axis to only have slice 0
        ###         z axis is the weighted average
        temporary = np.sum(o_cfw_ltwadj_pdams[:, :, :, :, :, 0:1, ...] * (a_prevjoining_o_pa1e1b1nwzida0e0b0xyg1 == index_da0e0b0xyg)
                           * period_is_join_pa1e1b1nwzida0e0b0xyg1, axis = 0)
        temporary = np.swapaxes(temporary, e1_pos, e0_pos)
        temporary = np.sum(temporary * (a_b0_b1nwzida0e0b0xyg == index_b0xyg), axis=b1_pos, keepdims=True)
        t_season_propn_pg = np.broadcast_to(season_propn_zida0e0b0xyg, temporary.shape)
        temporary = np.average(temporary, axis=z_pos, weights=t_season_propn_pg)
        sfw_ltwadj_a1e1b1nwzida0e0b0xyg3 = 1 + temporary / sfw_da0e0b0xyg3

        ## repeat for FD
        temporary = np.sum(o_fd_ltwadj_pdams[:, :, :, :, :, 0:1, ...] * (a_prevjoining_o_pa1e1b1nwzida0e0b0xyg1 == index_da0e0b0xyg), axis = 0)
        temporary = np.swapaxes(temporary, e1_pos, e0_pos)
        temporary = np.sum(temporary * (a_b0_b1nwzida0e0b0xyg == index_b0xyg), axis=b1_pos, keepdims=True)
        t_season_propn_pg = np.broadcast_to(season_propn_zida0e0b0xyg, temporary.shape)
        temporary = np.average(temporary, axis=z_pos, weights=t_season_propn_pg)
        sfd_ltwadj_a1e1b1nwzida0e0b0xyg3 = temporary

    postp_start=time.time()
    print('generator :', postp_start - generator_start)


    ## Call Steve graphing routine here if Generator is throwing an error in the post processing.
    ### Change scan-spreadsheet to True to activate
    scan_spreadsheet = False
    while scan_spreadsheet:
        try:
            yvar1, yvar2, xlabels, wvar, xvar, axes, dimensions, verticals = pv.read_spreadsheet()
            loc = locals()
            yvar1 = loc[yvar1]
            yvar2 = loc[yvar2]
            xlabels = loc[xlabels]
            wvar = loc[wvar]
            xvar = loc[xvar]
            pv.create_plots(yvar1, yvar2, xlabels, wvar, xvar, axes, dimensions, verticals)
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            scan_spreadsheet = input("Enter 1 to rescan spreadsheet for new plots: ")





    ###########################
    #post processing inputs  #
    ###########################
    ##general
    ###feed period
    a_p6_pa1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(a_p6_p, p_pos).astype(dtypeint)
    len_p6=np.max(a_p6_p)+1
    index_p6 = np.arange(len_p6)
    index_p6pa1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(index_p6, p_pos-1).astype(dtypeint)
    ###cash period
    cash_period_dates = per.cashflow_periods().iloc[:-1,0].to_numpy().astype('datetime64[D]') #don't include last cash period date because it is just the end date of the last period
    cash_period_dates_cy = cash_period_dates + (np.arange(np.ceil(sim_years)) * np.timedelta64(365,'D'))[:,na] #expand from single yr to all length of generator
    cash_period_dates_c = cash_period_dates_cy.ravel()
    a_c_p = sfun.f_next_prev_association(cash_period_dates_c, date_end_p, 1,'right') % len(cash_period_dates) #% len required to convert association back to only the number of cash periods
    a_c_pa1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(a_c_p, p_pos).astype(dtype)
    index_ctpa1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(np.arange(len(cash_period_dates)), p_pos-2)
    ###labour period
    labour_periods = per.p_date2_df().iloc[:,0].to_numpy().astype('datetime64[D]') #convert from df to numpy
    labour_periods_p5y = labour_periods + (np.arange(np.ceil(sim_years)) * np.timedelta64(365,'D'))[:,na] #expand from single yr to all length of generator
    labour_periods_p5 = labour_periods_p5y.ravel()
    a_p5_p = sfun.f_next_prev_association(labour_periods_p5, date_end_p, 1, 'right') % len(labour_periods)
    a_p5_pa1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(a_p5_p, p_pos).astype(dtype)
    index_p5tpa1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(np.arange(len(labour_periods)), p_pos-2)
    ###asset value timing - the date when the asset value is tallied
    assetvalue_timing = np.datetime64(uinp.structure['i_date_assetvalue']).astype('datetime64[D]') #convert from df to numpy
    assetvalue_timing_y = assetvalue_timing + (np.arange(np.ceil(sim_years)) * np.timedelta64(365,'D')) #timing of asset value calculation each yr
    a_assetvalue_p = sfun.f_next_prev_association(assetvalue_timing_y, date_end_p, 1,'right')
    a_assetvalue_pa1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(a_assetvalue_p, p_pos)
    assetvalue_timing_pa1e1b1nwzida0e0b0xyg = assetvalue_timing_y[a_assetvalue_pa1e1b1nwzida0e0b0xyg]
    period_is_assetvalue_pa1e1b1nwzida0e0b0xyg = sfun.f_period_is_('period_is', assetvalue_timing_pa1e1b1nwzida0e0b0xyg, date_start_pa1e1b1nwzida0e0b0xyg, date_end_p = date_end_pa1e1b1nwzida0e0b0xyg)
    ###feed pool - sheep are grouped based on energy volume ratio
    ev_propn_f = np.array([0.25, 0.50, 0.75]) #Set the values for the ranges required (same values for all 10 matrix feed periods). This spreads the feed pools evenly between the highest and lowest quality feed required by any of the animals.
    index_fpa1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(np.arange(ev_propn_f.shape[0]+1), p_pos-1)
    ##wool
    vm_m4a1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(pinp.sheep['i_vm_m4'], p_pos).astype(dtype)
    pmb_m4s4a1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(pinp.sheep['i_pmb_m4s'], p_pos).astype(dtype)
    ##sale
    score_range_s8s6pa1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(uinp.sheep['i_salep_score_range_s8s6'], p_pos - 1).astype(dtype)
    price_adj_months_s7s9m4a1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(uinp.sheep['i_salep_months_priceadj_s7s9m4'], p_pos, len_ax0=uinp.sheep['i_s7_len'],len_ax1=uinp.sheep['i_s9_len'],len_ax2=uinp.sheep['i_salep_months_priceadj_s7s9m4'].shape[-1]).astype(dtype)
    dresspercent_adj_s6pa1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(uinp.sheep['i_salep_dressp_adj_s6'], p_pos-1).astype(dtype)
    dresspercent_adj_s7pa1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(uinp.sheep['i_salep_dressp_adj_s7'], p_pos-1).astype(dtype)
    score_pricescalar_s7s5s6 = fun.f_reshape_expand(uinp.sheep['i_salep_score_scalar_s7s5s6'], len_ax0=uinp.sheep['i_s7_len'],len_ax1=uinp.sheep['i_s5_len'],len_ax2=uinp.sheep['i_salep_score_scalar_s7s5s6'].shape[-1]).astype(dtype)
    weight_pricescalar_s7s5s6 = fun.f_reshape_expand(uinp.sheep['i_salep_weight_scalar_s7s5s6'], len_ax0=uinp.sheep['i_s7_len'],len_ax1=uinp.sheep['i_s5_len'],len_ax2=uinp.sheep['i_salep_weight_scalar_s7s5s6'].shape[-1]).astype(dtype)
    grid_weightrange_s7s5pa1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(uinp.sheep['i_salep_weight_range_s7s5'], p_pos-1,len_ax0=uinp.sheep['i_s7_len'],len_ax1=uinp.sheep['i_s5_len']).astype(dtype)
    price_type_s7pa1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(uinp.sheep['i_salep_price_type_s7'], p_pos-1)
    # a_s8_s7pa1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(uinp.sheep['ia_s8_s7'], p_pos-1)
    cvlw_s7s5pa1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(uinp.sheep['i_cvlw_s7'], p_pos-2).astype(dtype)
    cvscore_s7s6pa1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(uinp.sheep['i_cvscore_s7'], p_pos-2).astype(dtype)
    discount_age_s7pa1e1b1nwzida0e0b0xyg = fun.f_convert_to_inf(fun.f_reshape_expand(uinp.sheep['i_salep_discount_age_s7'],
                                                                                     p_pos-1)).astype(dtype)  # convert -- and ++ to inf
    sale_cost_pc_s7pa1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(uinp.sheep['i_sale_cost_pc_s7'], p_pos-1).astype(dtype)
    sale_cost_hd_s7pa1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(uinp.sheep['i_sale_cost_hd_s7'], p_pos-1).astype(dtype)
    mask_s7x_s7pa1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(uinp.sheep['i_mask_s7x'], x_pos, left_pos2=p_pos-1, right_pos2=x_pos) #don't mask x axis
    mask_s7x_s7pa1e1b1nwzida0e0b0xyg3 = fun.f_reshape_expand(uinp.sheep['i_mask_s7x'], x_pos, left_pos2=p_pos-1, right_pos2=x_pos, condition=mask_x, axis=x_pos)
    sale_agemax_s7pa1e1b1nwzida0e0b0xyg0, sale_agemax_s7pa1e1b1nwzida0e0b0xyg1, sale_agemax_s7pa1e1b1nwzida0e0b0xyg2, sale_agemax_s7pa1e1b1nwzida0e0b0xyg3 = sfun.f_c2g(uinp.parameters['i_agemax_s7c2'],uinp.parameters['i_agemax_s7y'],p_pos-1, dtype=dtype)
    dresspercent_adj_yg0, dresspercent_adj_yg1, dresspercent_adj_yg2, dresspercent_adj_yg3 = sfun.f_c2g(uinp.parameters['i_dressp_adj_c2'],uinp.parameters['i_dressp_adj_y'], dtype=dtype)
    ##husbandry
    wool_genes_yg0, wool_genes_yg1, wool_genes_yg2, wool_genes_yg3 = sfun.f_c2g(uinp.parameters['i_wool_genes_c2'],uinp.parameters['i_wool_genes_y'], dtype=dtype)
    mobsize_pa1e1b1nwzida0e0b0xyg0 = fun.f_reshape_expand(pinp.sheep['i_mobsize_sire_p6i'][a_p6_p], i_pos, left_pos2=p_pos, right_pos2=i_pos, condition=pinp.sheep['i_masksire_i'], axis=i_pos)
    mobsize_pa1e1b1nwzida0e0b0xyg1 = fun.f_reshape_expand(pinp.sheep['i_mobsize_dams_p6i'][a_p6_p], i_pos, left_pos2=p_pos, right_pos2=i_pos, condition=pinp.sheep['i_mask_i'], axis=i_pos)
    mobsize_pa1e1b1nwzida0e0b0xyg3 = fun.f_reshape_expand(pinp.sheep['i_mobsize_offs_p6i'][a_p6_p[mask_p_offs_p]], i_pos, left_pos2=p_pos, right_pos2=i_pos, condition=pinp.sheep['i_mask_i'], axis=i_pos)
    animal_mated_b1g1 = fun.f_reshape_expand(uinp.structure['i_mated_b1'], b1_pos)
    operations_triggerlevels_h5h7h2pg = fun.f_convert_to_inf(fun.f_reshape_expand(pinp.sheep['i_husb_operations_triggerlevels_h5h7h2'], p_pos-1,len_ax0=pinp.sheep['i_h2_len'],len_ax1=pinp.sheep['i_h5_len'],len_ax2=pinp.sheep['i_husb_operations_triggerlevels_h5h7h2'].shape[-1],
                                                                                  swap=True, swap2=True)).astype(dtype)  # convert -- and ++ to inf
    husb_operations_muster_propn_h2pg = fun.f_reshape_expand(uinp.sheep['i_husb_operations_muster_propn_h2'], p_pos-1).astype(dtype)
    husb_requisite_cost_h6pg = fun.f_reshape_expand(uinp.sheep['i_husb_requisite_cost_h6'], p_pos-1).astype(dtype)
    husb_operations_requisites_prob_h6h2pg = fun.f_reshape_expand(uinp.sheep['i_husb_operations_requisites_prob_h6h2'], p_pos-1,swap=True).astype(dtype)
    operations_per_hour_l2h2pg = fun.f_reshape_expand(uinp.sheep['i_husb_operations_labourreq_l2h2'], p_pos-1,swap=True).astype(dtype)
    husb_operations_infrastructurereq_h1h2pg = fun.f_reshape_expand(uinp.sheep['i_husb_operations_infrastructurereq_h1h2'], p_pos-1,swap=True).astype(dtype)
    husb_operations_contract_cost_h2pg = fun.f_reshape_expand(uinp.sheep['i_husb_operations_contract_cost_h2'], p_pos-1).astype(dtype)
    husb_muster_requisites_prob_h6h4pg = fun.f_reshape_expand(uinp.sheep['i_husb_muster_requisites_prob_h6h4'], p_pos-1,len_ax0=uinp.sheep['i_h4_len'], len_ax1=uinp.sheep['i_husb_muster_requisites_prob_h6h4'].shape[-1],swap=True).astype(dtype)
    musters_per_hour_l2h4pg = fun.f_reshape_expand(uinp.sheep['i_husb_muster_labourreq_l2h4'], p_pos-1,len_ax0=uinp.sheep['i_h4_len'], len_ax1=uinp.sheep['i_husb_muster_labourreq_l2h4'].shape[-1],swap=True)
    husb_muster_infrastructurereq_h1h4pg = fun.f_reshape_expand(uinp.sheep['i_husb_muster_infrastructurereq_h1h4'], p_pos-1,len_ax0=uinp.sheep['i_h4_len'], len_ax1=uinp.sheep['i_husb_muster_infrastructurereq_h1h4'].shape[-1],swap=True).astype(dtype)
    period_is_wean_pa1e1b1nwzida0e0b0xyg0 = sfun.f_period_is_('period_is', date_weaned_ida0e0b0xyg0, date_start_pa1e1b1nwzida0e0b0xyg, date_end_p = date_end_pa1e1b1nwzida0e0b0xyg)
    period_is_wean_pa1e1b1nwzida0e0b0xyg1 = np.logical_or(period_is_wean_pa1e1b1nwzida0e0b0xyg1, sfun.f_period_is_('period_is', date_weaned_ida0e0b0xyg1, date_start_pa1e1b1nwzida0e0b0xyg, date_end_p = date_end_pa1e1b1nwzida0e0b0xyg)) #includes the weaning of the dam itself and the yatf because there is husbandry for the ewe when yatf are weaned eg the dams have to be mustered
    period_is_wean_pa1e1b1nwzida0e0b0xyg3 = sfun.f_period_is_('period_is', date_weaned_ida0e0b0xyg3, date_start_pa1e1b1nwzida0e0b0xyg3, date_end_p = date_end_pa1e1b1nwzida0e0b0xyg3)
    a_nextshear_pa1e1b1nwzida0e0b0xyg0 = sfun.f_next_prev_association(date_end_p, date_nextshear_pa1e1b1nwzida0e0b0xyg0, 1,'right').astype(dtypeint) #p indx of next shearing - when period is shearing this returns the current period
    a_nextshear_pa1e1b1nwzida0e0b0xyg1 = sfun.f_next_prev_association(date_end_p, date_nextshear_pa1e1b1nwzida0e0b0xyg1, 1,'right').astype(dtypeint) #p indx of next shearing - when period is shearing this returns the current period
    a_nextshear_pa1e1b1nwzida0e0b0xyg3 = sfun.f_next_prev_association(offs_date_end_p, date_nextshear_pa1e1b1nwzida0e0b0xyg3, 1,'right').astype(dtypeint) #p indx of next shearing - when period is shearing this returns the current period
    gender_xyg = fun.f_reshape_expand(np.arange(len(mask_x)), x_pos)
    ##sire
    purchcost_g0 = sfun.f_g2g(pinp.sheep['i_purchcost_sire_ig0'], 'sire', condition=pinp.sheep['i_masksire_i'], axis=0) #Not divided by number of years onhand because the number of years of use is reflected in the number of dams that are serviced (because one sire can service multiple dam ages)
    date_purch_oa1e1b1nwzida0e0b0xyg0 = sfun.f_g2g(pinp.sheep['i_date_purch_ig0'], 'sire', i_pos, left_pos2=p_pos-1, right_pos2=i_pos, condition=pinp.sheep['i_masksire_i'], axis=i_pos).astype('datetime64[D]')
    date_sale_oa1e1b1nwzida0e0b0xyg0 = sfun.f_g2g(pinp.sheep['i_date_sale_ig0'], 'sire', i_pos, left_pos2=p_pos-1, right_pos2=i_pos, condition=pinp.sheep['i_masksire_i'], axis=i_pos).astype('datetime64[D]')
    sire_periods_g0p8y = sire_periods_g0p8[..., na].astype('datetime64[D]') + (
                         np.arange(np.ceil(sim_years)) * np.timedelta64(365, 'D'))
    period_is_startp8_pa1e1b1nwzida0e0b0xyg0p8y = sfun.f_period_is_('period_is', sire_periods_g0p8y, date_start_pa1e1b1nwzida0e0b0xyg[...,na,na], date_end_p = date_end_pa1e1b1nwzida0e0b0xyg[...,na,na])
    period_is_startp8_pa1e1b1nwzida0e0b0xyg0p8 = np.any(period_is_startp8_pa1e1b1nwzida0e0b0xyg0p8y, axis=-1) #condense the y axis - it is now accounted for by p axis
    ##dams
    sale_delay_sa1e1b1nwzida0e0b0xyg1 = sfun.f_g2g(pinp.sheep['i_sales_delay_sg1'], 'dams', p_pos) #periods after shearing that sale occurs
    ###mask for nutrition profiles. this doesnt have a full w axis because it only has the nutrition options it is expanded to w further down.
    mask_nut_oa1e1b1nwzida0e0b0xyg1 = fun.f_reshape_expand(pinp.sheep['i_sai_lw_dams_owi'],i_pos,pinp.sheep['i_i_len'],pinp.sheep['i_o_len'],
                                                           int(len_w1/uinp.structure['i_n1_len']), left_pos2=w_pos, left_pos3=p_pos,
                                                           right_pos2=i_pos, right_pos3=w_pos,swap=True, swap2=True,
                                                           condition=pinp.sheep['i_mask_i'], axis=i_pos, condition2=mask_o_dams, axis2=p_pos)
    ##offs
    ###dvp mask - basically the shearing mask plus a true for the first dvp which is weaning
    dvp_mask_g3 = np.concatenate([np.array([True]), mask_shear_g3]) #need to add true to the start of the shear mask because the first dvp is weaning
    ###days from the start of the dvp when sale occurs
    sales_offset_tsa1e1b1nwzida0e0b0xyg3 = sfun.f_g2g(pinp.sheep['i_sales_offset_tsg3'], 'offs', p_pos, len_t3, pinp.sheep['i_s_len']+1, condition=dvp_mask_g3, axis=p_pos)
    ###target weight in a dvp where sale occurs
    target_weight_tsa1e1b1nwzida0e0b0xyg3 = sfun.f_g2g(pinp.sheep['i_target_weight_tsg3'], 'offs', p_pos, len_t3, pinp.sheep['i_s_len']+1, condition=dvp_mask_g3, axis=p_pos) #plus 1 because it is shearing opp and weaning (ie the dvp for offs)
    ###number of periods before sale that shearing occurs in each dvp
    shearing_offset_tsa1e1b1nwzida0e0b0xyg3= sfun.f_g2g(pinp.sheep['i_shear_prior_tsg3'], 'offs', p_pos, len_t3, pinp.sheep['i_s_len']+1, condition=dvp_mask_g3, axis=p_pos) #plus 1 because it is shearing opp and weaning (ie the dvp for offs)
    ###mask for nutrition profiles. this doesnt have a full w axis because it only has the nutrition options it is expanded to w further down.
    mask_nut_sa1e1b1nwzida0e0b0xyg3 = fun.f_reshape_expand(pinp.sheep['i_sai_lw_offs_swix'],x_pos,pinp.sheep['i_i_len'], pinp.sheep['i_s_len'],
                                                           pinp.sheep['i_x_len'], len_ax3=int(len_w3/uinp.structure['i_n3_len']),
                                                           left_pos2=i_pos, left_pos3=w_pos,left_pos4=p_pos,
                                                           right_pos2=x_pos,right_pos3=i_pos,right_pos4=w_pos,
                                                           swap=True, move=True, source=-1, dest=1, condition=pinp.sheep['i_mask_i'], axis=i_pos,
                                                           condition2=mask_shear_g3, axis2=p_pos, condition3=mask_x, axis3=x_pos)



    #################################
    ##post processing associations  #
    #################################
    ##yatf
    ###association between the birth time of yatf and the birth time of dams
    a_i_ida0e0b0xyg2 = sfun.f_g2g(pinp.sheep['ia_i_idg2'],'yatf',d_pos,pinp.sheep['i_i_len'],uinp.parameters['i_d_len'], condition=pinp.sheep['i_mask_i'], axis=i_pos, condition2=mask_d_offs, axis2=d_pos)
    a_g1_g2 = sfun.f_g2g(pinp.sheep['ia_g1_g2'],'yatf')

    ##dams
    ###transfer
    a_g1_tpa1e1b1nwzida0e0b0xyg1 = sfun.f_g2g(uinp.structure['ia_g1_tg1'], 'dams', p_pos-1)
    transfer_exists_tpa1e1b1nwzida0e0b0xyg1 = sfun.f_g2g(uinp.structure['i_transfer_exists_tg1'], 'dams', p_pos-1)
    #### adjust the pointers for excluded sires (t axis starts as just the sires eg dams transfer to different sire type)
    prior_sire_excluded_tpa1e1b1nwzida0e0b0xyg0 = fun.f_reshape_expand(np.cumsum(~mask_sire_inc_g0), p_pos-1) #put the g0 axis in the t position
    a_g1_tpa1e1b1nwzida0e0b0xyg1 = a_g1_tpa1e1b1nwzida0e0b0xyg1 - prior_sire_excluded_tpa1e1b1nwzida0e0b0xyg0
    ####mask inputs for g0
    transfer_exists_tpa1e1b1nwzida0e0b0xyg1 = transfer_exists_tpa1e1b1nwzida0e0b0xyg1[mask_sire_inc_g0]
    a_g1_tpa1e1b1nwzida0e0b0xyg1 = a_g1_tpa1e1b1nwzida0e0b0xyg1[mask_sire_inc_g0]
    #### add the sale slices for the t axis
    slices_to_add = np.full((pinp.sheep['i_n_dam_sales'],)+transfer_exists_tpa1e1b1nwzida0e0b0xyg1.shape[1:], False)
    transfer_exists_tpa1e1b1nwzida0e0b0xyg1 = np.concatenate([slices_to_add, transfer_exists_tpa1e1b1nwzida0e0b0xyg1],0)
    slices_to_add = ~slices_to_add * np.arange(len_g1)
    a_g1_tpa1e1b1nwzida0e0b0xyg1 = np.concatenate([slices_to_add, a_g1_tpa1e1b1nwzida0e0b0xyg1],0)
    ###dvp pointer - for dams there is a new dvp each fvp- #todo this is inflexible, maybe there is a better way to do this
    a_v_pa1e1b1nwzida0e0b0xyg1 = a_fvp_pa1e1b1nwzida0e0b0xyg1.astype(dtypeint)
    index_va1e1b1nwzida0e0b0xyg1 = fun.f_reshape_expand(np.arange(np.max(a_v_pa1e1b1nwzida0e0b0xyg1)+1), p_pos)
    index_vpa1e1b1nwzida0e0b0xyg1 = fun.f_reshape_expand(np.arange(np.max(a_v_pa1e1b1nwzida0e0b0xyg1)+1), p_pos-1)
    ###dvp are the same as fvp for dams    #todo we should create some variable eg scan_dvp=1 then where we do dvp_type==1 we can change it to dvp_type==scan dvp - this will make it easier to change dvps in future
    dvp_date_start_va1e1b1nwzida0e0b0xyg1 = fvp_date_start_fa1e1b1nwzida0e0b0xyg1
    a_dvp_p_va1e1b1nwzida0e0b0xyg1 = sfun.f_next_prev_association(date_start_p, dvp_date_start_va1e1b1nwzida0e0b0xyg1, 1, 'right').astype(dtypeint) #returns the period index for the start of each dvp
    dvp_date_start_pa1e1b1nwzida0e0b0xyg1=np.take_along_axis(dvp_date_start_va1e1b1nwzida0e0b0xyg1,a_v_pa1e1b1nwzida0e0b0xyg1,0)
    dvp_type_va1e1b1nwzida0e0b0xyg1=fvp_type_fa1e1b1nwzida0e0b0xyg1  #[:,:,0:1,...] #rename to keep consistent and take e slice 0 because dvp is the same for all
    dvp_type_next_va1e1b1nwzida0e0b0xyg1 = np.roll(dvp_type_va1e1b1nwzida0e0b0xyg1, -1, axis=p_pos)
    dvp_type_va1e1b1nwzida0e0b0xyg1[0] = 0 #make dvp_type[0] == 0 to correctly mask the animals in the post weaning period because there is only 3 different weights (which is not technically like type 2) but don't want to change fvp type because we still want to trigger the change at the first prejoining.
    period_is_startdvp_pa1e1b1nwzida0e0b0xyg1 = sfun.f_period_is_('period_is', dvp_date_start_pa1e1b1nwzida0e0b0xyg1, date_start_pa1e1b1nwzida0e0b0xyg, date_end_p = date_end_pa1e1b1nwzida0e0b0xyg)
    nextperiod_is_startdvp_pa1e1b1nwzida0e0b0xyg1 = np.roll(period_is_startdvp_pa1e1b1nwzida0e0b0xyg1,-1,axis=0)
    nextperiod_is_prejoin_pa1e1b1nwzida0e0b0xyg1 = np.roll(period_is_prejoin_pa1e1b1nwzida0e0b0xyg1,-1,axis=0)
    #### the transfer to a dvp_type other than type==0 only occurs when transferring to and from the same genotype
    #### this occurs when (index_g1 == a_g1_tg1) and the transfer exists
    mask_dvp_type_next_tg1 = transfer_exists_tpa1e1b1nwzida0e0b0xyg1 * (index_g1 == a_g1_tpa1e1b1nwzida0e0b0xyg1) #dvp type next is a little more complex for animals transferring. However the destination for transfer is always dvp type next ==0 (either it is going from dvp 2 to 0 or from 0 to 0.
    dvp_type_next_tva1e1b1nwzida0e0b0xyg1 = dvp_type_next_va1e1b1nwzida0e0b0xyg1 * mask_dvp_type_next_tg1
    ####association between dvp and lambing opp
    index_v1 = np.arange(index_vpa1e1b1nwzida0e0b0xyg1.shape[0])
    a_o_v = (np.trunc((index_v1 - 1) / uinp.structure['i_n_fvp_period1'])).astype(dtypeint)
    ###cluster
    a_ppk2g1_slva1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(uinp.structure['ia_ppk2g1_vlsb1'], b1_pos, swap=True, ax1=0, ax2=2, len_ax0=uinp.structure['i_n_v1type']
                                          , len_ax1=uinp.structure['i_len_l'], len_ax2=uinp.structure['i_len_s'], len_ax3=uinp.structure['ia_ppk2g1_vlsb1'].shape[-1]
                                          , left_pos2=p_pos, right_pos2=b1_pos)
    a_ppk2g1_va1e1b1nwzida0e0b0xygsl = np.moveaxis(np.moveaxis(a_ppk2g1_slva1e1b1nwzida0e0b0xyg, 0,-1),0,-1) #put s and l at the end they are summed away shortly
    a_ppk2g1_va1e1b1nwzida0e0b0xygsl = np.take_along_axis(a_ppk2g1_va1e1b1nwzida0e0b0xygsl,dvp_type_va1e1b1nwzida0e0b0xyg1[...,na,na], axis=0) #convert v type axis to normal v axis

    ##offs
    ###dvp pointer - for offs there is a new dvp each time fvp type goes back to 0 (eg once per yr)- ^this is inflexible, maybe there is a better way to do this
    a_v_pa1e1b1nwzida0e0b0xyg3 = (a_fvp_pa1e1b1nwzida0e0b0xyg3 / 3).astype(dtypeint)  #divide by 3 then round down to the int - because there are 3fvp's per yr but only 1 dvp per yr
    index_vpa1e1b1nwzida0e0b0xyg3 = fun.f_reshape_expand(np.arange(np.max(a_v_pa1e1b1nwzida0e0b0xyg3)+1), p_pos-1)
    ###dvp dates
    date_weaned_a1e1b1nwzida0e0b0xyg3 = np.broadcast_to(date_weaned_ida0e0b0xyg3,fvp_0_start_oa1e1b1nwzida0e0b0xyg3.shape[1:]) #need wean date rather than first day of yr because selling inputs are days from weaning.
    dvp_date_start_va1e1b1nwzida0e0b0xyg3 = np.concatenate([date_weaned_a1e1b1nwzida0e0b0xyg3[na,...],fvp_0_start_oa1e1b1nwzida0e0b0xyg3], axis=0)
    dvp_date_start_pa1e1b1nwzida0e0b0xyg3=np.take_along_axis(dvp_date_start_va1e1b1nwzida0e0b0xyg3,a_v_pa1e1b1nwzida0e0b0xyg3,0)
    period_is_startdvp_pa1e1b1nwzida0e0b0xyg3 = sfun.f_period_is_('period_is', dvp_date_start_pa1e1b1nwzida0e0b0xyg3, date_start_pa1e1b1nwzida0e0b0xyg3, date_end_p = date_end_pa1e1b1nwzida0e0b0xyg3)
    dvp_start2_date_va1e1b1nwzida0e0b0xyg3 = np.concatenate([fvp_b0_start_ba1e1b1nwzida0e0b0xyg3,fvp_0_start_oa1e1b1nwzida0e0b0xyg3], axis=0) #use start of year rather than weaning for the start of the dvp because for dvp next we don't want to trigger a true at weaning.
    dvp_start2_date_pa1e1b1nwzida0e0b0xyg3=np.take_along_axis(dvp_start2_date_va1e1b1nwzida0e0b0xyg3,a_v_pa1e1b1nwzida0e0b0xyg3,0) #doesn't include weaning date because don't want to trigger the end of dvp the period before weaning dvp 0 ends before shearing therefore nextdvp is true the period before shearing
    period_is_startdvp2_pa1e1b1nwzida0e0b0xyg3 = sfun.f_period_is_('period_is', dvp_start2_date_pa1e1b1nwzida0e0b0xyg3, date_start_pa1e1b1nwzida0e0b0xyg3, date_end_p = date_end_pa1e1b1nwzida0e0b0xyg3)
    nextperiod_is_startdvp_pa1e1b1nwzida0e0b0xyg3 = np.roll(period_is_startdvp2_pa1e1b1nwzida0e0b0xyg3,-1,axis=0)
    ####association between dvp and shearing - this is required because in the last dvp that the animal exist (ie when the generator ends) the sheep did not exist at shearing.
    index_v3 = np.arange(index_vpa1e1b1nwzida0e0b0xyg3.shape[0])
    a_s_v = np.minimum(np.count_nonzero(mask_shear_g3)-1,index_v3)
    ###cluster
    a_k5cluster_lsb0xyg = fun.f_reshape_expand(uinp.structure['ia_ppk5_lsb0'], b0_pos, len_ax0=uinp.structure['i_len_l'], len_ax1=uinp.structure['i_len_s']
                                                  , len_ax2=uinp.structure['ia_ppk5_lsb0'].shape[-1])
    a_k5cluster_b0xygls = np.moveaxis(np.moveaxis(a_k5cluster_lsb0xyg, 0,-1),0,-1) #put s and l at the end they are summed away shortly


    #######################
    #on hand / shear mask #
    #######################
    onhandshear_start=time.time()

    ##sire - purchased and sold on given date and shorn at main shearing - sires are simulated from weaning but for the pp we only look at a subset
    ### shearing - determined by the main shearing date - no t axis so just use the period is shearing from generator
    ###round purchase and sale date of sire to nearest period
    date_purch_oa1e1b1nwzida0e0b0xyg0 = sfun.f_next_prev_association(date_start_p, date_purch_oa1e1b1nwzida0e0b0xyg0, 0, 'left') #move input date to the beginning of the next generator period
    date_purch_oa1e1b1nwzida0e0b0xyg0 = date_start_p[date_purch_oa1e1b1nwzida0e0b0xyg0]
    date_sale_oa1e1b1nwzida0e0b0xyg0 = sfun.f_next_prev_association(date_start_p, date_sale_oa1e1b1nwzida0e0b0xyg0, 0, 'left') #move input date to the beginning of the next generator period
    date_sale_oa1e1b1nwzida0e0b0xyg0 = date_start_p[date_sale_oa1e1b1nwzida0e0b0xyg0]
    on_hand_pa1e1b1nwzida0e0b0xyg0 = sfun.f_period_is_('period_is_between', date_purch_oa1e1b1nwzida0e0b0xyg0, date_start_pa1e1b1nwzida0e0b0xyg, date_sale_oa1e1b1nwzida0e0b0xyg0, date_end_pa1e1b1nwzida0e0b0xyg)
    period_is_sale_pa1e1b1nwzida0e0b0xyg0 = np.logical_and(on_hand_pa1e1b1nwzida0e0b0xyg0==True, np.roll(on_hand_pa1e1b1nwzida0e0b0xyg0,-1,axis=0)==False)
    ###the dvp start for the sires is essentially the date they are purchased
    period_is_startdvp_purchase_pa1e1b1nwzida0e0b0xyg0 = sfun.f_period_is_('period_is', date_purch_oa1e1b1nwzida0e0b0xyg0, date_start_pa1e1b1nwzida0e0b0xyg, date_end_p = date_end_pa1e1b1nwzida0e0b0xyg)


    ##offs
    ###calc sale date then determine shearing date
    ###sale - on date
    sale_date_tsa1e1b1nwzida0e0b0xyg3 = sales_offset_tsa1e1b1nwzida0e0b0xyg3 + dvp_date_start_va1e1b1nwzida0e0b0xyg3 #date of dvp plus sale offset
    ####adjust sale date to be last day of period
    sale_date_idx_tsa1e1b1nwzida0e0b0xyg3 = sfun.f_next_prev_association(offs_date_end_p, sale_date_tsa1e1b1nwzida0e0b0xyg3,0, 'left')#sale occurs at the end of the current generator period therefore 0 offset
    sale_date_tsa1e1b1nwzida0e0b0xyg3 = offs_date_end_p[sale_date_idx_tsa1e1b1nwzida0e0b0xyg3]
    ###sale - weight target
    ####convert from shearing/dvp to p array. Increments at dvp ie point to previous sale opp until new dvp then point at next dvp.
    sale_date_tpa1e1b1nwzida0e0b0xyg3=np.take_along_axis(sale_date_tsa1e1b1nwzida0e0b0xyg3,a_v_pa1e1b1nwzida0e0b0xyg3[na],1)
    target_weight_tpa1e1b1nwzida0e0b0xyg3=np.take_along_axis(target_weight_tsa1e1b1nwzida0e0b0xyg3,a_v_pa1e1b1nwzida0e0b0xyg3[na],1) #gets the target weight for each gen period
    ####adjust generator lw to reflect the cumulative max per period
    #####lw could go above target then drop back below but it is already sold so the on hand bool shouldn't change. therefore need to use accumulative max and reset each dvp
    weight_pa1e1b1nwzida0e0b0xyg3= sfun.f_cum_dvp(o_ffcfw_poffs,a_v_pa1e1b1nwzida0e0b0xyg3)
    ###on hand
    #### t0 slice = True - this is handled by the inputs ie weight and date are high therefore not reached therefore on hand == true
    #### t1 & t2 slice date_p<sale_date and weight<target weight
    on_hand_tpa1e1b1nwzida0e0b0xyg3 = np.logical_and(date_start_pa1e1b1nwzida0e0b0xyg3<sale_date_tpa1e1b1nwzida0e0b0xyg3,
                                                     weight_pa1e1b1nwzida0e0b0xyg3<target_weight_tpa1e1b1nwzida0e0b0xyg3)
    ###period is sale - one true per dvp when sale actually occurs - sale occurs in the period where sheep were on hand at the beginning and not on hand at the beginning of the next period
    period_is_sale_tpa1e1b1nwzida0e0b0xyg3 = np.logical_and(on_hand_tpa1e1b1nwzida0e0b0xyg3==True, np.roll(on_hand_tpa1e1b1nwzida0e0b0xyg3,-1,axis=1)==False)

    ###shearing - one true per dvp when shearing actually occurs
    ###in t0 shearing occurs on specified date, in t1 & t2 it happens a certain number of gen periods before sale.
    ####convert from s/dvp to p
    shearing_offset_tpa1e1b1nwzida0e0b0xyg3=np.take_along_axis(shearing_offset_tsa1e1b1nwzida0e0b0xyg3,a_v_pa1e1b1nwzida0e0b0xyg3[na],1)
    ###shearing cant occur in a different period to sale therefore need to cap the offset for periods at the beginning of the dvp ie if sale occurs in p2 of dvp2 and offset is 3 the offset needs to be reduced because shearing must occur in dvp2
    ####get the period number where dvp changes
    prev_dvp_index = sfun.f_next_prev_association(offs_date_start_p, dvp_date_start_pa1e1b1nwzida0e0b0xyg3, 1, 'right')
    periods_since_dvp = np.maximum(0,p_index_pa1e1b1nwzida0e0b0xyg3 - prev_dvp_index)  #first dvp starts at weaning so just put in the max 0 to stop negative results when the p date is less than weaning
    ####period when shearing will occur - this is the min of the shearing offset or the periods since dvp start
    shearing_idx_tpa1e1b1nwzida0e0b0xyg3 = p_index_pa1e1b1nwzida0e0b0xyg3 - np.minimum(shearing_offset_tpa1e1b1nwzida0e0b0xyg3, periods_since_dvp)
    ###period is shearing is the sale array - offset
    shearing_idx_tpa1e1b1nwzida0e0b0xyg3 = period_is_sale_tpa1e1b1nwzida0e0b0xyg3*shearing_idx_tpa1e1b1nwzida0e0b0xyg3.astype(dtype)
    shearing_idx_tpa1e1b1nwzida0e0b0xyg3[shearing_idx_tpa1e1b1nwzida0e0b0xyg3==0] = np.inf #don't want 0 effecting minimum in next line
    shearing_idx_tpa1e1b1nwzida0e0b0xyg3= np.flip(np.minimum.accumulate(np.flip(shearing_idx_tpa1e1b1nwzida0e0b0xyg3,1),axis=1),1)
    period_is_shearing_tpa1e1b1nwzida0e0b0xyg3 = p_index_pa1e1b1nwzida0e0b0xyg3 == shearing_idx_tpa1e1b1nwzida0e0b0xyg3
    ###make slice t0 the shear dates for retained offs
    period_is_shearing_retained_pa1e1b1nwzida0e0b0xyg3 = sfun.f_period_is_('period_is', date_shear_pa1e1b1nwzida0e0b0xyg3, date_start_pa1e1b1nwzida0e0b0xyg3, date_end_p = date_end_pa1e1b1nwzida0e0b0xyg3)
    period_is_shearing_tpa1e1b1nwzida0e0b0xyg3[0,...] = period_is_shearing_retained_pa1e1b1nwzida0e0b0xyg3

    ##Dams
    ###t0 = sale after shearing
    ###t1 = sale drys
    ###t>=2 = retain
    ### calc shearing then determine sale
    shear_period_pa1e1b1nwzida0e0b0xyg1 = np.maximum.accumulate(p_index_pa1e1b1nwzida0e0b0xyg * period_is_shearing_pa1e1b1nwzida0e0b0xyg1)
    ### all shearing in all t slices is determined by the main shearing date (shearing is the same for all t slices)
    ###determine t0 sale slice - note sale must occur in the same dvp as shearing so the offset is capped if shearing occurs near the end of a period
    sale_delay_pa1e1b1nwzida0e0b0xyg1 = np.take_along_axis(sale_delay_sa1e1b1nwzida0e0b0xyg1, a_prev_s_pa1e1b1nwzida0e0b0xyg1,0)
    a_dvpnext_p_va1e1b1nwzida0e0b0xyg1 = np.roll(a_dvp_p_va1e1b1nwzida0e0b0xyg1,-1,0) #roll backwards to get the gen period index of the next dvp
    a_dvpnext_p_va1e1b1nwzida0e0b0xyg1[-1,...] = len_p #set the last element to the length of p (because the end period is the equivalent of the next dvp for the end dvp)
    next_dvp_index_pa1e1b1nwzida0e0b0xyg1 = np.take_along_axis(a_dvpnext_p_va1e1b1nwzida0e0b0xyg1, a_v_pa1e1b1nwzida0e0b0xyg1, 0) #points at the next dvp from the date at the start of the period
    periods_to_dvp = next_dvp_index_pa1e1b1nwzida0e0b0xyg1 - (p_index_pa1e1b1nwzida0e0b0xyg + 1) #periods to the next dvp. +1 because if the next period is the new dvp you must sell in the current period
    sale_period_pa1e1b1nwzida0e0b0xyg1 = np.minimum(sale_delay_pa1e1b1nwzida0e0b0xyg1, periods_to_dvp) + shear_period_pa1e1b1nwzida0e0b0xyg1
    period_is_sale_t0_pa1e1b1nwzida0e0b0xyg1 = sale_period_pa1e1b1nwzida0e0b0xyg1 == p_index_pa1e1b1nwzida0e0b0xyg
    period_is_sale_t0_pa1e1b1nwzida0e0b0xyg1[0] = False #don't want period 0 to be sale (but it will default to sale because the sale period association is 0 at the beginning which ==index in p[0])
    ###determine t1 slice - dry dams sold at scanning
    period_is_sale_drys_pa1e1b1nwzida0e0b0xyg1 = period_is_scan_pa1e1b1nwzida0e0b0xyg1 * scan_pa1e1b1nwzida0e0b0xyg1>=1 * (not pinp.sheep['i_dry_retained_forced']) #not is required because variable is drys off hand ie sold. if forced to retain the variable wants to be false
    period_is_sale_drys_pa1e1b1nwzida0e0b0xyg1 = period_is_sale_drys_pa1e1b1nwzida0e0b0xyg1 * (nfoet_b1nwzida0e0b0xyg==0) #make sure selling is not an option for animals with foet (have to do it this way so that b axis is added)
    period_is_sale_drys_pa1e1b1nwzida0e0b0xyg1[:,:,:,0:1,...] = False #make sure selling is not an option for not mated ^ may turn on again in seasonality version
    ###combine sale t slices (t1 & t2) to produce period is sale
    shape =  tuple(np.maximum.reduce([period_is_sale_t0_pa1e1b1nwzida0e0b0xyg1.shape, period_is_sale_drys_pa1e1b1nwzida0e0b0xyg1.shape]))
    period_is_sale_tpa1e1b1nwzida0e0b0xyg1 = np.zeros((len_t1,)+shape, dtype=bool) #initialise on hand array with 3 t slices.
    period_is_sale_tpa1e1b1nwzida0e0b0xyg1[...]=False
    period_is_sale_tpa1e1b1nwzida0e0b0xyg1[0] = period_is_sale_t0_pa1e1b1nwzida0e0b0xyg1
    period_is_sale_tpa1e1b1nwzida0e0b0xyg1[1] = period_is_sale_drys_pa1e1b1nwzida0e0b0xyg1
    ####transfer - calculate period_is_finish when the dams are transferred from the current g slice to the destination g slice
    period_is_transfer_tpa1e1b1nwzida0e0b0xyg1 = np.take_along_axis(nextperiod_is_prejoin_pa1e1b1nwzida0e0b0xyg1[na, ...], a_g1_tpa1e1b1nwzida0e0b0xyg1, -1) * transfer_exists_tpa1e1b1nwzida0e0b0xyg1
    ###on hand - combine period_is_sale & period_is_transfer then use cumulative max to convert to on_hand
    off_hand_tpa1e1b1nwzida0e0b0xyg1= sfun.f_cum_dvp(np.logical_or(period_is_sale_tpa1e1b1nwzida0e0b0xyg1,period_is_transfer_tpa1e1b1nwzida0e0b0xyg1),a_v_pa1e1b1nwzida0e0b0xyg1,axis=1, shift=1) #this ensures that once they are sold they remain off hand for the rest of the dvp, shift =1 so that sheep are on-hand in the period they are sold because sale is end of period
    on_hand_tpa1e1b1nwzida0e0b0xyg1 = np.logical_not(off_hand_tpa1e1b1nwzida0e0b0xyg1)

    ##Yatf
    ###t0 = sold at weaning as sucker, t1 & t2 = retained
    ###the other t slices are added further down in the code
    period_is_sale_t0_pa1e1b1nwzida0e0b0xyg2 = period_is_wean_pa1e1b1nwzida0e0b0xyg2
    # period_is_sale_t1_2_pa1e1b1nwzida0e0b0xyg2 = np.full_like(period_is_sale_t0_pa1e1b1nwzida0e0b0xyg2, False)
    # period_is_sale_tpa1e1b1nwzida0e0b0xyg2 = np.stack([period_is_sale_t0_pa1e1b1nwzida0e0b0xyg2 ,period_is_sale_t1_2_pa1e1b1nwzida0e0b0xyg2, period_is_sale_t1_2_pa1e1b1nwzida0e0b0xyg2],0)
    # on_hand_tpa1e1b1nwzida0e0b0xyg2 = np.logical_not(period_is_sale_tpa1e1b1nwzida0e0b0xyg2)


    ######################
    #calc cost and income#
    ######################
    calc_cost_start = time.time()
    ##calc wool value - To speed the calculation process the p array is condensed to only include periods where shearing occurs. Using a slightly different association it is then converted to a v array (this process usually used a p to v association, in this case we use s to v association).
    ###create mask which is the periods where shearing occurs
    shear_mask_p0 = np.any(np.logical_or(period_is_shearing_pa1e1b1nwzida0e0b0xyg0, period_is_assetvalue_pa1e1b1nwzida0e0b0xyg), axis=tuple(range(p_pos+1,0)))
    shear_mask_p1 = np.any(np.logical_or(period_is_shearing_pa1e1b1nwzida0e0b0xyg1, period_is_assetvalue_pa1e1b1nwzida0e0b0xyg), axis=tuple(range(p_pos+1,0)))
    shear_mask_p3 = fun.f_reduce_skipfew(np.any, np.logical_or(period_is_shearing_tpa1e1b1nwzida0e0b0xyg3, period_is_assetvalue_pa1e1b1nwzida0e0b0xyg[mask_p_offs_p]), preserveAxis=1) #preforms np.any across all axis except axis 1
    ###create association between p and s
    a_p_p9a1e1b1nwzida0e0b0xyg0 = fun.f_reshape_expand(np.nonzero(shear_mask_p0)[0],p_pos)  #take [0] because nonzero function returns tuple
    a_p_p9a1e1b1nwzida0e0b0xyg1 = fun.f_reshape_expand(np.nonzero(shear_mask_p1)[0],p_pos)  #take [0] because nonzero function returns tuple
    a_p_p9a1e1b1nwzida0e0b0xyg3 = fun.f_reshape_expand(np.nonzero(shear_mask_p3)[0],p_pos)  #take [0] because nonzero function returns tuple
    index_p9a1e1b1nwzida0e0b0xyg0 = fun.f_reshape_expand(np.arange(np.count_nonzero(shear_mask_p0)),p_pos)
    index_p9a1e1b1nwzida0e0b0xyg1 = fun.f_reshape_expand(np.arange(np.count_nonzero(shear_mask_p1)),p_pos)
    index_p9a1e1b1nwzida0e0b0xyg3 = fun.f_reshape_expand(np.arange(np.count_nonzero(shear_mask_p3)),p_pos)
    ###convert period is shearing array to the condensed version
    period_is_shearing_p9a1e1b1nwzida0e0b0xyg0 = period_is_shearing_pa1e1b1nwzida0e0b0xyg0[shear_mask_p0,...]
    period_is_shearing_p9a1e1b1nwzida0e0b0xyg1 = period_is_shearing_pa1e1b1nwzida0e0b0xyg1[shear_mask_p1,...]
    period_is_shearing_tp9a1e1b1nwzida0e0b0xyg3 = period_is_shearing_tpa1e1b1nwzida0e0b0xyg3[:,shear_mask_p3,...]
    ###Vegatative Matter if shorn(end)
    vm_p9a1e1b1nwzida0e0b0xyg0 = vm_m4a1e1b1nwzida0e0b0xyg[a_m4_p,...][shear_mask_p0]
    vm_p9a1e1b1nwzida0e0b0xyg1 = vm_m4a1e1b1nwzida0e0b0xyg[a_m4_p,...][shear_mask_p1]
    vm_p9a1e1b1nwzida0e0b0xyg3 = vm_m4a1e1b1nwzida0e0b0xyg[a_m4_p[mask_p_offs_p],...][shear_mask_p3]
    ###pmb - a little complex because it is dependent on time since previous shearing
    pmb_p9s4a1e1b1nwzida0e0b0xyg0 = pmb_m4s4a1e1b1nwzida0e0b0xyg[a_m4_p,...][shear_mask_p0]
    pmb_p9s4a1e1b1nwzida0e0b0xyg1 = pmb_m4s4a1e1b1nwzida0e0b0xyg[a_m4_p,...][shear_mask_p1]
    pmb_p9s4a1e1b1nwzida0e0b0xyg3 = pmb_m4s4a1e1b1nwzida0e0b0xyg[a_m4_p[mask_p_offs_p],...][shear_mask_p3]
    period_current_shearing_p9a1e1b1nwzida0e0b0xyg0 = np.maximum.accumulate(a_p_p9a1e1b1nwzida0e0b0xyg0 * period_is_shearing_p9a1e1b1nwzida0e0b0xyg0, axis=0) #returns the period number that the most recent shearing occurred
    period_current_shearing_p9a1e1b1nwzida0e0b0xyg1 = np.maximum.accumulate(a_p_p9a1e1b1nwzida0e0b0xyg1 * period_is_shearing_p9a1e1b1nwzida0e0b0xyg1, axis=0) #returns the period number that the most recent shearing occurred
    period_current_shearing_tp9a1e1b1nwzida0e0b0xyg3 = np.maximum.accumulate(a_p_p9a1e1b1nwzida0e0b0xyg3 * period_is_shearing_tp9a1e1b1nwzida0e0b0xyg3, axis=1) #returns the period number that the most recent shearing occurred
    period_previous_shearing_p9a1e1b1nwzida0e0b0xyg0 = np.roll(period_current_shearing_p9a1e1b1nwzida0e0b0xyg0, 1, axis=0)*(index_p9a1e1b1nwzida0e0b0xyg0>0)  #returns the period of the previous shearing and sets slice 0 to 0 (because there is no previous shearing for the first shearing)
    period_previous_shearing_p9a1e1b1nwzida0e0b0xyg1 = np.roll(period_current_shearing_p9a1e1b1nwzida0e0b0xyg1, 1, axis=0)*(index_p9a1e1b1nwzida0e0b0xyg1>0)  #returns the period of the previous shearing and sets slice 0 to 0 (because there is no previous shearing for the first shearing)
    period_previous_shearing_tp9a1e1b1nwzida0e0b0xyg3 = np.roll(period_current_shearing_tp9a1e1b1nwzida0e0b0xyg3, 1, axis=1)*(index_p9a1e1b1nwzida0e0b0xyg3>0)  #returns the period of the previous shearing and sets slice 0 to 0 (because there is no previous shearing for the first shearing)
    periods_since_shearing_p9a1e1b1nwzida0e0b0xyg0 = a_p_p9a1e1b1nwzida0e0b0xyg0 - np.maximum(period_previous_shearing_p9a1e1b1nwzida0e0b0xyg0, date_born_idx_ida0e0b0xyg0)
    periods_since_shearing_p9a1e1b1nwzida0e0b0xyg1 = a_p_p9a1e1b1nwzida0e0b0xyg1 - np.maximum(period_previous_shearing_p9a1e1b1nwzida0e0b0xyg1, date_born_idx_ida0e0b0xyg1)
    periods_since_shearing_tp9a1e1b1nwzida0e0b0xyg3 = a_p_p9a1e1b1nwzida0e0b0xyg3 - np.maximum(period_previous_shearing_tp9a1e1b1nwzida0e0b0xyg3, date_born_idx_ida0e0b0xyg3)
    months_since_shearing_p9a1e1b1nwzida0e0b0xyg0 = periods_since_shearing_p9a1e1b1nwzida0e0b0xyg0 * 7 / 30 #times 7 for day in period and div 30 to convert to months (this doesnt need to be perfect its only an approximation)
    months_since_shearing_p9a1e1b1nwzida0e0b0xyg1 = periods_since_shearing_p9a1e1b1nwzida0e0b0xyg1 * 7 / 30 #times 7 for day in period and div 30 to convert to months (this doesnt need to be perfect its only an approximation)
    months_since_shearing_tp9a1e1b1nwzida0e0b0xyg3 = periods_since_shearing_tp9a1e1b1nwzida0e0b0xyg3 * 7 / 30 #times 7 for day in period and div 30 to convert to months (this doesnt need to be perfect its only an approximation)
    a_months_since_shearing_p9a1e1b1nwzida0e0b0xyg0 = fun.f_find_closest(pinp.sheep['i_pmb_interval'], months_since_shearing_p9a1e1b1nwzida0e0b0xyg0)#provides the index of the index which is closest to the actual months since shearing
    a_months_since_shearing_p9a1e1b1nwzida0e0b0xyg1 = fun.f_find_closest(pinp.sheep['i_pmb_interval'], months_since_shearing_p9a1e1b1nwzida0e0b0xyg1)#provides the index of the index which is closest to the actual months since shearing
    a_months_since_shearing_tp9a1e1b1nwzida0e0b0xyg3 = fun.f_find_closest(pinp.sheep['i_pmb_interval'], months_since_shearing_tp9a1e1b1nwzida0e0b0xyg3)#provides the index of the index which is closest to the actual months since shearing
    pmb_p9a1e1b1nwzida0e0b0xyg0 = np.squeeze(np.take_along_axis(pmb_p9s4a1e1b1nwzida0e0b0xyg0,a_months_since_shearing_p9a1e1b1nwzida0e0b0xyg0[:,na,...],1),axis=p_pos) #select the relevant s4 (pmb interval) then squeeze that axis
    pmb_p9a1e1b1nwzida0e0b0xyg1 = np.squeeze(np.take_along_axis(pmb_p9s4a1e1b1nwzida0e0b0xyg1,a_months_since_shearing_p9a1e1b1nwzida0e0b0xyg1[:,na,...],1),axis=p_pos) #select the relevant s4 (pmb interval) then squeeze that axis
    pmb_tp9a1e1b1nwzida0e0b0xyg3 = np.squeeze(np.take_along_axis(pmb_p9s4a1e1b1nwzida0e0b0xyg3[na,...],a_months_since_shearing_tp9a1e1b1nwzida0e0b0xyg3[:,:,na,...],2),axis=p_pos) #select the relevant s4 (pmb interval) then squeeze that axis
    ###apply period mask to condense p axis
    cfw_sire_p9 = o_cfw_psire[shear_mask_p0]
    fd_sire_p9 = o_fd_psire[shear_mask_p0]
    sl_sire_p9 = o_sl_psire[shear_mask_p0]
    ss_sire_p9 = o_ss_psire[shear_mask_p0]
    cfw_dams_p9 = o_cfw_pdams[shear_mask_p1]
    fd_dams_p9 = o_fd_pdams[shear_mask_p1]
    sl_dams_p9 = o_sl_pdams[shear_mask_p1]
    ss_dams_p9 = o_ss_pdams[shear_mask_p1]
    cfw_offs_p9 = o_cfw_poffs[shear_mask_p3]
    fd_offs_p9 = o_fd_poffs[shear_mask_p3]
    sl_offs_p9 = o_sl_poffs[shear_mask_p3]
    ss_offs_p9 = o_ss_poffs[shear_mask_p3]
    ###micron price guide
    woolp_mpg_w4 = sfun.f_woolprice().astype(dtype)/100
    r_vals['woolp_mpg_w4'] = woolp_mpg_w4
    r_vals['fd_range'] = uinp.sheep['i_woolp_fd_range_w4']
    woolvalue_pa1e1b1nwzida0e0b0xyg0[shear_mask_p0], woolp_stbnib_sire = sfun.f_wool_value(woolp_mpg_w4, cfw_sire_p9, fd_sire_p9, sl_sire_p9, ss_sire_p9, vm_p9a1e1b1nwzida0e0b0xyg0,
                                                                             pmb_p9a1e1b1nwzida0e0b0xyg0, dtype)
    woolvalue_pa1e1b1nwzida0e0b0xyg1[shear_mask_p1], woolp_stbnib_dams = sfun.f_wool_value(woolp_mpg_w4, cfw_dams_p9, fd_dams_p9, sl_dams_p9, ss_dams_p9, vm_p9a1e1b1nwzida0e0b0xyg1,
                                                                             pmb_p9a1e1b1nwzida0e0b0xyg1, dtype)
    woolvalue_tpa1e1b1nwzida0e0b0xyg3[:,shear_mask_p3], woolp_stbnib_offs = sfun.f_wool_value(woolp_mpg_w4, cfw_offs_p9, fd_offs_p9, sl_offs_p9, ss_offs_p9, vm_p9a1e1b1nwzida0e0b0xyg3,
                                                                             pmb_tp9a1e1b1nwzida0e0b0xyg3, dtype)
    wool_finish= time.time()


    ##Sale value - To speed the calculation process the p array is condensed to only include periods where shearing occurs. Using a slightly different association it is then converted to a v array (this process usually used a p to v association, in this case we use s to v association).
    ###create mask which is the periods where shearing occurs
    sale_mask_p0 = np.any(period_is_sale_pa1e1b1nwzida0e0b0xyg0, axis=tuple(range(p_pos+1,0)))
    sale_mask_p1 = fun.f_reduce_skipfew(np.any, np.logical_or(period_is_sale_tpa1e1b1nwzida0e0b0xyg1, period_is_assetvalue_pa1e1b1nwzida0e0b0xyg), preserveAxis=1)  #preforms np.any on all axis except 1. only use the sale slices from the dam t axis
    sale_mask_p2 = fun.f_reduce_skipfew(np.any, np.logical_or(period_is_sale_t0_pa1e1b1nwzida0e0b0xyg2, period_is_assetvalue_pa1e1b1nwzida0e0b0xyg), preserveAxis=0)  #preforms np.any on all axis except 1. only use the sale slices from the dam t axis
    sale_mask_p3 = fun.f_reduce_skipfew(np.any, np.logical_or(period_is_sale_tpa1e1b1nwzida0e0b0xyg3, period_is_assetvalue_pa1e1b1nwzida0e0b0xyg[mask_p_offs_p]), preserveAxis=1)  #preforms np.any on all axis except 1
    ###manipulate axis with associations
    grid_scorerange_s7s6pa1e1b1nwzida0e0b0xyg = score_range_s8s6pa1e1b1nwzida0e0b0xyg[uinp.sheep['ia_s8_s7']] #s8 to s7
    month_scalar_s7pa1e1b1nwzida0e0b0xyg = price_adj_months_s7s9m4a1e1b1nwzida0e0b0xyg[:, 0, a_m4_p] #month to p
    month_discount_s7pa1e1b1nwzida0e0b0xyg = price_adj_months_s7s9m4a1e1b1nwzida0e0b0xyg[:, 1, a_m4_p] #month to p
    ###Sale price grids for selected price percentile and the scalars for LW & quality score
    grid_price_s7s5s6 = sfun.f_saleprice(score_pricescalar_s7s5s6, weight_pricescalar_s7s5s6, dtype)
    r_vals['grid_price_s7s5s6'] = grid_price_s7s5s6
    r_vals['weight_range_s7s5'] = uinp.sheep['i_salep_weight_range_s7s5'].reshape(uinp.sheep['i_s7_len'], uinp.sheep['i_s5_len'])
    r_vals['salegrid_keys'] = uinp.sheep['i_salegrid_keys']
    grid_price_s7s5s6pa1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(grid_price_s7s5s6,p_pos-1)
    ###apply condensed periods mask
    month_scalar_s7p9a1e1b1nwzida0e0b0xyg0 = month_scalar_s7pa1e1b1nwzida0e0b0xyg[:,sale_mask_p0] 
    month_scalar_s7p9a1e1b1nwzida0e0b0xyg1 = month_scalar_s7pa1e1b1nwzida0e0b0xyg[:,sale_mask_p1] 
    month_scalar_s7p9a1e1b1nwzida0e0b0xyg2 = month_scalar_s7pa1e1b1nwzida0e0b0xyg[:,sale_mask_p2]
    month_scalar_s7p9a1e1b1nwzida0e0b0xyg3 = month_scalar_s7pa1e1b1nwzida0e0b0xyg[:,mask_p_offs_p][:,sale_mask_p3] #mask p axis with off p mask then mask p axis with sale mask
    month_discount_s7p9a1e1b1nwzida0e0b0xyg0 = month_discount_s7pa1e1b1nwzida0e0b0xyg[:,sale_mask_p0] 
    month_discount_s7p9a1e1b1nwzida0e0b0xyg1 = month_discount_s7pa1e1b1nwzida0e0b0xyg[:,sale_mask_p1] 
    month_discount_s7p9a1e1b1nwzida0e0b0xyg2 = month_discount_s7pa1e1b1nwzida0e0b0xyg[:,sale_mask_p2]
    month_discount_s7p9a1e1b1nwzida0e0b0xyg3 = month_discount_s7pa1e1b1nwzida0e0b0xyg[:,mask_p_offs_p][:,sale_mask_p3] #mask p axis with off p mask then mask p axis with sale mask
    rc_start_sire_p9 = o_rc_start_psire[sale_mask_p0]
    rc_start_dams_p9 = o_rc_start_pdams[sale_mask_p1]
    rc_start_yatf_p9 = o_rc_start_pyatf[sale_mask_p2]
    rc_start_offs_p9 = o_rc_start_poffs[sale_mask_p3]
    age_end_p9a1e1b1nwzida0e0b0xyg0 = age_end_pa1e1b1nwzida0e0b0xyg0[sale_mask_p0]
    age_end_p9a1e1b1nwzida0e0b0xyg1 = age_end_pa1e1b1nwzida0e0b0xyg1[sale_mask_p1]
    age_end_p9a1e1b1nwzida0e0b0xyg2 = age_end_pa1e1b1nwzida0e0b0xyg2[sale_mask_p2]
    age_end_p9a1e1b1nwzida0e0b0xyg3 = age_end_pa1e1b1nwzida0e0b0xyg3[mask_p_offs_p][sale_mask_p3]#mask p axis with off p mask then mask p axis with sale mask
    ffcfw_p9a1e1b1nwzida0e0b0xyg0 = o_ffcfw_psire[sale_mask_p0]
    ffcfw_p9a1e1b1nwzida0e0b0xyg1 = o_ffcfw_pdams[sale_mask_p1]
    ffcfw_p9a1e1b1nwzida0e0b0xyg2 = o_ffcfw_start_pyatf[sale_mask_p2]
    ffcfw_p9a1e1b1nwzida0e0b0xyg3 = o_ffcfw_poffs[sale_mask_p3]

    salevalue_pa1e1b1nwzida0e0b0xyg0[sale_mask_p0] = sfun.f_sale_value(
        cu0_sire.astype(dtype), cx_sire[:,0:1,...].astype(dtype), rc_start_sire_p9, ffcfw_p9a1e1b1nwzida0e0b0xyg0, dresspercent_adj_yg0,
        dresspercent_adj_s6pa1e1b1nwzida0e0b0xyg,dresspercent_adj_s7pa1e1b1nwzida0e0b0xyg,
        grid_price_s7s5s6pa1e1b1nwzida0e0b0xyg, month_scalar_s7p9a1e1b1nwzida0e0b0xyg0,
        month_discount_s7p9a1e1b1nwzida0e0b0xyg0, price_type_s7pa1e1b1nwzida0e0b0xyg, cvlw_s7s5pa1e1b1nwzida0e0b0xyg,
        cvscore_s7s6pa1e1b1nwzida0e0b0xyg, grid_weightrange_s7s5pa1e1b1nwzida0e0b0xyg, grid_scorerange_s7s6pa1e1b1nwzida0e0b0xyg,
        age_end_p9a1e1b1nwzida0e0b0xyg0, discount_age_s7pa1e1b1nwzida0e0b0xyg,
        sale_cost_pc_s7pa1e1b1nwzida0e0b0xyg, sale_cost_hd_s7pa1e1b1nwzida0e0b0xyg,
        mask_s7x_s7pa1e1b1nwzida0e0b0xyg[...,0:1,:,:], sale_agemax_s7pa1e1b1nwzida0e0b0xyg0, dtype)
    salevalue_pa1e1b1nwzida0e0b0xyg1[sale_mask_p1] = sfun.f_sale_value(
        cu0_dams.astype(dtype), cx_dams[:,1:2,...].astype(dtype), rc_start_dams_p9, ffcfw_p9a1e1b1nwzida0e0b0xyg1, dresspercent_adj_yg1,
        dresspercent_adj_s6pa1e1b1nwzida0e0b0xyg,dresspercent_adj_s7pa1e1b1nwzida0e0b0xyg,
        grid_price_s7s5s6pa1e1b1nwzida0e0b0xyg, month_scalar_s7p9a1e1b1nwzida0e0b0xyg1,
        month_discount_s7p9a1e1b1nwzida0e0b0xyg1, price_type_s7pa1e1b1nwzida0e0b0xyg, cvlw_s7s5pa1e1b1nwzida0e0b0xyg,
        cvscore_s7s6pa1e1b1nwzida0e0b0xyg, grid_weightrange_s7s5pa1e1b1nwzida0e0b0xyg, grid_scorerange_s7s6pa1e1b1nwzida0e0b0xyg,
        age_end_p9a1e1b1nwzida0e0b0xyg1, discount_age_s7pa1e1b1nwzida0e0b0xyg,
        sale_cost_pc_s7pa1e1b1nwzida0e0b0xyg, sale_cost_hd_s7pa1e1b1nwzida0e0b0xyg,
        mask_s7x_s7pa1e1b1nwzida0e0b0xyg[...,1:2,:,:], sale_agemax_s7pa1e1b1nwzida0e0b0xyg1, dtype)
    salevalue_p9a1e1b1nwzida0e0b0xyg2 = sfun.f_sale_value(                                                #keep it as a condensed p axis
        cu0_yatf.astype(dtype), cx_yatf[:,mask_x,...].astype(dtype), rc_start_yatf_p9, ffcfw_p9a1e1b1nwzida0e0b0xyg2, dresspercent_adj_yg2,
        dresspercent_adj_s6pa1e1b1nwzida0e0b0xyg,dresspercent_adj_s7pa1e1b1nwzida0e0b0xyg,
        grid_price_s7s5s6pa1e1b1nwzida0e0b0xyg, month_scalar_s7p9a1e1b1nwzida0e0b0xyg2,
        month_discount_s7p9a1e1b1nwzida0e0b0xyg2, price_type_s7pa1e1b1nwzida0e0b0xyg, cvlw_s7s5pa1e1b1nwzida0e0b0xyg,
        cvscore_s7s6pa1e1b1nwzida0e0b0xyg, grid_weightrange_s7s5pa1e1b1nwzida0e0b0xyg, grid_scorerange_s7s6pa1e1b1nwzida0e0b0xyg,
        age_end_p9a1e1b1nwzida0e0b0xyg2, discount_age_s7pa1e1b1nwzida0e0b0xyg,
        sale_cost_pc_s7pa1e1b1nwzida0e0b0xyg, sale_cost_hd_s7pa1e1b1nwzida0e0b0xyg,
        mask_s7x_s7pa1e1b1nwzida0e0b0xyg3, sale_agemax_s7pa1e1b1nwzida0e0b0xyg2, dtype)
    salevalue_pa1e1b1nwzida0e0b0xyg3[sale_mask_p3] = sfun.f_sale_value(
        cu0_offs, cx_offs[:,mask_x,...].astype(dtype), rc_start_offs_p9, ffcfw_p9a1e1b1nwzida0e0b0xyg3, dresspercent_adj_yg3,
        dresspercent_adj_s6pa1e1b1nwzida0e0b0xyg,dresspercent_adj_s7pa1e1b1nwzida0e0b0xyg,
        grid_price_s7s5s6pa1e1b1nwzida0e0b0xyg, month_scalar_s7p9a1e1b1nwzida0e0b0xyg3,
        month_discount_s7p9a1e1b1nwzida0e0b0xyg3, price_type_s7pa1e1b1nwzida0e0b0xyg, cvlw_s7s5pa1e1b1nwzida0e0b0xyg,
        cvscore_s7s6pa1e1b1nwzida0e0b0xyg, grid_weightrange_s7s5pa1e1b1nwzida0e0b0xyg, grid_scorerange_s7s6pa1e1b1nwzida0e0b0xyg,
        age_end_p9a1e1b1nwzida0e0b0xyg3, discount_age_s7pa1e1b1nwzida0e0b0xyg,
        sale_cost_pc_s7pa1e1b1nwzida0e0b0xyg, sale_cost_hd_s7pa1e1b1nwzida0e0b0xyg,
        mask_s7x_s7pa1e1b1nwzida0e0b0xyg3, sale_agemax_s7pa1e1b1nwzida0e0b0xyg3, dtype)

    sale_finish= time.time()

    ##Husbandry #todo add feedbudgeting and labour for maintenance of infrastructure (it is currently has a cost that is representing materials and labour)
    ###Sire: cost, labour and infrastructure requirements
    husbandry_cost_pg0, husbandry_labour_l2pg0, husbandry_infrastructure_h1pg0 = sfun.f_husbandry(
        uinp.sheep['i_head_adjust_sire'], mobsize_pa1e1b1nwzida0e0b0xyg0, o_ffcfw_psire, o_cfw_psire, operations_triggerlevels_h5h7h2pg,
        p_index_pa1e1b1nwzida0e0b0xyg, age_start_pa1e1b1nwzida0e0b0xyg0, period_is_shearing_pa1e1b1nwzida0e0b0xyg0, a_nextshear_pa1e1b1nwzida0e0b0xyg0,
        period_is_wean_pa1e1b1nwzida0e0b0xyg0, gender_xyg[0], o_ebg_psire, wool_genes_yg0, husb_operations_muster_propn_h2pg,
        husb_requisite_cost_h6pg, husb_operations_requisites_prob_h6h2pg, operations_per_hour_l2h2pg,
        husb_operations_infrastructurereq_h1h2pg, husb_operations_contract_cost_h2pg, husb_muster_requisites_prob_h6h4pg,
        musters_per_hour_l2h4pg, husb_muster_infrastructurereq_h1h4pg, dtype=dtype)
    ###Dams: cost, labour and infrastructure requirements - accounts for yatf costs as well
    husbandry_cost_pg1, husbandry_labour_l2pg1, husbandry_infrastructure_h1pg1 = sfun.f_husbandry(
        uinp.sheep['i_head_adjust_dams'], mobsize_pa1e1b1nwzida0e0b0xyg1, o_ffcfw_pdams, o_cfw_pdams, operations_triggerlevels_h5h7h2pg,
        p_index_pa1e1b1nwzida0e0b0xyg, age_start_pa1e1b1nwzida0e0b0xyg1, period_is_shearing_pa1e1b1nwzida0e0b0xyg1, a_nextshear_pa1e1b1nwzida0e0b0xyg1,
        period_is_wean_pa1e1b1nwzida0e0b0xyg1, gender_xyg[1], o_ebg_pdams, wool_genes_yg1, husb_operations_muster_propn_h2pg,
        husb_requisite_cost_h6pg, husb_operations_requisites_prob_h6h2pg, operations_per_hour_l2h2pg,
        husb_operations_infrastructurereq_h1h2pg, husb_operations_contract_cost_h2pg, husb_muster_requisites_prob_h6h4pg,
        musters_per_hour_l2h4pg, husb_muster_infrastructurereq_h1h4pg,
        nyatf_b1nwzida0e0b0xyg, period_is_join_pa1e1b1nwzida0e0b0xyg1, animal_mated_b1g1, period_is_matingend_pa1e1b1nwzida0e0b0xyg1, dtype=dtype)
    ###offs: cost, labour and infrastructure requirements
    husbandry_cost_pg3, husbandry_labour_l2pg3, husbandry_infrastructure_h1pg3 = sfun.f_husbandry(
        uinp.sheep['i_head_adjust_offs'], mobsize_pa1e1b1nwzida0e0b0xyg3, o_ffcfw_poffs, o_cfw_poffs, operations_triggerlevels_h5h7h2pg,
        p_index_pa1e1b1nwzida0e0b0xyg3, age_start_pa1e1b1nwzida0e0b0xyg3[mask_p_offs_p], period_is_shearing_pa1e1b1nwzida0e0b0xyg3, a_nextshear_pa1e1b1nwzida0e0b0xyg3,
        period_is_wean_pa1e1b1nwzida0e0b0xyg3, gender_xyg[mask_x], o_ebg_poffs, wool_genes_yg3, husb_operations_muster_propn_h2pg,
        husb_requisite_cost_h6pg, husb_operations_requisites_prob_h6h2pg, operations_per_hour_l2h2pg,
        husb_operations_infrastructurereq_h1h2pg, husb_operations_contract_cost_h2pg, husb_muster_requisites_prob_h6h4pg,
        musters_per_hour_l2h4pg, husb_muster_infrastructurereq_h1h4pg, dtype=dtype)

    husb_finish= time.time()

    ##asset value infra
    assetvalue_infra_h1 = uinp.sheep['i_infrastructure_asset_h1']

    ##infra r&m cost - cost allocated equally into each cashflow period
    rm_stockinfra_var = uinp.sheep['i_infrastructure_costvariable_h1'] / len(uinp.structure['cashflow_periods'])
    rm_stockinfra_var_h1c = rm_stockinfra_var[:,na] * np.ones(len(uinp.structure['cashflow_periods']))
    rm_stockinfra_fix = uinp.sheep['i_infrastructure_costfixed_h1'] / len(uinp.structure['cashflow_periods'])
    rm_stockinfra_fix_h1c = rm_stockinfra_fix[:,na] * np.ones(len(uinp.structure['cashflow_periods']))

    ##combine income and cost from wool, sale and husb.
    ###sire
    assetvalue_pa1e1b1nwzida0e0b0xyg0 =  ((salevalue_pa1e1b1nwzida0e0b0xyg0 + woolvalue_pa1e1b1nwzida0e0b0xyg0) #calc asset value before adjusting by period is sale and shearing
                                            * period_is_assetvalue_pa1e1b1nwzida0e0b0xyg)
    salevalue_pa1e1b1nwzida0e0b0xyg0 = salevalue_pa1e1b1nwzida0e0b0xyg0 * period_is_sale_pa1e1b1nwzida0e0b0xyg0
    woolvalue_pa1e1b1nwzida0e0b0xyg0 = woolvalue_pa1e1b1nwzida0e0b0xyg0 * period_is_shearing_pa1e1b1nwzida0e0b0xyg0
    cashflow_pa1e1b1nwzida0e0b0xyg0 =  (salevalue_pa1e1b1nwzida0e0b0xyg0 + woolvalue_pa1e1b1nwzida0e0b0xyg0
                                         - husbandry_cost_pg0)
    ###dams
    assetvalue_pa1e1b1nwzida0e0b0xyg1 =  ((salevalue_pa1e1b1nwzida0e0b0xyg1 + woolvalue_pa1e1b1nwzida0e0b0xyg1) #calc asset value before adjusting by period is sale and shearing
                                            * period_is_assetvalue_pa1e1b1nwzida0e0b0xyg)
    salevalue_tpa1e1b1nwzida0e0b0xyg1 = salevalue_pa1e1b1nwzida0e0b0xyg1 * period_is_sale_tpa1e1b1nwzida0e0b0xyg1
    woolvalue_pa1e1b1nwzida0e0b0xyg1 = woolvalue_pa1e1b1nwzida0e0b0xyg1 * period_is_shearing_pa1e1b1nwzida0e0b0xyg1
    cashflow_tpa1e1b1nwzida0e0b0xyg1 =  (salevalue_tpa1e1b1nwzida0e0b0xyg1 + woolvalue_pa1e1b1nwzida0e0b0xyg1
                                         - husbandry_cost_pg1)
    ###offs
    assetvalue_tpa1e1b1nwzida0e0b0xyg3 =  ((salevalue_pa1e1b1nwzida0e0b0xyg3 + woolvalue_tpa1e1b1nwzida0e0b0xyg3) #calc asset value before adjusting by period is sale and shearing
                                            * period_is_assetvalue_pa1e1b1nwzida0e0b0xyg[mask_p_offs_p])
    salevalue_tpa1e1b1nwzida0e0b0xyg3 = salevalue_pa1e1b1nwzida0e0b0xyg3 * period_is_sale_tpa1e1b1nwzida0e0b0xyg3
    woolvalue_tpa1e1b1nwzida0e0b0xyg3 = woolvalue_tpa1e1b1nwzida0e0b0xyg3 * period_is_shearing_pa1e1b1nwzida0e0b0xyg3
    cashflow_tpa1e1b1nwzida0e0b0xyg3 =  (salevalue_tpa1e1b1nwzida0e0b0xyg3 + woolvalue_tpa1e1b1nwzida0e0b0xyg3
                                         - husbandry_cost_pg3)

    ######################
    # add yatf to dams   #
    ######################
    o_pi_pdams *= fun.f_divide(o_mei_solid_pdams + np.sum(o_mei_solid_pyatf * gender_propn_xyg, axis=x_pos, keepdims=True),
                              o_mei_solid_pdams, dtype=dtype)  # done before adding yatf mei. This is instead of adding pi yatf with pi dams because some of the potential intake of the yatf is 'used' consuming milk. Doing it via mei keeps the ratio mei_dams/pi_dams the same before and after adding the yatf. This is what we want because it is saying that there is a given energy intake and it needs to be of a certain quality.
    o_mei_solid_pdams = o_mei_solid_pdams + np.sum(o_mei_solid_pyatf * gender_propn_xyg, axis=x_pos, keepdims=True)


    ############
    #feed pools#
    ############
    feedpools_start = time.time()
    ##Calculate the feed pools (f) and allocate each intake period to a feed pool based on mei/volume (E/V). - this is done like this to handle the big arrays easier - also handles situations where offs and dams may have diff length p axis
    ###calculate ‘ev’ for each animal class.
    ev_sire = fun.f_divide(o_mei_solid_psire, o_pi_psire, dtype=dtype)
    ev_dams = fun.f_divide(o_mei_solid_pdams, o_pi_pdams, dtype=dtype)
    ev_offs = fun.f_divide(o_mei_solid_poffs, o_pi_poffs, dtype=dtype)
    ###Find the values that divides the values into 4 equal groups
    t_ev_pa1e1b1nwzida0e0b0xyg1 = ev_dams * (feedsupplyw_pa1e1b1nwzida0e0b0xyg1 < 3) # feedsupply >= 3 (ie the animals are in confinement)
    t_ev_pa1e1b1nwzida0e0b0xyg3 = ev_offs * (feedsupplyw_pa1e1b1nwzida0e0b0xyg3 < 3) # feedsupply >= 3 (ie the animals are in confinement)
    ###set 0 to high value so it doesnt get included in the next steps
    t_ev_min_pa1e1b1nwzida0e0b0xyg1 = t_ev_pa1e1b1nwzida0e0b0xyg1.copy() #have to copy so other array is not changed
    t_ev_min_pa1e1b1nwzida0e0b0xyg3 = t_ev_pa1e1b1nwzida0e0b0xyg3.copy()
    t_ev_min_pa1e1b1nwzida0e0b0xyg1[t_ev_min_pa1e1b1nwzida0e0b0xyg1<=0] = 100
    t_ev_min_pa1e1b1nwzida0e0b0xyg3[t_ev_min_pa1e1b1nwzida0e0b0xyg3<=0] = 100
    ###calc max and min - set 0 to high value so it doesnt get included in the next steps
    t_evmax_pdams = np.max(t_ev_pa1e1b1nwzida0e0b0xyg1,axis=tuple(range(a1_pos,0)))
    t_evmin_pdams = np.min(t_ev_min_pa1e1b1nwzida0e0b0xyg1,axis=tuple(range(a1_pos,0)))
    t_evmax_poffs = np.max(t_ev_pa1e1b1nwzida0e0b0xyg3,axis=tuple(range(a1_pos,0)))
    t_evmin_poffs = np.min(t_ev_min_pa1e1b1nwzida0e0b0xyg3,axis=tuple(range(a1_pos,0)))
    ###Create the p6p arrays
    t_evmax_p6pdams = t_evmax_pdams * (a_p6_p == index_p6[...,na])
    t_evmin_p6pdams = t_evmin_pdams * (a_p6_p == index_p6[...,na])
    t_evmax_p6poffs = t_evmax_poffs * (a_p6_p[mask_p_offs_p] == index_p6[...,na])
    t_evmin_p6poffs = t_evmin_poffs * (a_p6_p[mask_p_offs_p] == index_p6[...,na])
    ###set 0 to nan for p slices that are not in p6
    t_evmax_p6pdams[t_evmax_p6pdams<=0] = np.nan
    t_evmin_p6pdams[t_evmin_p6pdams<=0] = np.nan
    t_evmax_p6poffs[t_evmax_p6poffs<=0] = np.nan
    t_evmin_p6poffs[t_evmin_p6poffs<=0] = np.nan
    ###Calculate the max and min over the p axis for each p6
    t_evmax_p6dams = np.nanmax(t_evmax_p6pdams,axis=-1)
    t_evmin_p6dams = np.nanmin(t_evmin_p6pdams,axis=-1)
    t_evmax_p6offs = np.nanmax(t_evmax_p6poffs,axis=-1)
    t_evmin_p6offs = np.nanmin(t_evmin_p6poffs,axis=-1)
    ###Calculate the overall min & max for p6 by taking min & max of dams & offs
    t_evmax_p6 = np.maximum(t_evmax_p6dams, t_evmax_p6offs)
    t_evmin_p6 = np.minimum(t_evmin_p6dams, t_evmin_p6offs)
    ###Calculate the EV for each cutoff (upper value) for each matrix feed period (based on equal spacing, not equal numbers)
    ev_cutoff_p6f = t_evmax_p6[:,na] * ev_propn_f + t_evmin_p6[:,na] * (1 - ev_propn_f)
    ##allocate each sheep class to an ev group - use MRY version of searchsort which handles 2d array
    a_ev_pa1e1b1nwzida0e0b0xyg0 = fun.searchsort_multiple_dim(ev_cutoff_p6f[a_p6_p], ev_sire, 0, 0)
    a_ev_pa1e1b1nwzida0e0b0xyg1 = fun.searchsort_multiple_dim(ev_cutoff_p6f[a_p6_p], ev_dams, 0, 0)
    a_ev_pa1e1b1nwzida0e0b0xyg3 = fun.searchsort_multiple_dim(ev_cutoff_p6f[a_p6_p[mask_p_offs_p]], ev_offs, 0, 0)
    ##Any animals with feedsupply >= 3 has ev_group = 4 (the confinement pattern)
    a_ev_pa1e1b1nwzida0e0b0xyg0 = fun.f_update(a_ev_pa1e1b1nwzida0e0b0xyg0,4,(feedsupplyw_pa1e1b1nwzida0e0b0xyg0 >= 3)).astype(dtypeint) #for some reason adding float32 with int32 results in float64
    a_ev_pa1e1b1nwzida0e0b0xyg1 = fun.f_update(a_ev_pa1e1b1nwzida0e0b0xyg1,4,(feedsupplyw_pa1e1b1nwzida0e0b0xyg1 >= 3)).astype(dtypeint) #for some reason adding float32 with int32 results in float64
    a_ev_pa1e1b1nwzida0e0b0xyg3 = fun.f_update(a_ev_pa1e1b1nwzida0e0b0xyg3,4,(feedsupplyw_pa1e1b1nwzida0e0b0xyg3 >= 3)).astype(dtypeint) #for some reason adding float32 with int32 results in float64
    ##add ev params to dict for use in pasture.py
    ev['ev_cutoff_p6f'] = ev_cutoff_p6f
    ev['ev_max_p6'] = t_evmax_p6

    ################################
    #convert variables from p to v #
    ################################
    p2v_start = time.time()
    ##every period - with f & p6 axis
    ###sire - use p2v_std because there is not dvp so this version of the function may as well be used.
    mei_p6fa1e1b1nwzida0e0b0xyg0 = sfun.f_p2v_std(o_mei_solid_psire, numbers_p=o_numbers_end_psire, on_hand_tvp=on_hand_pa1e1b1nwzida0e0b0xyg0
                                         , days_period_p=days_period_pa1e1b1nwzida0e0b0xyg0, a_any1_p=a_ev_pa1e1b1nwzida0e0b0xyg0, index_any1tvp=index_fpa1e1b1nwzida0e0b0xyg
                                        , a_any2_p=a_p6_pa1e1b1nwzida0e0b0xyg, index_any2any1tvp=index_p6pa1e1b1nwzida0e0b0xyg[:,na,...])
    pi_p6fa1e1b1nwzida0e0b0xyg0 = sfun.f_p2v_std(o_pi_psire, numbers_p=o_numbers_end_psire, on_hand_tvp=on_hand_pa1e1b1nwzida0e0b0xyg0
                                         , days_period_p=days_period_pa1e1b1nwzida0e0b0xyg0, a_any1_p=a_ev_pa1e1b1nwzida0e0b0xyg0, index_any1tvp=index_fpa1e1b1nwzida0e0b0xyg
                                        , a_any2_p=a_p6_pa1e1b1nwzida0e0b0xyg, index_any2any1tvp=index_p6pa1e1b1nwzida0e0b0xyg[:,na,...])
    ###dams
    mei_p6ftva1e1b1nwzida0e0b0xyg1 = sfun.f_p2v(o_mei_solid_pdams, a_v_pa1e1b1nwzida0e0b0xyg1, o_numbers_end_pdams
                                       , on_hand_tpa1e1b1nwzida0e0b0xyg1, days_period_pa1e1b1nwzida0e0b0xyg1, a_any1_p=a_ev_pa1e1b1nwzida0e0b0xyg1, index_any1tp=index_fpa1e1b1nwzida0e0b0xyg[:,na,...]
                                       , a_any2_p=a_p6_pa1e1b1nwzida0e0b0xyg, index_any2any1tp=index_p6pa1e1b1nwzida0e0b0xyg[:,na,na,...])

    pi_p6ftva1e1b1nwzida0e0b0xyg1 = sfun.f_p2v(o_pi_pdams, a_v_pa1e1b1nwzida0e0b0xyg1, o_numbers_end_pdams
                                           , on_hand_tpa1e1b1nwzida0e0b0xyg1, days_period_pa1e1b1nwzida0e0b0xyg1, a_any1_p=a_ev_pa1e1b1nwzida0e0b0xyg1, index_any1tp=index_fpa1e1b1nwzida0e0b0xyg[:,na,...]
                                           , a_any2_p=a_p6_pa1e1b1nwzida0e0b0xyg, index_any2any1tp=index_p6pa1e1b1nwzida0e0b0xyg[:,na,na,...])

    ###offs
    mei_p6ftva1e1b1nwzida0e0b0xyg3 = sfun.f_p2v(o_mei_solid_poffs, a_v_pa1e1b1nwzida0e0b0xyg3, o_numbers_end_poffs
                                       , on_hand_tpa1e1b1nwzida0e0b0xyg3, days_period_cut_pa1e1b1nwzida0e0b0xyg3, a_any1_p=a_ev_pa1e1b1nwzida0e0b0xyg3, index_any1tp=index_fpa1e1b1nwzida0e0b0xyg[:,na,...]
                                       , a_any2_p=a_p6_pa1e1b1nwzida0e0b0xyg[mask_p_offs_p], index_any2any1tp=index_p6pa1e1b1nwzida0e0b0xyg[:,na,na,...])
    pi_p6ftva1e1b1nwzida0e0b0xyg3 = sfun.f_p2v(o_pi_poffs, a_v_pa1e1b1nwzida0e0b0xyg3, o_numbers_end_poffs
                                           , on_hand_tpa1e1b1nwzida0e0b0xyg3, days_period_cut_pa1e1b1nwzida0e0b0xyg3, a_any1_p=a_ev_pa1e1b1nwzida0e0b0xyg3, index_any1tp=index_fpa1e1b1nwzida0e0b0xyg[:,na,...]
                                           , a_any2_p=a_p6_pa1e1b1nwzida0e0b0xyg[mask_p_offs_p], index_any2any1tp=index_p6pa1e1b1nwzida0e0b0xyg[:,na,na,...])

    ##every period - with sire periods
    nsire_tva1e1b1nwzida0e0b0xyg1g0p8 = sfun.f_p2v_std(o_n_sire_pa1e1b1nwzida0e0b0xyg1g0p8, a_v_pa1e1b1nwzida0e0b0xyg1[...,na,na], index_vpa1e1b1nwzida0e0b0xyg1[...,na,na]
                                               , o_numbers_end_pdams[...,na,na], on_hand_tpa1e1b1nwzida0e0b0xyg1[:,na,...,na,na], sumadj=2)


    ##every period - with cost (c) axis (when combining the cost the period is arrays were already applied therefore converted from 'intermittent' to 'every period'
    ##cost requires a c axis for reporting - it is summed before converting to a param because MINROE doesnt need c axis
    purchcost_cva1e1b1nwzida0e0b0xyg0 = sfun.f_p2v_std(purchcost_g0, numbers_p=o_numbers_end_psire,
                                                       period_is_tvp=period_is_startdvp_purchase_pa1e1b1nwzida0e0b0xyg0,
                                                       a_any1_p=a_c_pa1e1b1nwzida0e0b0xyg, index_any1tvp=index_ctpa1e1b1nwzida0e0b0xyg)
    cashflow_ctva1e1b1nwzida0e0b0xyg0 = sfun.f_p2v_std(cashflow_pa1e1b1nwzida0e0b0xyg0, numbers_p=o_numbers_end_psire,
                                              on_hand_tvp=on_hand_pa1e1b1nwzida0e0b0xyg0, a_any1_p=a_c_pa1e1b1nwzida0e0b0xyg,index_any1tvp=index_ctpa1e1b1nwzida0e0b0xyg)
    cost_ctva1e1b1nwzida0e0b0xyg0 = sfun.f_p2v_std(husbandry_cost_pg0, numbers_p=o_numbers_end_psire,
                                              on_hand_tvp=on_hand_pa1e1b1nwzida0e0b0xyg0, a_any1_p=a_c_pa1e1b1nwzida0e0b0xyg,index_any1tvp=index_ctpa1e1b1nwzida0e0b0xyg)
    assetvalue_va1e1b1nwzida0e0b0xyg0 = sfun.f_p2v_std(assetvalue_pa1e1b1nwzida0e0b0xyg0, numbers_p=o_numbers_end_psire,
                                              on_hand_tvp=on_hand_pa1e1b1nwzida0e0b0xyg0)
    cashflow_ctva1e1b1nwzida0e0b0xyg1 = sfun.f_p2v(cashflow_tpa1e1b1nwzida0e0b0xyg1, a_v_pa1e1b1nwzida0e0b0xyg1, o_numbers_end_pdams,
                                              on_hand_tpa1e1b1nwzida0e0b0xyg1, a_any1_p=a_c_pa1e1b1nwzida0e0b0xyg,index_any1tp=index_ctpa1e1b1nwzida0e0b0xyg)
    cost_ctva1e1b1nwzida0e0b0xyg1 = sfun.f_p2v(husbandry_cost_pg1, a_v_pa1e1b1nwzida0e0b0xyg1, o_numbers_end_pdams,
                                              on_hand_tpa1e1b1nwzida0e0b0xyg1, a_any1_p=a_c_pa1e1b1nwzida0e0b0xyg,index_any1tp=index_ctpa1e1b1nwzida0e0b0xyg)
    assetvalue_tva1e1b1nwzida0e0b0xyg1 = sfun.f_p2v(assetvalue_pa1e1b1nwzida0e0b0xyg1, a_v_pa1e1b1nwzida0e0b0xyg1, o_numbers_end_pdams,
                                              on_hand_tpa1e1b1nwzida0e0b0xyg1)
    cashflow_ctva1e1b1nwzida0e0b0xyg3 = sfun.f_p2v(cashflow_tpa1e1b1nwzida0e0b0xyg3, a_v_pa1e1b1nwzida0e0b0xyg3, o_numbers_end_poffs,
                                              on_hand_tpa1e1b1nwzida0e0b0xyg3, a_any1_p=a_c_pa1e1b1nwzida0e0b0xyg[mask_p_offs_p],index_any1tp=index_ctpa1e1b1nwzida0e0b0xyg)
    cost_ctva1e1b1nwzida0e0b0xyg3 = sfun.f_p2v(husbandry_cost_pg3, a_v_pa1e1b1nwzida0e0b0xyg3, o_numbers_end_poffs,
                                              on_hand_tpa1e1b1nwzida0e0b0xyg3, a_any1_p=a_c_pa1e1b1nwzida0e0b0xyg[mask_p_offs_p],index_any1tp=index_ctpa1e1b1nwzida0e0b0xyg)
    assetvalue_tva1e1b1nwzida0e0b0xyg3 = sfun.f_p2v(assetvalue_tpa1e1b1nwzida0e0b0xyg3, a_v_pa1e1b1nwzida0e0b0xyg3, o_numbers_end_poffs,
                                              on_hand_tpa1e1b1nwzida0e0b0xyg3)

    ##every period - with labour (p5) axis
    labour_l2p5tva1e1b1nwzida0e0b0xyg0 = sfun.f_p2v_std(husbandry_labour_l2pg0[:,na,na,...], numbers_p=o_numbers_end_psire,
                                             on_hand_tvp=on_hand_pa1e1b1nwzida0e0b0xyg0, a_any1_p=a_p5_pa1e1b1nwzida0e0b0xyg,index_any1tvp=index_p5tpa1e1b1nwzida0e0b0xyg)
    labour_l2p5tva1e1b1nwzida0e0b0xyg1 = sfun.f_p2v(husbandry_labour_l2pg1[:,na,na,...], a_v_pa1e1b1nwzida0e0b0xyg1, o_numbers_end_pdams,
                                             on_hand_tpa1e1b1nwzida0e0b0xyg1, a_any1_p=a_p5_pa1e1b1nwzida0e0b0xyg,index_any1tp=index_p5tpa1e1b1nwzida0e0b0xyg)
    labour_l2p5tva1e1b1nwzida0e0b0xyg3 = sfun.f_p2v(husbandry_labour_l2pg3[:,na,na,...], a_v_pa1e1b1nwzida0e0b0xyg3, o_numbers_end_poffs,
                                             on_hand_tpa1e1b1nwzida0e0b0xyg3, a_any1_p=a_p5_pa1e1b1nwzida0e0b0xyg[mask_p_offs_p],index_any1tp=index_p5tpa1e1b1nwzida0e0b0xyg)

    ##every period - with infrastructure (h1) axis
    infrastructure_h1va1e1b1nwzida0e0b0xyg0 = sfun.f_p2v_std(husbandry_infrastructure_h1pg0, numbers_p=o_numbers_end_psire,
                                             on_hand_tvp=on_hand_pa1e1b1nwzida0e0b0xyg0)
    infrastructure_h1tva1e1b1nwzida0e0b0xyg1 = sfun.f_p2v(husbandry_infrastructure_h1pg1[:,na,...], a_v_pa1e1b1nwzida0e0b0xyg1, o_numbers_end_pdams,
                                             on_hand_tpa1e1b1nwzida0e0b0xyg1)
    infrastructure_h1tva1e1b1nwzida0e0b0xyg3 = sfun.f_p2v(husbandry_infrastructure_h1pg3[:,na,...], a_v_pa1e1b1nwzida0e0b0xyg3, o_numbers_end_poffs,
                                             on_hand_tpa1e1b1nwzida0e0b0xyg3)

    ##intermittent
    ###numbers
    numbers_start_va1e1b1nwzida0e0b0xyg0 = sfun.f_p2v_std(o_numbers_start_psire, on_hand_tvp=on_hand_pa1e1b1nwzida0e0b0xyg0,
                                                          period_is_tvp=period_is_startdvp_purchase_pa1e1b1nwzida0e0b0xyg0) #sires only have one dvp which essentially starts when the activity is purchased
    numbers_startp8_va1e1b1nwzida0e0b0xyg0p8 = sfun.f_p2v_std(o_numbers_start_psire[...,na], on_hand_tvp=on_hand_pa1e1b1nwzida0e0b0xyg0[...,na],
                                                          period_is_tvp=period_is_startp8_pa1e1b1nwzida0e0b0xyg0p8, sumadj=1) #sires only have one dvp which essentially starts when the activity is purchased
    numbers_end_tva1e1b1nwzida0e0b0xyg1 = sfun.f_p2v(o_numbers_end_pdams, a_v_pa1e1b1nwzida0e0b0xyg1, on_hand_tp=on_hand_tpa1e1b1nwzida0e0b0xyg1,
                                                     period_is_tp=np.logical_or(period_is_transfer_tpa1e1b1nwzida0e0b0xyg1, nextperiod_is_startdvp_pa1e1b1nwzida0e0b0xyg1))  #t axis so that the early termination of a dvp is accounted for when transferring between ram groups
    numbers_start_va1e1b1nwzida0e0b0xyg1 = sfun.f_p2v(o_numbers_start_pdams, a_v_pa1e1b1nwzida0e0b0xyg1,period_is_tp=period_is_startdvp_pa1e1b1nwzida0e0b0xyg1)
    # r_numbers_join_va1e1b1nwzida0e0b0xyg1 = sfun.f_p2v(o_numbers_join_pdams, a_v_pa1e1b1nwzida0e0b0xyg1,period_is_tp=period_is_join_pa1e1b1nwzida0e0b0xyg1) #used to calc wean %
    # r_numbers_birth_va1e1b1nwzida0e0b0xyg1 = sfun.f_p2v(o_numbers_end_pdams, a_v_pa1e1b1nwzida0e0b0xyg1,period_is_tp=period_is_birth_pa1e1b1nwzida0e0b0xyg1) #need to use numbers end so that the numbers represent the different b1 slices after birth
    numbers_end_va1e1b1nwzida0e0b0xyg3 = sfun.f_p2v(o_numbers_end_poffs, a_v_pa1e1b1nwzida0e0b0xyg3, period_is_tp=nextperiod_is_startdvp_pa1e1b1nwzida0e0b0xyg3)
    numbers_start_va1e1b1nwzida0e0b0xyg3 = sfun.f_p2v(o_numbers_start_poffs, a_v_pa1e1b1nwzida0e0b0xyg3, period_is_tp=period_is_startdvp_pa1e1b1nwzida0e0b0xyg3)
    numbers_start_d_yatf_a1e1b1nwzida0e0b0xyg2 = sfun.f_p2v_std(o_numbers_start_pyatf, period_is_tvp = period_is_wean_pa1e1b1nwzida0e0b0xyg2,
                                                        a_any1_p = a_prevbirth_d_pa1e1b1nwzida0e0b0xyg2, index_any1tvp = index_da0e0b0xyg) # Return the number of the yatf in the period in which they are weaned - with active d axis

    ###ffcfw
    #### Return the ‘source’ weight of the animal at the end of each period in which they can be transferred
    #### The period is based on period_is_transfer which points at the nextperiod_is_prejoin for the destination g1 slice
    ffcfw_end_tva1e1b1nwzida0e0b0xyg1 = sfun.f_p2v(o_ffcfw_pdams, a_v_pa1e1b1nwzida0e0b0xyg1, period_is_tp=period_is_transfer_tpa1e1b1nwzida0e0b0xyg1) #numbers not required for ffcfw
    ffcfw_end_va1e1b1nwzida0e0b0xyg3 = sfun.f_p2v(o_ffcfw_poffs, a_v_pa1e1b1nwzida0e0b0xyg3, period_is_tp=nextperiod_is_startdvp_pa1e1b1nwzida0e0b0xyg3) #numbers not required for ffcfw

    #### Return the ‘destination’ weight of each group of animal at the end of the period prior to the transfer (transfer is next period is prejoining for the destination animal)
    ##### for dams select the ‘destination’ condensed weight for the ‘source’ slices using a_g1_tg1
    ffcfw_condensed_tdams = np.take_along_axis(o_ffcfw_condensed_pdams[na,...], a_g1_tpa1e1b1nwzida0e0b0xyg1, -1)
    ##### Convert from p to v.
    ###### for dams the period is based on period_is_transfer which points at the nextperiod_is_prejoin for the destination g1 slice
    ffcfw_end_condensed_tva1e1b1nwzida0e0b0xyg1 = sfun.f_p2v(ffcfw_condensed_tdams, a_v_pa1e1b1nwzida0e0b0xyg1, period_is_tp=period_is_transfer_tpa1e1b1nwzida0e0b0xyg1)  #numbers not required for ffcfw
    ###### for offs the period is based on next period is prejoin
    ffcfw_end_condensed_va1e1b1nwzida0e0b0xyg3 = sfun.f_p2v(o_ffcfw_condensed_poffs, a_v_pa1e1b1nwzida0e0b0xyg3, period_is_tp=nextperiod_is_startdvp_pa1e1b1nwzida0e0b0xyg3) #numbers not required for ffcfw

    #### Return the weight of the yatf in the period in which they are weaned - with active dam v axis
    ffcfw_start_v_yatf_va1e1b1nwzida0e0b0xyg1 = sfun.f_p2v(o_ffcfw_start_pyatf, a_v_pa1e1b1nwzida0e0b0xyg1, period_is_tp=period_is_wean_pa1e1b1nwzida0e0b0xyg2)
    #### Return the weight of the yatf in the period in which they are weaned - with active d axis
    ffcfw_start_d_yatf_a1e1b1nwzida0e0b0xyg2 = sfun.f_p2v_std(o_ffcfw_start_pyatf, period_is_tvp=period_is_wean_pa1e1b1nwzida0e0b0xyg2,
                                                           a_any1_p=a_prevbirth_d_pa1e1b1nwzida0e0b0xyg2, index_any1tvp=index_da0e0b0xyg)

    ###npw - Return the number of the yatf in the period in which they are weaned - with active d axis
    npw_tva1e1b1nwzida0e0b0xyg1 = sfun.f_p2v(o_numbers_start_pyatf, a_v_pa1e1b1nwzida0e0b0xyg1, o_numbers_start_pdams,
                                        on_hand_tpa1e1b1nwzida0e0b0xyg1, period_is_tp=period_is_wean_pa1e1b1nwzida0e0b0xyg2,
                                        a_any1_p=a_prevbirth_d_pa1e1b1nwzida0e0b0xyg2,index_any1tp=index_da0e0b0xyg) #use numbers start because weaning is beginning of period
    ###npw2 for wean % - without d axis and x summed
    t_npw = np.sum(o_numbers_start_pyatf, axis=x_pos, keepdims=True)
    npw2_tva1e1b1nwzida0e0b0xyg1 = sfun.f_p2v(t_npw, a_v_pa1e1b1nwzida0e0b0xyg1, o_numbers_start_pdams,
                                        on_hand_tpa1e1b1nwzida0e0b0xyg1, period_is_tp=period_is_wean_pa1e1b1nwzida0e0b0xyg2) #use numbers start because weaning is beginning of period

    ###yatf can be sold as sucker, not shorn therefore only include sale value. husbandry is accounted for with dams so don't need that here.
    salevalue_d_a1e1b1nwzida0e0b0xyg2 = sfun.f_p2v_std(salevalue_p9a1e1b1nwzida0e0b0xyg2, period_is_tvp=period_is_sale_t0_pa1e1b1nwzida0e0b0xyg2[sale_mask_p2],
                                                   a_any1_p=a_prevbirth_d_pa1e1b1nwzida0e0b0xyg2[sale_mask_p2], index_any1tvp=index_da0e0b0xyg)

    ##################
    #lw distribution #
    ##################
    lwdist_start = time.time()
    ##offs are distributed each period dams only distributed when next dvp type == 0. T0 and t1 are distributed however this is not used because t0 and t1 don't transfer to next dvp
    distribution_tva1e1b1nw8zida0e0b0xyg1w9 = sfun.f_lw_distribution(ffcfw_end_condensed_tva1e1b1nwzida0e0b0xyg1, ffcfw_end_tva1e1b1nwzida0e0b0xyg1, uinp.structure['i_n1_len'], uinp.structure['i_n_fvp_period1'], dvp_type_next_tva1e1b1nwzida0e0b0xyg1[...,na])
    distribution_va1e1b1nw8zida0e0b0xyg3w9 = sfun.f_lw_distribution(ffcfw_end_condensed_va1e1b1nwzida0e0b0xyg3, ffcfw_end_va1e1b1nwzida0e0b0xyg3, uinp.structure['i_n3_len'], uinp.structure['i_n_fvp_period3'])

    ###################################
    ##animal shifting between classes #
    ###################################
    ##axis b1 is the equivalent of b18 so when adding na add it after the b1 axis
    # a_prepost_b19nwzida0e0b0xyg1 = fun.f_reshape_expand(uinp.structure['a_prepost_b1'], b1_pos)
    # index_b19nwzida0e0b0xyg1 = fun.f_reshape_expand(np.arange(len_b1), b1_pos)
    # index_b18b19nwzida0e0b0xyg1 = index_b19nwzida0e0b0xyg1[:,na,...]
    # numbers_end_adj_va1e1b18nwzida0e0b0xyg1 = fun.f_update(numbers_end_va1e1b1nwzida0e0b0xyg1, np.sum(numbers_end_va1e1b1nwzida0e0b0xyg1, axis=repro_tup, keepdims=True), dvp_type_va1e1b1nwzida0e0b0xyg1 == 0)
    # numbers_end_adj_va1e1b18nwzida0e0b0xyg1 = fun.f_update(numbers_end_adj_va1e1b18nwzida0e0b0xyg1, numbers_end_va1e1b1nwzida0e0b0xyg1[:,:,:,uinp.structure['a_prepost_b1'],...], dvp_type_va1e1b1nwzida0e0b0xyg1 == 2)
    # bb_pointer_va1e1b18b19nwzida0e0b0xyg1 = fun.f_update(index_b19nwzida0e0b0xyg1, index_b18b19nwzida0e0b0xyg1, dvp_type_va1e1b1nwzida0e0b0xyg1[:,:,:,:,na,...] == 0)
    # bb_pointer_va1e1b18b19nwzida0e0b0xyg1 = sfun.f_update(bb_pointer_va1e1b18b19nwzida0e0b0xyg1, a_prepost_b19nwzida0e0b0xyg1, dvp_type_va1e1b1nwzida0e0b0xyg1[:,:,:,:,na,...] == 2)
    # dam_shift_vb18b19 = numbers_start_next_va1e1b1nwzida0e0b0xyg1[:,:,:,:,na,...] / numbers_end_adj_va1e1b18nwzida0e0b0xyg1[:,:,:,:,na,...] * (bb_pointer_va1e1b18b19nwzida0e0b0xyg1==index_b18b19nwzida0e0b0xyg1)

    ##############
    ##clustering #
    ##############
    cluster_start = time.time()
    ##dams
    ###create k2 association based on scanning and gbal
    gbal_va1e1b1nwzida0e0b0xyg1 = np.take_along_axis(gbal_pa1e1b1nwzida0e0b0xyg1,a_dvp_p_va1e1b1nwzida0e0b0xyg1,0)
    scan_va1e1b1nwzida0e0b0xyg1 = np.take_along_axis(scan_pa1e1b1nwzida0e0b0xyg1, a_dvp_p_va1e1b1nwzida0e0b0xyg1,0)
    a_k2cluster_va1e1b1nwzida0e0b0xyg1 = np.sum(a_ppk2g1_va1e1b1nwzida0e0b0xygsl * (gbal_va1e1b1nwzida0e0b0xyg1[...,na,na]==index_l) * (scan_va1e1b1nwzida0e0b0xyg1[...,na,na]==index_s[:,na]), axis = (-1,-2))
    a_k2cluster_va1e1b1nwzida0e0b0xyg1 = a_k2cluster_va1e1b1nwzida0e0b0xyg1 + (len(uinp.structure['a_nfoet_b1']) * index_e1b1nwzida0e0b0xyg * (scan_va1e1b1nwzida0e0b0xyg1 == 4) * (nfoet_b1nwzida0e0b0xyg >= 1)) #If scanning for foetal age add 10 to the animals in the second & subsequent cycles that were scanned as pregnant (nfoet_b1 >= 1)
    ### Cluster with a t axis required for k29 which is associated with tvgg9. na to put result in g9 axis
    a_k2cluster_tva1e1b1nwzida0e0b0xyg1g9 = np.take_along_axis(a_k2cluster_va1e1b1nwzida0e0b0xyg1[na], a_g1_tpa1e1b1nwzida0e0b0xyg1, axis=-1)[..., na, :]
    ### a temporary array that is the cluster at prejoining with not mated (0) and mated (1) along the b1 axis
    temporary = np.ones_like(a_k2cluster_tva1e1b1nwzida0e0b0xyg1g9)
    temporary[:,:,:,:,0,...] = 0
    a_k2cluster_next_tva1e1b1nwzida0e0b0xyg1g9 = fun.f_update(np.roll(a_k2cluster_tva1e1b1nwzida0e0b0xyg1g9, -1, axis=1), temporary,
                                          (a_g1_tpa1e1b1nwzida0e0b0xyg1[..., na, :] != index_g1g) * transfer_exists_tpa1e1b1nwzida0e0b0xyg1[..., na])
    len_k2 = np.max(a_k2cluster_va1e1b1nwzida0e0b0xyg1)+1  #Added +1 because python starts at 0.
    index_k2tva1e1b1nwzida0e0b0xyg1 = fun.f_reshape_expand(np.arange(len_k2), uinp.structure['i_k2_pos'])
    index_k29tva1e1b1nwzida0e0b0xyg1g9 = index_k2tva1e1b1nwzida0e0b0xyg1[...,na]
    index_k28k29tva1e1b1nwzida0e0b0xyg1 = index_k2tva1e1b1nwzida0e0b0xyg1[:,na,...]

    ##offs
    ### d cluster
    a_k3cluster_da0e0b0xyg3 = fun.f_reshape_expand(np.minimum(len(pinp.sheep['i_k3_idx_offs'])-1, index_d), d_pos)
    ###b0 and e0 cluster
    a_k5cluster_da0e0b0xyg3 = np.sum(a_k5cluster_b0xygls * (gbal_da0e0b0xyg3[...,na,na]==index_l[:,na]) * (scan_da0e0b0xyg3[...,na,na]==index_s), axis = (-1,-2))
    a_k5cluster_da0e0b0xyg3 = a_k5cluster_da0e0b0xyg3 + (len_b0 * index_e0b0xyg * (scan_da0e0b0xyg3 == 4)) #If scanning for foetal age add 6 to the animals in the second & subsequent cycles. 6 is the number of slices in the b0 axes
    len_k3 = np.max(a_k3cluster_da0e0b0xyg3)+1  #Added +1 because python starts at 0.
    len_k5 = np.max(a_k5cluster_da0e0b0xyg3)+1  #Added +1 because python starts at 0.
    index_k3k5tva1e1b1nwzida0e0b0xyg3 = fun.f_reshape_expand(np.arange(len_k3), uinp.structure['i_k3_pos'])
    index_k5tva1e1b1nwzida0e0b0xyg3 = fun.f_reshape_expand(np.arange(len_k5), uinp.structure['i_k5_pos'])


    ######################################
    #Mask animals to nutrition profiles  #
    ######################################
    '''creates a mask that removes unnecessary values in the parameters. Because of the lw branching not every activity provides to a unique constraint 
        therefore some activities and constraints can be masked out'''
    allocation_start = time.time()
    ##dams
    ###Steps for ‘Numbers Provides’ is calculated with a t axis (because the t axis can alter the dvp type of the source relative to the destination)
    step_next_con1_tva1e1b1nw8zida0e0b0xyg1w9 = (uinp.structure['i_n1_len'] ** (uinp.structure['i_n_fvp_period1'] - dvp_type_next_tva1e1b1nwzida0e0b0xyg1))[...,na]
    ###Steps for ‘Numbers Requires’ & ‘Decision Variable’ is calculated without a t axis.
    step_con1_va1e1b1nw8zida0e0b0xyg1 = (uinp.structure['i_n1_len'] ** (uinp.structure['i_n_fvp_period1'] - dvp_type_va1e1b1nwzida0e0b0xyg1))
    step_dv1_va1e1b1nw8zida0e0b0xyg1 = step_con1_va1e1b1nw8zida0e0b0xyg1 / uinp.structure['i_n1_len']
    ##Mask the decision variables that are not yet active in the matrix because they share a common nutrition history (broadcast across t axis)
    mask_w8vars_va1e1b1nw8zida0e0b0xyg1 = index_wzida0e0b0xyg1 % step_dv1_va1e1b1nw8zida0e0b0xyg1 == 0
    ##mask for nutrition profiles (this allows the user to examine certain nutrition patterns eg high high high vs low low low) - this mask is combine with the other w8 masks below
    mask_nut_va1e1b1nwzida0e0b0xyg1 = mask_nut_oa1e1b1nwzida0e0b0xyg1[a_o_v]
    ###association between the shortlist of nutrition profile inputs and the full range of LW patterns that include starting LW
    a_shortlist_w1 = index_w1 % (uinp.structure['i_n1_len'] ** uinp.structure['i_n_fvp_period1'])
    mask_nut_va1e1b1nwzida0e0b0xyg1 = mask_nut_va1e1b1nwzida0e0b0xyg1[:,:,:,:,:,a_shortlist_w1,...]  # expands the nutrition mask to all lw patterns.
    ### match the pattern requested with the pattern that is the 'history' for that pattern in previous DVPs
    mask_w8nut_va1e1b1nzida0e0b0xyg1w9 = np.sum(mask_nut_va1e1b1nwzida0e0b0xyg1[...,na] *
                                               (np.trunc(index_wzida0e0b0xyg1[...,na] / step_dv1_va1e1b1nw8zida0e0b0xyg1[..., na])
                                                == index_w1 / step_dv1_va1e1b1nw8zida0e0b0xyg1[...,na]),
                                               axis=w_pos-1) > 0 #don't keepdims
    mask_w8nut_va1e1b1nwzida0e0b0xyg1 = np.moveaxis(mask_w8nut_va1e1b1nzida0e0b0xyg1w9,-1,w_pos) #move w9 axis to w position
    ## Combine the w8vars mask and the user nutrition mask
    mask_w8vars_va1e1b1nw8zida0e0b0xyg1 = mask_w8vars_va1e1b1nw8zida0e0b0xyg1 * mask_w8nut_va1e1b1nwzida0e0b0xyg1
    ##Mask numbers provided based on the steps (with a t axis) and the next dvp type (with a t axis)
    mask_numbers_provw8w9_tva1e1b1nw8zida0e0b0xyg1w9 = mask_w8vars_va1e1b1nw8zida0e0b0xyg1[...,na] * (np.trunc((index_wzida0e0b0xyg1[...,na] * (dvp_type_next_tva1e1b1nwzida0e0b0xyg1[...,na] !=0) +
                                                     index_w1 * (dvp_type_next_tva1e1b1nwzida0e0b0xyg1[...,na] == 0))
                                                    / step_next_con1_tva1e1b1nw8zida0e0b0xyg1w9) == index_w1 / step_next_con1_tva1e1b1nw8zida0e0b0xyg1w9)
    ##Mask numbers required from the previous period (broadcast across t axis) - Note: req does not need a t axis because the destination decision variable don’t change for the transfer
    mask_numbers_reqw8w9_va1e1b1nw8zida0e0b0xyg1w9 = mask_w8vars_va1e1b1nw8zida0e0b0xyg1[...,na] * (np.trunc(index_wzida0e0b0xyg1 / step_con1_va1e1b1nw8zida0e0b0xyg1)[...,na] == index_w1 / step_con1_va1e1b1nw8zida0e0b0xyg1[...,na])

    ##offs
    ##mask for nutrition profiles (this allows the user to examine certain nutrition patterns eg high high high vs low low low) - this mask is renamed the w8 masks to be consistent with dams
    mask_nut_va1e1b1nwzida0e0b0xyg3 = mask_nut_sa1e1b1nwzida0e0b0xyg3[a_s_v] #shearing opp is the same as dvp
    ###association between the shortlist of nutrition profile inputs and the full range of LW patterns that include starting LW
    a_shortlist_w3 = index_w3 % (uinp.structure['i_n3_len'] ** uinp.structure['i_n_fvp_period3'])
    mask_w8vars_va1e1b1nw8zida0e0b0xyg3 = mask_nut_va1e1b1nwzida0e0b0xyg3[:,:,:,:,:,a_shortlist_w3,...]  # expands the nutrition mask to all lw patterns.
    ###The gap between the active constraints is required
    step_con3 = uinp.structure['i_n3_len'] ** uinp.structure['i_n_fvp_period3']
    ###The 3 active constraints to leave after masking are 0, 27 & 54
    ####Each of the 81 decision variables in the previous period can have a value in any of these 3 active rows (the actual values are determined in the distribution function) so a mask is not required for these decision variables.
    mask_numbers_provw9_w9 = index_w3 % step_con3 == 0
    ###Each of the 81 decision variables in the next period will have a +1 in the constraint that relates to their starting weight.
    mask_numbers_reqw8w9_w8zida0e0b0xyg3w9 = np.trunc(index_wzida0e0b0xyg3[...,na] / step_con3) == index_w3 / step_con3 #na for w9
    mask_numbers_reqw8w9_va1e1b1nw8zida0e0b0xyg3w9 = mask_w8vars_va1e1b1nw8zida0e0b0xyg3[...,na] * mask_numbers_reqw8w9_w8zida0e0b0xyg3w9 #add the nut mask

    ####################################################
    #Masking numbers transferred to other ram groups   #
    ####################################################
    ''' Mask numbers transferred - these mask remove unnecessary decision variables for:
               transfers to different sires between dvps that are not prejoining
               sales in dvps that are not shearing (t[0]) or not scanning (t[1])'''
    ##dams
    ###create a t mask for dam decision variables - an animal that is transferring between ram groups only has parameters in the dvp that is transfer
    ###dvp0 has no transfer even though it is dvp type 0
    ###animals that are sold t[0] & t[1] only exist if the period is sale. Note t[1] sale is already masked for scan>=1 & for dry ewes only
    period_is_transfer_tva1e1b1nwzida0e0b0xyg1 = sfun.f_p2v(period_is_transfer_tpa1e1b1nwzida0e0b0xyg1, a_v_pa1e1b1nwzida0e0b0xyg1)
    mask_tvars_tva1e1b1nw8zida0e0b0xyg1 = np.logical_or(np.logical_and(period_is_transfer_tva1e1b1nwzida0e0b0xyg1, index_va1e1b1nwzida0e0b0xyg1 != 0)
                                                        , (a_g1_tpa1e1b1nwzida0e0b0xyg1 == index_g1))
    period_is_sale_tva1e1b1nwzida0e0b0xyg1 = sfun.f_p2v(period_is_sale_tpa1e1b1nwzida0e0b0xyg1, a_v_pa1e1b1nwzida0e0b0xyg1)
    period_is_sale_k2tva1e1b1nwzida0e0b0xyg1 = np.sum(period_is_sale_tva1e1b1nwzida0e0b0xyg1
                                                      * (a_k2cluster_va1e1b1nwzida0e0b0xyg1 == index_k2tva1e1b1nwzida0e0b0xyg1)
                                                      , axis=(e1_pos, b1_pos), keepdims=True)>0
    mask_tvars_k2tva1e1b1nw8zida0e0b0xyg1 = np.logical_and(mask_tvars_tva1e1b1nw8zida0e0b0xyg1,
                                                           np.logical_or(period_is_sale_k2tva1e1b1nwzida0e0b0xyg1,
                                                                         index_tva1e1b1nw8zida0e0b0xyg1 >= 2))
    ####make k5 version of mask (used for npw), index_k5 + 2 is allowing for NM & 00 that are 1st 2 entries in the k2cluster that don't exist in the k5cluster
    #### #todo alternative is mask_tvars_k5 = mask_tvars_k2[2:8] this is not any less flexible than '+2' in formula
    period_is_sale_k5tva1e1b1nwzida0e0b0xyg1 = np.sum(period_is_sale_tva1e1b1nwzida0e0b0xyg1
                                                      * (a_k2cluster_va1e1b1nwzida0e0b0xyg1 == index_k5tva1e1b1nwzida0e0b0xyg3+2)
                                                      , axis=(e1_pos, b1_pos), keepdims=True)>0
    mask_tvars_k5tva1e1b1nw8zida0e0b0xyg1 = np.logical_and(mask_tvars_tva1e1b1nw8zida0e0b0xyg1,
                                                           np.logical_or(period_is_sale_k5tva1e1b1nwzida0e0b0xyg1,
                                                                         index_tva1e1b1nw8zida0e0b0xyg1 >= 2))

    ###numbers are provided by g1 to g9 (a_g1_tg1) in the dvps that are transfer periods (mask_tvars) for the t slices that are not sale (transfer exists)
    #### the association is being used as (a_g9_tg1 == index_g9)
    mask_numbers_provt_k2tva1e1b1nwzida0e0b0xyg1g9 = mask_tvars_k2tva1e1b1nw8zida0e0b0xyg1[...,na] * transfer_exists_tpa1e1b1nwzida0e0b0xyg1[..., na]  \
                                                      * (a_g1_tpa1e1b1nwzida0e0b0xyg1[..., na] == index_g1[..., na, :])

    ###numbers are required across the identity array between g1 & g9 in the periods that the transfer decision variable exists exists
    mask_numbers_reqt_k2tva1e1b1nwzida0e0b0xyg1g9 = mask_tvars_k2tva1e1b1nw8zida0e0b0xyg1[...,na] \
                                                    * (index_g9 == index_g1g)

    ##0ffs
    ##mask the t array so that only slice t0 provides numbers
    mask_numbers_provt_tva1e1b1nw8zida0e0b0xyg3w9 = (index_tva1e1b1nw8zida0e0b0xyg3w9 == 0)

    #########################################
    #Masking numbers for forced sale of drys#
    #########################################
    ''' Create a mask to remove retaining dry dams when sale of drys is forced
    The transfer is removed if all the following are true: they are in the dry cluster that is not a sale group, DVP is scanning, ewes are scanned, dry sales are forced '''
    #todo add force sale of drys at shearing - bit more complex because shearing could be in different dvps. therefore might need period_is_shear_tvg. Also need to workout which way to handle how to allow model to choose if it wants to sell at scanning or shearing (could do this by just forcing sale at shearing then the model chooses if it does it at scanning or shearing)
    ##dams
    mask_numbers_provdry_k28k29tva1e1b1nwzida0e0b0xyg1 = np.logical_not((index_k28k29tva1e1b1nwzida0e0b0xyg1 == 1) * (index_tva1e1b1nw8zida0e0b0xyg1 >= 2)
                                                         * (dvp_type_va1e1b1nwzida0e0b0xyg1 == 1) * (scan_va1e1b1nwzida0e0b0xyg1 >= 1) #dvp1 because that's the scanning dvp
                                                         * (pinp.sheep['i_dry_sales_forced']))

    ###########################
    #create production params #
    ###########################
    '''some sire params don't go through here because no associations are required'''
    production_param_start = time.time()

    ##mei
    mei_p6fa1e1b1nwzida0e0b0xyg0 = sfun.f_create_production_param('sire', mei_p6fa1e1b1nwzida0e0b0xyg0,numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg0)
    mei_k2p6ftva1e1b1nwzida0e0b0xyg1 = sfun.f_create_production_param('dams', mei_p6ftva1e1b1nwzida0e0b0xyg1, a_k2cluster_va1e1b1nwzida0e0b0xyg1, index_k2tva1e1b1nwzida0e0b0xyg1[:,na,na,...],
                                                                 numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg1,
                                                                 mask_vg=(mask_w8vars_va1e1b1nw8zida0e0b0xyg1*mask_tvars_k2tva1e1b1nw8zida0e0b0xyg1))
    mei_k3k5p6ftva1e1b1nwzida0e0b0xyg3 = sfun.f_create_production_param('offs', mei_p6ftva1e1b1nwzida0e0b0xyg3, a_k3cluster_da0e0b0xyg3, index_k3k5tva1e1b1nwzida0e0b0xyg3[:,:,na,na,...],
                                                    a_k5cluster_da0e0b0xyg3, index_k5tva1e1b1nwzida0e0b0xyg3[:,na,na,...], numbers_start_va1e1b1nwzida0e0b0xyg3,
                                                    mask_vg=mask_w8vars_va1e1b1nw8zida0e0b0xyg3)

    ##pi
    pi_p6fa1e1b1nwzida0e0b0xyg0 = sfun.f_create_production_param('sire', pi_p6fa1e1b1nwzida0e0b0xyg0, numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg0)
    pi_k2p6ftva1e1b1nwzida0e0b0xyg1 = sfun.f_create_production_param('dams', pi_p6ftva1e1b1nwzida0e0b0xyg1, a_k2cluster_va1e1b1nwzida0e0b0xyg1, index_k2tva1e1b1nwzida0e0b0xyg1[:,na,na,...],
                                                                 numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg1,
                                                                 mask_vg=(mask_w8vars_va1e1b1nw8zida0e0b0xyg1*mask_tvars_k2tva1e1b1nw8zida0e0b0xyg1))
    pi_k3k5p6ftva1e1b1nwzida0e0b0xyg3 = sfun.f_create_production_param('offs', pi_p6ftva1e1b1nwzida0e0b0xyg3, a_k3cluster_da0e0b0xyg3, index_k3k5tva1e1b1nwzida0e0b0xyg3[:,:,na,na,...],
                                                    a_k5cluster_da0e0b0xyg3, index_k5tva1e1b1nwzida0e0b0xyg3[:,na,na,...], numbers_start_va1e1b1nwzida0e0b0xyg3,
                                                    mask_vg=mask_w8vars_va1e1b1nw8zida0e0b0xyg3)

    ##cashflow & cost
    purchcost_cva1e1b1nwzida0e0b0xyg0 = sfun.f_create_production_param('sire', purchcost_cva1e1b1nwzida0e0b0xyg0, numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg0)
    cashflow_ctva1e1b1nwzida0e0b0xyg0 = sfun.f_create_production_param('sire', cashflow_ctva1e1b1nwzida0e0b0xyg0, numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg0)
    cashflow_k2ctva1e1b1nwzida0e0b0xyg1 = sfun.f_create_production_param('dams', cashflow_ctva1e1b1nwzida0e0b0xyg1, a_k2cluster_va1e1b1nwzida0e0b0xyg1, index_k2tva1e1b1nwzida0e0b0xyg1[:,na,...],
                                                                 numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg1,
                                                                 mask_vg=(mask_w8vars_va1e1b1nw8zida0e0b0xyg1*mask_tvars_k2tva1e1b1nw8zida0e0b0xyg1[:,na,...]))
    cashflow_k3k5ctva1e1b1nwzida0e0b0xyg3 = sfun.f_create_production_param('offs', cashflow_ctva1e1b1nwzida0e0b0xyg3, a_k3cluster_da0e0b0xyg3, index_k3k5tva1e1b1nwzida0e0b0xyg3[:,:,na,...],
                                                    a_k5cluster_da0e0b0xyg3, index_k5tva1e1b1nwzida0e0b0xyg3[:,na,...], numbers_start_va1e1b1nwzida0e0b0xyg3,
                                                    mask_vg=mask_w8vars_va1e1b1nw8zida0e0b0xyg3)
    cost_ctva1e1b1nwzida0e0b0xyg0 = sfun.f_create_production_param('sire', cost_ctva1e1b1nwzida0e0b0xyg0, numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg0)
    cost_k2ctva1e1b1nwzida0e0b0xyg1 = sfun.f_create_production_param('dams', cost_ctva1e1b1nwzida0e0b0xyg1, a_k2cluster_va1e1b1nwzida0e0b0xyg1, index_k2tva1e1b1nwzida0e0b0xyg1[:,na,...],
                                                                 numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg1,
                                                                 mask_vg=(mask_w8vars_va1e1b1nw8zida0e0b0xyg1*mask_tvars_k2tva1e1b1nw8zida0e0b0xyg1[:,na,...]))
    cost_k3k5ctva1e1b1nwzida0e0b0xyg3 = sfun.f_create_production_param('offs', cost_ctva1e1b1nwzida0e0b0xyg3, a_k3cluster_da0e0b0xyg3, index_k3k5tva1e1b1nwzida0e0b0xyg3[:,:,na,...],
                                                    a_k5cluster_da0e0b0xyg3, index_k5tva1e1b1nwzida0e0b0xyg3[:,na,...], numbers_start_va1e1b1nwzida0e0b0xyg3,
                                                    mask_vg=mask_w8vars_va1e1b1nw8zida0e0b0xyg3)
    ###sum c axis for cost param - it must exist for reporting so can only be summed here
    cost_tva1e1b1nwzida0e0b0xyg0 = np.sum(cost_ctva1e1b1nwzida0e0b0xyg0, axis=0)
    cost_k2tva1e1b1nwzida0e0b0xyg1 = np.sum(cost_k2ctva1e1b1nwzida0e0b0xyg1, axis=1)
    cost_k3k5tva1e1b1nwzida0e0b0xyg3 = np.sum(cost_k3k5ctva1e1b1nwzida0e0b0xyg3, axis=2)

    ##asset value
    assetvalue_va1e1b1nwzida0e0b0xyg0 = sfun.f_create_production_param('sire', assetvalue_va1e1b1nwzida0e0b0xyg0, numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg0)
    assetvalue_k2tva1e1b1nwzida0e0b0xyg1 = sfun.f_create_production_param('dams', assetvalue_tva1e1b1nwzida0e0b0xyg1, a_k2cluster_va1e1b1nwzida0e0b0xyg1, index_k2tva1e1b1nwzida0e0b0xyg1,
                                                                 numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg1,
                                                                 mask_vg=(mask_w8vars_va1e1b1nw8zida0e0b0xyg1*mask_tvars_k2tva1e1b1nw8zida0e0b0xyg1))
    assetvalue_k3k5tva1e1b1nwzida0e0b0xyg3 = sfun.f_create_production_param('offs', assetvalue_tva1e1b1nwzida0e0b0xyg3, a_k3cluster_da0e0b0xyg3, index_k3k5tva1e1b1nwzida0e0b0xyg3,
                                                    a_k5cluster_da0e0b0xyg3, index_k5tva1e1b1nwzida0e0b0xyg3, numbers_start_va1e1b1nwzida0e0b0xyg3,
                                                    mask_vg=mask_w8vars_va1e1b1nw8zida0e0b0xyg3)

    ##labour - manager
    lab_manager_p5tva1e1b1nwzida0e0b0xyg0 = sfun.f_create_production_param('sire', labour_l2p5tva1e1b1nwzida0e0b0xyg0[0], numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg0)
    lab_manager_k2p5tva1e1b1nwzida0e0b0xyg1 = sfun.f_create_production_param('dams', labour_l2p5tva1e1b1nwzida0e0b0xyg1[0], a_k2cluster_va1e1b1nwzida0e0b0xyg1, index_k2tva1e1b1nwzida0e0b0xyg1[:,na,...],
                                                                 numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg1,
                                                                 mask_vg=(mask_w8vars_va1e1b1nw8zida0e0b0xyg1*mask_tvars_k2tva1e1b1nw8zida0e0b0xyg1[:,na,...]))
    lab_manager_k3k5p5tva1e1b1nwzida0e0b0xyg3 = sfun.f_create_production_param('offs', labour_l2p5tva1e1b1nwzida0e0b0xyg3[0], a_k3cluster_da0e0b0xyg3, index_k3k5tva1e1b1nwzida0e0b0xyg3[:,:,na,...],
                                                    a_k5cluster_da0e0b0xyg3, index_k5tva1e1b1nwzida0e0b0xyg3[:,na,...], numbers_start_va1e1b1nwzida0e0b0xyg3,
                                                    mask_vg=mask_w8vars_va1e1b1nw8zida0e0b0xyg3)

    ##labour - permanent
    lab_perm_p5tva1e1b1nwzida0e0b0xyg0 = sfun.f_create_production_param('sire', labour_l2p5tva1e1b1nwzida0e0b0xyg0[1], numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg0)
    lab_perm_k2p5tva1e1b1nwzida0e0b0xyg1 = sfun.f_create_production_param('dams', labour_l2p5tva1e1b1nwzida0e0b0xyg1[1], a_k2cluster_va1e1b1nwzida0e0b0xyg1, index_k2tva1e1b1nwzida0e0b0xyg1[:,na,...],
                                                                 numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg1,
                                                                 mask_vg=(mask_w8vars_va1e1b1nw8zida0e0b0xyg1*mask_tvars_k2tva1e1b1nw8zida0e0b0xyg1[:,na,...]))
    lab_perm_k3k5p5tva1e1b1nwzida0e0b0xyg3 = sfun.f_create_production_param('offs', labour_l2p5tva1e1b1nwzida0e0b0xyg3[1], a_k3cluster_da0e0b0xyg3, index_k3k5tva1e1b1nwzida0e0b0xyg3[:,:,na,...],
                                                    a_k5cluster_da0e0b0xyg3, index_k5tva1e1b1nwzida0e0b0xyg3[:,na,...], numbers_start_va1e1b1nwzida0e0b0xyg3,
                                                    mask_vg=mask_w8vars_va1e1b1nw8zida0e0b0xyg3)

    ##labour - anyone
    lab_anyone_p5tva1e1b1nwzida0e0b0xyg0 = sfun.f_create_production_param('sire', labour_l2p5tva1e1b1nwzida0e0b0xyg0[2], numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg0)
    lab_anyone_k2p5tva1e1b1nwzida0e0b0xyg1 = sfun.f_create_production_param('dams', labour_l2p5tva1e1b1nwzida0e0b0xyg1[2], a_k2cluster_va1e1b1nwzida0e0b0xyg1, index_k2tva1e1b1nwzida0e0b0xyg1[:,na,...],
                                                                 numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg1,
                                                                 mask_vg=(mask_w8vars_va1e1b1nw8zida0e0b0xyg1*mask_tvars_k2tva1e1b1nw8zida0e0b0xyg1[:,na,...]))
    lab_anyone_k3k5p5tva1e1b1nwzida0e0b0xyg3 = sfun.f_create_production_param('offs', labour_l2p5tva1e1b1nwzida0e0b0xyg3[2], a_k3cluster_da0e0b0xyg3, index_k3k5tva1e1b1nwzida0e0b0xyg3[:,:,na,...],
                                                    a_k5cluster_da0e0b0xyg3, index_k5tva1e1b1nwzida0e0b0xyg3[:,na,...], numbers_start_va1e1b1nwzida0e0b0xyg3,
                                                    mask_vg=mask_w8vars_va1e1b1nw8zida0e0b0xyg3)

    ##infrastructure
    infrastructure_h1va1e1b1nwzida0e0b0xyg0 = sfun.f_create_production_param('sire', infrastructure_h1va1e1b1nwzida0e0b0xyg0, numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg0)
    infrastructure_k2h1tva1e1b1nwzida0e0b0xyg1 = sfun.f_create_production_param('dams', infrastructure_h1tva1e1b1nwzida0e0b0xyg1, a_k2cluster_va1e1b1nwzida0e0b0xyg1, index_k2tva1e1b1nwzida0e0b0xyg1[:,na,...],
                                                                 numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg1,
                                                                 mask_vg=(mask_w8vars_va1e1b1nw8zida0e0b0xyg1*mask_tvars_k2tva1e1b1nw8zida0e0b0xyg1[:,na,...]))
    infrastructure_k3k5p5tva1e1b1nwzida0e0b0xyg3 = sfun.f_create_production_param('offs', infrastructure_h1tva1e1b1nwzida0e0b0xyg3, a_k3cluster_da0e0b0xyg3, index_k3k5tva1e1b1nwzida0e0b0xyg3[:,:,na,...],
                                                    a_k5cluster_da0e0b0xyg3, index_k5tva1e1b1nwzida0e0b0xyg3[:,na,...], numbers_start_va1e1b1nwzida0e0b0xyg3,
                                                    mask_vg=mask_w8vars_va1e1b1nw8zida0e0b0xyg3)




    ###########################
    #create numbers params    #
    ###########################
    number_param_start = time.time()
    ##number of sires available at mating - sire
    numbers_startp8_va1e1b1nwzida0e0b0xyg0p8 = sfun.f_create_production_param('sire', numbers_startp8_va1e1b1nwzida0e0b0xyg0p8, numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg0[...,na])
    ##number of sires for required for mating - dams
    ### mask the dams for w8 vars, t_vars. Also not mated if they are being transferred to another ram group. A transfer in the mating period (a_g1_tg1!=index_g1) indicates that the dam is going to be mated to another sire at a later date within the same DVP
    t_mask_k2tva1e1b1nw8zida0e0b0xyg1g0p8 = (mask_w8vars_va1e1b1nw8zida0e0b0xyg1 * mask_tvars_k2tva1e1b1nw8zida0e0b0xyg1 * (a_g1_tpa1e1b1nwzida0e0b0xyg1 == index_g1))[...,na,na]
    nsire_k2tva1e1b1nwzida0e0b0xyg1g0p8 = sfun.f_create_production_param('dams', nsire_tva1e1b1nwzida0e0b0xyg1g0p8,
                                                a_k2cluster_va1e1b1nwzida0e0b0xyg1[...,na,na], index_k2tva1e1b1nwzida0e0b0xyg1[...,na,na],
                                                numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg1[...,na,na],
                                                mask_vg=t_mask_k2tva1e1b1nw8zida0e0b0xyg1g0p8, pos_offset=2)
    nsire_k2tva1e1b1nwzida0e0b0xyg1g0p8[0] = 0 #nm animals don't require sires

    ##numbers prov - numbers at the end of a dvp with the cluster of the next dvp divided by start numbers with cluster of current period
    ###dams total provided from this period
    numerator  = 0
    denominator = 0
    for b1 in range(len_b1): #loop on b1 to reduce memory
        numerator += (np.sum(numbers_end_tva1e1b1nwzida0e0b0xyg1[:,:,:,:,b1:b1+1,..., na,na]
                    * mask_numbers_provw8w9_tva1e1b1nw8zida0e0b0xyg1w9[..., na,:]
                    * mask_numbers_provt_k2tva1e1b1nwzida0e0b0xyg1g9[:,na,..., na]
                    * mask_numbers_provdry_k28k29tva1e1b1nwzida0e0b0xyg1[...,na,na]
                    * distribution_tva1e1b1nw8zida0e0b0xyg1w9[:,:,:,:,b1:b1+1,..., na,:]
                    * (a_k2cluster_va1e1b1nwzida0e0b0xyg1[:,:,:,b1:b1+1,...] == index_k28k29tva1e1b1nwzida0e0b0xyg1)[..., na,na]                #The numerator has both k2 with g9 axis and without. One to reflect the decision variable (k28) and one for the constraint (k29). So I think this is all good
                    * (a_k2cluster_next_tva1e1b1nwzida0e0b0xyg1g9[:,:,:,:,b1:b1+1,...] == index_k29tva1e1b1nwzida0e0b0xyg1g9)[..., na],
                    axis=(e1_pos - 2), keepdims=True))
        denominator += (np.sum(numbers_start_va1e1b1nwzida0e0b0xyg1[:,:,:,b1:b1+1,...] * (a_k2cluster_va1e1b1nwzida0e0b0xyg1[:,:,:,b1:b1+1,...] == index_k28k29tva1e1b1nwzida0e0b0xyg1),
                    axis=e1_pos, keepdims=True)[..., na,na]) #na for w9 and g9 (use standard cluster without t/g9 axis because the denominator is (the clustering for) the decision variable as at the start of the DVP)
    numbers_prov_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9 = fun.f_divide(numerator,denominator, dtype=dtype)

    ####dams transferring between ram groups in the same DVP.
    #### This occurs if the transfer is to a different ram group (a_g1_tg1 != g1) and is occurring from a prejoining dvp (type == 0) which indicates that the transfer is from prejoining dvp to prejoining dvp because the destination ram group is joining after the source
    numbers_provthis_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9 = (numbers_prov_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9
                                                                * ((dvp_type_va1e1b1nwzida0e0b0xyg1[:, :, 0:1, ...] == 0)
                                                                   * (a_g1_tpa1e1b1nwzida0e0b0xyg1 != index_g1))[...,na,na])   #take slice 0 of e (for prejoining all e slices are the same)
    ####dams providing to the next period (the norm)
    ####Only different from the total because it excludes those providing to the same period
    numbers_prov_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9 = (numbers_prov_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9
                                                            - numbers_provthis_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9)
    ###combine nm and 00 cluster for the numbers provided to the prejoining period (so matrix can optimise choice of joining or not)
    temporary = np.sum(numbers_prov_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9, axis=1, keepdims=True) * (index_k29tva1e1b1nwzida0e0b0xyg1g9[...,na] == 0)  # put the sum of the k29 in slice 0
    numbers_prov_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9 = fun.f_update(numbers_prov_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9, temporary,
                                                                        dvp_type_next_tva1e1b1nwzida0e0b0xyg1[:, :, :, 0:1, ..., na,na] == 0)  #take slice 0 of e (for prejoining all e slices are the same)
    ###combine nm and 00 cluster (so matrix can optimise choice of joining or not). DVP type of destination is always 0 for the "provide this period" so don't need to test
    numbers_provthis_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9 = np.sum(numbers_provthis_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9, axis=1, keepdims=True) * (index_k29tva1e1b1nwzida0e0b0xyg1g9[...,na] == 0)  # put the sum of the k29 in slice 0
    ###combine wean numbers at prejoining to allow the matrix to select a different weaning time for the coming yr.
    #^cant just sum across the a slice (decision variable) so allow a0 to provide a1 we will need another a axis (see google doc) - fix this in version 2
    # temporary = np.sum(numbers_prov_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9, axis=a1_pos-1, keepdims=True) * (index_a1e1b1nwzida0e0b0xyg[...,na] == 0)
    # numbers_prov_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9 = fun.f_update(numbers_prov_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9, temporary, dvp_type_next_tva1e1b1nwzida0e0b0xyg1[:,:,:,0:1,...,na] == 0) #take slice 0 of e (for prejoining all e slices are the same

    ###offs
    numbers_prov_offs_k3k5tva1e1b1nw8zida0e0b0xygw9 = (fun.f_divide(np.sum(numbers_end_va1e1b1nwzida0e0b0xyg3[...,na]  * distribution_va1e1b1nw8zida0e0b0xyg3w9
                                                                        * (a_k3cluster_da0e0b0xyg3==index_k3k5tva1e1b1nwzida0e0b0xyg3)[...,na]
                                                                        * (a_k5cluster_da0e0b0xyg3==index_k5tva1e1b1nwzida0e0b0xyg3)[...,na]
                                                                            , axis = (d_pos-1, b0_pos-1, e0_pos-1), keepdims=True)
                                                                , np.sum(numbers_start_va1e1b1nwzida0e0b0xyg3 * (a_k3cluster_da0e0b0xyg3 == index_k3k5tva1e1b1nwzida0e0b0xyg3)
                                                                         * (a_k5cluster_da0e0b0xyg3==index_k5tva1e1b1nwzida0e0b0xyg3)
                                                                         , axis = (d_pos, b0_pos, e0_pos), keepdims=True)[...,na], dtype=dtype)
                                                       * mask_numbers_provt_tva1e1b1nw8zida0e0b0xyg3w9 * mask_numbers_provw9_w9)

    ##numbers required
    ###dams
    numbers_req_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9 =  1 * (np.sum(mask_numbers_reqw8w9_va1e1b1nw8zida0e0b0xyg1w9[...,na,:] * mask_numbers_reqt_k2tva1e1b1nwzida0e0b0xyg1g9[:,na,...,na]
                                                                       * ((a_k2cluster_va1e1b1nwzida0e0b0xyg1 == index_k28k29tva1e1b1nwzida0e0b0xyg1) * (a_k2cluster_va1e1b1nwzida0e0b0xyg1 == index_k2tva1e1b1nwzida0e0b0xyg1))[...,na,na]
                                                                       , axis = (b1_pos-2, e1_pos-2), keepdims=True)>0)
    ####combine nm and 00 cluster for prejoining to scanning
    temporary = np.sum(numbers_req_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9, axis=1, keepdims=True) * (index_k29tva1e1b1nwzida0e0b0xyg1g9[...,na] == 0)  # put the sum of the k29 in slice 0
    numbers_req_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9 = fun.f_update(numbers_req_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9, temporary,
                                                                        dvp_type_va1e1b1nwzida0e0b0xyg1[:, :, 0:1, ..., na,na] == 0)  #take slice 0 of e (for prejoining all e slices are the same)
    ####combine wean numbers at prejoining to allow the matrix to select a different weaning time for the coming yr.
    #^cant just sum across the a slice (decision variable) so allow a0 to provide a1 we will need another a axis (see google doc)
    # temporary = np.sum(numbers_req_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9, axis=a1_pos-1, keepdims=True) * (index_a1e1b1nwzida0e0b0xyg[...,na] == 0)
    # numbers_req_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9 = fun.f_update(numbers_req_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9, temporary, dvp_type_va1e1b1nwzida0e0b0xyg1[:,:,0:1,...,na] == 0) #take slice 0 of e (for prejoining all e slices are the same


    ###offs
    numbers_req_offs_k3k5tva1e1b1nw8zida0e0b0xygw9 =  1*(np.sum((a_k3cluster_da0e0b0xyg3 == index_k3k5tva1e1b1nwzida0e0b0xyg3)*(a_k5cluster_da0e0b0xyg3==index_k5tva1e1b1nwzida0e0b0xyg3)
                                                             , axis = (d_pos, b0_pos, e0_pos), keepdims=True)[...,na
                                                      ] * mask_numbers_reqw8w9_va1e1b1nw8zida0e0b0xyg3w9 * (index_vpa1e1b1nwzida0e0b0xyg3==index_vpa1e1b1nwzida0e0b0xyg3) >0) #add active v axis

    ##Setting the parameters at the end of the generator to 0 removes passing animals into the constraint that links the end of life with the beginning of life.
    numbers_prov_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9[:,:,:,-1,...] = 0
    numbers_provthis_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9[:,:,:,-1,...] = 0
    numbers_prov_offs_k3k5tva1e1b1nw8zida0e0b0xygw9[:,:,:,-1,...] = 0
    numbers_req_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9[:,:,:,0,...] = 0
    numbers_req_offs_k3k5tva1e1b1nw8zida0e0b0xygw9[:,:,:,0,...] = 0

    #################
    #progeny weaned#
    #################
    '''yatf are first transferred to progeny activity then they are either sold as sucker, transferred to dam or transferred to offs'''
    ##condense yatf from 81 finishing lw to 10
    ###reshape array so to stack/combine some axis - this new axis is called k
    ffcfw_range_zia0xg2k = np.moveaxis(ffcfw_start_d_yatf_a1e1b1nwzida0e0b0xyg2, [a1_pos, z_pos, i_pos, x_pos, -1]
                                       , [2,0,1,3,4]).reshape((len_z,len_i,len_a1,len_x,len_g2, -1))
    salevalue_range_zia0xg2k = np.moveaxis(salevalue_d_a1e1b1nwzida0e0b0xyg2, [a1_pos, z_pos, i_pos, x_pos, -1]
                                       , [2,0,1,3,4]).reshape((len_z,len_i,len_a1,len_x,len_g2, -1))
    numbers_range_zia0xg2k = np.moveaxis(numbers_start_d_yatf_a1e1b1nwzida0e0b0xyg2, [a1_pos, z_pos, i_pos, x_pos, -1]
                                         , [2,0,1,3,4]).reshape((len_z, len_i, len_a1, len_x, len_g2, -1))
    ### mask the ffcfw & salevalue for only those that have numbers > 0. Removes animals that have died or don't exist
    ffcfw_range_zia0xg2k = ffcfw_range_zia0xg2k * (numbers_range_zia0xg2k > 0)
    salevalue_range_zia0xg2k = salevalue_range_zia0xg2k * (numbers_range_zia0xg2k > 0)
    ### The index that sorts the weight array
    ind_sorted_zia0xg2k = np.argsort(ffcfw_range_zia0xg2k, axis = -1)
    ### Select the values for the 10 equally spaced values spanning lowest to highest inclusive. Adding w9 axis at -1
    start_zia0xg2 = ffcfw_range_zia0xg2k.shape[-1] - np.count_nonzero(ffcfw_range_zia0xg2k, axis=-1)
    ind_selected_a1zixg2w9 = np.linspace(start_zia0xg2, ffcfw_range_zia0xg2k.shape[-1] - 1, uinp.structure['i_progeny_w2_len'], dtype = int, axis=-1)
    ### The indices for the required values are the selected values from the sorted indices
    ind = np.take_along_axis(ind_sorted_zia0xg2k, ind_selected_a1zixg2w9, axis=-1)
    ### Extract the condensed weights, the numbers and the sale_value of the condensed vars
    #### Later these variables are used with the 10 weights in the i_w_pos, so note whether w9 on end or not
    ffcfw_prog_zia0xg2w9 = np.take_along_axis(ffcfw_range_zia0xg2k, ind, axis = -1)
    salevalue_zia0xg2w9 = np.take_along_axis(salevalue_range_zia0xg2k, ind, axis = -1)
    ###Reshape the progeny arrays to put axes in place - keeping w9 on the right hand end
    ffcfw_prog_zida0e0b0xyg2w9 = ffcfw_prog_zia0xg2w9.reshape(len_z, len_i, 1, len_a1, 1, 1, len_x, 1, len_g2, uinp.structure['i_progeny_w2_len'])
    salevalue_prog_zida0e0b0xyg2w9 = salevalue_zia0xg2w9.reshape(len_z, len_i, 1, len_a1, 1, 1, len_x, 1, len_g2, uinp.structure['i_progeny_w2_len'])

    ##distribute the yatf to the intermediate progeny activity
    distribution_2prog_va1e1b1nw8zida0e0b0xyg1w9 = sfun.f_lw_distribution_2prog(ffcfw_prog_zida0e0b0xyg2w9,ffcfw_start_v_yatf_va1e1b1nwzida0e0b0xyg1)

    ## move progeny weight axis to normal position for distribution to dams & offs at beginning of dvp0
    ffcfw_prog_wzida0e0b0xyg2 = np.moveaxis(ffcfw_prog_zida0e0b0xyg2w9,-1,w_pos)
    salevalue_prog_wzida0e0b0xyg2 = np.moveaxis(salevalue_prog_zida0e0b0xyg2w9,-1,w_pos)

    ##add t axis to progeny - slice 0 is sold as sucker, slice 1 and 2 are retained
    index_tpa1e1b1nwzida0e0b0xyg2 = fun.f_reshape_expand(index_t2, p_pos-1)
    salevalue_prog_tpa1e1b1nwzida0e0b0xyg2 = salevalue_prog_wzida0e0b0xyg2 * (index_tpa1e1b1nwzida0e0b0xyg2==0)

    ##add c axis to prog - using period_is_wean so that correct c slice is activated
    salevalue_prog_cta1e1b1nwzida0e0b0xyg2 = sfun.f_p2v_std(salevalue_prog_tpa1e1b1nwzida0e0b0xyg2, period_is_tvp=period_is_wean_pa1e1b1nwzida0e0b0xyg2[:,:,0:1,...], #weaning is same for all e slices
                                     a_any1_p=a_c_pa1e1b1nwzida0e0b0xyg,index_any1tvp=index_ctpa1e1b1nwzida0e0b0xyg) / np.count_nonzero(period_is_wean_pa1e1b1nwzida0e0b0xyg2[:,:,0:1,...], axis=0) #divide by the number of weaning times down the p axis because all weaning times for lambs with different age mums are combined into single activity.

    ##mask w8 (prog) to w9 (dams)
    step_con_prog2dams = uinp.structure['i_n1_len'] ** uinp.structure['i_n_fvp_period1']
    mask_numbers_prog2damsw8w9_w9 = (index_w1 % step_con_prog2dams) == 0
    ##mask w8 (prog) to w9 (offs)
    step_con_prog2offs = uinp.structure['i_n3_len'] ** uinp.structure['i_n_fvp_period3']
    mask_numbers_prog2offsw8w9_w9 = (index_w3 % step_con_prog2offs) == 0

    ###The association between birth time of the progeny and the birth time and lambing opportunity/dam age
    prior_times_excluded_ida0e0b0xyg = fun.f_reshape_expand(np.cumsum(~pinp.sheep['i_mask_i'])[pinp.sheep['i_mask_i']], i_pos)
    a_i_ida0e0b0xyg2 = (a_i_ida0e0b0xyg2 - prior_times_excluded_ida0e0b0xyg)

    ###k2 and k5 associations - keys also used for pyomo sets in the section below
    keys_k2 = np.ravel(uinp.structure['i_k2_idx_dams'])[:len_k2]
    keys_k2ktva1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(keys_k2, uinp.structure['i_k2_pos']-1)
    keys_k5 = np.ravel(uinp.structure['i_k5_idx_offs'])[:len_k5]
    keys_k5tva1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(keys_k5, uinp.structure['i_k2_pos'])


    ###number of progeny weaned - with d axis
    #### compare a_k2cluster with index_k5 to only retain the values for the dams that have yatf.
    #### index_k5 + 2 is allowing for NM & 00 that are 1st 2 entries in the k2cluster that don't exist in the k5cluster
    npw_k5tva1e1b1nwzida0e0b0xyg1w9i9 = fun.f_divide(np.sum(npw_tva1e1b1nwzida0e0b0xyg1[...,na,na] * distribution_2prog_va1e1b1nw8zida0e0b0xyg1w9[...,na]
                                                            * mask_w8vars_va1e1b1nw8zida0e0b0xyg1[...,na,na] * mask_tvars_k5tva1e1b1nw8zida0e0b0xyg1[...,na,na]
                                                          * (a_k2cluster_va1e1b1nwzida0e0b0xyg1==index_k5tva1e1b1nwzida0e0b0xyg3+2)[...,na,na] #convert e1 and b1 to k5 cluster - using a k5 cluster because progeny don't need all the k2 slices and the relevant ones align between k2 and k5 eg 11, 22 etc
                                                          * (a_i_ida0e0b0xyg2==index_ida0e0b0xyg)[...,na,na] * (index_ida0e0b0xyg[...,na,na] == index_i9)  #i9 (like w9 & g9) is the lambing time of the destination weaner. If lambing interval is not 12 months then a dam born in July may be giving birth in March and this weaner need to then become a dam replacement in the 'March' flock. Changing lambing time then requires a second i axis in teh parameter.
                                                          , axis=(b1_pos - 2, e1_pos - 2), keepdims=True)
                                                   , np.sum(numbers_start_va1e1b1nwzida0e0b0xyg1 * (a_k2cluster_va1e1b1nwzida0e0b0xyg1==index_k5tva1e1b1nwzida0e0b0xyg3+2),
                                                            axis=(b1_pos, e1_pos), keepdims=True)[...,na,na], dtype=dtype)

    ###npw required by prog activity
    ####mask numbers req (also used for prog2dams) - The progeny decision variable can be masked for gender and dam age for t[1] (t[1] are those that get transferred to dams). Gender only requires females, and the age of the dam only requires those that contribute to the initial age structure.
    mask_prog_tdx_tva1e1b1nwzida0e0b0xyg2w9 = np.logical_or((index_tva1e1b1nwzida0e0b0xyg2w9 != 1),
                                                            np.logical_and(np.logical_and((gender_xyg[mask_x] == 1)[...,na] ,
                                                                           (agedam_propn_da0e0b0xyg1 > 0)[...,na]),
                                                                           np.isin(index_g1, a_g1_g2)[...,na]))
    numbers_prog_req_tva1e1b1nwzida0e0b0xyg2w9 = 1 * mask_prog_tdx_tva1e1b1nwzida0e0b0xyg2w9

    ##transfer progeny to dam replacements
    ###liveweight distribution
    ffcfw_initial_wzida0e0b0xyg1 = lw_initial_wzida0e0b0xyg1 - cfw_initial_wzida0e0b0xyg1 / cw_dams[3, ...]
    distribution_2dams_wzida0e0b0xyg2w9 = sfun.f_lw_distribution(ffcfw_initial_wzida0e0b0xyg1, ffcfw_prog_wzida0e0b0xyg2, uinp.structure['i_n1_len'], uinp.structure['i_n_fvp_period1'])
    ###numbers provided - active d for Prog DVs
    numbers_prog2dams_k3tva1e1b1nwzida0e0b0xyg2g9w9 = 1 * (np.sum(distribution_2dams_wzida0e0b0xyg2w9[...,na,:] * mask_numbers_prog2damsw8w9_w9
                                                                    * mask_prog_tdx_tva1e1b1nwzida0e0b0xyg2w9[...,na,:]
                                                                    * (index_a0e0b0xyg == 0) #only a[0] prog can provide dams
                                                                    * (a_g1_g2[...,na,:]==index_g1)[...,na] * (index_tva1e1b1nwzida0e0b0xyg2w9 == 1)[...,na,:]
                                                                    * (a_k3cluster_da0e0b0xyg3 == index_k3k5tva1e1b1nwzida0e0b0xyg3)[...,na,na]
                                                                    , axis=(b0_pos-2, e0_pos-2),keepdims=True))
    ###numbers required - no d axis for Dam DVs
    ####collapse the e1 axis on the mask prior to np.sum because can't test for > 0 as per other numbers_req (because need proportions of age & BTRT)
    #### but don't want to increase the numbers if joining for multiple cycles
    numbers_progreq_k2k3k5tva1e1b1nw8zida0e0b0xyg1g9w9 = 1 * (np.sum(np.any(mask_numbers_reqw8w9_va1e1b1nw8zida0e0b0xyg1w9, axis=e1_pos-1, keepdims=True)[0, ...,na,:]
                                                                    * mask_tvars_k2tva1e1b1nw8zida0e0b0xyg1[:,na,na,:,0:1,...,na,na]  # mask based on the t axis for dvp0
                                                                    * (index_k2tva1e1b1nwzida0e0b0xyg1[:,na,na,..., na,na] == 0)
                                                                    * (index_g1[...,na]==index_g1)[...,na] * btrt_propn_b0xyg1[...,na,na] * e0_propn_ida0e0b0xyg[...,na,na]
                                                                    * agedam_propn_da0e0b0xyg1[...,na,na] * (a_k3cluster_da0e0b0xyg3 == index_k3k5tva1e1b1nwzida0e0b0xyg3)[...,na,na]
                                                                    * (a_k5cluster_da0e0b0xyg3 == index_k5tva1e1b1nwzida0e0b0xyg3)[...,na,na],
                                                                     axis=(e1_pos-2, d_pos-2, b0_pos-2, e0_pos-2),keepdims=True))

    ##transfer progeny to offs
    ###numbers provide - has d axis
    ffcfw_initial_wzida0e0b0xyg3 = lw_initial_wzida0e0b0xyg3 - cfw_initial_wzida0e0b0xyg3 / cw_offs[3, ...]
    ffcfw_initial_k5tva1e1b1nwzida0e0b0xyg3 = np.mean(ffcfw_initial_wzida0e0b0xyg3 * (a_k5cluster_da0e0b0xyg3 == index_k5tva1e1b1nwzida0e0b0xyg3)
                                                      , axis=(b0_pos, e0_pos),keepdims=True)
    distribution_2offs_k5tva1e1b1nwzida0e0b0xyg2w9 = sfun.f_lw_distribution(ffcfw_initial_k5tva1e1b1nwzida0e0b0xyg3, ffcfw_prog_wzida0e0b0xyg2, uinp.structure['i_n3_len'], uinp.structure['i_n_fvp_period3'])
    numbers_prog2offs_k3k5tva1e1b1nwzida0e0b0xyg2w9 = (distribution_2offs_k5tva1e1b1nwzida0e0b0xyg2w9
                                                             * mask_numbers_prog2offsw8w9_w9
                                                             * (index_tva1e1b1nwzida0e0b0xyg2w9 == 2)
                                                             * (a_k3cluster_da0e0b0xyg3 == index_k3k5tva1e1b1nwzida0e0b0xyg3)[...,na])

    ###numbers req
    numbers_progreq_va1e1b1nw8zida0e0b0xyg3w9 = 1 * (mask_numbers_reqw8w9_va1e1b1nw8zida0e0b0xyg3w9 > 0)



    ###########################
    #  report P2V             #
    ###########################
    ##cashflow stuff
    r_salevalue_ctva1e1b1nwzida0e0b0xyg0 = sfun.f_p2v_std(salevalue_pa1e1b1nwzida0e0b0xyg0, numbers_p=o_numbers_end_psire,
                                              on_hand_tvp=on_hand_pa1e1b1nwzida0e0b0xyg0, a_any1_p=a_c_pa1e1b1nwzida0e0b0xyg,index_any1tvp=index_ctpa1e1b1nwzida0e0b0xyg)
    r_woolvalue_ctva1e1b1nwzida0e0b0xyg0 = sfun.f_p2v_std(woolvalue_pa1e1b1nwzida0e0b0xyg0, numbers_p=o_numbers_end_psire,
                                              on_hand_tvp=on_hand_pa1e1b1nwzida0e0b0xyg0, a_any1_p=a_c_pa1e1b1nwzida0e0b0xyg,index_any1tvp=index_ctpa1e1b1nwzida0e0b0xyg)
    r_salevalue_ctva1e1b1nwzida0e0b0xyg1 = sfun.f_p2v(salevalue_tpa1e1b1nwzida0e0b0xyg1, a_v_pa1e1b1nwzida0e0b0xyg1, o_numbers_end_pdams,
                                              on_hand_tpa1e1b1nwzida0e0b0xyg1, a_any1_p=a_c_pa1e1b1nwzida0e0b0xyg,index_any1tp=index_ctpa1e1b1nwzida0e0b0xyg)
    r_woolvalue_ctva1e1b1nwzida0e0b0xyg1 = sfun.f_p2v(woolvalue_pa1e1b1nwzida0e0b0xyg1, a_v_pa1e1b1nwzida0e0b0xyg1, o_numbers_end_pdams,
                                              on_hand_tpa1e1b1nwzida0e0b0xyg1, a_any1_p=a_c_pa1e1b1nwzida0e0b0xyg,index_any1tp=index_ctpa1e1b1nwzida0e0b0xyg)
    r_salevalue_ctva1e1b1nwzida0e0b0xyg3 = sfun.f_p2v(salevalue_tpa1e1b1nwzida0e0b0xyg3, a_v_pa1e1b1nwzida0e0b0xyg3, o_numbers_end_poffs,
                                              on_hand_tpa1e1b1nwzida0e0b0xyg3, a_any1_p=a_c_pa1e1b1nwzida0e0b0xyg[mask_p_offs_p],index_any1tp=index_ctpa1e1b1nwzida0e0b0xyg)
    r_woolvalue_ctva1e1b1nwzida0e0b0xyg3 = sfun.f_p2v(woolvalue_tpa1e1b1nwzida0e0b0xyg3, a_v_pa1e1b1nwzida0e0b0xyg3, o_numbers_end_poffs,
                                              on_hand_tpa1e1b1nwzida0e0b0xyg3, a_any1_p=a_c_pa1e1b1nwzida0e0b0xyg[mask_p_offs_p],index_any1tp=index_ctpa1e1b1nwzida0e0b0xyg)

    ##cfw per head average for the mob - includes the mortality factor
    r_cfw_hdmob_vg0 = sfun.f_p2v_std(o_cfw_psire, numbers_p=o_numbers_end_psire, on_hand_tvp=on_hand_pa1e1b1nwzida0e0b0xyg0,
                                                  period_is_tvp=period_is_shearing_pa1e1b1nwzida0e0b0xyg0)
    r_cfw_hdmob_tvg1 = sfun.f_p2v(o_cfw_pdams, a_v_pa1e1b1nwzida0e0b0xyg1, o_numbers_end_pdams,
                                             on_hand_tpa1e1b1nwzida0e0b0xyg1, period_is_tp=period_is_shearing_pa1e1b1nwzida0e0b0xyg1)
    r_cfw_hdmob_tvg3 = sfun.f_p2v(o_cfw_poffs, a_v_pa1e1b1nwzida0e0b0xyg3, o_numbers_end_poffs,
                                             on_hand_tpa1e1b1nwzida0e0b0xyg3, period_is_tp=period_is_shearing_tpa1e1b1nwzida0e0b0xyg3)
    ##cfw per head - wool cut for 1 whole animal, no account for mortality
    r_cfw_hd_vg0 = sfun.f_p2v_std(o_cfw_psire, on_hand_tvp=on_hand_pa1e1b1nwzida0e0b0xyg0,
                                                  period_is_tvp=period_is_shearing_pa1e1b1nwzida0e0b0xyg0)
    r_cfw_hd_tvg1 = sfun.f_p2v(o_cfw_pdams, a_v_pa1e1b1nwzida0e0b0xyg1, on_hand_tp=on_hand_tpa1e1b1nwzida0e0b0xyg1,
                               period_is_tp=period_is_shearing_pa1e1b1nwzida0e0b0xyg1)
    r_cfw_hd_tvg3 = sfun.f_p2v(o_cfw_poffs, a_v_pa1e1b1nwzida0e0b0xyg3, on_hand_tp=on_hand_tpa1e1b1nwzida0e0b0xyg3,
                               period_is_tp=period_is_shearing_tpa1e1b1nwzida0e0b0xyg3)

    ##nfoet scanning
    r_nfoet_scan_tvg1 = sfun.f_p2v(nfoet_b1nwzida0e0b0xyg, a_v_pa1e1b1nwzida0e0b0xyg1, o_numbers_end_pdams,
                                on_hand_tp=on_hand_tpa1e1b1nwzida0e0b0xyg1, period_is_tp=period_is_scan_pa1e1b1nwzida0e0b0xyg1)

    ##nfoet birth
    r_nfoet_birth_tvg1 = sfun.f_p2v(nfoet_b1nwzida0e0b0xyg, a_v_pa1e1b1nwzida0e0b0xyg1, o_numbers_end_pdams,
                                   on_hand_tp=on_hand_tpa1e1b1nwzida0e0b0xyg1, period_is_tp=period_is_birth_pa1e1b1nwzida0e0b0xyg1)

    ##nyatf birth
    r_nyatf_birth_tvg1 = sfun.f_p2v(nyatf_b1nwzida0e0b0xyg, a_v_pa1e1b1nwzida0e0b0xyg1, o_numbers_end_pdams,
                                   on_hand_tp=on_hand_tpa1e1b1nwzida0e0b0xyg1, period_is_tp=period_is_birth_pa1e1b1nwzida0e0b0xyg1)

    ###########################
    # create report params    #
    ###########################
    ##sale value - needed for reporting
    r_salevalue_ctva1e1b1nwzida0e0b0xyg0 = sfun.f_create_production_param('sire',r_salevalue_ctva1e1b1nwzida0e0b0xyg0,
                                                                          numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg0)
    r_salevalue_k2ctva1e1b1nwzida0e0b0xyg1 = sfun.f_create_production_param('dams',r_salevalue_ctva1e1b1nwzida0e0b0xyg1,
                                                                            a_k2cluster_va1e1b1nwzida0e0b0xyg1,
                                                                            index_k2tva1e1b1nwzida0e0b0xyg1[:,na,...],
                                                                            numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg1,
                                                                            mask_vg=mask_w8vars_va1e1b1nw8zida0e0b0xyg1)
    r_salevalue_k3k5ctva1e1b1nwzida0e0b0xyg3 = sfun.f_create_production_param('offs',
                                                                              r_salevalue_ctva1e1b1nwzida0e0b0xyg3,
                                                                              a_k3cluster_da0e0b0xyg3,
                                                                              index_k3k5tva1e1b1nwzida0e0b0xyg3[:,:,na,
                                                                              ...],
                                                                              a_k5cluster_da0e0b0xyg3,
                                                                              index_k5tva1e1b1nwzida0e0b0xyg3[:,na,...],
                                                                              numbers_start_va1e1b1nwzida0e0b0xyg3,
                                                                              mask_vg=mask_w8vars_va1e1b1nw8zida0e0b0xyg3)

    ##wool value - needed for reporting
    r_woolvalue_ctva1e1b1nwzida0e0b0xyg0 = sfun.f_create_production_param('sire',r_woolvalue_ctva1e1b1nwzida0e0b0xyg0,
                                                                          numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg0)
    r_woolvalue_k2ctva1e1b1nwzida0e0b0xyg1 = sfun.f_create_production_param('dams',r_woolvalue_ctva1e1b1nwzida0e0b0xyg1,
                                                                            a_k2cluster_va1e1b1nwzida0e0b0xyg1,
                                                                            index_k2tva1e1b1nwzida0e0b0xyg1[:,na,...],
                                                                            numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg1,
                                                                            mask_vg=mask_w8vars_va1e1b1nw8zida0e0b0xyg1)
    r_woolvalue_k3k5ctva1e1b1nwzida0e0b0xyg3 = sfun.f_create_production_param('offs',
                                                                              r_woolvalue_ctva1e1b1nwzida0e0b0xyg3,
                                                                              a_k3cluster_da0e0b0xyg3,
                                                                              index_k3k5tva1e1b1nwzida0e0b0xyg3[:,:,na,
                                                                              ...],
                                                                              a_k5cluster_da0e0b0xyg3,
                                                                              index_k5tva1e1b1nwzida0e0b0xyg3[:,na,...],
                                                                              numbers_start_va1e1b1nwzida0e0b0xyg3,
                                                                              mask_vg=mask_w8vars_va1e1b1nw8zida0e0b0xyg3)

    ##cfw per head average for the mob - includes the mortality factor
    r_cfw_hdmob_tva1e1b1nwzida0e0b0xyg0 = sfun.f_create_production_param('sire',r_cfw_hdmob_vg0,
                                                                         numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg0)
    r_cfw_hdmob_k2tva1e1b1nwzida0e0b0xyg1 = sfun.f_create_production_param('dams',r_cfw_hdmob_tvg1,
                                                                           a_k2cluster_va1e1b1nwzida0e0b0xyg1,
                                                                           index_k2tva1e1b1nwzida0e0b0xyg1,
                                                                           numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg1,
                                                                           mask_vg=mask_w8vars_va1e1b1nw8zida0e0b0xyg1)
    r_cfw_hdmob_k3k5tva1e1b1nwzida0e0b0xyg3 = sfun.f_create_production_param('offs',r_cfw_hdmob_tvg3,
                                                                             a_k3cluster_da0e0b0xyg3,
                                                                             index_k3k5tva1e1b1nwzida0e0b0xyg3,
                                                                             a_k5cluster_da0e0b0xyg3,
                                                                             index_k5tva1e1b1nwzida0e0b0xyg3,
                                                                             numbers_start_va1e1b1nwzida0e0b0xyg3,
                                                                             mask_vg=mask_w8vars_va1e1b1nw8zida0e0b0xyg3)

    ##cfw per head - wool cut per animal at shearing, no account for mortality (numbers)
    r_cfw_hd_tva1e1b1nwzida0e0b0xyg0 = sfun.f_create_production_param('sire',r_cfw_hd_vg0)
    r_cfw_hd_k2tva1e1b1nwzida0e0b0xyg1 = sfun.f_create_production_param('dams',r_cfw_hd_tvg1,
                                                                        a_k2cluster_va1e1b1nwzida0e0b0xyg1,
                                                                        index_k2tva1e1b1nwzida0e0b0xyg1,
                                                                        mask_vg=mask_w8vars_va1e1b1nw8zida0e0b0xyg1)
    r_cfw_hd_k3k5tva1e1b1nwzida0e0b0xyg3 = sfun.f_create_production_param('offs',r_cfw_hd_tvg3,a_k3cluster_da0e0b0xyg3,
                                                                          index_k3k5tva1e1b1nwzida0e0b0xyg3,
                                                                          a_k5cluster_da0e0b0xyg3,
                                                                          index_k5tva1e1b1nwzida0e0b0xyg3,
                                                                          mask_vg=mask_w8vars_va1e1b1nw8zida0e0b0xyg3)


    ######################################
    #weaning %, scan % and lamb survival #
    ######################################
    # ##wean percent - weaning percent - npw per ewe at start of dvp (ie accounting for mortality)
    # r_npw_joining_tvg1 = fun.f_divide(npw2_tva1e1b1nwzida0e0b0xyg1,np.sum(r_numbers_join_va1e1b1nwzida0e0b0xyg1,
    #                                                                       axis=(a1_pos, b1_pos, e1_pos),keepdims=True))
    ###number of progeny weaned. Cluster and account for mortality between start of dvp and weaning so it is compatible with the dams variable
    r_nyatf_wean_tva1e1b1nwzida0e0b0xyg1 = sfun.f_create_production_param('dams',npw2_tva1e1b1nwzida0e0b0xyg1,
                                                                       numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg1,
                                                                       mask_vg=mask_w8vars_va1e1b1nw8zida0e0b0xyg1) # no clustering required for wean percent because it is a measure of all dams

    ##scanning percent - foetuses scanned per ewe at start of dvp (ie accounting for dam mortality)
    r_nfoet_scan_tva1e1b1nwzida0e0b0xyg1 = sfun.f_create_production_param('dams',r_nfoet_scan_tvg1,
                                                                       numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg1,
                                                                       mask_vg=mask_w8vars_va1e1b1nw8zida0e0b0xyg1)  # no clustering required for scanning percent because it is a measure of all dams

    ##nfoet - nfoet per ewe at start of dvp (ie accounting for dam mortality - so it can be multiplied by the v_dams from lp solution)
    # r_nfoet_birth_k2tva1e1b1nwzida0e0b0xyg1 = sfun.f_create_production_param('dams',r_nfoet_birth_tvg1,
    #                                                                    a_k2cluster_va1e1b1nwzida0e0b0xyg1,
    #                                                                    index_k2tva1e1b1nwzida0e0b0xyg1,
    #                                                                    numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg1,
    #                                                                    mask_vg=mask_w8vars_va1e1b1nw8zida0e0b0xyg1)

    r_nfoet_birth_k2tva1e1b1nwzida0e0b0xyg1 = fun.f_divide(r_nfoet_birth_tvg1 * (a_k2cluster_va1e1b1nwzida0e0b0xyg1 == index_k2tva1e1b1nwzida0e0b0xyg1) #cant use param function because we need to keep e and b axis
                                                           * mask_w8vars_va1e1b1nw8zida0e0b0xyg1
                                                            , np.sum(numbers_start_va1e1b1nwzida0e0b0xyg1 * (a_k2cluster_va1e1b1nwzida0e0b0xyg1 == index_k2tva1e1b1nwzida0e0b0xyg1),
                                                                     axis = (e1_pos, b1_pos), keepdims=True))


    ##nyatf - nyatf per ewe at start of dvp (ie accounting for dam mortality - so it can be multiplied by the v_dams from lp solution)
    # r_nyatf_birth_k2tva1e1b1nwzida0e0b0xyg1 = sfun.f_create_production_param('dams',r_nyatf_birth_tvg1,
    #                                                                    a_k2cluster_va1e1b1nwzida0e0b0xyg1,
    #                                                                    index_k2tva1e1b1nwzida0e0b0xyg1,
    #                                                                    numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg1,
    #                                                                    mask_vg=mask_w8vars_va1e1b1nw8zida0e0b0xyg1)

    r_nyatf_birth_k2tva1e1b1nwzida0e0b0xyg1 = fun.f_divide(r_nyatf_birth_tvg1 * (a_k2cluster_va1e1b1nwzida0e0b0xyg1 == index_k2tva1e1b1nwzida0e0b0xyg1) #cant use param function because we need to keep e and b axis
                                                           * mask_w8vars_va1e1b1nw8zida0e0b0xyg1
                                                            , np.sum(numbers_start_va1e1b1nwzida0e0b0xyg1 * (a_k2cluster_va1e1b1nwzida0e0b0xyg1 == index_k2tva1e1b1nwzida0e0b0xyg1),
                                                                     axis = (e1_pos, b1_pos), keepdims=True))

    # ##number of dams at birth with k, e1 & b1 axes
    # r_numbers_birth_k2tva1e1b1nwzida0e0b0xyg1 = r_numbers_birth_va1e1b1nwzida0e0b0xyg1 * (
    #             a_k2cluster_va1e1b1nwzida0e0b0xyg1 == index_k2tva1e1b1nwzida0e0b0xyg1)
    #
    # ##prog born per ewe mated ewe in cluster - nfoet has been adjusted to align with v_dams
    # ### It isn't possible to multiply the number of progeny per dam and sum to get to a average progeny per dam  todo i feel like a problem is that we are returning number of prog per ewe mated but v_dams at birth(start of dvp) does not represent ewes mated if drys have been sold.
    # r_prog_born_k2tva1e1b1nwzida0e0b0xyg1 = fun.f_divide(r_nfoet_birth_tva1e1b1nwzida0e0b0xyg1 * r_numbers_birth_k2tva1e1b1nwzida0e0b0xyg1
    #                                      , np.sum(r_numbers_birth_k2tva1e1b1nwzida0e0b0xyg1, axis=(0, e1_pos, b1_pos), keepdims=True)) # summing the k axis so that total number of dams is included (including drys)
    # ##prog alive (alive after birth) per ewe in cluster - nyatf has been adjusted to align with v_dams
    # r_prog_alive_k2tva1e1b1nwzida0e0b0xyg1 = fun.f_divide(r_nyatf_birth_k2tva1e1b1nwzida0e0b0xyg1 * r_numbers_birth_k2tva1e1b1nwzida0e0b0xyg1
    #                                       , np.sum(r_numbers_birth_k2tva1e1b1nwzida0e0b0xyg1, axis=(0, e1_pos, b1_pos), keepdims=True))

    ###lw - need to add v and k2 axis but still keep p, e and b so that we can graph the desired patterns. This is a big array so only stored if user wants. Don't need t because it doesnt effect lw
    if pinp.rep['i_store_lw_rep']:
        r_lw_sire_pg = o_lw_psire
        r_lw_dams_k2tvpg = o_lw_pdams * (a_v_pa1e1b1nwzida0e0b0xyg1 == index_vpa1e1b1nwzida0e0b0xyg1) * (
                    a_k2cluster_va1e1b1nwzida0e0b0xyg1 == index_k2tva1e1b1nwzida0e0b0xyg1[:,:,:,:,na,...])
        r_lw_offs_k3k5tvpg = o_lw_poffs * (a_v_pa1e1b1nwzida0e0b0xyg3 == index_vpa1e1b1nwzida0e0b0xyg3) * (
                    a_k3cluster_da0e0b0xyg3 == index_k3k5tva1e1b1nwzida0e0b0xyg3[:,:,:,:,na,...]) \
                             * (a_k5cluster_da0e0b0xyg3 == index_k5tva1e1b1nwzida0e0b0xyg3[:,:,:,:,na,...])

    ###fec - need to add v and k2 axis but still keep p, e and b so that we can graph the desired patterns. This is a big array so only stored if user wants. Don't need t because it doesnt effect lw
    if pinp.rep['i_store_fec_rep']:
        r_fec_sire_pg = ev_sire
        r_fec_dams_k2tvpg = (ev_dams * (a_v_pa1e1b1nwzida0e0b0xyg1 == index_vpa1e1b1nwzida0e0b0xyg1)
                             * (a_k2cluster_va1e1b1nwzida0e0b0xyg1[:,na,...] == index_k2tva1e1b1nwzida0e0b0xyg1[:,:,:,na,...]))
        r_fec_offs_k3k5tvpg = (ev_offs * (a_v_pa1e1b1nwzida0e0b0xyg3 == index_vpa1e1b1nwzida0e0b0xyg3)
                               * (a_k3cluster_da0e0b0xyg3 == index_k3k5tva1e1b1nwzida0e0b0xyg3[:,:,:,:,na,...])
                               * (a_k5cluster_da0e0b0xyg3 == index_k5tva1e1b1nwzida0e0b0xyg3[:,:,:,na,...]))

    ###############
    ## report dse #
    ###############
    days_p6 = np.array(pinp.feed_inputs['feed_periods'].loc[:pinp.feed_inputs['feed_periods'].index[-2], 'length'])  # not including last row because that is the start of the following year.
    days_p6_p6tva1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(days_p6, p_pos-2)
    ###DSE based on MJ/d
    ####returns the average mj/d for each animal for the each feed period (mei accounts for if the animal is on hand - if the animal is sold the average mei/d will be lower in that dvp)
    mj_ave_p6ftva1e1b1nwzida0e0b0xyg0 = mei_p6fa1e1b1nwzida0e0b0xyg0[:,:,na,na,...] / days_p6_p6tva1e1b1nwzida0e0b0xyg[:,na,...]
    mj_ave_k2p6ftva1e1b1nwzida0e0b0xyg1 = mei_k2p6ftva1e1b1nwzida0e0b0xyg1 / days_p6_p6tva1e1b1nwzida0e0b0xyg[:,na,...]
    mj_ave_k3k5p6ftva1e1b1nwzida0e0b0xyg3 = mei_k3k5p6ftva1e1b1nwzida0e0b0xyg3 / days_p6_p6tva1e1b1nwzida0e0b0xyg[:,na,...]
    ####returns the number of dse of each animal in each dvp - this is combined with the variable numbers in reporting to get the total dse
    dsemj_p6tva1e1b1nwzida0e0b0xyg0 = np.sum(mj_ave_p6ftva1e1b1nwzida0e0b0xyg0 / pinp.sheep['i_dse_mj'], axis = 1)
    dsemj_k2p6tva1e1b1nwzida0e0b0xyg1 = np.sum(mj_ave_k2p6ftva1e1b1nwzida0e0b0xyg1 / pinp.sheep['i_dse_mj'], axis = 2)
    dsemj_k3k5p6tva1e1b1nwzida0e0b0xyg3 = np.sum(mj_ave_k3k5p6ftva1e1b1nwzida0e0b0xyg3 / pinp.sheep['i_dse_mj'], axis = 3)

    ###DSE based on nw
    #### cumulative total of nw with p6 axis
    nw_cum_p6a1e1b1nwzida0e0b0xyg0 = sfun.f_p2v_std(o_nw_start_psire ** 0.75, numbers_p=o_numbers_end_psire,
                                        on_hand_tvp=on_hand_pa1e1b1nwzida0e0b0xyg0, days_period_p=days_period_pa1e1b1nwzida0e0b0xyg0,
                                        a_any1_p=a_p6_pa1e1b1nwzida0e0b0xyg, index_any1tvp=index_p6pa1e1b1nwzida0e0b0xyg)
    nw_cum_p6tva1e1b1nwzida0e0b0xyg1 = sfun.f_p2v(o_nw_start_pdams ** 0.75, a_v_pa1e1b1nwzida0e0b0xyg1, numbers_p=o_numbers_end_pdams,
                                        on_hand_tp=on_hand_tpa1e1b1nwzida0e0b0xyg1, days_period_p=days_period_pa1e1b1nwzida0e0b0xyg1,
                                        a_any1_p=a_p6_pa1e1b1nwzida0e0b0xyg, index_any1tp=index_p6pa1e1b1nwzida0e0b0xyg[:,na,...])
    nw_cum_p6tva1e1b1nwzida0e0b0xyg3 = sfun.f_p2v(o_nw_start_poffs**0.75, a_v_pa1e1b1nwzida0e0b0xyg3, numbers_p=o_numbers_end_poffs,
                                        on_hand_tp=on_hand_tpa1e1b1nwzida0e0b0xyg3, days_period_p=days_period_cut_pa1e1b1nwzida0e0b0xyg3,
                                        a_any1_p=a_p6_pa1e1b1nwzida0e0b0xyg[mask_p_offs_p], index_any1tp=index_p6pa1e1b1nwzida0e0b0xyg[:,na,...])
    ####returns the average nw for each animal for the each feed period (cum nw accounts for if the animal is on hand - if the animal is sold the average nw will be lower in that feed period)
    nw_ave_p6tva1e1b1nwzida0e0b0xyg0 = nw_cum_p6a1e1b1nwzida0e0b0xyg0[:,na,na,...] / days_p6_p6tva1e1b1nwzida0e0b0xyg
    nw_ave_p6tva1e1b1nwzida0e0b0xyg1 = nw_cum_p6tva1e1b1nwzida0e0b0xyg1 / days_p6_p6tva1e1b1nwzida0e0b0xyg
    nw_ave_p6tva1e1b1nwzida0e0b0xyg3 = nw_cum_p6tva1e1b1nwzida0e0b0xyg3 / days_p6_p6tva1e1b1nwzida0e0b0xyg
    ####convert nw to dse
    dsehd_p6tva1e1b1nwzida0e0b0xyg0 = nw_ave_p6tva1e1b1nwzida0e0b0xyg0 / pinp.sheep['i_dse_nw']**0.75
    dsehd_p6tva1e1b1nwzida0e0b0xyg1 = nw_ave_p6tva1e1b1nwzida0e0b0xyg1 / pinp.sheep['i_dse_nw']**0.75
    dsehd_p6tva1e1b1nwzida0e0b0xyg3 = nw_ave_p6tva1e1b1nwzida0e0b0xyg3 / pinp.sheep['i_dse_nw']**0.75
    ####account for b1 axis effect on dse & select the dse group (note sire and offs don't have b1 axis so simple slice)
    dse_group_dp6tva1e1b1nwzida0e0b0xyg = fun.f_reshape_expand(pinp.sheep['i_dse_group'], p_pos - 2)
    dams_dsegroup_b1p6tva1e1bnwzida0e0b0xyg = fun.f_reshape_expand(uinp.structure['ia_dams_dsegroup_b1'], p_pos-3) #put the b1 axis in the same place as the dse group axis
    dsenw_p6tva1e1b1nwzida0e0b0xyg0 = dsehd_p6tva1e1b1nwzida0e0b0xyg0 * dse_group_dp6tva1e1b1nwzida0e0b0xyg[uinp.structure['ia_sire_dsegroup']]
    dsenw_p6tva1e1b1nwzida0e0b0xyg1 = dsehd_p6tva1e1b1nwzida0e0b0xyg1 * np.moveaxis(np.take_along_axis(dse_group_dp6tva1e1b1nwzida0e0b0xyg, dams_dsegroup_b1p6tva1e1bnwzida0e0b0xyg,0)[...,0], 0, b1_pos) #take along the dse group axis, remove the last axis, then move b1 axis into place
    dsenw_p6tva1e1b1nwzida0e0b0xyg3 = dsehd_p6tva1e1b1nwzida0e0b0xyg3 * dse_group_dp6tva1e1b1nwzida0e0b0xyg[uinp.structure['ia_offs_dsegroup']]
    ##cluster and account for numbers/mortality
    dsenw_p6tva1e1b1nwzida0e0b0xyg0 = sfun.f_create_production_param('sire', dsenw_p6tva1e1b1nwzida0e0b0xyg0, numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg0)
    dsenw_k2p6tva1e1b1nwzida0e0b0xyg1 = sfun.f_create_production_param('dams', dsenw_p6tva1e1b1nwzida0e0b0xyg1, a_k2cluster_va1e1b1nwzida0e0b0xyg1,
                                                index_k2tva1e1b1nwzida0e0b0xyg1[:,na,...], numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg1,
                                                mask_vg = mask_w8vars_va1e1b1nw8zida0e0b0xyg1)
    dsenw_k3k5p6tva1e1b1nwzida0e0b0xyg3 = sfun.f_create_production_param('offs', dsenw_p6tva1e1b1nwzida0e0b0xyg3, a_k3cluster_da0e0b0xyg3, index_k3k5tva1e1b1nwzida0e0b0xyg3[:,:,na,...],
                                                    a_k5cluster_da0e0b0xyg3, index_k5tva1e1b1nwzida0e0b0xyg3[:,na,...], numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg3,
                                                    mask_vg=mask_w8vars_va1e1b1nw8zida0e0b0xyg3)

    ####################
    #report stock days #
    ####################
    ##this needs to be accounted for when reporting things that have p6 and v axis because they are both periods that do not align and the number variable
    ##returned from pyomo does not have p6 axis. So need to account for the propn of the dvp that the feed period exists.
    ##^this is not quite perfect because a_p6_p is such that a generator period is a whole feed period eg if the feed period changed mid gen period the proportion will be slightly off (exaggerated for smaller feed periods).
    stock_days_p6fa1e1b1nwzida0e0b0xyg0 = sfun.f_p2v_std(on_hand_pa1e1b1nwzida0e0b0xyg0, numbers_p=o_numbers_end_psire,
                                        days_period_p=days_period_pa1e1b1nwzida0e0b0xyg0, a_any1_p=a_ev_pa1e1b1nwzida0e0b0xyg0, index_any1tvp=index_fpa1e1b1nwzida0e0b0xyg,
                                        a_any2_p=a_p6_pa1e1b1nwzida0e0b0xyg, index_any2any1tvp=index_p6pa1e1b1nwzida0e0b0xyg[:,na,...])
    stock_days_p6ftva1e1b1nwzida0e0b0xyg1 = sfun.f_p2v(on_hand_tpa1e1b1nwzida0e0b0xyg1, a_v_pa1e1b1nwzida0e0b0xyg1, numbers_p=o_numbers_end_pdams,
                                            days_period_p=days_period_pa1e1b1nwzida0e0b0xyg1, a_any1_p=a_ev_pa1e1b1nwzida0e0b0xyg1, index_any1tp=index_fpa1e1b1nwzida0e0b0xyg[:,na,...],
                                            a_any2_p=a_p6_pa1e1b1nwzida0e0b0xyg, index_any2any1tp=index_p6pa1e1b1nwzida0e0b0xyg[:,na,na,...])
    stock_days_p6ftva1e1b1nwzida0e0b0xyg3 = sfun.f_p2v(on_hand_tpa1e1b1nwzida0e0b0xyg3, a_v_pa1e1b1nwzida0e0b0xyg3, numbers_p=o_numbers_end_poffs,
                                            days_period_p=days_period_cut_pa1e1b1nwzida0e0b0xyg3, a_any1_p=a_ev_pa1e1b1nwzida0e0b0xyg3, index_any1tp=index_fpa1e1b1nwzida0e0b0xyg[:,na,...],
                                            a_any2_p=a_p6_pa1e1b1nwzida0e0b0xyg[mask_p_offs_p], index_any2any1tp=index_p6pa1e1b1nwzida0e0b0xyg[:,na,na,...])

    ##cluster and account for numbers/mortality
    stock_days_p6fa1e1b1nwzida0e0b0xyg0 = sfun.f_create_production_param('sire', stock_days_p6fa1e1b1nwzida0e0b0xyg0, numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg0)
    stock_days_k2p6ftva1e1b1nwzida0e0b0xyg1 = sfun.f_create_production_param('dams', stock_days_p6ftva1e1b1nwzida0e0b0xyg1, a_k2cluster_va1e1b1nwzida0e0b0xyg1,
                                                index_k2tva1e1b1nwzida0e0b0xyg1[:,na,na,...], numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg1,
                                                mask_vg = mask_w8vars_va1e1b1nw8zida0e0b0xyg1)
    stock_days_k3k5p6ftva1e1b1nwzida0e0b0xyg3 = sfun.f_create_production_param('offs', stock_days_p6ftva1e1b1nwzida0e0b0xyg3, a_k3cluster_da0e0b0xyg3, index_k3k5tva1e1b1nwzida0e0b0xyg3[:,:,na,na,...],
                                                    a_k5cluster_da0e0b0xyg3, index_k5tva1e1b1nwzida0e0b0xyg3[:,na,na,...], numbers_start_vg=numbers_start_va1e1b1nwzida0e0b0xyg3,
                                                    mask_vg=mask_w8vars_va1e1b1nw8zida0e0b0xyg3)





    # plt.plot(o_ffcfw_pdams[:, 0, 0:2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])         #compare e1 for singles
    # plt.plot(o_ffcfw_pdams[:, 0, 1, 3, 0, 17:19, 0, 0, 0, 0, 0, 0, 0, 0, 0])         #compare w for singles and e1[1]
    # plt.plot(o_ffcfw_start_pyatf[:, 0, 0:2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])   #compare e1 for singles
    # plt.plot(o_ebg_pdams[:, 0, 0:2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])           #compare e1 for singles
    # plt.plot(o_pi_pdams[:, 0, 0:2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])            #compare e1 for singles
    # plt.plot(o_mei_solid_pdams[:, 0, 0, :, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])           #compare b1 for first cycle
    # plt.plot(r_intake_f_pdams[:, 0, 0:2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])        #compare e1 for singles
    # plt.plot(r_md_solid_pdams[:, 0, 0:2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])        #compare e1 for singles
    # plt.show()

    #############
    #params keys#
    #############
    keys_start=time.time()

    ##param keys - make numpy str to keep size small
    keys_a = pinp.sheep['i_a_idx'][pinp.sheep['i_mask_a']]
    keys_c = np.array(uinp.structure['cashflow_periods'])
    keys_d = pinp.sheep['i_d_idx'][mask_d_offs]
    keys_g0 = sfun.f_g2g(pinp.sheep['i_g_idx_sire'],'sire')
    keys_g1 = sfun.f_g2g(pinp.sheep['i_g_idx_dams'],'dams')
    keys_g2 = keys_g1
    keys_g3 = sfun.f_g2g(pinp.sheep['i_g_idx_offs'],'offs')
    keys_f = np.asarray(uinp.structure['sheep_pools'])
    keys_h1 = np.asarray(uinp.sheep['i_h1_idx'])
    keys_i = pinp.sheep['i_i_idx'][pinp.sheep['i_mask_i']]
    keys_k3 = np.ravel(pinp.sheep['i_k3_idx_offs'])[:len_k3]
    # keys_lw0 = np.array(uinp.structure['i_w_idx_sire'])
    keys_lw1 = np.array(uinp.structure['i_w_idx_dams'])
    keys_lw3 = np.array(uinp.structure['i_w_idx_offs'])
    keys_lw_prog = np.array(['lw%02d'%i for i in range(len_w_prog)])
    # keys_n0 = uinp.structure['i_n_idx_sire']
    keys_n1 = np.array(uinp.structure['i_n_idx_dams'])
    keys_n3 = np.array(uinp.structure['i_n_idx_offs'])
    keys_p5 = np.array(per.p_date2_df().index).astype('str')
    keys_p6 = np.array(pinp.feed_inputs['feed_periods'].index[:-1]).astype('str')
    keys_p8 = np.array(['sire_per%s'%i for i in range(len_p8)])
    keys_t1 = np.array(['t%s'%i for i in range(len_t1)])
    keys_t2 = np.array(['t%s'%i for i in range(len_t2)])
    keys_t3 = np.array(['t%s'%i for i in range(len_t3)])
    keys_v1 = np.array(['dvp%02d'%i for i in range(dvp_type_va1e1b1nwzida0e0b0xyg1.shape[0])])
    keys_v3 = np.array(['dvp%02d'%i for i in range(dvp_date_start_va1e1b1nwzida0e0b0xyg3.shape[0])])
    keys_y0 = uinp.parameters['i_y_idx_sire'][uinp.parameters['i_mask_y']]
    keys_y1 = uinp.parameters['i_y_idx_dams'][uinp.parameters['i_mask_y']]
    keys_y3 = uinp.parameters['i_y_idx_offs'][uinp.parameters['i_mask_y']]
    keys_x = pinp.sheep['i_x_idx'][mask_x]
    keys_z = np.array(pinp.general['season_info'].index[pinp.general['season_info']['included']]).astype('str')
    ##save k2 set for pyomo - required because this cant easily be built without information in this module
    params['a_idx'] = keys_a
    params['d_idx'] = keys_d
    params['i_idx'] = keys_i
    params['p8_idx'] = keys_p8
    params['g_idx_sire'] = keys_g0
    params['y_idx_sire'] = keys_y0
    params['dvp_idx_dams'] = keys_v1
    params['g_idx_dams'] = keys_g1
    params['g_idx_yatf'] = keys_g2
    params['k2_idx_dams'] = keys_k2
    params['t_idx_dams'] = keys_t1
    params['y_idx_dams'] = keys_y1
    params['dvp_idx_offs'] = keys_v3
    params['g_idx_offs'] = keys_g3
    params['k3_idx_offs'] = keys_k3
    params['k5_idx_offs'] = keys_k5
    params['y_idx_offs'] = keys_y3
    params['x_idx_offs'] = keys_x
    ##make param indexs
    ###k2k2tvanwziyg1g0p8 - nsire
    arrays = [keys_k2, keys_t1, keys_v1, keys_a, keys_n1, keys_lw1, keys_z, keys_i, keys_y1, keys_g1, keys_g0, keys_p8]
    index_k2tvanwziyg1g0p8 = fun.cartesian_product_simple_transpose(arrays)

    ###g0p8 - nsire
    arrays = [keys_g0, keys_p8]
    index_g0p8 = fun.cartesian_product_simple_transpose(arrays)

    # ###k5tvanwzidxyg1w9i9 - npw
    # arrays = [keys_k5, keys_t1, keys_v1, keys_a, keys_n1, keys_lw1, keys_z, keys_i, keys_d, keys_x, keys_y1, keys_g1, keys_lw_prog, keys_i]
    # index_k5tva1nw8zidxyg1w9i9 = fun.cartesian_product_simple_transpose(arrays)

    ###tdxg - npw req
    arrays = [keys_t2, keys_d, keys_x, keys_g2]
    index_tdxg = fun.cartesian_product_simple_transpose(arrays)

    ###k3tvw8zidaxyg2g9w9 - prog to dams prov
    arrays = [keys_k3, keys_t2, keys_lw_prog, keys_z, keys_i, keys_d, keys_a, keys_x, keys_y1, keys_g2, keys_g1, keys_lw1]
    index_k3tw8zida0xyg2g9w9 = fun.cartesian_product_simple_transpose(arrays)

    ###k3tvw8zidyg2w9 - prog to offs prov
    arrays = [keys_k3, keys_k5, keys_t2, keys_lw_prog, keys_z, keys_i, keys_d, keys_a, keys_x, keys_y1, keys_g3, keys_lw3]
    index_k3k5tw8zidaxyg2w9 = fun.cartesian_product_simple_transpose(arrays)

    ###k3k5tva1w8zidyg1g9w9 - prog to dams req
    arrays = [keys_k2, keys_k3, keys_k5, keys_t1, keys_lw1, keys_z, keys_i, keys_y1, keys_g1, keys_g1, keys_lw1]
    index_k2k3k5tw8ziyg1g9w9 = fun.cartesian_product_simple_transpose(arrays)


    ###vw8ixw9 - prog to offs req
    arrays = [keys_v3, keys_lw3, keys_i, keys_x, keys_lw3]
    index_vw8ixw9 = fun.cartesian_product_simple_transpose(arrays)

    ##k2k2tvanwziyg1g9w9 - numbers dams
    # arrays = [keys_k2, keys_k2, keys_t1, keys_v1, keys_a, keys_n1, keys_lw1, keys_z, keys_i, keys_y1, keys_g1, keys_g1, keys_lw1]
    # index_k2k2tvanwziyg1g9w = fun.cartesian_product_simple_transpose(arrays)

    ###k3k5tvnwziayg3w9 - numbers offs
    arrays = [keys_k3, keys_k5, keys_t3, keys_v3, keys_n3, keys_lw3, keys_z, keys_i, keys_a, keys_x, keys_y3, keys_g3, keys_lw3]
    index_k3k5tvnw8ziaxyg3w9 = fun.cartesian_product_simple_transpose(arrays)
    ###k3k5wixg3w9 - numbers req offs (doesnt have many active axis)
    arrays = [keys_k3, keys_k5, keys_v3, keys_lw3, keys_i, keys_x, keys_g3, keys_lw3]
    index_k3k5vw8ixg3w9 = fun.cartesian_product_simple_transpose(arrays)

    ###p6fg0 - mei sire
    arrays = [keys_p6, keys_f, keys_g0]
    index_p6fg0 = fun.cartesian_product_simple_transpose(arrays)
    ###k2p6ftva1nw8ziyg1 - mei dams
    arrays = [keys_k2, keys_p6, keys_f, keys_t1, keys_v1, keys_a, keys_n1, keys_lw1, keys_z, keys_i, keys_y1, keys_g1]
    index_k2p6ftva1nw8ziyg1 = fun.cartesian_product_simple_transpose(arrays)
    ###k3k5p6ftvnw8ziaxyg3 - mei offs
    arrays = [keys_k3, keys_k5, keys_p6, keys_f, keys_t3, keys_v3, keys_n3, keys_lw3, keys_z, keys_i, keys_a, keys_x, keys_y3, keys_g3]
    index_k3k5p6ftvnw8ziaxyg3 = fun.cartesian_product_simple_transpose(arrays)

    ###p6g0 - dse sire
    arrays = [keys_p6, keys_g0]
    index_p6g0 = fun.cartesian_product_simple_transpose(arrays)
    ###k2p6tva1nw8ziyg1 - dse dams
    arrays = [keys_k2, keys_p6, keys_t1, keys_v1, keys_a, keys_n1, keys_lw1, keys_z, keys_i, keys_y1, keys_g1]
    index_k2p6tva1nw8ziyg1 = fun.cartesian_product_simple_transpose(arrays)
    ###k3k5p6tvnw8ziaxyg3 - dse offs
    arrays = [keys_k3, keys_k5, keys_p6, keys_t3, keys_v3, keys_n3, keys_lw3, keys_z, keys_i, keys_a, keys_x, keys_y3, keys_g3]
    index_k3k5p6tvnw8ziaxyg3 = fun.cartesian_product_simple_transpose(arrays)

    ###cg0 - cashflow sire
    arrays = [keys_c, keys_g0]
    index_cg0 = fun.cartesian_product_simple_transpose(arrays)
    ###k2ctvanwziyg1 - cashflow dams
    arrays = [keys_k2, keys_c, keys_t1, keys_v1, keys_a, keys_n1, keys_lw1, keys_z, keys_i, keys_y1, keys_g1]
    index_k2ctvanwziyg1 = fun.cartesian_product_simple_transpose(arrays)
    ###ctwziaxg2 - cashflow prog
    arrays = [keys_c, keys_t2, keys_lw_prog, keys_z, keys_i, keys_a, keys_x, keys_g2]
    index_ctwzia0xg2 = fun.cartesian_product_simple_transpose(arrays)
    ###k3k5ctvnw8ziaxyg3 - cashflow offs
    arrays = [keys_k3, keys_k5, keys_c, keys_t3, keys_v3, keys_n3, keys_lw3, keys_z, keys_i, keys_a, keys_x, keys_y3, keys_g3]
    index_k3k5ctvnw8ziaxyg3 = fun.cartesian_product_simple_transpose(arrays)

    ###g0 - cost sire
    arrays = [keys_g0]
    index_g0 = fun.cartesian_product_simple_transpose(arrays)
    ###k2tvanwziyg1 - cost dams
    arrays = [keys_k2, keys_t1, keys_v1, keys_a, keys_n1, keys_lw1, keys_z, keys_i, keys_y1, keys_g1]
    index_k2tvanwziyg1 = fun.cartesian_product_simple_transpose(arrays)
    ###k3k5tvnw8ziaxyg3 - cost offs
    arrays = [keys_k3, keys_k5, keys_t3, keys_v3, keys_n3, keys_lw3, keys_z, keys_i, keys_a, keys_x, keys_y3, keys_g3]
    index_k3k5tvnw8ziaxyg3 = fun.cartesian_product_simple_transpose(arrays)

    ###p5g0 - labour sire
    arrays = [keys_p5, keys_g0]
    index_p5g0 = fun.cartesian_product_simple_transpose(arrays)
    ###k2p5tvanwziyg1 - labour dams
    arrays = [keys_k2, keys_p5, keys_t1, keys_v1, keys_a, keys_n1, keys_lw1, keys_z, keys_i, keys_y1, keys_g1]
    index_k2p5tvanwziyg1 = fun.cartesian_product_simple_transpose(arrays)
    ###k3k5p5tvnw8ziaxyg3 - labour offs
    arrays = [keys_k3, keys_k5, keys_p5, keys_t3, keys_v3, keys_n3, keys_lw3, keys_z, keys_i, keys_a, keys_x, keys_y3, keys_g3]
    index_k3k5p5tvnw8ziaxyg3 = fun.cartesian_product_simple_transpose(arrays)

    ###h1g0 - infrastructure dams
    arrays = [keys_h1, keys_g0]
    index_h1g0 = fun.cartesian_product_simple_transpose(arrays)
    ###k2h1tvanwziyg1 - infrastructure dams
    arrays = [keys_k2, keys_h1, keys_t1, keys_v1, keys_a, keys_n1, keys_lw1, keys_z, keys_i, keys_y1, keys_g1]
    index_k2h1tvanwziyg1 = fun.cartesian_product_simple_transpose(arrays)
    ###k3k5h1tvnw8ziaxyg3 - infrastructure offs
    arrays = [keys_k3, keys_k5, keys_h1, keys_t3, keys_v3, keys_n3, keys_lw3, keys_z, keys_i, keys_a, keys_x, keys_y3, keys_g3]
    index_k3k5h1tvnw8ziaxyg3 = fun.cartesian_product_simple_transpose(arrays)

    ###h1c - infrastructure
    arrays = [keys_h1, keys_c]
    index_h1c = fun.cartesian_product_simple_transpose(arrays)


    ################
    #create params #
    ################
    ##ravel and zip params with keys. This step removes 0's first using a mask because this saves considerable time.
    ##note need to do the tups each time even if same keys because the mask may be different
    ###nsire_sire
    mask=numbers_startp8_va1e1b1nwzida0e0b0xyg0p8!=0
    nsire_g0p8 = numbers_startp8_va1e1b1nwzida0e0b0xyg0p8[mask] #applying the mask does the raveling and squeezing of singleton axis
    mask=mask.ravel()
    index_cut_g0p8=index_g0p8[mask,:]
    tup_g0p8 = tuple(map(tuple, index_cut_g0p8))
    params['p_nsire_prov_sire'] =dict(zip(tup_g0p8, nsire_g0p8))
    ###nsire_dams
    mask=nsire_k2tva1e1b1nwzida0e0b0xyg1g0p8!=0
    nsire_k2tva1nw8ziyg1g0p8 = nsire_k2tva1e1b1nwzida0e0b0xyg1g0p8[mask] #applying the mask does the raveling and squeezing of singleton axis
    mask=mask.ravel()
    index_cut_k2tvanwziyg1g0p8=index_k2tvanwziyg1g0p8[mask,:]
    tup_k2tvanwziyg1g0p8 = tuple(map(tuple, index_cut_k2tvanwziyg1g0p8))
    params['p_nsire_req_dams'] =dict(zip(tup_k2tvanwziyg1g0p8, nsire_k2tva1nw8ziyg1g0p8))

    ###number prog weaned
    # mask=npw_k5tva1e1b1nwzida0e0b0xyg1w9i9!=0
    # npw_k5tva1nw8zidxyg1w9i9 = npw_k5tva1e1b1nwzida0e0b0xyg1w9i9[mask] #applying the mask does the raveling and squeezing of singleton axis
    # mask=mask.ravel()
    # index_cut_k5tva1nw8zidxyg1w9i9=index_k5tva1nw8zidxyg1w9i9[mask,:]
    # tup_k5tva1nw8zidxyg1w9i9 = tuple(map(tuple, index_cut_k5tva1nw8zidxyg1w9i9))
    # params['p_npw_dams'] =dict(zip(tup_k5tva1nw8zidxyg1w9i9, npw_k5tva1nw8zidxyg1w9i9))

    npw_k5tva1nw8zidxyg1w9i9 = np.array([])
    index_cut_k5tva1nw8zidxyg1w9i9 = np.array([])
    for k5 in range(len(keys_k5)):
        mask=npw_k5tva1e1b1nwzida0e0b0xyg1w9i9[k5,...]!=0
        npw_k5tva1nw8zidxyg1w9i9 = np.concatenate([npw_k5tva1nw8zidxyg1w9i9,npw_k5tva1e1b1nwzida0e0b0xyg1w9i9[k5,mask]],0) #applying the mask does the raveling and squeezing of singleton axis
        mask=mask.ravel()
        arrays = [keys_k5[k5:k5+1], keys_t1, keys_v1, keys_a, keys_n1, keys_lw1, keys_z, keys_i, keys_d, keys_x, keys_y1, keys_g1, keys_lw_prog, keys_i]
        index_tva1nw8zidxyg1w9i9 = fun.cartesian_product_simple_transpose(arrays)
        index_cut_k5tva1nw8zidxyg1w9i9 = np.vstack([index_cut_k5tva1nw8zidxyg1w9i9,index_tva1nw8zidxyg1w9i9[mask,:]]) if index_cut_k5tva1nw8zidxyg1w9i9.size else index_tva1nw8zidxyg1w9i9[mask,:]
    tup_k5tva1nw8zidxyg1w9i9 = tuple(map(tuple, index_cut_k5tva1nw8zidxyg1w9i9))
    params['p_npw_dams'] =dict(zip(tup_k5tva1nw8zidxyg1w9i9, npw_k5tva1nw8zidxyg1w9i9))

    ###npw required by prog activity
    mask=numbers_prog_req_tva1e1b1nwzida0e0b0xyg2w9!=0
    npw_tdxg = numbers_prog_req_tva1e1b1nwzida0e0b0xyg2w9[mask] #applying the mask does the raveling and squeezing of singleton axis
    mask=mask.ravel()
    index_cut_tdxg=index_tdxg[mask,:]
    tup_tdxg = tuple(map(tuple, index_cut_tdxg))
    params['p_npw_req_prog'] =dict(zip(tup_tdxg, npw_tdxg))

    ###number prog provided to dams
    mask=numbers_prog2dams_k3tva1e1b1nwzida0e0b0xyg2g9w9!=0
    progprov_dams_k3tw8zida0xyg2g9w9 = numbers_prog2dams_k3tva1e1b1nwzida0e0b0xyg2g9w9[mask] #applying the mask does the raveling and squeezing of singleton axis
    mask=mask.ravel()
    index_cut_k3tw8zida0xyg2g9w9=index_k3tw8zida0xyg2g9w9[mask,:]
    tup_k3tw8zida0xyg2g9w9 = tuple(map(tuple, index_cut_k3tw8zida0xyg2g9w9))
    params['p_progprov_dams'] =dict(zip(tup_k3tw8zida0xyg2g9w9, progprov_dams_k3tw8zida0xyg2g9w9))

    ###number prog require by dams
    mask=numbers_progreq_k2k3k5tva1e1b1nw8zida0e0b0xyg1g9w9!=0
    progreq_k2k3k5tw8ziyg1g9w9 = numbers_progreq_k2k3k5tva1e1b1nw8zida0e0b0xyg1g9w9[mask] #applying the mask does the raveling and squeezing of singleton axis
    mask=mask.ravel()
    index_cut_k2k3k5tw8ziyg1g9w9=index_k2k3k5tw8ziyg1g9w9[mask,:]
    tup_k2k3k5tw8ziyg1g9w9 = tuple(map(tuple, index_cut_k2k3k5tw8ziyg1g9w9))
    params['p_progreq_dams'] =dict(zip(tup_k2k3k5tw8ziyg1g9w9, progreq_k2k3k5tw8ziyg1g9w9))

    ###number prog provided to offs
    mask=numbers_prog2offs_k3k5tva1e1b1nwzida0e0b0xyg2w9!=0
    progprov_offs_k3k5tw8zidaxyg2w9 = numbers_prog2offs_k3k5tva1e1b1nwzida0e0b0xyg2w9[mask] #applying the mask does the raveling and squeezing of singleton axis
    mask=mask.ravel()
    index_cut_k3k5tw8zidaxyg2w9=index_k3k5tw8zidaxyg2w9[mask,:]
    tup_k3k5tw8zidaxyg2w9 = tuple(map(tuple, index_cut_k3k5tw8zidaxyg2w9))
    params['p_progprov_offs'] =dict(zip(tup_k3k5tw8zidaxyg2w9, progprov_offs_k3k5tw8zidaxyg2w9))

    ###number prog require by offs
    mask=numbers_progreq_va1e1b1nw8zida0e0b0xyg3w9!=0
    progreq_vw8ixw9 = numbers_progreq_va1e1b1nw8zida0e0b0xyg3w9[mask] #applying the mask does the raveling and squeezing of singleton axis
    mask=mask.ravel()
    index_cut_vw8ixw9=index_vw8ixw9[mask,:]
    tup_vw8ixw9 = tuple(map(tuple, index_cut_vw8ixw9))
    params['p_progreq_offs'] =dict(zip(tup_vw8ixw9, progreq_vw8ixw9))

    ###numbers_prov_dams
    ####numbers provided into next period (the norm)
    numbers_prov_dams_k2k2tva1nw8ziyg1g9w9 = np.array([])
    index_cut_k2k2tvanwziyg1g9w = np.array([])
    for w in range(len(keys_lw1)):
        mask=numbers_prov_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9[...,w]!=0
        numbers_prov_dams_k2k2tva1nw8ziyg1g9w9 = np.concatenate([numbers_prov_dams_k2k2tva1nw8ziyg1g9w9,numbers_prov_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9[mask,w]],0) #applying the mask does the raveling and squeezing of singleton axis
        mask=mask.ravel()
        arrays = [keys_k2, keys_k2, keys_t1, keys_v1, keys_a, keys_n1, keys_lw1, keys_z, keys_i, keys_y1, keys_g1, keys_g1, keys_lw1[w:w+1]]
        index_k2k2tvanwziyg1g9 = fun.cartesian_product_simple_transpose(arrays)
        index_cut_k2k2tvanwziyg1g9w = np.vstack([index_cut_k2k2tvanwziyg1g9w,index_k2k2tvanwziyg1g9[mask,:]]) if index_cut_k2k2tvanwziyg1g9w.size else index_k2k2tvanwziyg1g9[mask,:]
    tup_k2k2tvanwziyg1g9w = tuple(map(tuple, index_cut_k2k2tvanwziyg1g9w))
    params['p_numbers_prov_dams'] =dict(zip(tup_k2k2tvanwziyg1g9w, numbers_prov_dams_k2k2tva1nw8ziyg1g9w9))

    #### provided into this period (when transferring from an earlier lambing ram group to a later lambing)
    # mask=numbers_provthis_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9!=0
    # numbers_provthis_dams_k2k2tva1nw8ziyg1g9w9 = numbers_provthis_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9[mask] #applying the mask does the raveling and squeezing of singleton axis
    # mask=mask.ravel()
    # index_cut_k2k2tvanwziyg1g9w=index_k2k2tvanwziyg1g9w[mask,:]
    # tup_k2k2tvanwziyg1g9w = tuple(map(tuple, index_cut_k2k2tvanwziyg1g9w))
    # params['p_numbers_provthis_dams'] =dict(zip(tup_k2k2tvanwziyg1g9w, numbers_provthis_dams_k2k2tva1nw8ziyg1g9w9))

    numbers_provthis_dams_k2k2tva1nw8ziyg1g9w9 = np.array([])
    index_cut_k2k2tvanwziyg1g9w = np.array([])
    for w in range(len(keys_lw1)): #loop on w to reduce memory
        mask=numbers_provthis_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9[...,w]!=0
        numbers_provthis_dams_k2k2tva1nw8ziyg1g9w9 = np.concatenate([numbers_provthis_dams_k2k2tva1nw8ziyg1g9w9,numbers_provthis_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9[mask,w]],0) #applying the mask does the raveling and squeezing of singleton axis
        mask=mask.ravel()
        arrays = [keys_k2, keys_k2, keys_t1, keys_v1, keys_a, keys_n1, keys_lw1, keys_z, keys_i, keys_y1, keys_g1, keys_g1, keys_lw1[w:w+1]]
        index_k2k2tvanwziyg1g9 = fun.cartesian_product_simple_transpose(arrays)
        index_cut_k2k2tvanwziyg1g9w = np.vstack([index_cut_k2k2tvanwziyg1g9w,index_k2k2tvanwziyg1g9[mask,:]]) if index_cut_k2k2tvanwziyg1g9w.size else index_k2k2tvanwziyg1g9[mask,:]
    tup_k2k2tvanwziyg1g9w = tuple(map(tuple, index_cut_k2k2tvanwziyg1g9w))
    params['p_numbers_provthis_dams'] =dict(zip(tup_k2k2tvanwziyg1g9w, numbers_provthis_dams_k2k2tva1nw8ziyg1g9w9))


    ###numbers_prov_offs
    mask=numbers_prov_offs_k3k5tva1e1b1nw8zida0e0b0xygw9!=0
    numbers_prov_offs_k3k5tvnw8zia0xyg3w9 = numbers_prov_offs_k3k5tva1e1b1nw8zida0e0b0xygw9[mask] #applying the mask does the raveling and squeezing of singleton axis
    mask=mask.ravel()
    index_cut_k3k5tvnw8ziaxyg3w9=index_k3k5tvnw8ziaxyg3w9[mask,:]
    tup_k3k5tvnw8ziaxyg3w9 = tuple(map(tuple, index_cut_k3k5tvnw8ziaxyg3w9))
    params['p_numbers_prov_offs'] =dict(zip(tup_k3k5tvnw8ziaxyg3w9, numbers_prov_offs_k3k5tvnw8zia0xyg3w9))

    ###numbers_req_dams
    # mask=numbers_req_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9!=0
    # params['numbers_req_numpyversion_k2k2tva1nw8ziyg1g9w9'] = numbers_req_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9[:,:,:,:,:,0,0,:,:,:,:,0,0,0,0,0,:,:,:,:]  #cant use squeeze here because i need to keep all relevant axis even if singleton. this is used to speed pyomo constraint.
    # numbers_req_dams_k2k2tva1nw8ziyg1g9w9 = numbers_req_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9[mask] #applying the mask does the raveling and squeezing of singleton axis
    # mask=mask.ravel()
    # index_cut_k2k2tvanwziyg1g9w=index_k2k2tvanwziyg1g9w[mask,:]
    # tup_k2k2tvanwziyg1g9w = tuple(map(tuple, index_cut_k2k2tvanwziyg1g9w))
    # params['p_numbers_req_dams'] =dict(zip(tup_k2k2tvanwziyg1g9w, numbers_req_dams_k2k2tva1nw8ziyg1g9w9)) #same keys as prov so don't need to recalc again

    numbers_req_dams_k2k2tva1nw8ziyg1g9w9 = np.array([])
    index_cut_k2k2tvanwziyg1g9w = np.array([])
    params['numbers_req_numpyversion_k2k2tva1nw8ziyg1g9w9'] = numbers_req_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9[:,:,:,:,:,0,0,:,:,:,:,0,0,0,0,0,:,:,:,:]  #cant use squeeze here because i need to keep all relevant axis even if singleton. this is used to speed pyomo constraint.
    for w in range(len(keys_lw1)): #loop on w to reduce memory
        mask=numbers_req_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9[...,w]!=0
        numbers_req_dams_k2k2tva1nw8ziyg1g9w9 = np.concatenate([numbers_req_dams_k2k2tva1nw8ziyg1g9w9,numbers_req_dams_k28k29tva1e1b1nw8zida0e0b0xyg1g9w9[mask,w]],0) #applying the mask does the raveling and squeezing of singleton axis
        mask=mask.ravel()
        arrays = [keys_k2, keys_k2, keys_t1, keys_v1, keys_a, keys_n1, keys_lw1, keys_z, keys_i, keys_y1, keys_g1, keys_g1, keys_lw1[w:w+1]]
        index_k2k2tvanwziyg1g9 = fun.cartesian_product_simple_transpose(arrays)
        index_cut_k2k2tvanwziyg1g9w = np.vstack([index_cut_k2k2tvanwziyg1g9w,index_k2k2tvanwziyg1g9[mask,:]]) if index_cut_k2k2tvanwziyg1g9w.size else index_k2k2tvanwziyg1g9[mask,:]
    tup_k2k2tvanwziyg1g9w = tuple(map(tuple, index_cut_k2k2tvanwziyg1g9w))
    params['p_numbers_req_dams'] =dict(zip(tup_k2k2tvanwziyg1g9w, numbers_req_dams_k2k2tva1nw8ziyg1g9w9)) #same keys as prov so don't need to recalc again


    ###numbers_req_offs
    mask=numbers_req_offs_k3k5tva1e1b1nw8zida0e0b0xygw9!=0
    params['numbers_req_numpyversion_k3k5vw8ixg3w9'] = numbers_req_offs_k3k5tva1e1b1nw8zida0e0b0xygw9[:,:,0,:,0,0,0,0,:,0,:,0,0,0,0,:,0,:,:]  #cant use squeeze here because i need to keep all relevant axis even if singleton. this is used to speed pyomo constraint.
    numbers_req_offs_k3k5vw8ixg3w9 = numbers_req_offs_k3k5tva1e1b1nw8zida0e0b0xygw9[mask] #applying the mask does the raveling and squeezing of singleton axis
    mask=mask.ravel()
    index_cut_k3k5vw8ixg3w9=index_k3k5vw8ixg3w9[mask,:]
    tup_k3k5vw8ixg3w9 = tuple(map(tuple, index_cut_k3k5vw8ixg3w9))
    params['p_numbers_req_offs'] =dict(zip(tup_k3k5vw8ixg3w9, numbers_req_offs_k3k5vw8ixg3w9))

    ###mei - sire
    mask=mei_p6fa1e1b1nwzida0e0b0xyg0!=0
    mei_sire_p6fg0 = mei_p6fa1e1b1nwzida0e0b0xyg0[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_p6fg0=index_p6fg0[mask,:]
    tup_p6fg0 = tuple(map(tuple, index_cut_p6fg0))
    params['p_mei_sire'] =dict(zip(tup_p6fg0, mei_sire_p6fg0))
    ###mei - dams
    mask=mei_k2p6ftva1e1b1nwzida0e0b0xyg1!=0
    mei_dams_k2p6ftva1nw8ziyg1 = mei_k2p6ftva1e1b1nwzida0e0b0xyg1[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_k2p6ftva1nw8ziyg1=index_k2p6ftva1nw8ziyg1[mask,:]
    tup_k2p6ftva1nw8ziyg1 = tuple(map(tuple, index_cut_k2p6ftva1nw8ziyg1))
    params['p_mei_dams'] =dict(zip(tup_k2p6ftva1nw8ziyg1, mei_dams_k2p6ftva1nw8ziyg1))
    ###mei - offs
    mask=mei_k3k5p6ftva1e1b1nwzida0e0b0xyg3!=0
    mei_offs_k3k5p6ftvnw8ziaxyg3 = mei_k3k5p6ftva1e1b1nwzida0e0b0xyg3[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_k3k5p6ftvnw8ziaxyg3=index_k3k5p6ftvnw8ziaxyg3[mask,:]
    tup_k3k5p6ftvnw8ziaxyg3 = tuple(map(tuple, index_cut_k3k5p6ftvnw8ziaxyg3))
    params['p_mei_offs'] =dict(zip(tup_k3k5p6ftvnw8ziaxyg3, mei_offs_k3k5p6ftvnw8ziaxyg3))
    
    ###pi - sire
    mask=pi_p6fa1e1b1nwzida0e0b0xyg0!=0
    pi_sire_p6fg0 = pi_p6fa1e1b1nwzida0e0b0xyg0[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_p6fg0=index_p6fg0[mask,:]
    tup_p6fg0 = tuple(map(tuple, index_cut_p6fg0))
    params['p_pi_sire'] =dict(zip(tup_p6fg0, pi_sire_p6fg0))
    ###pi - dams
    mask=pi_k2p6ftva1e1b1nwzida0e0b0xyg1!=0
    pi_dams_k2p6ftva1nw8ziyg1 = pi_k2p6ftva1e1b1nwzida0e0b0xyg1[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_k2p6ftva1nw8ziyg1=index_k2p6ftva1nw8ziyg1[mask,:]
    tup_k2p6ftva1nw8ziyg1 = tuple(map(tuple, index_cut_k2p6ftva1nw8ziyg1))
    params['p_pi_dams'] =dict(zip(tup_k2p6ftva1nw8ziyg1, pi_dams_k2p6ftva1nw8ziyg1))
    ###pi - offs
    mask=pi_k3k5p6ftva1e1b1nwzida0e0b0xyg3!=0
    pi_offs_k3k5p6ftvnw8ziaxyg3 = pi_k3k5p6ftva1e1b1nwzida0e0b0xyg3[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_k3k5p6ftvnw8ziaxyg3=index_k3k5p6ftvnw8ziaxyg3[mask,:]
    tup_k3k5p6ftvnw8ziaxyg3 = tuple(map(tuple, index_cut_k3k5p6ftvnw8ziaxyg3))
    params['p_pi_offs'] =dict(zip(tup_k3k5p6ftvnw8ziaxyg3, pi_offs_k3k5p6ftvnw8ziaxyg3))
    
    ###cashflow - sire
    mask=cashflow_ctva1e1b1nwzida0e0b0xyg0!=0
    cashflow_sire_cg0 = cashflow_ctva1e1b1nwzida0e0b0xyg0[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_cg0=index_cg0[mask,:]
    tup_cg0 = tuple(map(tuple, index_cut_cg0))
    params['p_cashflow_sire'] =dict(zip(tup_cg0, cashflow_sire_cg0))
    ###cashflow - dams
    mask=cashflow_k2ctva1e1b1nwzida0e0b0xyg1!=0
    cashflow_dams_k2ctva1nw8ziyg = cashflow_k2ctva1e1b1nwzida0e0b0xyg1[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_k2ctvanwziyg1=index_k2ctvanwziyg1[mask,:]
    tup_k2ctvanwziyg1 = tuple(map(tuple, index_cut_k2ctvanwziyg1))
    params['p_cashflow_dams'] =dict(zip(tup_k2ctvanwziyg1, cashflow_dams_k2ctva1nw8ziyg))
    ###cashflow - prog - only consists of sale value
    mask=salevalue_prog_cta1e1b1nwzida0e0b0xyg2!=0
    cashflow_prog_ctwzia0xg2 = salevalue_prog_cta1e1b1nwzida0e0b0xyg2[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_ctwzia0xg2=index_ctwzia0xg2[mask,:]
    tup_ctwzia0xg2 = tuple(map(tuple, index_cut_ctwzia0xg2))
    params['p_cashflow_prog'] =dict(zip(tup_ctwzia0xg2, cashflow_prog_ctwzia0xg2))
    ###cashflow - offs
    mask=cashflow_k3k5ctva1e1b1nwzida0e0b0xyg3!=0
    cashflow_offs_k3k5ctvnw8ziaxyg3 = cashflow_k3k5ctva1e1b1nwzida0e0b0xyg3[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_k3k5ctvnw8ziaxyg3=index_k3k5ctvnw8ziaxyg3[mask,:]
    tup_k3k5ctvnw8ziaxyg3 = tuple(map(tuple, index_cut_k3k5ctvnw8ziaxyg3))
    params['p_cashflow_offs'] =dict(zip(tup_k3k5ctvnw8ziaxyg3, cashflow_offs_k3k5ctvnw8ziaxyg3))

    ###cost - sire
    mask=cost_tva1e1b1nwzida0e0b0xyg0!=0
    cost_sire_g0 = cost_tva1e1b1nwzida0e0b0xyg0[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_g0=index_g0[mask,:]
    tup_g0 = tuple(map(tuple, index_cut_g0))
    params['p_cost_sire'] =dict(zip(tup_g0, cost_sire_g0))
    ###cost - dams
    mask=cost_k2tva1e1b1nwzida0e0b0xyg1!=0
    cost_dams_k2tva1nw8ziyg = cost_k2tva1e1b1nwzida0e0b0xyg1[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_k2tvanwziyg1=index_k2tvanwziyg1[mask,:]
    tup_k2tvanwziyg1 = tuple(map(tuple, index_cut_k2tvanwziyg1))
    params['p_cost_dams'] =dict(zip(tup_k2tvanwziyg1, cost_dams_k2tva1nw8ziyg))
    ###cost - offs
    mask=cost_k3k5tva1e1b1nwzida0e0b0xyg3!=0
    cost_offs_k3k5tvnw8ziaxyg3 = cost_k3k5tva1e1b1nwzida0e0b0xyg3[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_k3k5tvnw8ziaxyg3=index_k3k5tvnw8ziaxyg3[mask,:]
    tup_k3k5tvnw8ziaxyg3 = tuple(map(tuple, index_cut_k3k5tvnw8ziaxyg3))
    params['p_cost_offs'] =dict(zip(tup_k3k5tvnw8ziaxyg3, cost_offs_k3k5tvnw8ziaxyg3))

    ###purchcost - sire
    mask=purchcost_cva1e1b1nwzida0e0b0xyg0!=0
    purchcost_sire_cg0 = purchcost_cva1e1b1nwzida0e0b0xyg0[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_cg0=index_cg0[mask,:]
    tup_cg0 = tuple(map(tuple, index_cut_cg0))
    params['p_purchcost_sire'] =dict(zip(tup_cg0, purchcost_sire_cg0))

    ###infra r&m cost
    tup_h1c = tuple(map(tuple,index_h1c))
    params['p_rm_stockinfra_var'] = dict(zip(tup_h1c, rm_stockinfra_var_h1c.ravel()))
    params['p_rm_stockinfra_fix'] = dict(zip(tup_h1c,rm_stockinfra_fix_h1c.ravel()))


    ###assetvalue - sire
    mask=assetvalue_va1e1b1nwzida0e0b0xyg0!=0
    assetvalue_sire_g0 = assetvalue_va1e1b1nwzida0e0b0xyg0[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_g0=index_g0[mask,:]
    tup_g0 = tuple(map(tuple, index_cut_g0))
    params['p_assetvalue_sire'] =dict(zip(tup_g0, assetvalue_sire_g0))
    ###assetvalue - dams
    mask=assetvalue_k2tva1e1b1nwzida0e0b0xyg1!=0
    assetvalue_dams_k2tva1nw8ziyg = assetvalue_k2tva1e1b1nwzida0e0b0xyg1[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_k2tvanwziyg1=index_k2tvanwziyg1[mask,:]
    tup_k2tvanwziyg1 = tuple(map(tuple, index_cut_k2tvanwziyg1))
    params['p_assetvalue_dams'] =dict(zip(tup_k2tvanwziyg1, assetvalue_dams_k2tva1nw8ziyg))
    ###assetvalue - offs
    mask=assetvalue_k3k5tva1e1b1nwzida0e0b0xyg3!=0
    assetvalue_offs_k3k5tvnw8ziaxyg3 = assetvalue_k3k5tva1e1b1nwzida0e0b0xyg3[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_k3k5tvnw8ziaxyg3=index_k3k5tvnw8ziaxyg3[mask,:]
    tup_k3k5tvnw8ziaxyg3 = tuple(map(tuple, index_cut_k3k5tvnw8ziaxyg3))
    params['p_assetvalue_offs'] =dict(zip(tup_k3k5tvnw8ziaxyg3, assetvalue_offs_k3k5tvnw8ziaxyg3))

    ##asset value infra
    params['p_infra'] = dict(zip(keys_h1, assetvalue_infra_h1))

    ###anyone labour - sire
    mask=lab_anyone_p5tva1e1b1nwzida0e0b0xyg0!=0
    lab_any_sire_p5g0 = lab_anyone_p5tva1e1b1nwzida0e0b0xyg0[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_p5g0=index_p5g0[mask,:]
    tup_p5g0 = tuple(map(tuple, index_cut_p5g0))
    params['p_labour_anyone_sire'] =dict(zip(tup_p5g0, lab_any_sire_p5g0))
    ###perm labour - sire
    mask=lab_perm_p5tva1e1b1nwzida0e0b0xyg0!=0
    lab_perm_sire_p5g0 = lab_perm_p5tva1e1b1nwzida0e0b0xyg0[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_p5g0=index_p5g0[mask,:]
    tup_p5g0 = tuple(map(tuple, index_cut_p5g0))
    params['p_labour_perm_sire'] =dict(zip(tup_p5g0, lab_perm_sire_p5g0))
    ###manager labour - sire
    mask=lab_manager_p5tva1e1b1nwzida0e0b0xyg0!=0
    lab_manager_sire_p5g0 = lab_manager_p5tva1e1b1nwzida0e0b0xyg0[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_p5g0=index_p5g0[mask,:]
    tup_p5g0 = tuple(map(tuple, index_cut_p5g0))
    params['p_labour_manager_sire'] =dict(zip(tup_p5g0, lab_manager_sire_p5g0))
    
    ###anyone labour - dams
    mask=lab_anyone_k2p5tva1e1b1nwzida0e0b0xyg1!=0
    lab_any_dams_k2p5tva1nw8ziyg = lab_anyone_k2p5tva1e1b1nwzida0e0b0xyg1[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_k2p5tvanwziyg1=index_k2p5tvanwziyg1[mask,:]
    tup_k2p5tvanwziyg1 = tuple(map(tuple, index_cut_k2p5tvanwziyg1))
    params['p_labour_anyone_dams'] =dict(zip(tup_k2p5tvanwziyg1, lab_any_dams_k2p5tva1nw8ziyg))
    ###perm labour - dams
    mask=lab_perm_k2p5tva1e1b1nwzida0e0b0xyg1!=0
    lab_perm_dams_k2p5tva1nw8ziyg = lab_perm_k2p5tva1e1b1nwzida0e0b0xyg1[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_k2p5tvanwziyg1=index_k2p5tvanwziyg1[mask,:]
    tup_k2p5tvanwziyg1 = tuple(map(tuple, index_cut_k2p5tvanwziyg1))
    params['p_labour_perm_dams'] =dict(zip(tup_k2p5tvanwziyg1, lab_perm_dams_k2p5tva1nw8ziyg))
    ###manager labour - dams
    mask=lab_manager_k2p5tva1e1b1nwzida0e0b0xyg1!=0
    lab_manager_dams_k2p5tva1nw8ziyg = lab_manager_k2p5tva1e1b1nwzida0e0b0xyg1[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_k2p5tvanwziyg1=index_k2p5tvanwziyg1[mask,:]
    tup_k2p5tvanwziyg1 = tuple(map(tuple, index_cut_k2p5tvanwziyg1))
    params['p_labour_manager_dams'] =dict(zip(tup_k2p5tvanwziyg1, lab_manager_dams_k2p5tva1nw8ziyg))

    ###anyone labour - offs
    mask=lab_anyone_k3k5p5tva1e1b1nwzida0e0b0xyg3!=0
    lab_any_offs_k3k5p5tvnw8ziaxyg3 = lab_anyone_k3k5p5tva1e1b1nwzida0e0b0xyg3[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_k3k5p5tvnw8ziaxyg3=index_k3k5p5tvnw8ziaxyg3[mask,:]
    tup_k3k5p5tvnw8ziaxyg3 = tuple(map(tuple, index_cut_k3k5p5tvnw8ziaxyg3))
    params['p_labour_anyone_offs'] =dict(zip(tup_k3k5p5tvnw8ziaxyg3, lab_any_offs_k3k5p5tvnw8ziaxyg3))
    ###perm labour - offs
    mask=lab_perm_k3k5p5tva1e1b1nwzida0e0b0xyg3!=0
    lab_perm_offs_k3k5p5tvnw8ziaxyg3 = lab_perm_k3k5p5tva1e1b1nwzida0e0b0xyg3[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_k3k5p5tvnw8ziaxyg3=index_k3k5p5tvnw8ziaxyg3[mask,:]
    tup_k3k5p5tvnw8ziaxyg3 = tuple(map(tuple, index_cut_k3k5p5tvnw8ziaxyg3))
    params['p_labour_perm_offs'] =dict(zip(tup_k3k5p5tvnw8ziaxyg3, lab_perm_offs_k3k5p5tvnw8ziaxyg3))
    ###manager labour - offs
    mask=lab_manager_k3k5p5tva1e1b1nwzida0e0b0xyg3!=0
    lab_manager_offs_k3k5p5tvnw8ziaxyg3 = lab_manager_k3k5p5tva1e1b1nwzida0e0b0xyg3[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_k3k5p5tvnw8ziaxyg3=index_k3k5p5tvnw8ziaxyg3[mask,:]
    tup_k3k5p5tvnw8ziaxyg3 = tuple(map(tuple, index_cut_k3k5p5tvnw8ziaxyg3))
    params['p_labour_manager_offs'] =dict(zip(tup_k3k5p5tvnw8ziaxyg3, lab_manager_offs_k3k5p5tvnw8ziaxyg3))
    
    ###infrastructure - sire
    mask=infrastructure_h1va1e1b1nwzida0e0b0xyg0!=0
    infrastructure_sire_h1g0 = infrastructure_h1va1e1b1nwzida0e0b0xyg0[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_h1g0=index_h1g0[mask,:]
    tup_h1g0 = tuple(map(tuple, index_cut_h1g0))
    params['p_infrastructure_sire'] =dict(zip(tup_h1g0, infrastructure_sire_h1g0))
    ###infrastructure - dams
    mask=infrastructure_k2h1tva1e1b1nwzida0e0b0xyg1!=0
    infrastructure_dams_k2h1tva1nw8ziyg = infrastructure_k2h1tva1e1b1nwzida0e0b0xyg1[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_k2h1tvanwziyg1=index_k2h1tvanwziyg1[mask,:]
    tup_k2h1tvanwziyg1 = tuple(map(tuple, index_cut_k2h1tvanwziyg1))
    params['p_infrastructure_dams'] =dict(zip(tup_k2h1tvanwziyg1, infrastructure_dams_k2h1tva1nw8ziyg))
    ###infrastructure - offs
    mask=infrastructure_k3k5p5tva1e1b1nwzida0e0b0xyg3!=0
    infrastructure_offs_k3k5h1tvnw8ziaxyg3 = infrastructure_k3k5p5tva1e1b1nwzida0e0b0xyg3[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_k3k5h1tvnw8ziaxyg3=index_k3k5h1tvnw8ziaxyg3[mask,:]
    tup_k3k5h1tvnw8ziaxyg3 = tuple(map(tuple, index_cut_k3k5h1tvnw8ziaxyg3))
    params['p_infrastructure_offs'] =dict(zip(tup_k3k5h1tvnw8ziaxyg3, infrastructure_offs_k3k5h1tvnw8ziaxyg3))

    ##DSE - sire
    mask=dsemj_p6tva1e1b1nwzida0e0b0xyg0!=0
    dsemj_sire_p6g0 = dsemj_p6tva1e1b1nwzida0e0b0xyg0[mask] #applying the mask does the raveling and squeezing of array
    dsenw_sire_p6g0 = dsenw_p6tva1e1b1nwzida0e0b0xyg0[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_p6g0=index_p6g0[mask,:]
    tup_p6g0 = tuple(map(tuple, index_cut_p6g0))
    if pinp.sheep['i_dse_type'] == 0:
        params['p_dse_sire'] =dict(zip(tup_p6g0, dsemj_sire_p6g0))
    else:
        params['p_dse_sire'] =dict(zip(tup_p6g0, dsenw_sire_p6g0))
    ##DSE - dams
    mask=dsemj_k2p6tva1e1b1nwzida0e0b0xyg1!=0
    dsemj_dams_k2p6tva1nw8ziyg1 = dsemj_k2p6tva1e1b1nwzida0e0b0xyg1[mask] #applying the mask does the raveling and squeezing of array
    dsenw_dams_k2p6tva1nw8ziyg1 = dsenw_k2p6tva1e1b1nwzida0e0b0xyg1[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_k2p6tva1nw8ziyg1=index_k2p6tva1nw8ziyg1[mask,:]
    tup_k2p6tva1nw8ziyg1 = tuple(map(tuple, index_cut_k2p6tva1nw8ziyg1))
    if pinp.sheep['i_dse_type'] == 0:
        params['p_dse_dams'] =dict(zip(tup_k2p6tva1nw8ziyg1, dsemj_dams_k2p6tva1nw8ziyg1))
    else:
        params['p_dse_dams'] =dict(zip(tup_k2p6tva1nw8ziyg1, dsenw_dams_k2p6tva1nw8ziyg1))
    ##DSE - dams
    mask=dsemj_k3k5p6tva1e1b1nwzida0e0b0xyg3!=0
    dsemj_dams_k3k5p6tvnw8ziaxyg3 = dsemj_k3k5p6tva1e1b1nwzida0e0b0xyg3[mask] #applying the mask does the raveling and squeezing of array
    dsenw_dams_k3k5p6tvnw8ziaxyg3 = dsenw_k3k5p6tva1e1b1nwzida0e0b0xyg3[mask] #applying the mask does the raveling and squeezing of array
    mask=mask.ravel()
    index_cut_k3k5p6tvnw8ziaxyg3=index_k3k5p6tvnw8ziaxyg3[mask,:]
    tup_k3k5p6tvnw8ziaxyg3 = tuple(map(tuple, index_cut_k3k5p6tvnw8ziaxyg3))
    if pinp.sheep['i_dse_type'] == 0:
        params['p_dse_offs'] =dict(zip(tup_k3k5p6tvnw8ziaxyg3, dsemj_dams_k3k5p6tvnw8ziaxyg3))
    else:
        params['p_dse_offs'] =dict(zip(tup_k3k5p6tvnw8ziaxyg3, dsenw_dams_k3k5p6tvnw8ziaxyg3))





    ###############
    # report      #
    ###############
    '''add report values to report dict and do any additional calculations'''

    ##store in report dict
    ###keys
    r_vals['keys_a'] = keys_a
    r_vals['keys_d'] = keys_d
    r_vals['keys_g0'] = keys_g0
    r_vals['keys_g1'] = keys_g1
    r_vals['keys_g2'] = keys_g2
    r_vals['keys_g3'] = keys_g3
    r_vals['keys_f'] = keys_f
    r_vals['keys_h1'] = keys_h1
    r_vals['keys_i'] = keys_i
    r_vals['keys_k2'] = keys_k2
    r_vals['keys_k3'] = keys_k3
    r_vals['keys_k5'] = keys_k5
    r_vals['keys_lw1'] = keys_lw1
    r_vals['keys_lw3'] = keys_lw3
    r_vals['keys_lw_prog'] = keys_lw_prog
    r_vals['keys_n1'] = keys_n1
    r_vals['keys_n3'] = keys_n3
    r_vals['keys_p8'] = keys_p8
    r_vals['keys_t1'] = keys_t1
    r_vals['keys_t2'] = keys_t2
    r_vals['keys_t3'] = keys_t3
    r_vals['keys_v1'] = keys_v1
    r_vals['keys_v3'] = keys_v3
    r_vals['keys_y0'] = keys_y0
    r_vals['keys_y1'] = keys_y1
    r_vals['keys_y3'] = keys_y3
    r_vals['keys_x'] = keys_x
    r_vals['keys_z'] = keys_z
    r_vals['keys_p6'] = keys_p6

    ##key lists used to form table headers and indexs
    keys_e = ['e%s'%i for i in range(len_e1)]
    keys_b = uinp.structure['i_lsln_idx_dams']
    keys_b9 = uinp.structure['i_lsln_idx_dams'][1:5]
    keys_p = ['p%s'%i for i in range(len_p)]

    r_vals['sire_keys_g0'] = [keys_g0]
    r_vals['sire_keys_p6fg0'] = [keys_p6, keys_f, keys_g0]
    r_vals['dams_keys_tvanwziy1g1'] = [keys_t1, keys_v1, keys_a, keys_n1, keys_lw1, keys_z, keys_i,
                                             keys_y1, keys_g1]
    r_vals['dams_keys_k2tvanwziy1g1'] = [keys_k2, keys_t1, keys_v1, keys_a, keys_n1, keys_lw1, keys_z, keys_i,
                                             keys_y1, keys_g1]
    r_vals['dams_keys_k2tvaeb9nwziy1g1'] = [keys_k2, keys_t1, keys_v1, keys_a, keys_e, keys_b9, keys_n1, keys_lw1, keys_z, keys_i,
                                             keys_y1, keys_g1]
    r_vals['dams_keys_k2tvpaebnwziy1g1'] = [keys_k2, keys_t1, keys_v1, keys_p, keys_a, keys_e, keys_b, keys_n1, keys_lw1, keys_z, keys_i,
                                             keys_y1, keys_g1]
    r_vals['dams_keys_k2p6ftvanwziy1g1'] = [keys_k2, keys_p6, keys_f, keys_t1, keys_v1, keys_a, keys_n1, keys_lw1,
                                                keys_z, keys_i, keys_y1, keys_g1]
    r_vals['offs_keys_k3k5tvnwziaxyg3'] = [keys_k3, keys_k5, keys_t3, keys_v3, keys_n3, keys_lw3, keys_z, keys_i,
                                               keys_a, keys_x, keys_y3, keys_g3]
    r_vals['offs_keys_k3k5p6ftvnwziaxyg3'] = [keys_k3, keys_k5, keys_p6, keys_f, keys_t3, keys_v3, keys_n3,
                                                  keys_lw3, keys_z, keys_i, keys_a, keys_x, keys_y3, keys_g3]

    ###shapes
    len_v1 = len(keys_v1)
    len_v3 = len(keys_v3)
    ####std
    g0_shape = len_g0
    k2tva1nwziyg1_shape = len_k2, len_t1, len_v1, len_a1, len_n1, len_w1, len_z, len_i, len_y1, len_g1
    k5twzidaxyg2_shape = len_k5, len_t2, len_w_prog, len_z, len_i, len_d, len_a1, len_x, len_g2
    k3k5tvnwziaxyg3_shape = len_k3, len_k5, len_t3, len_v3, len_n3, len_w3, len_z, len_i, len_a0, len_x, len_y3, len_g3

    ####kveb
    k2tva1e1b1nwziyg1_shape = len_k2, len_t1, len_v1, len_a1, len_e1, len_b1, len_n1, len_w1, len_z, len_i, len_y1, len_g1

    ####kpveb
    pg0_shape = len_p, len_g0
    k2vpa1e1b1nwziyg1_shape = len_k2, len_v1, len_p, len_a1, len_e1, len_b1, len_n1, len_w1, len_z, len_i, len_y1, len_g1
    k3k5vpnwzidae0b0xyg3_shape = len_k3, len_k5, len_v3, len_p3, len_n3, len_w3, len_z, len_i, len_d, len_a0, len_e0, len_b0, len_x, len_y3, len_g3

    ####p6
    p6g0_shape = len_p6, len_g0
    k2p6tva1nwziyg1_shape = len_k2, len_p6, len_t1, len_v1, len_a1, len_n1, len_w1, len_z, len_i, len_y1, len_g1
    k3k5p6tvnwziaxyg3_shape = len_k3, len_k5, len_p6, len_t3, len_v3, len_n3, len_w3, len_z, len_i, len_a0, len_x, len_y3, len_g3

    ####p6f
    p6fg0_shape = len_p6, len_f, len_g0
    k2p6ftva1nwziyg1_shape = len_k2, len_p6, len_f, len_t1, len_v1, len_a1, len_n1, len_w1, len_z, len_i, len_y1, len_g1
    k3k5p6ftvnwziaxyg3_shape = len_k3, len_k5, len_p6, len_f, len_t3, len_v3, len_n3, len_w3, len_z, len_i, len_a0, len_x, len_y3, len_g3

    cg0_shape = len_c, len_g0
    k2ctva1nwziyg1_shape = len_k2, len_c, len_t1, len_v1, len_a1, len_n1, len_w1, len_z, len_i, len_y1, len_g1
    k5ctwziaxyg2_shape = len_c, len_t2, len_w_prog, len_z, len_i, len_a1, len_x, len_g2
    k3k5ctvnwziaxyg3_shape = len_k3, len_k5, len_c, len_t3, len_v3, len_n3, len_w3, len_z, len_i, len_a0, len_x, len_y3, len_g3



    ###dse
    r_vals['dsenw_p6g0'] = dsenw_p6tva1e1b1nwzida0e0b0xyg0.reshape(p6g0_shape)
    r_vals['dsemj_p6g0'] = dsemj_p6tva1e1b1nwzida0e0b0xyg0.reshape(p6g0_shape)
    r_vals['dsenw_k2p6tva1nwziyg1'] = dsenw_k2p6tva1e1b1nwzida0e0b0xyg1.reshape(k2p6tva1nwziyg1_shape)
    r_vals['dsemj_k2p6tva1nwziyg1'] = dsemj_k2p6tva1e1b1nwzida0e0b0xyg1.reshape(k2p6tva1nwziyg1_shape)
    r_vals['dsenw_k3k5p6tvnwziaxyg3'] = dsenw_k3k5p6tva1e1b1nwzida0e0b0xyg3.reshape(k3k5p6tvnwziaxyg3_shape)
    r_vals['dsemj_k3k5p6tvnwziaxyg3'] = dsemj_k3k5p6tva1e1b1nwzida0e0b0xyg3.reshape(k3k5p6tvnwziaxyg3_shape)

    ###stock days
    r_vals['stock_days_p6fg0'] = stock_days_p6fa1e1b1nwzida0e0b0xyg0.reshape(p6fg0_shape)
    r_vals['stock_days_k2p6ftva1nwziyg1'] = stock_days_k2p6ftva1e1b1nwzida0e0b0xyg1.reshape(k2p6ftva1nwziyg1_shape)
    r_vals['stock_days_k3k5p6ftvnwziaxyg3'] = stock_days_k3k5p6ftva1e1b1nwzida0e0b0xyg3.reshape(k3k5p6ftvnwziaxyg3_shape)

    ###cashflow
    r_vals['sire_cost_cg0'] = cost_ctva1e1b1nwzida0e0b0xyg0.reshape(cg0_shape)
    r_vals['dams_cost_k2ctva1nwziyg1'] = cost_k2ctva1e1b1nwzida0e0b0xyg1.reshape(k2ctva1nwziyg1_shape)
    r_vals['offs_cost_k3k5ctvnwziaxyg3'] =cost_k3k5ctva1e1b1nwzida0e0b0xyg3.reshape(k3k5ctvnwziaxyg3_shape)

    r_vals['salevalue_cg0'] = r_salevalue_ctva1e1b1nwzida0e0b0xyg0.reshape(cg0_shape)
    r_vals['salevalue_k2ctva1nwziyg1'] = r_salevalue_k2ctva1e1b1nwzida0e0b0xyg1.reshape(k2ctva1nwziyg1_shape)
    r_vals['salevalue_ctwzia0xg2'] = salevalue_prog_cta1e1b1nwzida0e0b0xyg2.reshape(k5ctwziaxyg2_shape)
    r_vals['salevalue_k3k5ctvnwziaxyg3'] = r_salevalue_k3k5ctva1e1b1nwzida0e0b0xyg3.reshape(k3k5ctvnwziaxyg3_shape)

    r_vals['woolvalue_cg0'] = r_woolvalue_ctva1e1b1nwzida0e0b0xyg0.reshape(cg0_shape)
    r_vals['woolvalue_k2ctva1nwziyg1'] = r_woolvalue_k2ctva1e1b1nwzida0e0b0xyg1.reshape(k2ctva1nwziyg1_shape)
    r_vals['woolvalue_k3k5ctvnwziaxyg3'] =r_woolvalue_k3k5ctva1e1b1nwzida0e0b0xyg3.reshape(k3k5ctvnwziaxyg3_shape)

    ###cfw
    r_vals['cfw_hdmob_g0'] = r_cfw_hdmob_tva1e1b1nwzida0e0b0xyg0.reshape(g0_shape)
    r_vals['cfw_hdmob_k2tva1nwziyg1'] = r_cfw_hdmob_k2tva1e1b1nwzida0e0b0xyg1.reshape(k2tva1nwziyg1_shape)
    r_vals['cfw_hdmob_k3k5tvnwziaxyg3'] = r_cfw_hdmob_k3k5tva1e1b1nwzida0e0b0xyg3.reshape(k3k5tvnwziaxyg3_shape)

    r_vals['cfw_hd_g0'] = r_cfw_hd_tva1e1b1nwzida0e0b0xyg0.reshape(g0_shape)
    r_vals['cfw_hd_k2tva1nwziyg1'] = r_cfw_hd_k2tva1e1b1nwzida0e0b0xyg1.reshape(k2tva1nwziyg1_shape)
    r_vals['cfw_hd_k3k5tvnwziaxyg3'] = r_cfw_hd_k3k5tva1e1b1nwzida0e0b0xyg3.reshape(k3k5tvnwziaxyg3_shape)

    ###mei and pi and fec (feed energy concentration)
    r_vals['mei_sire_p6fg0'] = mei_p6fa1e1b1nwzida0e0b0xyg0.reshape(p6fg0_shape)
    r_vals['mei_dams_k2p6ftva1nw8ziyg1'] = mei_k2p6ftva1e1b1nwzida0e0b0xyg1.reshape(k2p6ftva1nwziyg1_shape)
    r_vals['mei_offs_k3k5p6ftvnw8ziaxyg3'] = mei_k3k5p6ftva1e1b1nwzida0e0b0xyg3.reshape(k3k5p6ftvnwziaxyg3_shape)

    r_vals['pi_sire_p6fg0'] = pi_p6fa1e1b1nwzida0e0b0xyg0.reshape(p6fg0_shape)
    r_vals['pi_dams_k2p6ftva1nw8ziyg1'] = pi_k2p6ftva1e1b1nwzida0e0b0xyg1.reshape(k2p6ftva1nwziyg1_shape)
    r_vals['pi_offs_k3k5p6ftvnw8ziaxyg3'] = pi_k3k5p6ftva1e1b1nwzida0e0b0xyg3.reshape(k3k5p6ftvnwziaxyg3_shape)


    ###number of foetuses scanned per dam at beginning of the period (eg accounts for mortality)
    r_vals['nfoet_scan_tva1nw8ziyg1'] = r_nfoet_scan_tva1e1b1nwzida0e0b0xyg1.reshape(k2tva1nwziyg1_shape[1:])

    ###wean percent
    r_vals['nyatf_wean_tva1nw8ziyg1'] = r_nyatf_wean_tva1e1b1nwzida0e0b0xyg1.reshape(k2tva1nwziyg1_shape[1:])

    ###nfoet and nyatf used to calc lamb survival and mortality
    r_vals['nfoet_birth_k2tva1e1b1nw8ziyg1'] = r_nfoet_birth_k2tva1e1b1nwzida0e0b0xyg1.reshape(k2tva1e1b1nwziyg1_shape)
    r_vals['nyatf_birth_k2tva1e1b1nw8ziyg1'] = r_nyatf_birth_k2tva1e1b1nwzida0e0b0xyg1.reshape(k2tva1e1b1nwziyg1_shape)
    # r_vals['prog_born_k2tva1e1b1nw8ziyg1'] = r_prog_born_k2tva1e1b1nwzida0e0b0xyg1.reshape(k2tva1e1b1nwziyg1_shape)
    # r_vals['prog_alive_k2tva1e1b1nw8ziyg1'] = r_prog_alive_k2tva1e1b1nwzida0e0b0xyg1.reshape(k2tva1e1b1nwziyg1_shape)
    index_b9 = [0,1,2,3]
    nfoet_b1nwzida0e0b0xygb9 = nfoet_b1nwzida0e0b0xyg[...,na] == index_b9
    nyatf_b1nwzida0e0b0xygb9 = nyatf_b1nwzida0e0b0xyg[...,na] == index_b9
    r_vals['mask_b1b9_preg_b1nwziygb9'] = nfoet_b1nwzida0e0b0xygb9.squeeze(axis=(d_pos-1, a0_pos-1, e0_pos-1, b0_pos-1, x_pos-1))

    ###denom weights for arrays that keep axis that are not present in lp array.
    r_vals['pe1b1_denom_weights_k2tvpa1e1b1nw8ziyg1'] = ((a_v_pa1e1b1nwzida0e0b0xyg1 == index_vpa1e1b1nwzida0e0b0xyg1)
    *(a_k2cluster_va1e1b1nwzida0e0b0xyg1[:,na,...] == index_k2tva1e1b1nwzida0e0b0xyg1[:,:,:,na,...])).squeeze(axis=(d_pos, a0_pos, e0_pos, b0_pos, x_pos))

    r_vals['pde0b0_denom_weights_k3k5tvpnw8zida0e0b0xyg3'] = ((a_v_pa1e1b1nwzida0e0b0xyg3 == index_vpa1e1b1nwzida0e0b0xyg3)
                                                        *(a_k3cluster_da0e0b0xyg3 == index_k3k5tva1e1b1nwzida0e0b0xyg3[:,:,:,:,na,...])
                                                        *(a_k5cluster_da0e0b0xyg3 == index_k5tva1e1b1nwzida0e0b0xyg3[:,:,:,na,...])).squeeze(axis=(a1_pos, e1_pos, b1_pos))

    r_vals['e1b1_denom_weights_k2tva1e1b1nw8ziyg1'] = (a_k2cluster_va1e1b1nwzida0e0b0xyg1 == index_k2tva1e1b1nwzida0e0b0xyg1).squeeze(axis=(d_pos, a0_pos, e0_pos, b0_pos, x_pos))

    r_vals['de0b0_denom_weights_k3k5tvnw8zida0e0b0xyg3'] = ((a_k3cluster_da0e0b0xyg3 == index_k3k5tva1e1b1nwzida0e0b0xyg3)
                                                        *(a_k5cluster_da0e0b0xyg3 == index_k5tva1e1b1nwzida0e0b0xyg3)).squeeze(axis=(a1_pos, e1_pos, b1_pos))

    ###lw - with p, e, b
    if pinp.rep['i_store_lw_rep']:
        r_vals['lw_sire_pg0'] = r_lw_sire_pg.reshape(pg0_shape)
        r_vals['lw_dams_k2vpa1e1b1nw8ziyg1'] = r_lw_dams_k2tvpg.reshape(k2vpa1e1b1nwziyg1_shape)
        r_vals['lw_offs_k3k5vpnw8zida0e0b0xyg3'] = r_lw_offs_k3k5tvpg.reshape(k3k5vpnwzidae0b0xyg3_shape)

    ###fec - with p, e, b
    if pinp.rep['i_store_fec_rep']:
        r_vals['fec_sire_pg0'] = r_fec_sire_pg.reshape(pg0_shape)
        r_vals['fec_dams_k2vpa1e1b1nw8ziyg1'] = r_fec_dams_k2tvpg.reshape(k2vpa1e1b1nwziyg1_shape)
        r_vals['fec_offs_k3k5vpnw8zida0e0b0xyg3'] = r_fec_offs_k3k5tvpg.reshape(k3k5vpnwzidae0b0xyg3_shape)



    finish = time.time()
    # print('onhand and shearing arrays: ',calc_cost_start - onhandshear_start)
    # print('wool value calcs :', wool_finish - calc_cost_start)
    # print('sale value calcs :', sale_finish - wool_finish)
    # print('husb cost calcs :', husb_finish - sale_finish)
    print('calc cost and income: ',feedpools_start - calc_cost_start)
    # print('feed pools arrays: ',p2v_start - feedpools_start)
    # print('p2v: ',lwdist_start - p2v_start)
    # print('lw distribution: ',cluster_start - lwdist_start)
    # print('clustering: ',allocation_start - cluster_start)
    # print('allocation: ',production_param_start - allocation_start)
    print('p2v and building masks: ',lwdist_start - p2v_start)
    print('production params: ', number_param_start - production_param_start)
    print('number params: ', keys_start - number_param_start)
    print('convert numpy to pyomo dict and reporting: ',finish - keys_start)

    ## Call Steve's graph generator.
    ## Will be bypassed unless called from SheepTest.py or line below is uncommented
    if plots:
        print('Interact with the graph generator using the PlotViewer spreadsheet')
    scan_spreadsheet = plots   # argument passed to the StockGen function. True if called from SheepTest
    #    scan_spreadsheet = True    #make line active to generate plots when called from exp.py
    while scan_spreadsheet:
        try:
            yvar1, yvar2, xlabels, wvar, xvar, axes, dimensions, verticals = pv.read_spreadsheet()
            loc = locals()
            yvar1 = loc[yvar1]
            yvar2 = loc[yvar2]
            xlabels = loc[xlabels]
            wvar = loc[wvar]
            xvar = loc[xvar]
            pv.create_plots(yvar1, yvar2, xlabels, wvar, xvar, axes, dimensions, verticals)
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            scan_spreadsheet = input("Enter 1 to rescan spreadsheet for new plots: ")

    print('end of generator')   # a line that can be used to break at the end of the generator
