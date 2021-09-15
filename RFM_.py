import pandas as pd
import datetime as dt


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

df_ = pd.read_excel("online_retail_II.xlsx", sheet_name= "Year 2010-2011")
df_.head()
df = df_.copy()

## Pandas Exercises ##
df.describe().T
df.isnull().sum()
df.dropna(inplace=True)
df['Description'].nunique
df['Description'].value_counts().head()
df.groupby('Description').agg({'Quantity' : 'sum'}).sort_values('Quantity' , ascending=False).head(5)
df = df[~df['Invoice'].str.contains("C", na= False)]
df["TotalPrice"] = df["Quantity"]*df["Price"]


#### Calculating RFM metrics #####

df['InvoiceDate'].max()
today_date = dt.datetime(2021, 12, 11)
rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date - date.max()).days, 'Invoice' : lambda num: num.nunique(), 'TotalPrice': lambda TotalPrice: TotalPrice.sum()})
rfm.columns = ["recency", "frequency","monetary"]
rfm.head()
rfm = rfm[rfm["monetary"]>0]



rfm['recency_score'] = pd.qcut(rfm["recency"],5,labels=[5,4,3,2,1])
rfm['frequency_score'] = pd.qcut(rfm["frequency"].rank(method="first"),5,labels=[5,4,3,2,1])
rfm['monetary_score'] = pd.qcut(rfm["monetary"],5,labels=[5,4,3,2,1])
rfm["RFM_SCORE"] = (rfm["recency_score"].astype(str) + rfm["frequency_score"].astype(str))


## Segment map ##

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm["SEGMENT"] = rfm["RFM_SCORE"].replace(seg_map, regex=True)
rfm.head()


df_merge = pd.merge(df, rfm, on="Customer ID")
df_merge.head(5)
df_merge.groupby("SEGMENT").agg({"Price": "sum"}).sort_values("Price", ascending=False)   

rfm[["SEGMENT", "recency", "frequency", "monetary"]].groupby("SEGMENT").agg(["mean", "count"]).head()
new_df = pd.DataFrame()
new_df["loyal_customers_id"] = rfm[rfm["SEGMENT"] == "loyal_customers"].index
new_df.head()

new_df.to_csv("loyal_customer.csv")

#### Functionalization of the RFM Process #####

def check_rfm(dataframe, ):
    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]
    dataframe = dataframe[(dataframe['Quantity'] > 0)]
    dataframe = dataframe[(dataframe['Price'] > 0)]
    dataframe["TotalPrice"] = dataframe["Quantity"] * dataframe["Price"]

    today_date = dt.datetime(2011, 12, 11)
    rfm = dataframe.groupby('Customer ID').agg(
        {'InvoiceDate': lambda date: (today_date - date.max()).days, 'Invoice': lambda num: num.nunique(),
         'TotalPrice': lambda TotalPrice: TotalPrice.sum()})

    rfm.columns = ['recency', 'frequency', "monetary"]
    rfm = rfm[(rfm['monetary'] > 0)]

    rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

    rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                        rfm['frequency_score'].astype(str))


    seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_risk',
        r'[1-2]5': 'cant_loose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising',
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }

    rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
    rfm = rfm[["recency", "frequency", "monetary", "segment"]]
    return rfm

df = df_.copy()
rfm_new = check_rfm(df)
rfm_new.head()
