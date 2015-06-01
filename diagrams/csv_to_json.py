import sys
import numpy
import json
if len(sys.argv) != 3:
    print("Usage: diagram_gen.py [input csv file] [output json file]")
    print("WARNING: THIS WILL OVERWRITE THE OUTPUT FILE!")
    sys.exit(0)
else:
    in_file = sys.argv[1]
    out_path = sys.argv[2]
print("%s -> %s" %(in_file,out_path))
diagram=numpy.genfromtxt(in_file, names=True)
col_names=[]
for name in diagram.dtype.names:
    col_names.append(name)
matrix = []
for column in range(len(diagram[0])):
    col_val=[]
    for line in range(len(diagram)):
        col_val.append(diagram[line][column])
    matrix.append(col_val)
diagram_dict = {col_names[i]:matrix[i] for i in range(len(col_names))}
out_file = open(out_path, 'w')
json.dump(diagram_dict, out_file)
out_file.close()
