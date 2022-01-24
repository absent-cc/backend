from schoology.parsing.columnDetection import ColumnDetection
from dataTypes import structs
det = ColumnDetection(structs.SchoolName.NEWTON_NORTH)
print(det.isFirst("Alberg"))
print(det.isLast("Alberg"))
print(det.isDate("1/1/1"))