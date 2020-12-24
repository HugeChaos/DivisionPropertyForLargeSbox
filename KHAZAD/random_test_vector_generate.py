#!/usr/bin/python
# -*- coding: UTF-8 -*-
__author__ = "HugeChaos"


import random
import copy


def generate_random_test_vector0(bound):
    search_space = list()
    count = 0
    while count < bound:
        weight = random.randint(1, 63)
        b = [0 for bii in range(0, 64)]
        e = [0 for eii in range(0, 64)]
        weight_l = []
        while len(weight_l) < weight:
            bi = random.randint(1, 63)
            if bi not in weight_l:
                weight_l.append(bi)
        for wl in weight_l:
            b[wl] = 1
        ei = random.randint(1, 63)
        e[ei] = 1
        sp = copy.deepcopy([copy.deepcopy(b), copy.deepcopy(e)])
        if sp not in search_space:
            search_space.append(sp)
            count += 1
    f = open("test_vector.py", "w")
    f.write("#!/usr/bin/python\n# -*- coding: UTF-8 -*-\n\n")
    f.write("tv0 = [")
    for i in range(0, bound):
        f.write(str(search_space[i]))
        if i != bound - 1:
            f.write(",\n")
    f.write("]")
    f.close()


def generate_random_test_vector1(bound):
    search_space = list()
    count = 0
    while count < bound:
        b = [1 for bii in range(0, 64)]
        e = [0 for eii in range(0, 64)]

        bi = random.randint(1, 63)
        b[bi] = 0

        ei = random.randint(0, 63)
        e[ei] = 1
        sp = copy.deepcopy([copy.deepcopy(b), copy.deepcopy(e)])
        if sp not in search_space:
            search_space.append(sp)
            count += 1
    f = open("test_vector.py", "a")
    f.write("\n\n\ntv1 = [")
    for i in range(0, bound):
        f.write(str(search_space[i]))
        if i != bound - 1:
            f.write(",\n")
    f.write("]")
    f.close()


generate_random_test_vector0(1024)
generate_random_test_vector1(1024)
