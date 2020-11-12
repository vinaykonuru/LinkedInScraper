import xlrd
import xlsxwriter
import pandas as pd

workbook = xlsxwriter.Workbook('interests.xlsx')
people_interests = workbook.add_worksheet()
interestsSheet=workbook.add_worksheet()


df = pd.read_csv('Altamonte Springs.csv',',')
data=df.values.tolist()
rowCount=0
interestsString=[]
df.to_excel(r'exceltest.xlsx',index=False,header=True)
print(data)
# for row in data:
#     i=data.index(row)
#     interest=data[i][1]
#     if str(interest)!='nan':
#         interestList=str(interest).split('.')
#         interestList.pop()#last entry adds an unnecessary space
#         for item in interestList:
#             if str(item) not in interestsString:
#                 interestsString.append(item)
#             print(str(item))
#             people_interests.write(rowCount,0,data[i][0])
#             people_interests.write(rowCount,1,item)
#             rowCount+=1
# for row in interestsString:
#     i=interestsString.index(row)
#     interestsSheet.write(i,0,str(row))
# workbook.close()
