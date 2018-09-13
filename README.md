# test
for test
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import datetime

rptdates=pd.read_csv(r'C:\Users\xiangjiang.hu\Desktop\data2\rptdates.csv',index_col=[0])
ocf=pd.read_csv(r'C:\Users\xiangjiang.hu\Desktop\data2\CashFields_Concat\cash_cash_equ_end_period.csv',index_col=[0])
rptdates=rptdates.loc[:,ocf.columns]
tot_equity=tot_equity.loc[:,ocf.columns]

def handle_bar(x):
    npi = x
    data0 = npi.diff()
    rpt_year = list(filter(lambda x: '0331' in str(x), data0.index))
    data0.loc[rpt_year] = npi.loc[rpt_year]
    data0 = data0.diff(4)
    Data = (data0 - data0.rolling(window=8).mean().shift(1)) / data0.rolling(window=8).std().shift(1)
    Data[abs(Data) > 10] = 10
    Data[np.isinf(Data)] = np.nan
    Data = Data.fillna(method='pad')
    return Data
ocf1=handle_bar(ocf)

def data_process(x):
    N=x.copy()
    for i in (x.dropna()).index:
            N[i]=ocf1.loc[x[i],x.name] 
    return N
M=rptdates.copy()
ocf2=M.apply(data_process,axis=0)
ocf3=ocf2.fillna(method='pad',limit=200)

pct=pd.read_csv(r'C:\Users\xiangjiang.hu\Desktop\data2\pct_prm.csv',index_col=[0])
ocf3=ocf3.loc[:,pct.columns]
pct_chg=pct.loc[20130105:20180508]
OCF=ocf3.loc[20130101:20180507]
RDS=OCF
A1=RDS.rank(axis=1,pct=True)
pct2=pct_chg.as_matrix()
B=A1.as_matrix()
final=np.array([(B.reshape(np.size(B))),(pct2.reshape(np.size(pct2)))])
final1=pd.DataFrame(final.T)
final2=final1.sort_values(0)
final3=final2.dropna()
plt.plot(final3[0],final3[1].cumsum())
plt.show()

Final1=((A1>0.8))
pct_chg=pct.loc[20130105:20180508]
M=pct_chg.index.copy()
M=pd.Series(M)
for i in range(len(pct_chg)):
    M[i]=datetime.datetime.strptime(str(pct_chg.index[i]),'%Y%m%d')
Final1.index=pct_chg.index=M
plt.plot((pct_chg[Final1==1]).mean(axis=1).cumsum())
plt.show()

##sharpe
Q=np.array((pct_chg[Final1==1]).mean(axis=1).dropna())
np.mean(Q)/np.std(Q)*16
