import csv
from atomic_writer import SimpleWriter

rows = [("id","name","score"),(1,"Gautr",100),(2,"Breaker",95)]
with SimpleWriter("results/top.csv", mode="w") as f:
	writer = csv.writer(f)
	writer.writerows(rows)