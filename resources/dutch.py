
with open('./dutch-clean2.txt', 'w') as w: 
    with open('./dutch-combined.txt', 'r') as r:
        for line in r.readlines():
            if line.endswith('-\n'): 
                line = line.replace('-\n', '\n')

            w.write(line)


            # if '\EF' in line:
            #     line = line.replace('\EB', 'ï')
            #     w.write(line)
            # else:
            #     w.write(line)

        # print(lijst)
        # for item in lijst: 
        #     print(item)
        #     # w.write(item +'\n')