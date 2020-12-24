#!/usr/bin/python
# -*- coding: UTF-8 -*-
__author__ = "HugeChaos"

from gurobipy import *
import ITUbee.ITUbee_specify
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
    for i in range(0, 5):
        statement += sbox(var1[8*i:8*(i+1)], var2[8*i:8*(i+1)], ine)
    return statement


def get_auxiliary_var(head1):
    auxiliary_var = []
    mat = ITUbee.ITUbee_specify.dl
    for r in range(0, len(mat)):
        for c in range(0, len(mat[0])):
            if mat[r][c] != 0:
                auxiliary_var.append("{}_{}_{}".format(head1, r, c))
    return auxiliary_var


def mds1(var1, var2, auxiliary_var_head):
    statement = ""
    auxiliary_var = get_auxiliary_var(auxiliary_var_head)
    mat = ITUbee.ITUbee_specify.dl
    for j in range(0, len(mat[0])):
        temp = []
        for i in range(0, len(mat)):
            if mat[i][j] == 1:
                temp.append("{}_{}_{}".format(auxiliary_var_head, i, j))
        t = " + ".join(temp)
        statement += "{} - {} = 0\n".format(t, var1[j])
    for i in range(0, len(mat)):
        temp = []
        for j in range(0, len(mat[0])):
            if mat[i][j] == 1:
                temp.append("{}_{}_{}".format(auxiliary_var_head, i, j))
        t = " + ".join(temp)
        statement += "{} - {} = 0\n".format(t, var2[i])
    return statement, auxiliary_var


def dll(var1, var2, auxiliary_head):
    statement = ""
    auxiliary_var = []
    for i in range(0, 8):
        v1 = [var1[i], var1[i + 8], var1[i + 16], var1[i + 24], var1[i+32]]
        v2 = [var2[i], var2[i + 8], var2[i + 16], var2[i + 24], var2[i+32]]
        statement1, auxiliary_var1 = mds1(v1, v2, "{}_{}".format(auxiliary_head, i))
        statement += statement1
        auxiliary_var += copy.deepcopy(auxiliary_var1)
    return statement, auxiliary_var


def var_dec(var, rou):
    return ["{}_{}_{}".format(var, rou, i) for i in range(0, 40)]


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


def propagate(cd):
    statement = ""
    all_var = []
    x = var_dec("x", 0)
    y = var_dec("y", 0)
    begin_var = copy.deepcopy(x + y)
    for rou in range(0, cd["total_round"]):
        all_var.append(copy.deepcopy(x))
        all_var.append(copy.deepcopy(y))

        x1 = var_dec("x", rou + 1)
        y1 = var_dec("y", rou + 1)

        z0 = var_dec("z0", rou)
        all_var.append(copy.deepcopy(z0))
        z1 = var_dec("z1", rou)
        all_var.append(copy.deepcopy(z1))
        z2 = var_dec("z2", rou)
        all_var.append(copy.deepcopy(z2))
        z3 = var_dec("z3", rou)
        all_var.append(copy.deepcopy(z3))
        z4 = var_dec("z4", rou)
        all_var.append(copy.deepcopy(z4))
        z5 = var_dec("z5", rou)
        all_var.append(copy.deepcopy(z5))
        z6 = var_dec("z6", rou)
        all_var.append(copy.deepcopy(z6))
        z7 = var_dec("z7", rou)
        all_var.append(copy.deepcopy(z7))

        statement += copy1(copy.deepcopy(y), copy.deepcopy(z0), copy.deepcopy(x1))

        statement += sbox_layer(copy.deepcopy(z0), copy.deepcopy(z1), cd["inequalities"])
        statement1, aux_var1 = dll(copy.deepcopy(z1), copy.deepcopy(z2), "t0_{}".format(rou))
        statement += statement1
        all_var.append(copy.deepcopy(aux_var1))

        statement += sbox_layer(copy.deepcopy(z2), copy.deepcopy(z3), cd["inequalities"])
        statement2, aux_var2 = dll(copy.deepcopy(z3), copy.deepcopy(z4), "t1_{}".format(rou))
        statement += statement2
        all_var.append(copy.deepcopy(aux_var2))

        statement += sbox_layer(copy.deepcopy(z4), copy.deepcopy(z5), cd["inequalities"])
        statement3, aux_var3 = dll(copy.deepcopy(z5), copy.deepcopy(z6), "t2_{}".format(rou))
        statement += statement3
        all_var.append(copy.deepcopy(aux_var3))

        statement += sbox_layer(copy.deepcopy(z6), copy.deepcopy(z7), cd["inequalities"])

        statement += xor1(copy.deepcopy(x), copy.deepcopy(z7), copy.deepcopy(y1))

        x = copy.deepcopy(x1)
        y = copy.deepcopy(y1)
    all_var.append(copy.deepcopy(x))
    all_var.append(copy.deepcopy(y))
    end_var = copy.deepcopy(x + y)
    return begin_var, end_var, statement, all_var


def head():
    return "Minimize\n\nSubject To\n"


def var_assign_value(var, value):
    statement = ""
    for i in range(0, 80):
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
