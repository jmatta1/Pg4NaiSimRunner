#!/usr/bin/python
"""A simple script to set up simulation runs for the PG4 simulations of the
large volume NaI detectors"""
import sys
import os

MIN_ENERGY = 14.990  # minimum energy to simulate in MeV
MAX_ENERGY = 15.000  # maximum energy to simulate in MeV (inclusive)
STEP_ENERGY = 0.010  # step size of energy to simulate in MeV
# 0=WideFront,     1=WideBack
# 2=LongNarrowTop, 3=LongNarrowBottom
# 4=OppositePmt,    5=PmtEnd
SIDE_LIST = [0, 2, 4]  # list of sides to simulate throwing gammas at
SIDE_FILE_NAMES = ["side0", "side2", "side4"]
PRIMARY_COUNT = [36000000, 36000000, 36000000]


def main():
    """Primary entry point for the code"""
    output_dir = sys.argv[1]
    energy = MIN_ENERGY
    while energy <= MAX_ENERGY:
        # make the folder
        folder_name = os.path.join(output_dir, "{0:05.2f}MeV".format(energy))
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        for side, cnt, name in zip(SIDE_LIST, PRIMARY_COUNT, SIDE_FILE_NAMES):
            fmtdict = {}
            fmtdict["file_name"] = name + ".root"
            fmtdict["energy_in_mev"] = energy
            fmtdict["side_number"] = side
            fmtdict["particle_count"] = cnt
            macro_name = (name + ".mac")
            macro_path = os.path.join(folder_name, macro_name)
            outfile = open(macro_name, 'w')
            outfile.write(MACRO_TMPL.format(**fmtdict))
        energy += STEP_ENERGY

# {output_dir:s}
# {run_macro_lines:s}
QSUB_SCRIPT_TMPL = """
cd {output_dir:s}
mkdir {output_dir:s}/PG4
cp -r $PG4_SRC {output_dir:s}/PG4
mkdir {output_dir:s}/PG4/bld
cd {output_dir:s}/PG4/bld
cmake3 ../PROSPECT-G4 -DG4VIS_NONE=TRUE
cd {output_dir:s}
{run_macro_lines:s}
rm -rf {output_dir:s}/PG4
"""

# {macro_name:s}
RUN_MACRO_LINES = "./PG4/bld/bin/PROSPECT-G4 {macro_name:s}"

# {file_name:s}
# {energy_in_mev:5.2f}
# {side_number:d}
# {particle_count:d}
MACRO_TMPL = """
/output/setRunNum 0
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
