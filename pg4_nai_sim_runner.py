#!/usr/bin/python
"""A simple script to set up simulation runs for the PG4 simulations of the
large volume NaI detectors"""
import sys
import os

MIN_ENERGY = 00.000  # minimum energy to simulate in MeV
MAX_ENERGY = 15.000  # maximum energy to simulate in MeV (inclusive)
STEP_ENERGY = 0.010  # step size of energy to simulate in MeV
# 0=WideFront,     1=WideBack
# 2=LongNarrowTop, 3=LongNarrowBottom
# 4=OppositePmt,    5=PmtEnd
SIDE_LIST = [0, 2, 4]  # list of sides to simulate throwing gammas at
SIDE_FILE_NAMES = ["side0", "side2", "side4"]
PRIMARY_COUNT = [1000000, 1000000, 1000000]


def main():
    """Primary entry point for the code"""
    output_dir = sys.argv[1]
    energy = MIN_ENERGY
    qsub_list_file = open('qsub_list','w')
    while energy <= MAX_ENERGY:
        fmt_dir = {}
        # make the folder
        folder_name = os.path.join(output_dir, "{0:05.2f}MeV".format(energy))
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        temp = []
        for side, cnt, name in zip(SIDE_LIST, PRIMARY_COUNT, SIDE_FILE_NAMES):
            fmtdict = {}
            fmtdict["file_name"] = name + ".root"
            fmtdict["energy_in_mev"] = energy
            fmtdict["side_number"] = side
            fmtdict["particle_count"] = cnt
            mname = (name + ".mac")
            macro_path = os.path.join(folder_name, mname)
            outfile = open(macro_path, 'w')
            outfile.write(MACRO_TMPL.format(**fmtdict))
            outfile.close()
            temp.append(RUN_MACRO_LINE.format(macro_name=mname))
        fmt_dir["run_macro_lines"] = "".join(temp)
        fmt_dir["output_dir"] = folder_name
        qsub_script = file(os.path.join(folder_name, "sub_script.sh"), "w")
        qsub_script.write(QSUB_SCRIPT_TMPL.format(**fmt_dir))
        qsub_script.close()
        qsub_list_file.write(os.path.join(folder_name, "sub_script.sh"))
        qsub_list_file.write("\n")
        energy += STEP_ENERGY
    qsub_list_file.close()


QSUB_SCRIPT_TMPL = """#!/bin/bash
#PBS -M mattajt@ornl.gov
cd {output_dir:s}
cp $NAI_EXEC ./NaiSim

{run_macro_lines:s}
rm -rf {output_dir:s}/PG4
"""


RUN_MACRO_LINE = "./NaiSim {macro_name:s}\n"


MACRO_TMPL = """/output/setRunNum 0
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
