file_path = input("Input your filepath (exp : home/usr/file.bin) : ")

with open(file_path, 'rb') as f:
    content_bytes = f.read()

j = 0
for i in content_bytes:
    if len(str(hex(i))[2:]) < 2 :
        print("0" +str(hex(i))[2:],end=' ')
    else :
        print(str(hex(i))[2:], end=' ')
    if j%8== 7 :
        print()
    j +=1