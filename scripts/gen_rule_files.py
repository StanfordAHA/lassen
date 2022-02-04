import glob, os

rrule_files = glob.glob(f'./lassen/rewrite_rules/fp_*.py')

for file in rrule_files:
    if "pipelined" not in file:
        op = os.path.basename(file).split(".")[0]
        file_name = os.path.basename(file).split(".")[0]
        print(op)
        new_filename = f"{os.path.dirname(file)}/{file_name}_pipelined.py"
        print(new_filename)
        fin = open(file, "r")
        fout = open(new_filename, "w")
        fin_lines = fin.readlines()
        reg_line = False
        for line in fin_lines:
            # if "def __call__(self," in line:
            #     line = line.replace("in1 : Data", "in1 : Const(Data)").replace("in1 : Bit", "in1 : Const(Bit)")

            write_line = line
            # if '"width": 2,' in line:
            #     reg_line = True
            # else:
            #     if reg_line:
            #         write_line = write_line.replace('"value": 2', '"value": 3')
            #     reg_line = False

            write_line = write_line.replace(f" {op}", f" {op}_pipelined")

            fout.write(write_line)
