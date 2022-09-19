import argparse
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("input")
args = parser.parse_args()

data = dict()
with open(args.input) as f:
    for line in f:
        thresh_key, group_size, group_count = [int(el) for el in line.strip().split(",")]
        if not thresh_key in data:
            data[thresh_key] = []
        data[thresh_key].append((group_size, group_count))

data_sorted = dict()
for key in data:
    data_sorted[key] = list(sorted(data[key], key=lambda x: x[0]))

data_cumul = dict()
for key in data_sorted:
    datap = data_sorted[key][::-1]
    data_cumul[key] = [datap[0]]
    for i in range(1, len(datap)):
        data_cumul[key].append((datap[i][0], datap[i][0] + data_cumul[key][-1][1]))
    data_cumul[key] = data_cumul[key][::-1]

for key in data_cumul:
    x = [el[0] for el in data_cumul[key]]
    y = [el[1] for el in data_cumul[key]]
    plt.plot(x, y, label=key)

plt.xlabel("Minimum cluster sizes")
plt.ylabel("Amount of clusters with minimum cluster size n")
plt.legend(title="Max. distance")
plt.show()