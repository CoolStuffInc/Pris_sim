import numpy as np
import csv
import datetime as dt

a = np.array([1,2,3])
b = np.array([5,6,7])
print a
print b
a = np.vstack((a,b))
print a

with open('test.csv', 'wb') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    a = dt.datetime.now().today()
    spamwriter.writerow([a])
    spamwriter.writerow([b])
