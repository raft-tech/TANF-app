import statistics
l = []
with open("/Users/ericlipe/work/repos/tdrs/TANF-app/tdrs-backend/res.txt", 'r') as f:
    for line in f:
        l.append(float(line))
print(len(l))
print(sum(l))
print(sum(l) / len(l))
print(statistics.median(l))
