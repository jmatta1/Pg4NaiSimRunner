#!/usr/bin/python
"""A simple script to set up simulation runs for the PG4 simulations of the
large volume NaI detectors"""
import sys
import os
import shutil

MIN_ENERGY = 00.010  # minimum energy to simulate in MeV
MAX_ENERGY = 15.000  # maximum energy to simulate in MeV (inclusive)
STEP_ENERGY = 0.010  # step size of energy to simulate in MeV
# 0=WideFront,     1=WideBack
# 2=LongNarrowTop, 3=LongNarrowBottom
# 4=OppositePmt,    5=PmtEnd
SIDE_LIST = [0, 2, 4]  # list of sides to simulate throwing gammas at
SIDE_FILE_NAMES = ["side0", "side2", "side4"]
PRIMARY_COUNT = [11050000, 5850000, 1530000]
# the values of primary count were decided by saying there would be 160000
# gammas thrown per square inch of surface area, the surfaces are
# 16.25*4.25 = 69 + 1/16 in^2 --> 11,050,000
# 16.25*2.25 = 36 + 9/16 in^2 -->  5,850,000
#  4.25*2.25 =  9 + 9/16 in^2 -->  1,530,000


def main():
    """Primary entry point for the code"""
    qsub_list_file = open('qsub_list', 'w')
    energy = MIN_ENERGY
    loop_num = 0
    while energy <= MAX_ENERGY:
        folder_name = make_folder_name(sys.argv[1], energy)
        # make the folder if need be
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        # generate the macros
        macro_list = generate_sim_runs(energy, folder_name, loop_num)
        fmt_dic = {}
        fmt_dic["run_macro_lines"] = "".join(macro_list)
        fmt_dic["output_dir"] = folder_name
        # now copy the root merge script into the directory'
        merge_dest = os.path.join(folder_name, "merge_hists.C")
        shutil.copyfile("./merge_hists.C", merge_dest)
        # write the qsub script
        qsub_script = file(os.path.join(folder_name, "sub_script.sh"), "w")
        qsub_script.write(QSUB_SCRIPT_TMPL.format(**fmt_dic))
        qsub_script.close()
        # add the entry to the list of qsub scripts to run
        qsub_list_file.write(os.path.join(folder_name, "sub_script.sh"))
        qsub_list_file.write("\n")
        energy += STEP_ENERGY
        loop_num += 1
    qsub_list_file.close()


def generate_sim_runs(energy, folder_name, loop_num):
    """Takes the energy and output folder name and generates the sub runs
    then returns the list of lines to run each macro"""
    temp = []
    base_run = len(SIDE_LIST) * loop_num
    run_num = 0
    for side, cnt, name in zip(SIDE_LIST, PRIMARY_COUNT, SIDE_FILE_NAMES):
        fmtdict = {}
        fmtdict["file_name"] = name + ".root"
        fmtdict["energy_in_mev"] = energy
        fmtdict["side_number"] = side
        fmtdict["particle_count"] = cnt
        fmtdict["run_num"] = (base_run + run_num)
        mname = (name + ".mac")
        macro_path = os.path.join(folder_name, mname)
        outfile = open(macro_path, 'w')
        outfile.write(MACRO_TMPL.format(**fmtdict))
        outfile.close()
        temp.append(RUN_MACRO_LINE.format(macro_name=mname))
        run_num += 1
    return temp


def make_folder_name(base_dir, energy):
    """Makes the directory name from the base directory and energy"""
    dir_pat = "{0:05.2f}_to_{1:05.2f}_MeV"
    temp = float(int(energy*2.0))/2.0
    en_str = "{0:05.2f}MeV".format(energy)
    if en_str in ["02.00MeV", "01.50MeV", "01.00MeV", "00.50MeV"]:
        temp -= 0.5
    output_dir = os.path.join(base_dir, dir_pat.format(temp + STEP_ENERGY,
                                                       temp + 0.5))
    ret_val = os.path.join(output_dir, "{0:05.2f}MeV".format(energy))
    return ret_val


QSUB_SCRIPT_TMPL = """#!/bin/bash
#PBS -M mattajt@ornl.gov

cd {output_dir:s}
cp $NAI_EXEC ./NaiSim

{run_macro_lines:s}
rm ./NaiSim

root -q -b merge_hists.C
"""


RUN_MACRO_LINE = "./NaiSim {macro_name:s}\n"


MACRO_TMPL = """/output/setRunNum {run_num:d}
/output/filename {file_name:s}
/output/setRecordLevel 2
/geom/mode BkgNaI
/run/initialize
/generator/module DetectorSurface
/detectorsurface/energy {energy_in_mev:5.2f} MeV
/detectorsurface/sidenumber {side_number:d}
/run/beamOn {particle_count:d}
"""

if __name__ == "__main__":
    main()
