#!/usr/bin/python
# -*- coding: UTF-8 -*-

import copy
import ITUbee.ITUbee_model
import time
import os
import ITUbee.ITUbee_specify
import ITUbee.test_vector

if __name__ == "__main__":

    cd = dict()

    cd["cipher_name"] = "ITUbee"

    cd["cipher_size"] = 80

    cd["inequalities"] = ITUbee.ITUbee_specify.inequalities_EDPPT1

    folder = cd["cipher_name"] + "_compare_max_round_edppt1"
    if not os.path.exists(folder):
        os.mkdir(folder)

    distinguish_find = True

    search_space = ITUbee.test_vector.tv1

    round_i = 6
    cd["record_file"] = folder + "////" + cd["cipher_name"] + "_record.txt"
    cd["time_record"] = folder + "////" + cd["cipher_name"] + "_time_record.txt"
    total_search = len(search_space)
    ttt1 = time.time()

    cd["solve_file"] = folder + "////" + cd["cipher_name"] + "_round{}.lp".format(round_i)
    t1 = time.time()
    search_count = 0
    cd["total_round"] = round_i
    for ss in search_space:
        cd["b"] = copy.deepcopy(ss[0])
        cd["e"] = copy.deepcopy(ss[1])

        t11 = time.time()
        search_count += 1
        ITUbee.ITUbee_model.model(cd)
        flag = ITUbee.ITUbee_model.model_solve(cd["solve_file"])
        t22 = time.time()
        print(t22 - t11)
        if flag:
            rf = open(cd["record_file"], "a")
            rf.write("*" * 20)
            rf.write("{} round integral distinguish based on division property is found.\n".format(round_i))
            rf.write("when the values:\n")
            rf.write("b = {}\n".format(str(cd["b"])))
            rf.write("e = {}\n".format(str(cd["e"])))
            rf.close()
        print("testing: round = {}, search_count = {}, total_search = {}".format(round_i, search_count, total_search))
    t2 = time.time()
    tf = open(cd["time_record"], "a")
    tf.write("This process total cost time {} seconds.\n\n".format(t2- t1))
    tf.close()
