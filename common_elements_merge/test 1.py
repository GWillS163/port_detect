

lst = [['137.78.5.43', 23],
 ['137.78.5.43', 22],
 ['137.78.5.43', 27],
 ['137.78.5.43', 24],
 ['137.78.5.43', 26],
 ['137.78.5.43', 25],
 ['1.78.5.35', 28],
 ['1.78.5.35', 443]]


def lst_auto_merge(lst):
    data = {}
    for i in lst:
        data.update({i[0]: []})
    for i in lst:
        data[i[0]].append(i[1])
    for i in data:
        print(f"主机为:{i:^16}的  {str(data[i]):^28}端口未检测到开放")
    return data

data = lst_auto_merge(lst)
