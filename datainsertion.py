import json
file = open('correct.json')
data = json.load(file)
list1 = []
for word in data:
  list1.append("insert into CORRECTWORD(correct_word) VALUES('"+ word +"');\n")
  
print(list1)

file1 = open('myfile.txt', 'w')
file1.writelines(list1)
  
# Closing file
file1.close()
