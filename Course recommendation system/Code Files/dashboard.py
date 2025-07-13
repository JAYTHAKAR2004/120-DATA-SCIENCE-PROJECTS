import pandas as pd


def getvaluecounts(df):
    return dict(df['subject'].value_counts())


def getlevelcount(df):
    return dict(list(df.groupby(['level'])['num_subscribers'].count().items())[1:])


def getsubjectsperlevel(df):
    ans = list(dict(df.groupby(['subject'])['level'].value_counts()).keys())
    alllabels = [ans[i][0] + '_' + ans[i][1] for i in range(len(ans))]
    ansvalues = list(dict(df.groupby(['subject'])['level'].value_counts()).values())
    completedict = dict(zip(alllabels, ansvalues))
    return completedict


def yearwiseprofit(df):
    # ✅ Step 1: Replace known string values
    df['price'] = df['price'].astype(str)  # Ensure everything is a string first
    df['price'] = df['price'].str.replace('Free', '0', case=False)
    df['price'] = df['price'].str.replace('TRUE', '0', case=False)

    # ✅ Step 2: Remove currency symbols, commas (e.g., ₹1,999 -> 1999)
    df['price'] = df['price'].str.replace(r'[^\d.]', '', regex=True)

    # ✅ Step 3: Convert to float safely
    df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0)

    # ✅ Step 4: Calculate profit
    df['profit'] = df['price'] * df['num_subscribers']

    # ✅ Step 5: Extract date components
    df['published_date'] = df['published_timestamp'].apply(lambda x: x.split('T')[0])

    # ✅ Drop invalid row manually (bad timestamp string)
    df = df.drop(df.index[2066])

    # ✅ Convert to datetime
    df['published_date'] = pd.to_datetime(df['published_date'], format="%Y-%m-%d", errors='coerce')
    df = df.dropna(subset=['published_date'])

    # ✅ Extract year, month, day
    df['Year'] = df['published_date'].dt.year
    df['Month'] = df['published_date'].dt.month
    df['Day'] = df['published_date'].dt.day
    df['Month_name'] = df['published_date'].dt.month_name()

    # ✅ Grouped Aggregations
    profitmap = dict(df.groupby(['Year'])['profit'].sum())
    subscribersmap = dict(df.groupby(['Year'])['num_subscribers'].sum())
    profitmonthwise = dict(df.groupby(['Month_name'])['profit'].sum())
    monthwisesub = dict(df.groupby(['Month_name'])['num_subscribers'].sum())

    return profitmap, subscribersmap, profitmonthwise, monthwisesub

