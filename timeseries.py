#以市值因子为例
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import datetime
pct=pd.read_csv(r'C:\Users\xiangjiang.hu\Desktop\project1\pct_prm.csv',index_col=[0])
mkt_cap_ard=pd.read_csv(r'C:\Users\xiangjiang.hu\Desktop\project1\mkt_cap_ard.csv',index_col=[0])
ipo=pd.read_csv(r'C:\Users\xiangjiang.hu\Desktop\project1\IPO.csv',index_col=[0])
lu=pd.read_csv(r'C:\Users\xiangjiang.hu\Desktop\project1\limit_up.csv',index_col=[0])
ld=pd.read_csv(r'C:\Users\xiangjiang.hu\Desktop\project1\limit_down.csv',index_col=[0])
suspend=pd.read_csv(r'C:\Users\xiangjiang.hu\Desktop\project1\suspend.csv',index_col=[0])
ranking=(mkt_cap_ard.rank(axis=1))
counting=(mkt_cap_ard.count(axis=1))
factor=ranking.apply(lambda x:x/counting,axis=0)
holding=factor<0.3
del suspend['date']
del lu['date']
del ld['date']
lu.index=ld.index=ipo.index=suspend.index=holding.index
LU=1-lu.as_matrix()
LD=1-ld.as_matrix()
SUS=1-suspend.as_matrix()
IPO=(1-ipo.as_matrix())
IPO=1-IPO
A=1-holding.as_matrix()
A=1-A
B=A.copy()
CH=A.copy()
C=np.multiply(B[0]==1,LU[0])
B[0]=np.multiply(C,SUS[0])
B[0]=np.multiply(B[0],IPO[0])
CH[0]=B[0]
for i in range(1,1213):
    B[i]=A[i]-B[i-1]
    C=np.multiply(B[i]==1,LU[i])-np.multiply(B[i]==-1,LD[i])
    B[i]=np.multiply(C,SUS[i])
    CH[i]=np.multiply(B[i],IPO[i])
    B[i]=np.multiply(B[i],IPO[i])+B[i-1]
final=pd.DataFrame(B)
pct=pct.drop([u'2013-01-04'])
final=final.drop([1212])
final.index=pct.index
final.columns=pct.columns
F=pct.fillna(0)*final
G=F.sum(axis=1)/final.sum(axis=1)
G.index=range(1212)
plt.plot(G.cumsum())
plt.show()
