'''
THis is where you can set up constraints on individual variables
withing a set of variables. This will act as bounds.

bounds are all controlled from this module
'''

import numpy as np
import pandas as pd

import Functions as fun
import Sensitivity as sen
import UniversalInputs as uinp
import PropertyInputs as pinp
from CreateModel import model
import pyomo.environ as pe


'''
Bounds
- lo bound on rotations
- stocking rate must equal specified level

note:
-forcing sale/retention of drys is done in the stock module (there are inputs which user can control this with)
'''


def boundarypyomo_local():

    ##set bounds to include
    bounds_inc=True #controls all bounds (typically on)
    rot_lobound_inc = False #controls rot bound
    sr_bound_inc = False #controls sr bound
    total_pasture_bound = fun.f_sa(False, sen.sav['bnd_pasarea_inc'], 5)  #bound on total pasture (hence also total crop)
    landuse_bound = False #bound on area of each landuse


    if bounds_inc:
        print('bounds implemented - make sure they are correct')

        ###########################
        # initialise array        #
        ###########################
        '''initialise arrays which are used as bounds'''

        ##keys to build arrays
        arrays = [model.s_phases, model.s_lmus]
        index_rl = fun.cartesian_product_simple_transpose(arrays)


        ##build array
        rot_lobound_rl = np.zeros((len(model.s_phases), len(model.s_lmus)))
        pasture_dse_carry = {} #populate straight into dict
        ##landuse area abound - note that setting to zero is the equivelent of no bound
        landuse_bound_k = pd.Series(0,index=model.s_landuses) #use landuse2 because that is the expanded version of pasture phases eg t, tr not just tedera

        ###########################
        # set bound               #
        ###########################
        '''set the bound here, can do this like assigning any value to numpy.
            These could be adjusted with SA values if you want to alter the bounds for different trials
            - The forced sale or retain of drys is controled by livestock generator inputs'''
        ##rot
        rot_lobound_rl[0,2] = 150
        ##sr - carry cap of each ha of each pasture
        for t, pasture in enumerate(uinp.structure['pastures']):
            pasture_dse_carry[pasture] = pinp.sheep['i_sr_constraint_t'][t]

        ##total pas area
        total_pas_area = sen.sav['bnd_total_pas_area']

        ##landuse area abound - note that setting to zero is the equivelent of no bound
        landuse_bound_k.iloc[0] = 50

        #################################
        # ravel and zip bound and dict  #
        #################################
        ##rotation
        rot_lobound = rot_lobound_rl.ravel()
        tup_rl = tuple(map(tuple, index_rl))
        rot_lobound = dict(zip(tup_rl, rot_lobound))
        ##landuse area abound - note that setting to zero is the equivelent of no bound
        landuse_area_bound = dict(landuse_bound_k)


        #################################
        # build the constraint          #
        #################################
        ##rotations
        if rot_lobound_inc:
            try:
                model.del_component(model.con_rotation_lobound)
                model.del_component(model.con_rotation_lobound_index)
            except AttributeError:
                pass
            def rot_lo_bound(model, r, l):
                return model.v_phase_area[r, l] >= rot_lobound[r,l]
            model.con_rotation_lobound = pe.Constraint(model.s_phases, model.s_lmus, rule=rot_lo_bound,
                                                    doc='lo bound for the number of each phase')

        ##SR - this cant set the sr on an actual pasture but it means different pastures provide a different level of carry capacity although nothing fixes sheep to that pasture
        if sr_bound_inc:
            try:
                model.del_component(model.con_SR_bound)
                model.del_component(model.con_SR_bound_index)
            except AttributeError:
                pass
            def SR_bound(model, p6):
                return(
                - sum(model.v_phase_area[r, l] * model.p_pasture_area[r, t] * pasture_dse_carry[t] for r in model.s_phases for l in model.s_lmus for t in model.s_pastures)
                + sum(model.v_sire[g0] * model.p_dse_sire[p6,g0] for g0 in model.s_groups_sire if model.p_dse_sire[p6,g0]!=0)
                + sum(sum(model.v_dams[k2,t1,v1,a,n1,w1,z,i,y1,g1] * model.p_dse_dams[k2,p6,t1,v1,a,n1,w1,z,i,y1,g1]
                         for k2 in model.s_k2_birth_dams for t1 in model.s_sale_dams for v1 in model.s_dvp_dams for n1 in model.s_nut_dams
                         for w1 in model.s_lw_dams for y1 in model.s_gen_merit_dams for g1 in model.s_groups_dams if model.p_dse_dams[k2,p6,t1,v1,a,n1,w1,z,i,y1,g1]!=0)
                    + sum(model.v_offs[k3,k5,t3,v3,n3,w3,z,i,a,x,y3,g3]  * model.p_dse_offs[k3,k5,p6,t3,v3,n3,w3,z,i,a,x,y3,g3]
                          for k3 in model.s_k3_damage_offs for k5 in model.s_k5_birth_offs for t3 in model.s_sale_offs for v3 in model.s_dvp_offs
                          for n3 in model.s_nut_offs for w3 in model.s_lw_offs for x in model.s_gender for y3 in model.s_gen_merit_offs for g3 in model.s_groups_offs if model.p_dse_offs[k3,k5,p6,t3,v3,n3,w3,z,i,a,x,y3,g3]!=0)
               for a in model.s_wean_times for z in model.s_season_types for i in model.s_tol) ==0)
            model.con_SR_bound = pe.Constraint(model.s_feed_periods, rule=SR_bound,
                                                doc='stocking rate bound for each feed period')

        ##total pasture area - hence also total crop area
        if total_pasture_bound != False:
            try:
                model.del_component(model.con_pas_bound)
            except AttributeError:
                pass
            def pas_bound(model):
                return(
                       sum(model.v_phase_area[r, l] * model.p_pasture_area[r, t] for r in model.s_phases for l in model.s_lmus for t in model.s_pastures)
                       == total_pas_area)
            model.con_pas_bound = pe.Constraint(rule=pas_bound, doc='bound on total pasture area')

        ##landuse bound
        if landuse_bound:
            try:
                model.del_component(model.con_landuse_bound)
            except AttributeError:
                pass
            def k_bound(model, k):
                if landuse_area_bound[k]!=0:  #bound will not be built if param == 0
                    return(
                           sum(model.v_phase_area[r, l] * model.p_landuse_area[r, k] for r in model.s_phases for l in model.s_lmus for t in model.s_pastures)
                           == landuse_area_bound[k])
                else:
                    pe.Constraint.Skip
            model.con_pas_bound = pe.Constraint(model.s_landuses, rule=k_bound, doc='bound on total pasture area')
