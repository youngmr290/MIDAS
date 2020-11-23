# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 16:03:35 2020

@author: John
"""

#python modules
import pyomo.environ as pe
import time
from io import StringIO
import numpy as np

#MUDAS modules
from CreateModel import model
import StockGenerator as sgen


def stock_precalcs(params, report):
    sgen.generator(params, report)



def stockpyomo_local(params):

    ##these sets require info from the stock module
    model.s_wean_times = pe.Set(initialize=params['a_idx'], doc='weaning options')
    model.s_tol = pe.Set(initialize=params['i_idx'], doc='birth groups (times of lambing)')
    model.s_sire_periods = pe.Set(initialize=params['p8_idx'], doc='sire periods')
    model.s_groups_sire = pe.Set(initialize=params['g_idx_sire'], doc='geneotype groups of sires')
    model.s_gen_merit_sire = pe.Set(initialize=params['y_idx_sire'], doc='genetic merit of sires')
    model.s_k2_birth_dams = pe.Set(initialize=params['k2_idx_dams'], doc='Cluster for LSLN & oestrus cycle based on scanning, global & weaning management')
    model.s_dvp_dams = pe.Set(ordered=True, initialize=params['dvp_idx_dams'], doc='Decision variable periods for dams') #ordered so they can be indexed in constraint to determine previous period
    model.s_groups_dams = pe.Set(initialize=params['g_idx_dams'], doc='geneotype groups of dams')
    model.s_groups_prog = pe.Set(initialize=params['g_idx_dams'], doc='geneotype groups of prog') #same as dams and offs
    model.s_gen_merit_dams = pe.Set(initialize=params['y_idx_dams'], doc='genetic merit of dams')
    model.s_sale_dams = pe.Set(initialize=params['t_idx_dams'], doc='Sales within the year for damss')
    model.s_dvp_offs = pe.Set(ordered=True, initialize=params['dvp_idx_offs'], doc='Decision variable periods for offs') #ordered so they can be indexed in constraint to determine previous period
    model.s_damage = pe.Set(initialize=params['d_idx'], doc='age of mother - offs')
    model.s_k3_damage_offs = pe.Set(initialize=params['k3_idx_offs'], doc='age of mother - offs')
    model.s_k5_birth_offs = pe.Set(initialize=params['k5_idx_offs'], doc='Cluster for BTRT & oestrus cycle based on scanning, global & weaning management')
    model.s_groups_offs = pe.Set(initialize=params['g_idx_offs'], doc='geneotype groups of offs')
    model.s_gen_merit_offs = pe.Set(initialize=params['y_idx_offs'], doc='genetic merit of offs')
    model.s_gender = pe.Set(initialize=params['x_idx_offs'], doc='gender of offs')

    #####################
    ##  setup variables # #variables that use dynamic sets must be defined each itteration of exp
    #####################
    print('set up variables')
    ##animals
    model.v_sire = pe.Var(model.s_groups_sire, bounds = (0,None) , doc='number of sire animals')
    model.v_dams = pe.Var(model.s_k2_birth_dams, model.s_sale_dams, model.s_dvp_dams, model.s_wean_times, model.s_nut_dams, model.s_lw_dams,
                          model.s_season_types, model.s_tol, model.s_gen_merit_dams, model.s_groups_dams, bounds = (0,None) , doc='number of dam animals')
    model.v_offs = pe.Var(model.s_k3_damage_offs, model.s_k5_birth_offs, model.s_sale_offs, model.s_dvp_offs, model.s_nut_offs, model.s_lw_offs, model.s_season_types,
                          model.s_tol, model.s_wean_times, model.s_gender, model.s_gen_merit_offs,
                          model.s_groups_offs, bounds = (0,None) , doc='number of offs animals')
    model.v_prog = pe.Var(model.s_k5_birth_offs, model.s_sale_prog, model.s_lw_prog, model.s_season_types,
                          model.s_tol, model.s_damage, model.s_wean_times, model.s_gender,
                          model.s_groups_prog, bounds = (0,None) , doc='number of offs animals')


    ##purchases
    model.v_purchase_dams = pe.Var(model.s_dvp_dams, model.s_lw_dams, model.s_season_types, model.s_tol, model.s_groups_dams, bounds = (0,None) , doc='number of purchased dam animals')
    model.v_purchase_offs = pe.Var(model.s_dvp_offs, model.s_lw_offs, model.s_season_types, model.s_tol, model.s_groups_offs, bounds = (0,None) , doc='number of purchased offs animals')


    ######################
    ### setup parameters #
    ######################
    print('set up params')
    param_start = time.time()

    ##nsire - mating
    try:
        model.del_component(model.p_nsires_req_index)
        model.del_component(model.p_nsires_req)
    except AttributeError:
        pass
    model.p_nsires_req = pe.Param(model.s_k2_birth_dams, model.s_sale_dams, model.s_dvp_dams, model.s_wean_times, model.s_nut_dams, model.s_lw_dams,
                               model.s_season_types, model.s_tol, model.s_gen_merit_dams, model.s_groups_dams, model.s_groups_sire, model.s_sire_periods,
                               initialize=params['p_nsire_req_dams'], default=0.0, doc='requirement for sires for mating')

    try:
        model.del_component(model.p_nsires_prov_index)
        model.del_component(model.p_nsires_prov)
    except AttributeError:
        pass
    model.p_nsires_prov = pe.Param(model.s_groups_sire, model.s_sire_periods,
                               initialize=params['p_nsire_prov_sire'], default=0.0, doc='sires available for mating')

    ##progeny
    try:
        model.del_component(model.p_npw_index)
        model.del_component(model.p_npw)
    except AttributeError:
        pass
    model.p_npw = pe.Param(model.s_k2_birth_dams, model.s_k5_birth_offs, model.s_sale_dams, model.s_dvp_dams, model.s_wean_times, model.s_nut_dams, model.s_lw_dams,
                              model.s_season_types, model.s_tol, model.s_damage, model.s_gender, model.s_gen_merit_dams, model.s_groups_dams, model.s_lw_prog, model.s_tol,
                              initialize=params['p_npw_dams'], default=0.0, doc='number of prodgeny weaned')
    try:
        model.del_component(model.p_progprov_dams_index)
        model.del_component(model.p_npp_progprov_damsw)
    except AttributeError:
        pass
    model.p_progprov_dams = pe.Param(model.s_k3_damage_offs, model.s_k5_birth_offs, model.s_sale_prog, model.s_wean_times, model.s_lw_prog,
                              model.s_season_types, model.s_tol, model.s_damage, model.s_gender, model.s_gen_merit_dams, model.s_groups_prog, model.s_groups_dams, model.s_lw_dams,
                              initialize=params['p_progprov_dams'], default=0.0, doc='number of prodgeny provided to dams')
    try:
        model.del_component(model.p_progreq_dams_index)
        model.del_component(model.p_progreq_dams)
    except AttributeError:
        pass
    model.p_progreq_dams = pe.Param(model.s_k2_birth_dams, model.s_k3_damage_offs, model.s_k5_birth_offs, model.s_wean_times, model.s_lw_dams,
                              model.s_season_types, model.s_tol, model.s_gen_merit_dams, model.s_groups_dams, model.s_groups_dams, model.s_lw_dams,
                              initialize=params['p_progreq_dams'], default=0.0, doc='number of prodgeny required by dams')
    try:
        model.del_component(model.p_progprov_offs_index)
        model.del_component(model.p_progprov_offs)
    except AttributeError:
        pass
    model.p_progprov_offs = pe.Param(model.s_k3_damage_offs, model.s_k5_birth_offs, model.s_sale_prog, model.s_wean_times, model.s_lw_prog,
                              model.s_season_types, model.s_tol, model.s_damage, model.s_gender, model.s_gen_merit_offs, model.s_groups_offs, model.s_lw_offs,
                              initialize=params['p_progprov_offs'], default=0.0, doc='number of prodgeny provided to dams')
    try:
        model.del_component(model.p_progreq_offs_index)
        model.del_component(model.p_progreq_offs)
    except AttributeError:
        pass
    model.p_progreq_offs = pe.Param(model.s_lw_offs, model.s_groups_offs, model.s_lw_offs,
                              initialize=params['p_progreq_offs'], default=0.0, doc='number of prodgeny required by dams')


    ##stock - dams
    try:
        model.del_component(model.p_numbers_prov_dams_index)
        model.del_component(model.p_numbers_prov_dams)
    except AttributeError:
        pass
    model.p_numbers_prov_dams = pe.Param(model.s_k2_birth_dams, model.s_k2_birth_dams, model.s_sale_dams, model.s_dvp_dams, model.s_wean_times, model.s_nut_dams, model.s_lw_dams,
                                         model.s_season_types, model.s_tol, model.s_gen_merit_dams, model.s_groups_dams, model.s_groups_dams, model.s_lw_dams,
                                         initialize=params['p_numbers_prov_dams'], default=0.0, doc='numbers provided by each dam activity into the next period')

    try:
        model.del_component(model.p_numbers_req_dams_index)
        model.del_component(model.p_numbers_req_dams)
    except AttributeError:
        pass
    model.p_numbers_req_dams = pe.Param(model.s_k2_birth_dams, model.s_k2_birth_dams, model.s_sale_dams, model.s_dvp_dams, model.s_wean_times, model.s_nut_dams, model.s_lw_dams,
                                         model.s_season_types, model.s_tol, model.s_gen_merit_dams, model.s_groups_dams, model.s_groups_dams, model.s_lw_dams,
                                         initialize=params['p_numbers_req_dams'], default=0.0, doc='numbers required by each dam activity in the current period')

    ##stock - offs
    try:
        model.del_component(model.p_numbers_prov_offs_index)
        model.del_component(model.p_numbers_prov_offs)
    except AttributeError:
        pass
    model.p_numbers_prov_offs = pe.Param(model.s_k3_damage_offs, model.s_k5_birth_offs, model.s_sale_offs, model.s_dvp_offs, model.s_nut_offs, model.s_lw_offs, model.s_season_types, model.s_tol,
                                 model.s_wean_times, model.s_gender, model.s_gen_merit_offs, model.s_groups_offs, model.s_lw_offs,
                                 initialize=params['p_numbers_prov_offs'], default=0.0, doc='numbers provided into the current period from the previous periods activities')
    try:
        model.del_component(model.p_numbers_req_offs_index)
        model.del_component(model.p_numbers_req_offs)
    except AttributeError:
        pass
    model.p_numbers_req_offs = pe.Param(model.s_k3_damage_offs, model.s_k5_birth_offs, model.s_dvp_offs, model.s_lw_offs,
                                        model.s_groups_offs, model.s_lw_offs,
                                        initialize=params['p_numbers_req_offs'], default=0.0, doc='requirment of off in the current period')

    ##energy intake
    try:
        model.del_component(model.p_mei_sire)
    except AttributeError:
        pass
    model.p_mei_sire = pe.Param(model.s_feed_periods, model.s_sheep_pools, model.s_groups_sire, initialize=params['p_mei_sire'], 
                                  default=0.0, doc='energy requirement sire')
    try:
        model.del_component(model.p_mei_dams)
    except AttributeError:
        pass
    model.p_mei_dams = pe.Param(model.s_k2_birth_dams, model.s_feed_periods, model.s_sheep_pools, model.s_sale_dams, 
                               model.s_dvp_dams, model.s_wean_times, model.s_nut_dams, model.s_lw_dams, model.s_season_types, 
                               model.s_tol, model.s_gen_merit_dams, model.s_groups_dams, initialize=params['p_mei_dams'], default=0.0, doc='energy requirement dams')
    try:
        model.del_component(model.p_mei_offs)
    except AttributeError:
        pass
    model.p_mei_offs = pe.Param(model.s_k3_damage_offs, model.s_k5_birth_offs, model.s_feed_periods, model.s_sheep_pools, model.s_sale_offs, 
                               model.s_dvp_offs, model.s_nut_offs, model.s_lw_offs, model.s_season_types, model.s_tol, model.s_wean_times, 
                               model.s_gender, model.s_gen_merit_offs, model.s_groups_offs, initialize=params['p_mei_offs'], default=0.0, doc='energy requirement offs')

    ##potential intake
    try:
        model.del_component(model.p_pi_sire)
    except AttributeError:
        pass
    model.p_pi_sire = pe.Param(model.s_feed_periods, model.s_sheep_pools, model.s_groups_sire, initialize=params['p_pi_sire'], 
                                  default=0.0, doc='pi sire')
    try:
        model.del_component(model.p_pi_dams)
    except AttributeError:
        pass
    model.p_pi_dams = pe.Param(model.s_k2_birth_dams, model.s_feed_periods, model.s_sheep_pools, model.s_sale_dams, 
                               model.s_dvp_dams, model.s_wean_times, model.s_nut_dams, model.s_lw_dams, model.s_season_types, 
                               model.s_tol, model.s_gen_merit_dams, model.s_groups_dams, initialize=params['p_pi_dams'], default=0.0, doc='pi dams')
    try:
        model.del_component(model.p_pi_offs)
    except AttributeError:
        pass
    model.p_pi_offs = pe.Param(model.s_k3_damage_offs, model.s_k5_birth_offs, model.s_feed_periods, model.s_sheep_pools, model.s_sale_offs, 
                               model.s_dvp_offs, model.s_nut_offs, model.s_lw_offs, model.s_season_types, model.s_tol, model.s_wean_times, 
                               model.s_gender, model.s_gen_merit_offs, model.s_groups_offs, initialize=params['p_pi_offs'], default=0.0, doc='pi offs')

    
    ##cashflow
    try:
        model.del_component(model.p_cashflow_sire)
    except AttributeError:
        pass
    model.p_cashflow_sire = pe.Param(model.s_cashflow_periods, model.s_groups_sire, initialize=params['p_cashflow_sire'], 
                                  default=0.0, doc='cashflow sire')
    try:
        model.del_component(model.p_cashflow_dams)
    except AttributeError:
        pass
    model.p_cashflow_dams = pe.Param(model.s_k2_birth_dams, model.s_cashflow_periods, model.s_sale_dams, model.s_dvp_dams, model.s_wean_times, model.s_nut_dams, 
                                  model.s_lw_dams, model.s_season_types, model.s_tol, model.s_gen_merit_dams, model.s_groups_dams,
                                  initialize=params['p_cashflow_dams'], default=0.0, doc='cashflow dams')
    try:
        model.del_component(model.p_cashflow_offs)
    except AttributeError:
        pass
    model.p_cashflow_offs = pe.Param(model.s_k3_damage_offs, model.s_k5_birth_offs, model.s_cashflow_periods, model.s_sale_offs, model.s_dvp_offs, model.s_nut_offs, model.s_lw_offs,
                             model.s_season_types, model.s_tol, model.s_wean_times, model.s_gender, model.s_gen_merit_offs, model.s_groups_offs,
                             initialize=params['p_cashflow_offs'], default=0.0, doc='cashflow offs')
    ##cost - minroe
    try:
        model.del_component(model.p_cost_sire)
    except AttributeError:
        pass
    model.p_cost_sire = pe.Param(model.s_groups_sire, initialize=params['p_cost_sire'], 
                                  default=0.0, doc='husbandry cost sire')
    try:
        model.del_component(model.p_cost_dams)
    except AttributeError:
        pass
    model.p_cost_dams = pe.Param(model.s_k2_birth_dams, model.s_sale_dams, model.s_dvp_dams, model.s_wean_times, model.s_nut_dams, 
                                  model.s_lw_dams, model.s_season_types, model.s_tol, model.s_gen_merit_dams, model.s_groups_dams,
                                  initialize=params['p_cost_dams'], default=0.0, doc='husbandry cost dams')
    try:
        model.del_component(model.p_cost_offs)
    except AttributeError:
        pass
    model.p_cost_offs = pe.Param(model.s_k3_damage_offs, model.s_k5_birth_offs, model.s_sale_offs, model.s_dvp_offs, model.s_nut_offs, model.s_lw_offs,
                             model.s_season_types, model.s_tol, model.s_wean_times, model.s_gender, model.s_gen_merit_offs, model.s_groups_offs,
                             initialize=params['p_cost_offs'], default=0.0, doc='husbandry cost offs')

    ##asset value stock
    try:
        model.del_component(model.p_asset_sire)
    except AttributeError:
        pass
    model.p_asset_sire = pe.Param(model.s_groups_sire, initialize=params['p_assetvalue_sire'], default=0.0, doc='Asset value of sire')
    try:
        model.del_component(model.p_asset_dams)
    except AttributeError:
        pass
    model.p_asset_dams = pe.Param(model.s_k2_birth_dams, model.s_sale_dams, model.s_dvp_dams, model.s_wean_times, model.s_nut_dams,
                                  model.s_lw_dams, model.s_season_types, model.s_tol, model.s_gen_merit_dams, model.s_groups_dams,
                                  initialize=params['p_assetvalue_dams'], default=0.0, doc='Asset value of dams')
    try:
        model.del_component(model.p_asset_offs)
    except AttributeError:
        pass
    model.p_asset_offs = pe.Param(model.s_k3_damage_offs, model.s_k5_birth_offs, model.s_sale_offs, model.s_dvp_offs, model.s_nut_offs, model.s_lw_offs,
                                 model.s_season_types, model.s_tol, model.s_wean_times, model.s_gender, model.s_gen_merit_offs, model.s_groups_offs,
                                 initialize=params['p_assetvalue_offs'], default=0.0, doc='Asset value of offs')

    ##labour - sire
    try:
        model.del_component(model.p_lab_anyone_sire)
    except AttributeError:
        pass
    model.p_lab_anyone_sire = pe.Param(model.s_labperiods, model.s_groups_sire,  initialize=params['p_labour_anyone_sire'], default=0.0, doc='labour requirment sire that can be done by anyone')
    try:
        model.del_component(model.p_lab_perm_sire)
    except AttributeError:
        pass
    model.p_lab_perm_sire = pe.Param(model.s_labperiods, model.s_groups_sire, initialize=params['p_labour_perm_sire'], default=0.0, doc='labour requirment sire that can be done by perm staff')
    try:
        model.del_component(model.p_lab_manager_sire)
    except AttributeError:
        pass
    model.p_lab_manager_sire = pe.Param(model.s_labperiods, model.s_groups_sire, initialize=params['p_labour_manager_sire'], default=0.0, doc='labour requirment sire that can be done by manager')
    
    ##labour - dams
    try:
        model.del_component(model.p_lab_anyone_dams)
    except AttributeError:
        pass
    model.p_lab_anyone_dams = pe.Param(model.s_k2_birth_dams, model.s_labperiods, model.s_sale_dams, model.s_dvp_dams, model.s_wean_times, model.s_nut_dams, model.s_lw_dams,
                            model.s_season_types, model.s_tol, model.s_gen_merit_dams, model.s_groups_dams,
                                       initialize=params['p_labour_anyone_dams'], default=0.0, doc='labour requirment dams that can be done by anyone')
    try:
        model.del_component(model.p_lab_perm_dams)
    except AttributeError:
        pass
    model.p_lab_perm_dams = pe.Param(model.s_k2_birth_dams, model.s_labperiods, model.s_sale_dams, model.s_dvp_dams, model.s_wean_times, model.s_nut_dams, model.s_lw_dams,
                            model.s_season_types, model.s_tol, model.s_gen_merit_dams, model.s_groups_dams,
                                     initialize=params['p_labour_perm_dams'], default=0.0, doc='labour requirment dams that can be done by perm staff')
    try:
        model.del_component(model.p_lab_manager_dams)
    except AttributeError:
        pass
    model.p_lab_manager_dams = pe.Param(model.s_k2_birth_dams, model.s_labperiods, model.s_sale_dams, model.s_dvp_dams, model.s_wean_times, model.s_nut_dams, model.s_lw_dams,
                            model.s_season_types, model.s_tol, model.s_gen_merit_dams, model.s_groups_dams,
                                        initialize=params['p_labour_manager_dams'], default=0.0, doc='labour requirment dams that can be done by manager')
    
    ##labour - offs
    try:
        model.del_component(model.p_lab_anyone_offs)
    except AttributeError:
        pass
    model.p_lab_anyone_offs = pe.Param(model.s_k3_damage_offs, model.s_k5_birth_offs, model.s_labperiods, model.s_sale_offs, model.s_dvp_offs, model.s_nut_offs, model.s_lw_offs,
                             model.s_season_types, model.s_tol, model.s_wean_times, model.s_gender, model.s_gen_merit_offs, model.s_groups_offs,
                             initialize=params['p_labour_anyone_offs'], default=0.0, doc='labour requirment offs - anyone')
    try:
        model.del_component(model.p_lab_perm_offs)
    except AttributeError:
        pass
    model.p_lab_perm_offs = pe.Param(model.s_k3_damage_offs, model.s_k5_birth_offs, model.s_labperiods, model.s_sale_offs, model.s_dvp_offs, model.s_nut_offs, model.s_lw_offs,
                             model.s_season_types, model.s_tol, model.s_wean_times, model.s_gender, model.s_gen_merit_offs, model.s_groups_offs,
                             initialize=params['p_labour_perm_offs'], default=0.0, doc='labour requirment offs - perm')
    try:
        model.del_component(model.p_lab_manager_offs)
    except AttributeError:
        pass
    model.p_lab_manager_offs = pe.Param(model.s_k3_damage_offs, model.s_k5_birth_offs, model.s_labperiods, model.s_sale_offs, model.s_dvp_offs, model.s_nut_offs, model.s_lw_offs,
                             model.s_season_types, model.s_tol, model.s_wean_times, model.s_gender, model.s_gen_merit_offs, model.s_groups_offs,
                             initialize=params['p_labour_manager_offs'], default=0.0, doc='labour requirment offs - manager')

    ##infrastructure
    try:
        model.del_component(model.p_infra_sire)
    except AttributeError:
        pass
    model.p_infra_sire = pe.Param(model.s_infrastructure, model.s_groups_sire, initialize=params['p_infrastructure_sire'], 
                                  default=0.0, doc='sire requirement for infrastructure (based on number of times yarded and shearing activity)')
    try:
        model.del_component(model.p_infra_dams)
    except AttributeError:
        pass
    model.p_infra_dams = pe.Param(model.s_k2_birth_dams, model.s_infrastructure, model.s_sale_dams, model.s_dvp_dams, model.s_wean_times, model.s_nut_dams, 
                                  model.s_lw_dams, model.s_season_types, model.s_tol, model.s_gen_merit_dams, model.s_groups_dams,
                                  initialize=params['p_infrastructure_dams'], default=0.0, doc='Dams requirement for infrastructure (based on number of times yarded and shearing activity)')
    try:
        model.del_component(model.p_infra_offs)
    except AttributeError:
        pass
    model.p_infra_offs = pe.Param(model.s_k3_damage_offs, model.s_k5_birth_offs, model.s_infrastructure, model.s_sale_offs, model.s_dvp_offs, model.s_nut_offs, model.s_lw_offs,
                             model.s_season_types, model.s_tol, model.s_wean_times, model.s_gender, model.s_gen_merit_offs, model.s_groups_offs,
                             initialize=params['p_infrastructure_offs'], default=0.0, doc='offs requirement for infrastructure (based on number of times yarded and shearing activity)')


    # try:
    #     model.del_component(model.p_asset_stockinfra)
    # except AttributeError:
    #     pass
    # model.p_asset_stockinfra = Param(model.s_infrastructure, initialize=, default=0.0, doc='Asset value per animal mustered  or shorn')
    # try:
    #     model.del_component(model.p_dep_stockinfra)
    # except AttributeError:
    #     pass
    # model.p_dep_stockinfra = Param(model.s_infrastructure, initialize=, default=0.0, doc='Depreciation of the asset value')
    # try:
    #     model.del_component(model.p_rm_stockinfra)
    # except AttributeError:
    #     pass
    # model.p_rm_stockinfra = Param(model.s_infrastructure, model.s_cashflow_periods,initialize=, default=0.0, doc='Cost of R&M of the infrastructure (per animal mustered/shorn)')
    # try:
    #     model.del_component(model.p_lab_stockinfra)
    # except AttributeError:
    #     pass
    # model.p_lab_stockinfra = Param(model.s_infrastructure, model.s_labperiods, initialize=, default=0.0, doc='Labour required for R&M of the infrastructure (per animal mustered/shorn)')


    ##purchases
    # model.p_cost_purch_sire = Param(model.s_groups_sire, model.s_cashflow_periods,
    #                                initialize=, default=0.0, doc='cost of purchased sires')
    # model.p_numberpurch_dam = Param(model.s_dvp_dams, model.s_wean_times, model.s_k2_birth_dams, model.s_lw_dams,
    #                           model.s_season_types, model.s_tol, model.s_gen_merit_dams, model.s_groups_dams, model.s_co_conception,
    #                           model.s_co_bw, model.s_co_ww, model.s_co_cfw, model.s_co_fd, model.s_co_min_fd, model.s_co_fl, initialize=, default=0.0, doc='purchase transfer - ie how a purchased dam is allocated into damR')
    # model.p_cost_purch_dam = Param(model.s_dvp_dams, model.s_lw_dams, model.s_season_types, model.s_tol, model.s_groups_dams, model.s_cashflow_periods,
    #                                initialize=, default=0.0, doc='cost of purchased dams')
    # model.p_numberpurch_offs = Param(model.s_dvp_offs, model.s_lw_offs, model.s_season_types, model.s_tol, model.s_k3_damage_offs,
    #                                  model.s_wean_times, model.s_k5_birth_offs, model.s_gender, model.s_gen_merit_offs, model.s_groups_offs,
    #                                  initialize=, default=0.0, doc='purchase transfer - ie how a purchased offs is allocated into offsR')
    # model.p_cost_purch_offs = Param(model.s_dvp_offs, model.s_lw_offs, model.s_season_types, model.s_tol, model.s_groups_offs, model.s_cashflow_periods,
    #                                initialize=, default=0.0, doc='cost of purchased offs')
    # ##transfers
    # model.p_offs2dam_numbers = Param(model.s_dvp_offs, model.s_nut_offs, model.s_lw_offs, model.s_season_types, model.s_tol, model.s_k3_damage_offs,
    #                                  model.s_wean_times, model.s_k5_birth_offs, model.s_gender, model.s_gen_merit_offs, model.s_co_cfw,
    #                                  model.s_co_fd, model.s_co_min_fd, model.s_co_fl, model.s_groups_dams, model.s_dvp_dams, model.s_wean_times,
    #                                  model.s_k2_birth_dams, model.s_lw_dams, model.s_season_types, model.s_tol, model.s_gen_merit_dams, model.s_groups_dams,
    #                                  initialize=, default=0.0, doc='Proportion of the offs distributed to each of the starting LWs at the beginning of the current dam feed variation period')
    # model.p_dam2sire_numbers = Param(model.s_dvp_dams, model.s_wean_times, model.s_k2_birth_dams, model.s_lw_dams, model.s_season_types, model.s_tol,
    #                                  model.s_gen_merit_dams, model.s_groups_dams, model.s_groups_dams,
    #                                  initialize=, default=0.0, doc='Proportion of the animals distributed to each of the starting LWs of the recipient animals at the beginning of the recipients next feed variation period')

    # textbuffer = StringIO()
    # model.p_numbers_prov_dams.pprint(textbuffer)
    # textbuffer.write('\n')
    # with open('number_prov.txt', 'w') as outputfile:
    #     outputfile.write(textbuffer.getvalue())
    #
    # textbuffer = StringIO()
    # model.p_numbers_req_dams.pprint(textbuffer)
    # textbuffer.write('\n')
    # with open('number_prov.txt', 'w') as outputfile:
    #     outputfile.write(textbuffer.getvalue())


    end_params = time.time()
    print('params time: ',end_params-param_start)

    ########################
    ### set up constraints #
    ########################
    '''pyomo summary:
            - if a set has a 9 on the end of it, it is a special constraint set. And it is used to link with a decision variable set (the corresponding letter without 9 eg g? and g9). The
              set without a 9 must be summed.
            - if a given set doesnt have a corresponding 9 set, then you have two options
                1. transfer from one desision variable to another 1:1 (or at another ratio determined be the param - but it means that it transfers to the same set eg x1_dams transfers to x1_prog)
                2. treat all decision variable in a set the same. Done by summing. eg the npw provided by each dam t slice can be treated the same because it doesnt make a difference
                   if the progeny came from a dam that gets sold vs retained. (for most of the livestock it has been built in a way that doesnt need summing except for the sets which have a corresponding 9 set).
    
    speed info:
    - constraint.skip is fast, the trick is designing the code efficiently so that is knows when to skip.
    - in method 2 i use the param to determine when the constraint should be skipped, this still requires looping through the param
    - in method 3 i use the numpy array to determine when the constraint should be skipped. This is messier and requires some extra code but it is much more efficient reducing time 2x.
    - using if statements to save summing 0 values is faster but it still takes time to evaluate the if therefore it saves time to select the minimum number of if statements
    - constraints can only be skipped on based on the req param. if the provide side is 0 and you skip the constraint then that would mean there would be no restriction for the require variable.
    '''

    print('set up constraints')


    ##turn sets into list so they can be indexed (required for advanced mehtod to save time)
    l_k29 = list(model.s_k2_birth_dams)
    l_v1 = list(model.s_dvp_dams)
    l_a = list(model.s_wean_times)
    l_z = list(model.s_season_types)
    l_i = list(model.s_tol)
    l_y1 = list(model.s_gen_merit_dams)
    l_g9 = list(model.s_groups_dams)
    l_w9 = list(model.s_lw_dams)
    l_k3 = list(model.s_k3_damage_offs)
    l_k5 = list(model.s_k5_birth_offs)
    l_v3 = list(model.s_dvp_offs)
    l_g3 = list(model.s_groups_offs)
    l_w9_offs = list(model.s_lw_offs)


    try:
        model.del_component(model.con_damR_index)
        model.del_component(model.con_damR)
    except AttributeError:
        pass
    def damR(model,k29,v1,a,z,i,y1,g9,w9):
        v1_prev = l_v1[l_v1.index(v1) - 1]  #used to get the activity number from the last period - to determine the number of dam provided into this period
        ##skip constraint if the require param is 0 - using the numpy array because it is 2x faster becasue dont need to loop through activity keys eg k28
        ###get the index number - required so numpy array can be indexed
        t_k29 = l_k29.index(k29)
        t_v1 = l_v1.index(v1)
        t_a = l_a.index(a)
        t_z = l_z.index(z)
        t_i = l_i.index(i)
        t_y1 = l_y1.index(y1)
        t_g9 = l_g9.index(g9)
        t_w9 = l_w9.index(w9)
        if not np.any(params['numbers_req_numpyvesion_k2k2tva1nw8ziyg1g9w9'][:,t_k29,:,t_v1,t_a,:,:,t_z,t_i,t_y1,:,t_g9,t_w9]):
            return pe.Constraint.Skip
        return sum(model.v_dams[k28,t1,v1,a,n1,w8,z,i,y1,g1] * model.p_numbers_req_dams[k28,k29,t1,v1,a,n1,w8,z,i,y1,g1,g9,w9]
                   - model.v_dams[k28,t1,v1_prev,a,n1,w8,z,i,y1,g1] * model.p_numbers_prov_dams[k28,k29,t1,v1_prev,a,n1,w8,z,i,y1,g1,g9,w9]
                    for t1 in model.s_sale_dams for k28 in model.s_k2_birth_dams
                    for n1 in model.s_nut_dams for w8 in model.s_lw_dams for g1 in model.s_groups_dams if
                    model.p_numbers_req_dams[k28, k29, t1, v1, a, n1, w8, z, i, y1, g1,g9, w9] != 0 or model.p_numbers_prov_dams[k28, k29, t1, v1_prev, a, n1, w8, z, i, y1, g1, g9, w9] != 0) <=0 #need to use both in the if statement (even though it is slower) becasue there are stitustions eg dvp4 (prejoining) where prov will have a value and req will not.
    start=time.time()
    model.con_damR = pe.Constraint(model.s_k2_birth_dams, model.s_dvp_dams, model.s_wean_times, model.s_season_types, model.s_tol, model.s_gen_merit_dams,
                                   model.s_groups_dams, model.s_lw_dams, rule=damR, doc='transfer dam to dam from last dvp to current dvp.')
    end=time.time()
    print('method 3: ',end-start)


    try:
        model.del_component(model.con_offR_index)
        model.del_component(model.con_offR)
    except AttributeError:
        pass
    def offR(model,k3,k5,v3,a,z,i,x,y3,g3,w9):
        v3_prev = l_v1[l_v3.index(v3) - 1]  #used to get the activity number from the last period
        ##skip constraint if the require param is 0 - using the numpy array because it is 2x faster becasue dont need to loop through activity keys eg k28
        ###get the index number - required so numpy array can be indexed
        t_k3 = l_k3.index(k3)
        t_k5 = l_k5.index(k5)
        t_v3 = l_v3.index(v3)
        t_g3 = l_g3.index(g3)
        t_w9 = l_w9_offs.index(w9)
        if not np.any(params['numbers_req_numpyvesion_k3k5vw8g3w9'][t_k3,t_k5,t_v3,:,t_g3,t_w9]):
            return pe.Constraint.Skip
        return sum(model.v_offs[k3,k5,t3,v3,n3,w8,z,i,a,x,y3,g3] * model.p_numbers_req_offs[k3,k5,v3,w8,g3,w9]
                   - model.v_offs[k3,k5,t3,v3_prev,n3,w8,z,i,a,x,y3,g3] * model.p_numbers_prov_offs[k3,k5,t3,v3_prev,n3,w8,z,i,a,x,y3,g3,w9]
                    for t3 in model.s_sale_offs for n3 in model.s_nut_offs for w8 in model.s_lw_offs
                   if model.p_numbers_req_offs[k3,k5,v3,w8,g3,w9] != 0 or model.p_numbers_prov_offs[k3,k5,t3,v3_prev,n3,w8,z,i,a,x,y3,g3,w9] != 0) <=0 #need to use both in the if statement (even though it is slower) becasue there are stitustions eg dvp4 (prejoining) where prov will have a value and req will not.
    start=time.time()
    model.con_offR = pe.Constraint(model.s_k3_damage_offs, model.s_k5_birth_offs, model.s_dvp_offs, model.s_wean_times, model.s_season_types, model.s_tol, model.s_gender,
                                   model.s_gen_merit_dams, model.s_groups_offs, model.s_lw_offs, rule=offR, doc='transfer off to off from last dvp to current dvp.')
    end=time.time()
    print('method 3: ',end-start)


    try:
        model.del_component(model.con_progR_index)
        model.del_component(model.con_progR)
    except AttributeError:
        pass
    def progR(model, k5, a, z, i9, d, x, y1, g1, w9):
        ###cant skip constraints based on the provide param otherwise the model could select the prg variable without restriction (maybe a req param can be added then we could skip on that ??)
        return (- sum(model.v_dams[k2, t1, v1, a, n1, w18, z, i, y1, g1]  * model.p_npw[k2, k5, t1, v1, a, n1, w18, z, i, d, x, y1, g1, w9, i9]
                    for k2 in model.s_k2_birth_dams for t1 in model.s_sale_dams for v1 in model.s_dvp_dams for n1 in model.s_nut_dams for w18 in model.s_lw_dams for i in model.s_tol
                         if model.p_npw[k2, k5, t1, v1, a, n1, w18, z, i, d, x, y1, g1, w9, i9]!= 0)
                + sum(model.v_prog[k5, t2, w9, z, i9, d, a, x, g1] for t2 in model.s_sale_prog ))<=0
    start = time.time()
    model.con_progR = pe.Constraint(model.s_k5_birth_offs, model.s_wean_times, model.s_season_types, model.s_tol,
                                    model.s_damage, model.s_gender, model.s_gen_merit_dams, model.s_groups_dams, model.s_lw_prog, rule=progR,
                                   doc='transfer npw from dams to prog.')
    end = time.time()
    print('con_progR ',end-start)

    try:
        model.del_component(model.con_prog2damR_index)
        model.del_component(model.con_prog2damR)
    except AttributeError:
        pass
    def prog2damR(model, k3, k5, v1, a, z, i, y1, g9, w9):
        if v1=='dvp0' and any(model.p_progreq_dams[k2, k3, k5, a, w18, z, i, y1, g1, g9, w9] for k2 in model.s_k2_birth_dams for w18 in model.s_lw_dams for g1 in model.s_groups_dams):
            return (sum(- model.v_prog[k5, t2, w28, z, i, d, a, x, g2] * model.p_progprov_dams[k3, k5, t2, a, w28, z, i, d, x, y1, g2,g9,w9]
                        for d in model.s_damage for x in model.s_gender for w28 in model.s_lw_prog for t2 in model.s_sale_prog for g2 in model.s_groups_prog
                        if model.p_progprov_dams[k3, k5, t2, a, w28, z, i, d, x, y1, g2, g9, w9]!= 0)
                       + sum(model.v_dams[k2, t1, v1, a, n1, w18, z, i, y1, g1]  * model.p_progreq_dams[k2, k3, k5, a, w18, z, i, y1, g1, g9, w9]
                        for k2 in model.s_k2_birth_dams for t1 in model.s_sale_dams for n1 in model.s_nut_dams for w18 in model.s_lw_dams for g1 in model.s_groups_dams
                             if model.p_progreq_dams[k2, k3, k5, a, w18, z, i, y1, g1, g9, w9]!= 0))<=0
        else:
            return pe.Constraint.Skip
    start = time.time()
    model.con_prog2damR = pe.Constraint(model.s_k3_damage_offs, model.s_k5_birth_offs, model.s_dvp_dams, model.s_wean_times, model.s_season_types,
                                   model.s_tol, model.s_gen_merit_dams, model.s_groups_dams, model.s_lw_dams, rule=prog2damR,
                                   doc='transfer prog to dams in dvp 0.')
    end = time.time()
    print('con_prog2damR ',end-start)

    try:
        model.del_component(model.con_prog2offsR_index)
        model.del_component(model.con_prog2offsR)
    except AttributeError:
        pass
    def prog2offsR(model, k3, k5, v3, a, z, i, x, y3, g3, w9):
        if v3=='dvp0' and any(model.p_progreq_offs[w38, g3, w9] for w38 in model.s_lw_offs):
            return (sum(- model.v_prog[k5, t2, w28, z, i, d, a, x, g3] * model.p_progprov_offs[k3, k5, t2, a, w28, z, i, d, x, y3, g3, w9]
                        for d in model.s_damage for w28 in model.s_lw_prog for t2 in model.s_sale_prog
                        if model.p_progprov_offs[k3, k5, t2, a, w28, z, i, d, x, y3, g3, w9]!= 0)
                       + sum(model.v_offs[k3,k5,t3,v3,n3,w38,z,i,a,x,y3,g3]  * model.p_progreq_offs[w38, g3, w9]
                        for t3 in model.s_sale_offs for n3 in model.s_nut_dams for w38 in model.s_lw_offs if model.p_progreq_offs[w38, g3, w9]!= 0))<=0
        else:
            return pe.Constraint.Skip
    start = time.time()
    model.con_prog2offsR = pe.Constraint(model.s_k3_damage_offs, model.s_k5_birth_offs, model.s_dvp_dams, model.s_wean_times, model.s_season_types,
                                   model.s_tol, model.s_gender, model.s_gen_merit_dams, model.s_groups_offs, model.s_lw_dams, rule=prog2offsR,
                                   doc='transfer prog to off in dvp 0.')
    end = time.time()
    print(end-start)



    try:
        model.del_component(model.con_matingR)
    except AttributeError:
        pass
    def mating(model,g0,p8):
        return - model.v_sire[g0] + sum(model.v_dams[k2,t1,v1,a,n1,w1,z,i,y1,g1] * model.p_nsires_req[k2,t1,v1,a,n1,w1,z,i,y1,g1,g0,p8]
                  for k2 in model.s_k2_birth_dams for t1 in model.s_sale_dams for v1 in model.s_dvp_dams for a in model.s_wean_times for n1 in model.s_nut_dams
                   for w1 in model.s_lw_dams for z in model.s_season_types for i in model.s_tol for y1 in model.s_gen_merit_dams  for g1 in model.s_groups_dams) <=0
    model.con_matingR = pe.Constraint(model.s_groups_sire, model.s_sire_periods, rule=mating, doc='sire requirment for mating')

    try:
        model.del_component(model.con_stockinfra)
    except AttributeError:
        pass
    def stockinfra(model,h1):
        return -model.v_infrastructure[h1] + sum(model.v_sire[g0] * model.p_infra_sire[h1,g0] for g0 in model.s_groups_sire)  \
               + sum(sum(model.v_dams[k2,t1,v1,a,n1,w1,z,i,y1,g1] * model.p_infra_dams[k2,h1,t1,v1,a,n1,w1,z,i,y1,g1]
                         for k2 in model.s_k2_birth_dams for t1 in model.s_sale_dams for v1 in model.s_dvp_dams for n1 in model.s_nut_dams
                         for w1 in model.s_lw_dams for y1 in model.s_gen_merit_dams for g1 in model.s_groups_dams)
                    + sum(model.v_offs[k3,k5,t3,v3,n3,w3,z,i,a,x,y3,g3]  * model.p_infra_offs[k3,k5,h1,t3,v3,n3,w3,z,i,a,x,y3,g3]
                          for k3 in model.s_k3_damage_offs for k5 in model.s_k5_birth_offs for t3 in model.s_sale_offs for v3 in model.s_dvp_offs
                          for n3 in model.s_nut_offs for w3 in model.s_lw_offs for x in model.s_gender for y3 in model.s_gen_merit_offs for g3 in model.s_groups_offs)
               for a in model.s_wean_times for z in model.s_season_types for i in model.s_tol) <=0
    model.con_stockinfra = pe.Constraint(model.s_infrastructure, rule=stockinfra, doc='Requirement for infrastructure (based on number of times yarded and shearing activity)')

    end_cons=time.time()
    print('time con: ', end_cons-end_params)

    # textbuffer = StringIO()
    # model.con_offR.pprint(textbuffer)
    # textbuffer.write('\n')
    # with open('cons.txt', 'w') as outputfile:
    #     outputfile.write(textbuffer.getvalue())

#####################
##  setup variables # these variables only need initialising once ie sets wont change within and iteration of exp.
#####################
##infrastructure
model.v_infrastructure = pe.Var(model.s_infrastructure, bounds = (0,None) , doc='amount of infustructure required for given animal enterprise (based on number of sheep through infra)')

# ##################################
# ### setup core model constraints #
# ##################################

def stock_me(model,f,p6):
    return sum(model.v_sire[g0] * model.p_mei_sire[p6,f,g0] for g0 in model.s_groups_sire)\
           + sum(sum(model.v_dams[k2,t1,v1,a,n1,w1,z,i,y1,g1] * model.p_mei_dams[k2,p6,f,t1,v1,a,n1,w1,z,i,y1,g1]
                     for k2 in model.s_k2_birth_dams for t1 in model.s_sale_dams for v1 in model.s_dvp_dams for n1 in model.s_nut_dams
                     for w1 in model.s_lw_dams for y1 in model.s_gen_merit_dams for g1 in model.s_groups_dams)
                + sum(model.v_offs[k3,k5,t3,v3,n3,w3,z,i,a,x,y3,g3]  * model.p_mei_offs[k3,k5,p6,f,t3,v3,n3,w3,z,i,a,x,y3,g3]
                      for k3 in model.s_k3_damage_offs for k5 in model.s_k5_birth_offs for t3 in model.s_sale_offs for v3 in model.s_dvp_offs
                      for n3 in model.s_nut_offs for w3 in model.s_lw_offs for x in model.s_gender for y3 in model.s_gen_merit_offs for g3 in model.s_groups_offs)
               for a in model.s_wean_times for z in model.s_season_types for i in model.s_tol)


def stock_pi(model,f,p6):
    return sum(model.v_sire[g0] * model.p_pi_sire[p6,f,g0] for g0 in model.s_groups_sire)\
           + sum(sum(model.v_dams[k2,t1,v1,a,n1,w1,z,i,y1,g1] * model.p_pi_dams[k2,p6,f,t1,v1,a,n1,w1,z,i,y1,g1]
                     for k2 in model.s_k2_birth_dams for t1 in model.s_sale_dams for v1 in model.s_dvp_dams for n1 in model.s_nut_dams
                     for w1 in model.s_lw_dams for y1 in model.s_gen_merit_dams for g1 in model.s_groups_dams)
                + sum(model.v_offs[k3,k5,t3,v3,n3,w3,z,i,a,x,y3,g3]  * model.p_pi_offs[k3,k5,p6,f,t3,v3,n3,w3,z,i,a,x,y3,g3]
                      for k3 in model.s_k3_damage_offs for k5 in model.s_k5_birth_offs for t3 in model.s_sale_offs for v3 in model.s_dvp_offs
                      for n3 in model.s_nut_offs for w3 in model.s_lw_offs for x in model.s_gender for y3 in model.s_gen_merit_offs for g3 in model.s_groups_offs)
               for a in model.s_wean_times for z in model.s_season_types for i in model.s_tol)

def stock_cashflow(model,c):
    # infrastructure = sum(model.p_rm_stockinfra[h3,c] * model.v_infrastructure[h3] for h3 in model.s_infrastructure)
    stock = sum(model.v_sire[g0] * model.p_cashflow_sire[g0,c] for g0 in model.s_groups_sire) \
           + sum(sum(model.v_dams[k2,t1,v1,a,n1,w1,z,i,y1,g1] * model.p_cashflow_dams[k2,c,t1,v1,a,n1,w1,z,i,y1,g1]
                     for k2 in model.s_k2_birth_dams for t1 in model.s_sale_dams for v1 in model.s_dvp_dams for n1 in model.s_nut_dams
                     for w1 in model.s_lw_dams for y1 in model.s_gen_merit_dams for g1 in model.s_groups_dams)
                + sum(model.v_offs[k3,k5,t3,v3,n3,w3,z,i,a,x,y3,g3]  * model.p_cashflow_offs[k3,k5,c,t3,v3,n3,w3,z,i,a,x,y3,g3]
                      for k3 in model.s_k3_damage_offs for k5 in model.s_k5_birth_offs for t3 in model.s_sale_offs for v3 in model.s_dvp_offs
                      for n3 in model.s_nut_offs for w3 in model.s_lw_offs for x in model.s_gender for y3 in model.s_gen_merit_offs for g3 in model.s_groups_offs)
               for a in model.s_wean_times for z in model.s_season_types for i in model.s_tol)

    return stock #- infastrucure - purchases

#     purchases = sum(model.v_sire[g0] * model.p_cost_purch_sire[g0,c] for g0 in model.s_groups_sire)  \
#                 + sum(sum(model.v_purchase_dams[v1,w1,z,i,g1] * model.p_cost_purch_dam[v1,w1,z,i,g1,c] for v1 in model.s_dvp_dams for w1 in model.s_lw_dams for g1 in model.s_groups_dams)
#                     + sum(model.v_purchase_offs[v3,w3,z,i,g3] * model.p_cost_purch_offs[v3,w3,z,i,g3,c] for v3 in model.s_dvp_offs for w3 in model.s_lw_offs for g3 in model.s_groups_offs)
#                     for z in model.s_season_types for i in model.s_tol)
#     return stock - infastrucure - purchases


def stock_cost(model):
    # infrastrucure = sum(model.p_rm_stockinfra[h3,c] for c in model.s_cashflow_periods * model.v_infrastructure[h3] for h3 in model.s_infrastructure)
    stock = sum(model.v_sire[g0] * model.p_cost_sire[g0] for g0 in model.s_groups_sire) \
            + sum(sum(model.v_dams[k2,t1,v1,a,n1,w1,z,i,y1,g1] * model.p_cost_dams[k2,t1,v1,a,n1,w1,z,i,y1,g1]
                     for k2 in model.s_k2_birth_dams for t1 in model.s_sale_dams for v1 in model.s_dvp_dams for n1 in model.s_nut_dams
                     for w1 in model.s_lw_dams for y1 in model.s_gen_merit_dams for g1 in model.s_groups_dams)
                + sum(model.v_offs[k3,k5,t3,v3,n3,w3,z,i,a,x,y3,g3]  * model.p_cost_offs[k3,k5,t3,v3,n3,w3,z,i,a,x,y3,g3]
                      for k3 in model.s_k3_damage_offs for k5 in model.s_k5_birth_offs for t3 in model.s_sale_offs for v3 in model.s_dvp_offs
                      for n3 in model.s_nut_offs for w3 in model.s_lw_offs for x in model.s_gender for y3 in model.s_gen_merit_offs for g3 in model.s_groups_offs)
               for a in model.s_wean_times for z in model.s_season_types for i in model.s_tol)
    # purchases = sum(sum(model.v_purchase_dams[v1,w1,z,i,g1] * sum(model.p_cost_purch_dam[v1,w1,z,i,g1,c] for c in model.s_cashflow_periods) for v1 in model.s_dvp_dams for w1 in model.s_lw_dams for g1 in model.s_groups_dams)
    #                 +sum(model.v_purchase_offs[v3,w3,z,i,g3] * sum(model.p_cost_purch_offs[v3,w3,z,i,g3,c] for c in model.s_cashflow_periods) for v3 in model.s_dvp_offs for w3 in model.s_lw_offs for g3 in model.s_groups_offs)
    return  stock #+ infrastrucure + purchases
#
#
def stock_labour_anyone(model,p5):
    # infastrucure = sum(model.p_lab_stockinfra[h3,p5] * model.v_infrastructure[h3,p5] for h3 in model.s_infrastructure)
    stock = sum(model.v_sire[g0] * model.p_lab_anyone_sire[g0,p5] for g0 in model.s_groups_sire)\
            + sum(sum(model.v_dams[k2,t1,v1,a,n1,w1,z,i,y1,g1] * model.p_lab_anyone_dams[k2,p5,t1,v1,a,n1,w1,z,i,y1,g1]
                     for k2 in model.s_k2_birth_dams for t1 in model.s_sale_dams for v1 in model.s_dvp_dams for n1 in model.s_nut_dams
                     for w1 in model.s_lw_dams for y1 in model.s_gen_merit_dams for g1 in model.s_groups_dams)
                + sum(model.v_offs[k3,k5,t3,v3,n3,w3,z,i,a,x,y3,g3]  * model.p_lab_anyone_offs[k3,k5,p5,t3,v3,n3,w3,z,i,a,x,y3,g3]
                      for k3 in model.s_k3_damage_offs for k5 in model.s_k5_birth_offs for t3 in model.s_sale_offs for v3 in model.s_dvp_offs
                      for n3 in model.s_nut_offs for w3 in model.s_lw_offs for x in model.s_gender for y3 in model.s_gen_merit_offs for g3 in model.s_groups_offs)
               for a in model.s_wean_times for z in model.s_season_types for i in model.s_tol)
    return stock
#


# def stock_dep(model):
#     return sum(model.p_dep_stockinfra[h3]  * model.v_infrastructure[h3] for h3 in model.s_infrastructure)

#
# def stock_asset(model):
#     infastrucure = sum(model.p_asset_stockinfra[h3] * model.v_infrastructure[h3] for h3 in model.s_infrastructure)
#     stock = sum(model.v_sire[g0] * model.p_asset_sire[g0] for g0 in model.s_groups_sire)
#           + sum(sum(sum(sum(model.v_dams[t1,v1,a,b1,n1,w1,z,i,y1,g1,r1,r2,r3,r4,r5,r6,r7] for r1 in model.s_co_conception for r2 in model.s_co_bw for r3 in  model.s_co_ww)
#                     * model.p_asset_dams[t1,v1,a,b1,n1,w1,z,i,y1,g1,r4,r5,r6,r7] for t1 in model.s_sale_dams)
#                     + sum(model.v_dams2sire[v1,a,b1,n1,w1,z,i,y1,g1,r1,r2,r3,r4,r5,r6,r7,g1_new] for r1 in model.s_co_conception for r2 in model.s_co_bw for r3 in  model.s_co_ww for g1_new in model.s_groups_dams)
#                     * model.p_asset_trans_dams[v1,a,b1,n1,w1,z,i,y1,g1,r4,r5,r6,r7]
#                     for v1 in model.s_dvp_dams for b1 in model.s_k2_birth_dams for n1 in model.s_nut_dams for w1 in model.s_lw_dams for y1 in model.s_gen_merit_dams for g1 in model.s_groups_dams)
#           + sum(sum(model.v_offs[t3,v3,n3,w3,z,i,d,a,b3,x,y3,g3,r4,r5,r6,r7] * model.p_asset_offs[t3,v3,n3,w3,z,i,d,a,b3,x,y3,g3,r4,r5,r6,r7] for t3 in model.s_sale_offs)
#                 + sum(model.v_offs2dam[v3,n3,w3,z,i,d,a,b3,x,y3,g3,r4,r5,r6,r7,g1_new] for g1_new in model.s_groups_dams)
#                 * model.p_asset_trans_offs[v3,n3,w3,z,i,d,a,b3,x,y3,g3,r4,r5,r6,r7] for v3 in model.s_dvp_offs  for n3 in model.s_nut_offs for w3 in model.s_lw_offs for d in model.s_k3_damage_offs for b3 in model.s_k5_birth_offs for x in model.s_gender for y3 in model.s_gen_merit_offs for g3 in model.s_groups_offs)
#           for a in model.s_wean_times for z in model.s_season_types for i in model.s_tol for r4 in model.s_co_cfw for r5 in model.s_co_fd for r6 in model.s_co_min_fd for r7 in model.s_co_fl)
#     return infastrucure + stock
#
#

##################################
# old methods used to find speed #
##################################

    # try:
    #     model.del_component(model.con_damR_index)
    #     model.del_component(model.con_damR)
    # except AttributeError:
    #     pass
    # def damR(model,k29,v1,a,z,i,y1,g1,w9):
    #     v1_prev = list(model.s_dvp_dams)[list(model.s_dvp_dams).index(v1) - 1]  #used to get the activity number from the last period - to determine the number of dam provided into this period
    #     con = sum(model.v_dams[k28,t1,v1,a,n1,w8,z,i,y1,g1] * model.p_numbers_req_dams[k28,k29,v1,a,n1,w8,z,i,y1,g1,w9]
    #                - model.v_dams[k28,t1,v1_prev,a,n1,w8,z,i,y1,g1] * model.p_numbers_prov_dams[k28,k29,t1,v1_prev,a,n1,w8,z,i,y1,g1,w9]
    #                for t1 in model.s_sale_dams for k28 in model.s_k2_birth_dams for n1 in model.s_nut_dams for w8 in model.s_lw_dams
    #                if model.p_numbers_req_dams[k28,k29,v1,a,n1,w8,z,i,y1,g1,w9] !=0 or model.p_numbers_prov_dams[k28,k29,t1,v1_prev,a,n1,w8,z,i,y1,g1,w9] !=0) <= 0
    #         # + sum(model.v_dams2sire[v1,a,b1,n1,w1,z,i,y1,g1,g1_new]
    #         #       - model.v_dams2sire[v1_prev,a,b1,n1,w1,z,i,y1,g1,g1_new] * model.p_dam2sire_numbers[v1,a,b1,n1,w1,z,i,y1,g1,g1_new]
    #         #       for n1 in model.s_nut_dams for g1_new in model.s_groups_dams) \
    #         # - model.v_purchase_dams[v1,w1,z,i,g1] * model.p_numberpurch_dam[v1,a,b1,w1,z,i,y1,g1] \ #p_numpurch allocates the purchased dams into certain sets, in this case it is correct to multiply a var with less sets to a param with more sets
    #         # - sum(model.v_offs2dam[v3,n3,w3,z3,i3,d,a3,b3,x,y3,g3,g1_off] * model.p_offs2dam_numbers[v3,n3,w3,z3,i3,d,a3,b3,x,y3,g3,g1_off,v1,a,b1,w1,z,i,y1,g1]
    #         #       for v3 in model.s_dvp_offs for n3 in model.s_nut_offs for w3 in model.s_lw_offs for z3 in model.s_season_types for i3 in model.s_tol for d in model.s_k3_damage_offs for a3 in model.s_wean_times
    #         #       for b3 in model.s_k5_birth_offs for x in model.s_gender for y3 in model.s_gen_merit_offs for g3 in model.s_groups_offs for g1_off in model.s_groups_dams)  #have to track off sets so only they are summed.
    #     ###if statement required to handle the constraints that dont exist due to lw clustering
    #     # if sum(model.p_numbers_req_dams[k28,k29,v1,a,n1,w8,z,i,y1,g1,w9] for k28 in model.s_k2_birth_dams for n1 in model.s_nut_dams for w8 in model.s_lw_dams if model.p_numbers_req_dams[k28,k29,v1,a,n1,w8,z,i,y1,g1,w9] !=0) ==0 and sum(model.p_numbers_prov_dams[k28,k29,t1,v1_prev,a,n1,w8,z,i,y1,g1,w9]
    #     #         for t1 in model.s_sale_dams for k28 in model.s_k2_birth_dams for n1 in model.s_nut_dams for w8 in model.s_lw_dams if model.p_numbers_prov_dams[k28,k29,t1,v1_prev,a,n1,w8,z,i,y1,g1,w9] !=0)==0:
    #     #     pass
    #     if type(con)==bool:
    #         return pe.Constraint.Skip
    #     else: return con

    # try:
    #     model.del_component(model.con_damR_index)
    #     model.del_component(model.con_damR)
    # except AttributeError:
    #     pass
    # def damR1(model,k29,v1,a,z,i,y1,g1,w9):
    #     v1_prev = list(model.s_dvp_dams)[list(model.s_dvp_dams).index(v1) - 1]  #used to get the activity number from the last period - to determine the number of dam provided into this period
    #     con = sum(model.v_dams[k28,t1,v1,a,n1,w8,z,i,y1,g1] * model.p_numbers_req_dams[k28,k29,v1,a,n1,w8,z,i,y1,g1,w9]
    #                - model.v_dams[k28,t1,v1_prev,a,n1,w8,z,i,y1,g1] * model.p_numbers_prov_dams[k28,k29,t1,v1_prev,a,n1,w8,z,i,y1,g1,w9]
    #                for t1 in model.s_sale_dams for k28 in model.s_k2_birth_dams for n1 in model.s_nut_dams for w8 in model.s_lw_dams
    #                if model.p_numbers_req_dams[k28,k29,v1,a,n1,w8,z,i,y1,g1,w9] !=0) <= 0
    #     if type(con)==bool:
    #         return pe.Constraint.Skip
    #     else: return con
    # start=time.time()
    # # model.con_damR = pe.Constraint(model.s_k2_birth_dams, model.s_dvp_dams, model.s_wean_times, model.s_season_types, model.s_tol, model.s_gen_merit_dams, model.s_groups_dams, model.s_lw_dams, rule=damR1, doc='transfer of off to dam and dam from last dvp to current dvp.')
    # end=time.time()
    # print('method 1: ',end-start)

    # ##method 2
    # try:
    #     model.del_component(model.con_damR_index)
    #     model.del_component(model.con_damR)
    # except AttributeError:
    #     pass
    # def damR2(model,k29,v1,a,z,i,y1,g1,w9):
    #     v1_prev = list(model.s_dvp_dams)[list(model.s_dvp_dams).index(v1) - 1]  #used to get the activity number from the last period - to determine the number of dam provided into this period
    #     ##skip constraint if the require param is 0
    #     if not any(model.p_numbers_req_dams[k28,k29,v1,a,n1,w8,z,i,y1,g1,w9] for k28 in model.s_k2_birth_dams for n1 in model.s_nut_dams for w8 in model.s_lw_dams):
    #         return pe.Constraint.Skip
    #     return sum(model.v_dams[k28,t1,v1,a,n1,w8,z,i,y1,g1] * model.p_numbers_req_dams[k28,k29,v1,a,n1,w8,z,i,y1,g1,w9]
    #                - model.v_dams[k28,t1,v1_prev,a,n1,w8,z,i,y1,g1] * model.p_numbers_prov_dams[k28,k29,t1,v1_prev,a,n1,w8,z,i,y1,g1,w9]
    #                for t1 in model.s_sale_dams for k28 in model.s_k2_birth_dams for n1 in model.s_nut_dams for w8 in model.s_lw_dams
    #                if model.p_numbers_req_dams[k28,k29,v1,a,n1,w8,z,i,y1,g1,w9] !=0) <= 0
    # start=time.time()
    # model.con_damR = pe.Constraint(model.s_k2_birth_dams, model.s_dvp_dams, model.s_wean_times, model.s_season_types, model.s_tol, model.s_gen_merit_dams, model.s_groups_dams, model.s_lw_dams, rule=damR2, doc='transfer of off to dam and dam from last dvp to current dvp.')
    # end=time.time()
    # print('method 2: ',end-start)



