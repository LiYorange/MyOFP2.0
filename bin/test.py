# ############################################# 合并df
import pandas as pd

left = pd.DataFrame({
    'A': ['A0', 'A1', 'A2', 'A3']})
middle = pd.DataFrame({
    'B': ['B0', 'B1', 'B2', 'B3']})
right = pd.DataFrame({
    'C': ['C0', 'C1', 'C2', 'C3']})

df2 = pd.concat([left, middle, right], axis=1).astype("int32")
print(df2)
# ############################################ 测试元组
# int_li = []
# flot_li = []
# li = [(100, "float"), (200, "int"), (1.1, "float"), (1.2, "float")]
# for i, j in zip(li, range(len(li))):
#     if i[1] == "int":
#         int_li.append((i[0], li.index(i)))
#     elif i[1] == "float":
#         flot_li.append((i[0], li.index(i)))
# print(int_li)
# print(flot_li)

# ############################################ 字符串错误测试
# s = "abc"
# print(s.strip("_")[8])
