import pandas as pd
import time
import re

frame = pd.read_csv('all_gov_sites_data_1.1.csv')
#print(frame.head(5))
i = 0
"""for each in frame['name']:

    #print(frame)

    frame['name'][i] = str(frame['name'][i]).strip()
    if frame['name'][i].lower().endswith('|'):
        frame['name'][i] = frame['name'][i][0:-2]
    elif frame['name'][i].lower().startswith('|'):
        frame['name'][i] = frame['name'][i][1:-1]
    if 'welcome' in frame['name'][i].lower() or 'home' in frame['name'][i].lower() or '|' in frame['name'][i].lower():
        print('\n', frame['name'][i], frame['link'][i], frame['meta_description'][i])
        inp = input('Warning! The name is missing or ambiguous!\n Type "d" to delete or the value to replace it with.\nType "q" to quit.')
        if inp.lower() == 'd':
          frame['name'][i] = ' '
        elif inp.lower() == 'q':
            break
        else:
          frame['name'][i] = inp
    if 'restricted' in frame['name'][i].lower() or 'denied' in frame['name'][i].lower() or 'forbidden' in frame['name'][i].lower() or 'sales' in frame['name'][i].lower():
        frame['name'][i] = ' '
    if len(frame['name'][i]) < 5 or '.org' in frame['name'][i].lower() or '.com' in frame['name'][i].lower() or '.net' in frame['name'][i].lower() or '.gov' in frame['name'][i].lower():
        print('\n', frame['name'][i], frame['link'][i], frame['meta_description'][i])
        inp = input('Please check the name of the company\n Type "d" to delete or the value to replace it with.\nType "q" to quit.')
        if inp.lower() == 'd':
          frame['name'][i] = ' '
        elif inp.lower() == 'q':
            break
        else:
          frame['name'][i] = inp

    i += 1"""

#regex = re.compile('\d*')
#pattern_phones = [r'\d\d\d[-.*, ]\d\d\d[-.*, ]\d\d\d\d', r'+1\d\d\d[-.*, ]\d\d\d[-.*, ]\d\d\d\d', 
#                    r'\(\d\d\d\)[-.*, ]\d\d\d[-.*, ]\d\d\d\d', r'+1\(\d\d\d\)[-.*, ]\d\d\d.[-.*, ]\d\d\d\d']
for each in frame['phone']:
    counter = 0
    if len(str(frame['phone'])) == 0:
        continue
    if str(frame['phone'][i]) == '(999) 999-9999' or str(frame['phone'][i]) == '999.999.9999' or str(frame['phone'][i]) == '999-999-9999':
        print('Invalid phone number:', frame['phone'][i], frame['link'][i])
        inp = input('Press "d" to leave blank or enter a valid phone number. Press "q" to quit.')
        if inp == 'd':
            frame['phone'][i] = ''
        elif inp == 'q':
            break
        else:
            frame['name'][i] = inp

    i += 1
            
print(frame)
frame.to_csv('all_gov_sites_data_1.1.csv')

"""print('review the data: \nq - quit\ne - edit a record\nd - delete a record \ns - skip')
for col, row in frame.iterrows():
    
    print(row)
    choice = input()
    if choice == 'q':
        frame.to_csv('all_gov_sites_data_1.csv')
        break
    if choice == 'd':
          frame.drop(col, axis=0, inplace=True)
    if choice == 'e':
        print('press "f" if record needs no correction')
        for col, value in row.iteritems():
            print(col, '-', value)
            choice_2 = input()
            if choice_2 == 'f':
                frame.loc[col, value] = value
            else:
                frame.loc[col, value] = choice_2
                
    if choice == 's':
          continue
    else:
          print('invalid input')
    
print(frame)"""
    #break






#for row in range(frame.shape[0]):
#	for col in range(frame.shape[1]):
#		print(frame[ [col]+1, [row]+1 ])
#		break