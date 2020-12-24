#!/usr/bin/python
# -*- coding: UTF-8 -*-
__author__ = "HugeChaos"

from gurobipy import *
import copy
import os


def sbox(var1, var2, ine):
    statement = ""
    for row in ine:
        temp = []
        for u in range(0, 8):
            temp.append(str(row[u]) + " " + var1[7 - u])
        for v in range(0, 8):
            temp.append(str(row[v + 8]) + " " + var2[7 - v])
        temp1 = " + ".join(temp)
        temp1 = temp1.replace("+ -", "- ")
        s = str(-row[16])
        s = s.replace("--", "")
        temp1 += " >= " + s + "\n"
        statement += temp1
    return statement


def sbox_layer(var1, var2, ine):
    statement = ""
    for i in range(0, 4):
        statement += sbox(var1[8*i:8*(i+1)], var2[8*i:8*(i+1)], ine)
    return statement


def var_dec1(var):
    return ["{}_{}".format(var, i) for i in range(0, 32)]


def left_rotation(var, num):
    res = ["" for ii in range(0, 32)]
    for i in range(0, 32):
        res[i] = var[(i - num) % 32]
    return res


def mds(var1, var2, auxiliary_var_head):
    statement = ""
    auxiliary_var = []
    a0 = var_dec1("{}_{}".format(auxiliary_var_head, 0))
    auxiliary_var.append(copy.deepcopy(a0))
    a1 = var_dec1("{}_{}".format(auxiliary_var_head, 1))
    auxiliary_var.append(copy.deepcopy(a1))
    a2 = var_dec1("{}_{}".format(auxiliary_var_head, 2))
    auxiliary_var.append(copy.deepcopy(a2))
    a3 = var_dec1("{}_{}".format(auxiliary_var_head, 3))
    auxiliary_var.append(copy.deepcopy(a3))
    a4 = var_dec1("{}_{}".format(auxiliary_var_head, 4))
    auxiliary_var.append(copy.deepcopy(a4))

    b0 = copy.deepcopy(a0)
    b1 = copy.deepcopy(left_rotation(a1, 2))
    b2 = copy.deepcopy(left_rotation(a2, 10))
    b3 = copy.deepcopy(left_rotation(a3, 18))
    b4 = copy.deepcopy(left_rotation(a4, 24))

    for i in range(0, 32):
        statement += "{} + {} + {} + {} + {} - {} = 0\n".format(a0[i], a1[i], a2[i], a3[i], a4[i], var1[i])
    for i in range(0, 32):
        statement += "{} + {} + {} + {} + {} - {} = 0\n".format(b0[i], b1[i], b2[i], b3[i], b4[i], var2[i])

    return statement, auxiliary_var


def var_dec(var, rou):
    return ["{}_{}_{}".format(var, rou, i) for i in range(0, 32)]


def copy1(var1, var2, var3):
    statement = ""
    for i in range(0, len(var1)):
        statement += "{} + {} - {} = 0\n".format(var2[i], var3[i], var1[i])
    return statement


def xor1(var1, var2, var3):
    statement = ""
    for i in range(0, len(var1)):
        statement += "{} + {} - {} = 0\n".format(var1[i], var2[i], var3[i])
    return statement


def xor3(var1, var2, var3, var4):
    statement = ""
    for i in range(0, len(var1)):
        statement += "{} + {} + {} - {} = 0\n".format(var1[i], var2[i], var3[i], var4[i])
    return statement


def propagate(cd):
    statement = ""
    all_var = []
    x00 = var_dec("x0", 0)
    x01 = var_dec("x1", 0)
    x02 = var_dec("x2", 0)
    x03 = var_dec("x3", 0)
    begin_var = copy.deepcopy(x00 + x01 + x02 + x03)
    for rou in range(0, cd["total_round"]):
        all_var.append(copy.deepcopy(x00))
        all_var.append(copy.deepcopy(x01))
        all_var.append(copy.deepcopy(x02))
        all_var.append(copy.deepcopy(x03))

        y0 = var_dec("y0", rou)
        all_var.append(copy.deepcopy(y0))
        y1 = var_dec("y1", rou)
        all_var.append(copy.deepcopy(y1))
        y2 = var_dec("y2", rou)
        all_var.append(copy.deepcopy(y2))
        y3 = var_dec("y3", rou)
        all_var.append(copy.deepcopy(y3))
        y4 = var_dec("y4", rou)
        all_var.append(copy.deepcopy(y4))
        y5 = var_dec("y5", rou)
        all_var.append(copy.deepcopy(y5))

        x10 = var_dec("x0", rou + 1)
        x11 = var_dec("x1", rou + 1)
        x12 = var_dec("x2", rou + 1)
        x13 = var_dec("x3", rou + 1)

        statement += copy1(copy.deepcopy(x00), copy.deepcopy(y0), copy.deepcopy(x11))
        statement += copy1(copy.deepcopy(x01), copy.deepcopy(y1), copy.deepcopy(x12))
        statement += copy1(copy.deepcopy(x02), copy.deepcopy(y2), copy.deepcopy(x13))
        statement += xor3(copy.deepcopy(y0), copy.deepcopy(y1), copy.deepcopy(y2), copy.deepcopy(y3))
        statement += sbox_layer(copy.deepcopy(y3), copy.deepcopy(y4), cd["inequalities"])
        statement1, aux_var1 = mds(copy.deepcopy(y4), copy.deepcopy(y5), "t_{}".format(rou))
        statement += statement1
        all_var += copy.deepcopy(aux_var1)
        statement += xor1(copy.deepcopy(x03), copy.deepcopy(y5), copy.deepcopy(x10))
        x00 = copy.deepcopy(x10)
        x01 = copy.deepcopy(x11)
        x02 = copy.deepcopy(x12)
        x03 = copy.deepcopy(x13)

    all_var.append(copy.deepcopy(x00))
    all_var.append(copy.deepcopy(x01))
    all_var.append(copy.deepcopy(x02))
    all_var.append(copy.deepcopy(x03))
    end_var = copy.deepcopy(x00 + x01 + x02 + x03)
    return begin_var, end_var, statement, all_var


def head():
    return "Minimize\n\nSubject To\n"


def var_assign_value(var, value):
    statement = ""
    for i in range(0, 128):
        statement += "{} = {}\n".format(var[i], value[i])
    return statement


def trailer(all_var):
    statement = "Binary\n"
    for var in all_var:
        for i in range(0, len(var)):
            statement += "{}\n".format(var[i])
    statement += "END"
    return statement


def model(cd):
    statement = head()
    begin_var, end_var, statement1, all_var = propagate(cd)
    statement += var_assign_value(copy.deepcopy(begin_var), copy.deepcopy(cd["b"]))
    statement += statement1
    statement += var_assign_value(copy.deepcopy(end_var), copy.deepcopy(cd["e"]))
    statement += trailer(all_var)
    if os.path.exists(cd["solve_file"]):
        os.remove(cd["solve_file"])
    f = open(cd["solve_file"], "w")
    f.write(statement)
    f.close()


def model_solve(milp_file):
    m = read(milp_file)
    m.optimize()
    if m.Status == 2:
        return False
    elif m.Status == 3:
        return True
    else:
        print("unknown error!")
