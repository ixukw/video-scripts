def generateLayout(row, col):
    layout = ''
    for c in range(col):
        for r in range(row):
            row_part = ''.join([f'h{i}+' for i in range(r)])
            row_part = row_part[:-1] if len(row_part) > 0 else '0'
            col_part = ''.join([f'w{i*col}+' for i in range(c)])
            col_part = col_part[:-1] if len(col_part) > 0 else '0'
            layout += f'|{col_part}_{row_part}'

    return layout[1:]

print(generateLayout(6,7))
print(generateLayout(6,8))
exit()
n=7

layout_col = ["h0"]
for i in range(n-2):
    current_col = "h" + str(i+1)
    current_col = layout_col[-1]+"+"+current_col
    layout_col.append(current_col)
layout_col.insert(0,"0")

layout_row = ["w0"] 
for i in range(n-2):
    current_row = "w"+str((i+1)*n)
    current_row = layout_row[-1]+"+"+current_row
    layout_row.append(current_row)
layout_row.insert(0,"0")

layout = []
for i in range(n):
    for j in range(n):
        comb =   layout_row[i] + "_" + layout_col[j] 
        layout.append(comb)
layout = "|".join(layout)
layout = "xstack=inputs="+str(n)+":layout="+layout

print (layout)