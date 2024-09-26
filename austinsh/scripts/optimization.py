from models.Buses import Buses
from models.Loads import Loads
from models.Generators import Generators
from scipy import sparse

def optimize_linear(buses, branches, slack, transformer, shunt, size):
    i_linear = []
    j_linear = []
    linear_value = []
    j_row = []
    j_column = []
    j_value = []
    for ele in buses:
        ir_infeasible = ele.node_infeasible_r
        ii_infeasible = ele.node_infeasible_i
        vr = ele.node_Vr
        vi = ele.node_Vi
        lr = ele.node_lambda_r
        li = ele.node_lambda_i
        y_stamps = [
            [ir_infeasible, ir_infeasible, 2], [ir_infeasible, lr, 1],
            [ii_infeasible, ii_infeasible, 2], [ii_infeasible, li, 1],
            [vr, ir_infeasible, 1],
            [vi, ii_infeasible, 1]
        ]
        for indicies in y_stamps:
            i, j, value = indicies
            i_linear.append(i)
            j_linear.append(j)
            linear_value.append(value)
    for ele in branches:
        lr_i = Buses.bus_key_[str(ele.from_bus) + "_lambda_r"]
        li_i = Buses.bus_key_[str(ele.from_bus) + "_lambda_i"]
        lr_j = Buses.bus_key_[str(ele.to_bus) + "_lambda_r"]
        li_j = Buses.bus_key_[str(ele.to_bus) + "_lambda_i"]
        y_stamps = [
            [lr_i, lr_i, ele.conductance], [lr_i, lr_j, -ele.conductance], 
            [lr_i, li_i, -ele.se_coeff], [lr_i, li_j, ele.se_coeff],
            [lr_j, lr_j, ele.conductance], [lr_j, lr_i, -ele.conductance],
            [lr_j, li_j, -ele.se_coeff], [lr_j, li_i, ele.se_coeff],
            [li_i, li_i, ele.conductance], [li_i, li_j, -ele.conductance],
            [li_i, lr_i, ele.se_coeff], [li_i, lr_j, -ele.se_coeff],
            [li_j, li_j, ele.conductance], [li_j, li_i, -ele.conductance],
            [li_j, lr_j, ele.se_coeff], [li_j, lr_i, -ele.se_coeff],
            [lr_i, li_i, -ele.sh_coeff], [li_i, lr_i, ele.sh_coeff],
            [lr_j, li_j, -ele.sh_coeff], [li_j, lr_j, ele.sh_coeff]
        ]
        for indicies in y_stamps:
            i, j, value = indicies
            i_linear.append(i)
            j_linear.append(j)
            linear_value.append(value)
    for ele in slack:
        lr = Buses.bus_key_[str(ele.bus) + "_lambda_r"]
        li = Buses.bus_key_[str(ele.bus) + "_lambda_i"]
        lr_ir = ele.node_lambdar_ir
        li_ii = ele.node_lambdai_ii
        y_stamps = [
            [lr_ir, lr, 1], [li_ii, li, 1],
            [lr, lr_ir, 1], [li, li_ii, 1]
        ]
        for indicies in y_stamps:
            i, j, value = indicies
            i_linear.append(i)
            j_linear.append(j)
            linear_value.append(value)
    for ele in transformer:
        lr_i = Buses.bus_key_[str(ele.from_bus) + "_lambda_r"]
        li_i = Buses.bus_key_[str(ele.from_bus) + "_lambda_i"]
        lr_j = Buses.bus_key_[str(ele.to_bus) + "_lambda_r"]
        li_j = Buses.bus_key_[str(ele.to_bus) + "_lambda_i"]
        lr_ir = ele.node_LR_IR
        li_ii = ele.node_LI_II
        lr_2 = ele.node_LR_2
        li_2 = ele.node_LI_2
        y_stamps = [
            [lr_i, lr_ir, 1],
            [li_i, li_ii, 1],
            [lr_j, lr_j, ele.conductance], [lr_j, li_j, -ele.se_coeff],
            [lr_j, lr_2, -ele.conductance], [lr_j, li_2, ele.se_coeff],
            [li_j, lr_j, ele.se_coeff], [li_j, li_j, ele.conductance],
            [li_j, lr_2, -ele.se_coeff], [li_j, li_2, -ele.conductance],
            [lr_2, lr_j, -ele.conductance], [lr_2, li_j, ele.se_coeff],
            [lr_2, lr_2, ele.conductance], [lr_2, li_2, -ele.se_coeff],
            [lr_2, lr_ir, -ele.cos], [lr_2, li_ii, -ele.sin],
            [li_2, lr_j, -ele.se_coeff], [li_2, li_j, -ele.conductance],
            [li_2, lr_2, ele.se_coeff], [li_2, li_2, ele.conductance],
            [li_2, lr_ir, ele.sin], [li_2, li_ii, -ele.cos],
            [lr_ir, lr_i, 1],
            [li_ii, li_i, 1],
            [lr_ir, lr_2, -ele.cos], [lr_ir, li_2, ele.sin],
            [li_ii, lr_2, -ele.sin], [li_ii, li_2, -ele.cos]
        ]
        for indicies in y_stamps:
            i, j, value = indicies
            i_linear.append(i)
            j_linear.append(j)
            linear_value.append(value)
    for ele in shunt:
        lr = Buses.bus_key_[str(ele.bus) + "_lambda_r"]
        li = Buses.bus_key_[str(ele.bus) + "_lambda_i"]
        y_stamps = [
            [lr, lr, ele.g], [lr, li, ele.b],
            [li, lr, -ele.b], [li, li, ele.g]
        ]
        for indicies in y_stamps:
            i, j, value = indicies
            i_linear.append(i)
            j_linear.append(j)
            linear_value.append(value)
    y_matrix = sparse.coo_matrix((linear_value, (i_linear, j_linear)), shape = (size, size)).tocsr()
    j_vector = sparse.coo_matrix((j_value, (j_row, j_column)), shape = (size, 1)).tocsr()
    return y_matrix, j_vector

def optimize_nonlinear(generators, loads, pre_sol, size):
    i_nonlinear = []
    j_nonlinear = []
    nonlinear_value = []
    j_row = []
    j_column = []
    j_value = []
    for elem in loads:
        lr = Buses.bus_key_[str(elem.bus) + "_lambda_r"]
        li = Buses.bus_key_[str(elem.bus) + "_lambda_i"]
        vr = Buses.bus_key_[str(elem.bus) + "_vr"]
        vi = Buses.bus_key_[str(elem.bus) + "_vi"]
        IR_by_VR, IR_by_VI, II_by_VR, II_by_VI = Loads.pq_derivative(elem, pre_sol)
        AR_by_VR, AR_by_VI, AI_by_VR, AI_by_VI = Loads.optimize_derivative(elem, pre_sol)
        y_stamps = [
            [lr, vr, AR_by_VR], [lr, vi, AR_by_VI], [lr, lr, IR_by_VR], [lr, li, II_by_VR],
            [li, vr, AI_by_VR], [li, vi, AI_by_VI], [li, li, II_by_VI], [li, lr, IR_by_VI]
        ]
        j_LR, j_LI = Loads.optimize_history(
            elem, pre_sol, IR_by_VR, IR_by_VI, II_by_VR, II_by_VI,
            AR_by_VR, AR_by_VI, AI_by_VR, AI_by_VI
        )
        j_stamps = [
            [lr, 0, j_LR],
            [li, 0, j_LI]
        ]
        for indicies in y_stamps:
            i, j, value = indicies
            i_nonlinear.append(i)
            j_nonlinear.append(j)
            nonlinear_value.append(value)
        for index in j_stamps:
            i, j, value = index
            j_row.append(i)
            j_column.append(j)
            j_value.append(value)
    for elem in generators:
        lr = Buses.bus_key_[str(elem.bus) + "_lambda_r"]
        li = Buses.bus_key_[str(elem.bus) + "_lambda_i"]
        lq = Buses.bus_key_[str(elem.bus) + "_lambda_q"]
        vr = Buses.bus_key_[str(elem.bus) + "_vr"]
        vi = Buses.bus_key_[str(elem.bus) + "_vi"]
        q = Buses.bus_key_[str(elem.bus) + "_q"]
        (
            IR_by_Q, IR_by_VR, IR_by_VI, II_by_Q,
            II_by_VR, II_by_VI, Q_by_VR, Q_by_VI
        ) = Generators.pv_derivative(elem, pre_sol)
        (
            AR_by_VR, AR_by_VI, AR_by_Q, AI_by_VR,
            AI_by_VI, AI_by_Q, AQ_by_VR, AQ_by_VI
        ) = Generators.optimize_derivative(elem, pre_sol)
        y_stamps = [
            [lr, vr, AR_by_VR], [lr, vi, AR_by_VI], [lr, q, AR_by_Q],
            [lr, lr, IR_by_VR], [lr, li, II_by_VR], [lr, lq, Q_by_VR],
            [li, vr, AI_by_VR], [li, vi, AI_by_VI], [li, q, AI_by_Q],
            [li, lr, IR_by_VI], [li, li, II_by_VI], [li, lq, Q_by_VI],
            [lq, vr, AQ_by_VR], [lq, vi, AQ_by_VI],
            [lq, lr, IR_by_Q], [lq, li, II_by_Q]
        ]
        j_LR, j_LI, j_LQ = Generators.optimize_history(
            elem, pre_sol, IR_by_VR, IR_by_VI, II_by_VR, II_by_VI,
            IR_by_Q, Q_by_VR, Q_by_VI, II_by_Q, AR_by_VR, AR_by_VI,
            AI_by_VR, AI_by_VI, AR_by_Q, AI_by_Q, AQ_by_VR, AQ_by_VI
        )
        j_stamps = [
            [lr, 0, j_LR],
            [li, 0, j_LI],
            [lq, 0, j_LQ]
        ]
        for indicies in y_stamps:
            i, j, value = indicies
            i_nonlinear.append(i)
            j_nonlinear.append(j)
            nonlinear_value.append(value)
        for index in j_stamps:
            i, j, value = index
            j_row.append(i)
            j_column.append(j)
            j_value.append(value)
        y_matrix = sparse.coo_matrix((nonlinear_value, (i_nonlinear, j_nonlinear)), shape = (size,size)).tocsr()
        j_vector = sparse.coo_matrix((j_value, (j_row, j_column)), shape = (size, 1)).tocsr()
        return y_matrix, j_vector