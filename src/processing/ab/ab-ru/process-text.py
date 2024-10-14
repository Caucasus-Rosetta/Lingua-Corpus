from tempfile import NamedTemporaryFile
import shutil, csv, re, os

p = re.compile('#')
f = re.compile('^[0-9]*.tsv.temp$')
tempfile = NamedTemporaryFile('w+t', newline='', delete=False)

for file in os.scandir('.'):
    if file.is_file() & bool(f.match(file.name)):
        with open(file.name, 'r', newline='') as tsvFile:
            reader = csv.reader(tsvFile, delimiter='\t')
            with open(tempfile.name, 'w', newline='') as tempfile:
                writer = csv.writer(tempfile, delimiter='\t')
                for row in reader:
                    if len(row) == 2:
                        # r1 = re.sub(re.compile('[\w ,-]'),'',row[0])
                        # r2 = re.sub(re.compile('[\w ,-]'),'',row[1])
                        # punc = set(list(r1))==set(list(r2))
                        # import pdb; pdb.set_trace()
                        row[0] = p.split(row[0])
                        row[1] = p.split(row[1])
                        max = len(row[0]) if len(row[0]) > len(row[1]) else len(row[1])
                        for i in range(max):
                            value1 = row[0][i].strip() if i < len(row[0]) else ' '
                            value2 = row[1][i].strip() if i < len(row[1]) else ' '
                            value2 = value2 if len(value2) > 0 else ' '
                            error = '0' if 0.66 < len(value1)/len(value2) < 1.5 else '1'
                            if value1 == value2:
                                error = '1'
                            if len(value1) < 20 or len(value2) < 20:
                                error = '0' if 0.5 < len(value1)/len(value2) < 2 else '1'
                            id = (('+'+file.name[0:-9] if len(row[0]) >1 else file.name[0:-9]) if len(row[0]) == len(row[1]) else '-'+file.name[0:-9])
                            writer.writerow([id, value1, value2, error])
                shutil.move(tempfile.name, file.name)
