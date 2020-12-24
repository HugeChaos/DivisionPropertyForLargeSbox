#!/usr/bin/python
# -*- coding: UTF-8 -*-

import copy
import Camellia.Camellia_model
import time
import os
import Camellia.Camellia_specify


def weight_select1(l1, l2, l3, len1):
    if len(l3) == len1:
        l2.append(l3)
        return l2
    elif len(l1) == 0:
        return l2
    else:
        l2p = []
        for i in range(0, len(l1)):
            l3.append(l1[i])
            l2q = weight_select1(copy.deepcopy(l1[(i+1):]), copy.deepcopy(l2), copy.deepcopy(l3), len1)
            l2p += copy.deepcopy(l2q)
            l3.remove(l1[i])
        return l2p


'''
def weight_select(len1):
    l11 = [i for i in range(0, 16)]
    l22 = []
    l33 = []
    l222 = weight_select1(l11, l22, l33, len1)
    return l222
'''


def weight_select(len1):
    l11 = [0, 1, 2, 3, 4, 5, 6, 7]
    l12 = []
    l13 = []
    l14 = weight_select1(l11, l12, l13, len1)
    return l14


def get_b_search_space(len1):
    vec = weight_select(len1)
    b_search_space = list()
    for i in range(0, 16):
        for vec1 in vec:
            bi = [0 for ii in range(0, 128)]
            for kk in range(0, 128):
                if kk // 8 != i:
                    bi[kk] = 1
            for vec11 in vec1:
                bi[i * 8 + vec11] = 1
            b_search_space.append(copy.deepcopy(bi))
    return b_search_space


if __name__ == "__main__":

    cd = dict()

    cd["cipher_name"] = "Camellia"

    cd["cipher_size"] = 128

    ine0 = Camellia.Camellia_specify.inequalities_EDPPT_s0
    ine1 = Camellia.Camellia_specify.inequalities_EDPPT_s1
    ine2 = Camellia.Camellia_specify.inequalities_EDPPT_s2
    ine3 = Camellia.Camellia_specify.inequalities_EDPPT_s3

    cd["inequalities"] = [ine0, ine3, ine2, ine1, ine3, ine2, ine1, ine0]

    folder = cd["cipher_name"] + "_integral_distinguish"
    if not os.path.exists(folder):
        os.mkdir(folder)

    distinguish_find = True

    e_search_space = list()
    e_dict = dict()
    for ei in range(0, 128):
        e = [0 for eii in range(0, 128)]
        e[ei] = 1
        e_search_space.append(copy.deepcopy(e))
        e_dict[str(e)] = ei

    round_i = 7
    cd["total_round"] = round_i
    cd["record_file"] = folder + "////" + cd["cipher_name"] + "_record.txt"
    cd["time_record"] = folder + "////" + cd["cipher_name"] + "_time_record.txt"
    cd["solve_file"] = folder + "////" + cd["cipher_name"] + "_round{}.lp".format(round_i)
    t1 = time.time()
    for weight in range(5, 6):
        distinguish_find = False
        distinguish_count = 0

        cd["search_apace"] = folder + "////" + "search_weight{}.txt".format(weight)

        for b in get_b_search_space(weight):
            f = open(cd["search_apace"], "a")
            f.write(str(b) + "\n")
            f.close()

            cd["b"] = copy.deepcopy(b)
            balance_position = ["?" for bpi in range(0, 128)]
            distinguish_find1 = False
            for e in e_search_space:
                cd["e"] = copy.deepcopy(e)
                Camellia.Camellia_model.model(cd)
                flag = Camellia.Camellia_model.model_solve(cd["solve_file"])
                if flag:
                    bll = e_dict[str(e)]
                    balance_position[bll] = "b"
                    distinguish_find1 = True
            if distinguish_find1:
                distinguish_find = True
                distinguish_count += 1
                rf = open(cd["record_file"], "a")
                rf.write("*" * 20)
                rf.write("{}th  7round integral distinguish (weight = {}) based on division property"
                         " is found.\n".format(distinguish_count, weight))
                rf.write("when the values:\n")
                rf.write("b = {}\n".format(str(cd["b"])))
                rf.write("the balance position is:\n")
                for row in range(0, 128):
                    rf.write(balance_position[row])
                    if row % 8 == 7:
                        rf.write(" ")
                    if row % 32 == 31:
                        rf.write("\n")
                rf.close()
        if distinguish_find:
            break
    t2 = time.time()
    f = open(cd["time_record"], "w")
    f.write("this process cost time total {}".format(t2 - t1))
    f.close()
