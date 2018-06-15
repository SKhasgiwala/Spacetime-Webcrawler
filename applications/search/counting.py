file = open('count.csv', 'r')
count = file.read()
file.close()

print('Starting Count: ' + count)
count = int(count)

for i in range(10):
    count += 1

print('Final Count: ' + str(count))
file = open('count.csv', 'w')
file.write(str(count))
file.close()