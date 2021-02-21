start = []
end = []
q = []
for i in range(0,53,1):
    q.append(i)
for i in range(0,53,5):
    start.append(i)
    if i + 5 >= 53:
        end.append(53)
    else:
        end.append(i+5)
for i, s in enumerate(start):
    print(start[i], end[i])
    print(q[start[i]: end[i]])