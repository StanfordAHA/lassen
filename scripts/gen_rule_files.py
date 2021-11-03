import glob, os

rrule_files = glob.glob(f'./lassen/rewrite_rules/*.py')

for file in rrule_files:
    if "const" not in file and "middle" not in file:
        op = os.path.basename(file).replace("_","").split(".")[0]
        file_name = os.path.basename(file).split(".")[0]
        print(op)
        new_filename = f"{os.path.dirname(file)}/{file_name}_const.py"
        print(new_filename)
        fin = open(file, "r")
        fout = open(new_filename, "w")
        fin_lines = fin.readlines()
        for line in fin_lines:
            if op in line:
                fout.write(line.replace(op, op + "_const"))
            elif "def __call__(self," in line:
                fout.write(line.replace("in1 : Data", "in1 : Const(Data)").replace("in1 : Bit", "in1 : Const(Bit)"))
            else:
                fout.write(line)
