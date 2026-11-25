import pandas as pd, numpy as np

df = pd.read_csv('duka_sales.csv', parse_dates=['order_date'])
df['revenue']    = df['quantity'] * df['unit_price']
df['is_weekend'] = df['order_date'].dt.dayofweek >= 5
df['month']      = df['order_date'].dt.to_period('M')
df['price_band'] = np.where(df['unit_price'] >= 28000, 'Premium', 'Value')
df['weekday']    = df['order_date'].dt.day_name()

print("=SHAPE=")
print(df.shape)

print("=DTYPES=")
print(df.dtypes)

print("=NULLS=")
print(df.isnull().sum())

print("=DATE_RANGE=")
print("Min:", df['order_date'].min().date(), "Max:", df['order_date'].max().date())

print("=BRANCH_VC=")
print(df['branch'].value_counts())

print("=CHANNEL_VC=")
print(df['channel'].value_counts())

print("=CATEGORY_VC=")
print(df['category'].value_counts())

print("=PRICEBAND=")
print(df['price_band'].value_counts())

print("=BRANCH_REV=")
br = df.groupby('branch')['revenue'].sum().sort_values(ascending=False)
print(br)

print("=BRANCH_ORD=")
bo = df.groupby('branch').size().sort_values(ascending=False)
print(bo)

print("=BRANCH_SUMMARY=")
bs = pd.concat([br.rename('total_revenue'), bo.rename('num_orders')], axis=1)
bs['rev_rank']   = bs['total_revenue'].rank(ascending=False).astype(int)
bs['order_rank'] = bs['num_orders'].rank(ascending=False).astype(int)
print(bs.sort_values('rev_rank'))

print("=TOP3_REV=")
pr = df.groupby('product')['revenue'].sum().sort_values(ascending=False).head(3)
print(pr)

print("=TOP3_UNITS=")
pu = df.groupby('product')['quantity'].sum().sort_values(ascending=False).head(3)
print(pu)

print("=WEEKEND=")
wk = df.groupby('is_weekend').agg(
    num_orders=('order_id','count'),
    total_revenue=('revenue','sum'),
    avg_revenue=('revenue','mean')
).rename(index={False:'Weekday', True:'Weekend'})
wk['pct_orders'] = (wk['num_orders'] / wk['num_orders'].sum() * 100).round(1)
print(wk.round(0))

print("=MONTHLY=")
mo = df.groupby('month')['revenue'].sum().sort_values(ascending=False)
print(mo)
bm  = mo.idxmax()
wom = mo.idxmin()
pct = (mo.max() - mo.min()) / mo.min() * 100
print(f"Best:  {bm}  KES {mo.max():,.0f}")
print(f"Worst: {wom} KES {mo.min():,.0f}")
print(f"Pct diff: {pct:.1f}%")

print("=PREMIUM_ONLINE=")
po = df[
    (df['price_band'] == 'Premium') &
    (df['channel']    == 'Online')  &
    (df['branch'].isin(['Nairobi CBD', 'Mombasa']))
]
print(f"Count: {len(po)}")
rev_sum = po['revenue'].sum()
print(f"Total revenue: KES {rev_sum:,.0f}")

print("=GRAND_TOTAL=")
print(f"KES {df['revenue'].sum():,.0f}")

print("=HEAD=")
print(df[['order_id','order_date','branch','channel','product','category',
          'quantity','unit_price','revenue','month','weekday','is_weekend','price_band']].head(5).to_string())
