import sys
sys.stdout.reconfigure(encoding='utf-8')

plat_1 = [1,2,3,4,
         4,3,1,1,
         3,4,2,2,
         2,1,4,3]

plat_2 = [3,2,1,4,
         4,2,1,3,
         1,4,3,2,
         2,3,4,1]

plat_3 = [3,2,4,1,
         2,3,2,4,
         1,4,1,3,
         4,3,1,2]

plat_4 = [1,2,3,4,
         4,2,1,1,
         2,3,4,3,
         3,4,1,2]

plat_1i = plat_1[:]  
for i in range(0, len(plat_1), 4):  
    if i + 3 < len(plat_1):  
        plat_1i[i:i+4] = plat_1[i:i+4][::-1]  

plat_2i = plat_2[:]  
for i in range(0, len(plat_2), 4):  
    if i + 3 < len(plat_2):  
        plat_2i[i:i+4] = plat_2[i:i+4][::-1]  

plat_3i = plat_3[:]  
for i in range(0, len(plat_3), 4):  
    if i + 3 < len(plat_3):  
        plat_3i[i:i+4] = plat_3[i:i+4][::-1]  

plat_4i = plat_4[:]  
for i in range(0, len(plat_4), 4):  
    if i + 3 < len(plat_4):  
        plat_4i[i:i+4] = plat_4[i:i+4][::-1]  


colors = {
    1 : "🟨",
    2 : "🟦",
    3 : "🟩",
    4 : "🟥"
}


x = input("Quel plateau ? ")  
y = eval("plat_" + x)

for i in range(0, 16, 4):  
    print("".join(colors[couleur] for couleur in y[i:i+4]))
