import glob, os
from solve_rewrite_rules import solve_rules

# if input("This will delete all saved rewrite rules, only do this if you are changing the PE hardware, are you sure you want to continue? (y/n)") != "y":
#         exit()

dir_path = os.path.dirname(os.path.realpath(__file__))

rr_path = f"{dir_path}/../lassen/rewrite_rules"

rrule_files = glob.glob(f"{rr_path}/*.json")

print("Removing saved rewrite rules")
for file_ in rrule_files:
    os.remove(file_)

rrule_peak_files = glob.glob(f"{rr_path}/*.py")

for file_ in rrule_peak_files:
    if "pipelined" in file_:
        os.remove(file_)

solve_rules()

print("Generating pipelined rules")

rrule_peak_files = glob.glob(f"{rr_path}/*.py")
i = 0
for file_ in rrule_peak_files:
    print(f"{i:3}: {file_}")
    i = i + 1

for file_ in rrule_peak_files:
    print(f"{file_} : ", end="")

    op = os.path.basename(file_).split(".")[0]
    file_name = os.path.basename(file_).split(".")[0]
    new_filename = f"{os.path.dirname(file_)}/{file_name}_pipelined.py"

    fin = open(file_, "r")
    fout = open(new_filename, "w")
    fin_lines = fin.readlines()
    reg_line = False
    for line in fin_lines:
        write_line = line
        write_line = write_line.replace(f" {op}_fc", f" {op}_pipelined_fc")
        write_line = write_line.replace(f" {op}(Peak", f" {op}_pipelined(Peak")
        write_line = write_line.replace(f"return {op}", f"return {op}_pipelined")
        fout.write(write_line)

    json_file_ = f"{os.path.dirname(file_)}/{file_name}.json"
    new_filename = f"{os.path.dirname(file_)}/{file_name}_pipelined.json"

    fin = open(json_file_, "r")
    fout = open(new_filename, "w")
    fin_lines = fin.readlines()
    reg_line = False
    for line in fin_lines:
        write_line = line
        if '"width": 2,' in line:
            reg_line = True
        else:
            if reg_line:
                write_line = write_line.replace('"value": 2', '"value": 3')
            reg_line = False

        fout.write(write_line)

    print(f"Generated {file_name}_pipelined")
