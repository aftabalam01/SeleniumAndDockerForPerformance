import csv
import random



def create_number_urls():

    with open('./urls/confluence_url_count.csv','r') as csv_file:

        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                #print(f'url {row[0]} needs to be simulated {row[-1]} times')
                with open('./urls/url_file.txt', mode='a') as url_file:
                    for i in range(1,int(row[-1])):
                        url_file.write(row[0]+"\n")
                line_count += 1

    with open('./urls/url_file.txt', 'r') as source:
        data = [(random.random(), line) for line in source]
    data.sort()
    with open('./urls/data_file.txt', 'w') as target:
        for _, line in data:
            target.write(line)
        print(f'Processed {line_count} lines.')


if __name__=='__main__':
    create_number_urls()