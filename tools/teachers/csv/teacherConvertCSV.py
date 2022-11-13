# Quick and dirty of converting TSV file of teachers from Newton Site to CSV

import csv

# files = ['NSHS_teachers', 'NNHS_teachers']

# for path in files:
path = "NNHS_teachers"  # Specify the file to be converted

with open(path + ".tsv", "r") as file:
    file = file.readlines()

fields = ["First", "Last"]

with open(path + ".csv", "w") as csvFile:
    writer = csv.writer(csvFile)
    writer.writerow(fields)
    for row in file:
        seperated = row.split("\t")
        rowToWrite = []
        for i in range(1, -1, -1):
            line = seperated[i]
            actualContent = line[0:-1]
            rowToWrite.append(actualContent)
        writer.writerow(rowToWrite)
