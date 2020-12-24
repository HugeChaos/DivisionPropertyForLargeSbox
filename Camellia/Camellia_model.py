#!/usr/bin/python
# -*- coding: UTF-8 -*-
__author__ = "HugeChaos"

from gurobipy import *
import Camellia.Camellia_specify
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
    for i in range(0, 8):
        statement += sbox(var1[8*i:8*(i+1)], var2[8*i:8*(i+1)], ine[i])
    return statement


def get_auxiliary_var(head1):
    auxiliary_var = []
    mat = Camellia.Camellia_specify.dl
    for r in range(0, len(mat)):
        for c in range(0, len(mat[0])):
            if mat[r][c] != 0:
                auxiliary_var.append("{}_{}_{}".format(head1, r, c))
    return auxiliary_var


def mds1(var1, var2, auxiliary_var_head):
    statement = ""
    auxiliary_var = get_auxiliary_var(auxiliary_var_head)
    mat = Camellia.Camellia_specify.dl
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
        v1 = []
        v2 = []
        for j in range(0, 8):
            v1.append(var1[i + 8 * (7 - j)])
            v2.append(var2[i + 8 * (7 - j)])

        statement1, auxiliary_var1 = mds1(v1, v2, "{}_{}".format(auxiliary_head, i))
        statement += statement1
        auxiliary_var.append(copy.deepcopy(auxiliary_var1))
    return statement, auxiliary_var


def var_dec(var, rou):
    return ["{}_{}_{}".format(var, rou, i) for i in range(0, 64)]


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


def fl(var1, var2, auxiliary_head):
    statement = ""
    aux_var = []
    t0 = ["{}_0_{}".format(auxiliary_head, i0) for i0 in range(0, 32)]
    aux_var.append(copy.deepcopy(t0))
    t1 = ["{}_1_{}".format(auxiliary_head, i1) for i1 in range(0, 32)]
    aux_var.append(copy.deepcopy(t1))
    t2 = ["{}_2_{}".format(auxiliary_head, i2) for i2 in range(0, 32)]
    aux_var.append(copy.deepcopy(t2))
    t3 = ["{}_3_{}".format(auxiliary_head, i3) for i3 in range(0, 32)]
    aux_var.append(copy.deepcopy(t3))
    st1 = ["" for is0 in range(0, 32)]
    for ii in range(0, 32):
        st1[ii] = t1[(ii - 1) % 32]
    statement += copy1(copy.deepcopy(var1[32:64]), copy.deepcopy(t0), copy.deepcopy(t1))
    statement += xor1(copy.deepcopy(var1[0:32]), copy.deepcopy(st1), copy.deepcopy(t2))
    statement += copy1(copy.deepcopy(t2), copy.deepcopy(t3), copy.deepcopy(var2[0:32]))
    statement += xor1(copy.deepcopy(t3), copy.deepcopy(t0), copy.deepcopy(var2[32:64]))

    return statement, aux_var


def fl_inv(var1, var2, auxiliary_head):
    statement = ""
    aux_var = []
    t0 = ["{}_0_{}".format(auxiliary_head, i0) for i0 in range(0, 32)]
    aux_var.append(copy.deepcopy(t0))
    t1 = ["{}_1_{}".format(auxiliary_head, i1) for i1 in range(0, 32)]
    aux_var.append(copy.deepcopy(t1))
    t2 = ["{}_2_{}".format(auxiliary_head, i2) for i2 in range(0, 32)]
    aux_var.append(copy.deepcopy(t2))
    t3 = ["{}_3_{}".format(auxiliary_head, i3) for i3 in range(0, 32)]
    aux_var.append(copy.deepcopy(t3))
    st3 = ["" for is3 in range(0, 32)]
    for ii in range(0, 32):
        st3[ii] = t3[(ii - 1) % 32]
    statement += copy1(copy.deepcopy(var1[0:32]), copy.deepcopy(t0), copy.deepcopy(t1))
    statement += xor1(copy.deepcopy(var1[32:64]), copy.deepcopy(t0), copy.deepcopy(t2))
    statement += copy1(copy.deepcopy(t2), copy.deepcopy(t3), copy.deepcopy(var2[32:64]))
    statement += xor1(copy.deepcopy(st3), copy.deepcopy(t1), copy.deepcopy(var2[0:32]))

    return statement, aux_var


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

        if (rou != 0) and (rou % 6 == 0):

            x11 = var_dec("x11", rou)
            y11 = var_dec("y11", rou)
            all_var.append(copy.deepcopy(x11))
            all_var.append(copy.deepcopy(y11))

            statement11, aux_var11 = fl(copy.deepcopy(x), copy.deepcopy(x11), "p_{}".format(rou))
            statement12, aux_var12 = fl(copy.deepcopy(y), copy.deepcopy(y11), "q_{}".format(rou))

            statement += statement11
            statement += statement12

            all_var += copy.deepcopy(aux_var11)
            all_var += copy.deepcopy(aux_var12)

            z = var_dec("z", rou)
            all_var.append(copy.deepcopy(z))
            w = var_dec("w", rou)
            all_var.append(copy.deepcopy(w))
            v = var_dec("v", rou)
            all_var.append(copy.deepcopy(v))
            statement += copy1(copy.deepcopy(y11), copy.deepcopy(z), copy.deepcopy(x1))
            statement += sbox_layer(copy.deepcopy(z), copy.deepcopy(w), cd["inequalities"])
            statement1, aux_var1 = dll(copy.deepcopy(w), copy.deepcopy(v), "t_{}".format(rou))
            statement += xor1(copy.deepcopy(v), copy.deepcopy(x11), copy.deepcopy(y1))
            statement += statement1
            all_var += copy.deepcopy(aux_var1)
        else:
            x1 = var_dec("x", rou + 1)
            y1 = var_dec("y", rou + 1)
            z = var_dec("z", rou)
            all_var.append(copy.deepcopy(z))
            w = var_dec("w", rou)
            all_var.append(copy.deepcopy(w))
            v = var_dec("v", rou)
            all_var.append(copy.deepcopy(v))
            statement += copy1(copy.deepcopy(y), copy.deepcopy(z), copy.deepcopy(x1))
            statement += sbox_layer(copy.deepcopy(z), copy.deepcopy(w), cd["inequalities"])
            statement1, aux_var1 = dll(copy.deepcopy(w), copy.deepcopy(v), "t_{}".format(rou))

            statement += statement1
            all_var += copy.deepcopy(aux_var1)

            statement += xor1(copy.deepcopy(v), copy.deepcopy(x), copy.deepcopy(y1))

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
