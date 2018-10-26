# 可以自己import我们平台支持的第三方python模块，比如pandas、numpy等。
# 在这个方法中设置固定参数值start_date, end_date, lag, parameter, frequent, finance, report_lag
# start_date为回测开始日期
# end_date为回测结束日期
# bar为bar_dict参数的配置参数，key为固定，现支持daily、minutely、finance
# lag为用户在handle_bar中bar_dict可获取的最大日期间隔
# lag_init为用户在precompute中bar_dict可获取的最大日期间隔
# parameter为用户计算因子所需的参数，daily、minutely可选参数有open, high, low, close, volumn, amt, adjfactor, pre_close, ipo_date, suspend, mkt_cap_ard, pe_ttm, pcf_ncf_ttm, pb, turn, vmap
# finance可选参数有acc_exp, acct_payable等
# lag_dict为用户在handle_bar中indicator_dict中除'indicator'外其他变量可获取的最大日期间隔
# frequent版本1默认为daily,不能覆盖，之后会陆续支持minute、tick数据
# intermediate_keys为indicator_dict的key，其中indicator为默认必选
def init(context):
    context.start_date = "20180325"
    context.end_date = "20180506"
    context.bar = {
        "day": {
            "parameter": ["open", "close", "low", "ipo_date", "suspend", "adjfactor", "high", "volumn"],
            "lag": 20,
            "lag_init": 20
        },
        "finance": {
            "parameter": ["net_profit_is"],
            "lag": 20,
            "lag_init": 0
        }
    }
    context.frequent = "daily"
    context.intermediate_keys = ["indicator", "high_low_SMA"]
    context.lag_dict = 20
    # 实时打印日志
    logger.info("Start from: {}".format(datetime.datetime.now()))


# precompute在handler_bar之前调用，用以返回第一次调用handle_bar时的indicator_dict
# bar_dict为字典格式，key为context.bar的key，value为dict，key为parameter，value为index从start_date-lag_init-1到start_date-1的日期（daily为每天，minutely为每分钟，finance为每季度），key为各股票类型，value为各参数为dataframe
# 用户返回indicatot_dict应为dict格式，key应为context.intermediate_keys中除indicator之外的key
def precompute(bar_dict):
    adjfactor_tmp = bar_dict["day"]['adjfactor']
    high_tmp = bar_dict["day"]['high'] * adjfactor_tmp
    low_tmp = bar_dict["day"]['low'] * adjfactor_tmp
    high_low = high_tmp - low_tmp
    high_low_SMA = pd.DataFrame(0, index=high_tmp.index, columns=high_tmp.columns)
    for hls_ind, hls in enumerate(high_low_SMA.index):
        if hls_ind == 0:
            high_low_SMA.loc[hls] = high_low.loc[hls].fillna(0)
        high_low_SMA.loc[hls] = (high_low.iloc[hls_ind-1] * 2 +
                                 high_low_SMA.iloc[hls_ind-1] * (11 - 2)) / 11
    indicator_dict = {'high_low_SMA': high_low_SMA}
    return indicator_dict


# 在这个方法中可删选所需的股票，可删选key为context.parameter中设置的字段等，返回值应为index为日期序列，key为各个股票，若要剔除股票，则value为np.nan即可
def filter_stock(data):
    IPOdate = data['ipo_date']
    IPO_index = IPOdate.index
    IPOdate_t = IPOdate.apply(lambda x: IPO_index > x + 20000)
    IPOdate_t[IPOdate_t == False] = np.nan
    return IPOdate_t * 1.0


# 你选择的证券数据按照所填频率将会触发此段逻辑
# bar_dict为字典格式，key为context.bar的key，value为dict，key为parameter，value为index从start_date-lag_init-1到start_date-1的日期（daily为每天，minutely为每分钟，finance为每季度），key为各股票类型，value为各参数为dataframe
# 返回return_data[key]应为pandas.core.series.Series类型，key为context.intermediate_keys,indicator_dict即为将增加index日期间隔为lag_dict的return_data
def handle_bar(bar_dict, indicator_dict=None):
    adjfactor_tmp = bar_dict["day"]['adjfactor'].iloc[-1]
    high_tmp = bar_dict["day"]['high'].iloc[-1] * adjfactor_tmp
    low_tmp = bar_dict["day"]['low'].iloc[-1] * adjfactor_tmp
    high_low = high_tmp - low_tmp
    high_low_SMA = indicator_dict['high_low_SMA'].iloc[-1]
    high_low_SMA_new = (high_low * 2 + high_low_SMA * (11 - 2)) / 11
    indicator = (high_low - high_low_SMA_new) / high_low_SMA_new * 100
    return_data = {'indicator': indicator, 'high_low_SMA': high_low_SMA_new}
    return return_data


#下面的例子中使用了finnce参数
# def handle_bar(bar_dict,  indicator_dict=None):
#     npi = bar_dict['finance']['net_profit_is']
#     data0 = npi.diff()
#     rpt_year = list(filter(lambda x: '0331' in str(x), data0.index))
#     data0.loc[rpt_year] = npi.loc[rpt_year]
#     data0 = data0.diff(4)
#     Data = (data0 - data0.rolling(window=8).mean().shift(1)) / data0.rolling(window=8).std().shift(1)
#     Data[abs(Data) > 10] = 10
#     Data[np.isinf(Data)] = np.nan
#     Data = Data.fillna(method='pad')
#     return {'indicator': Data.iloc[-1]}
