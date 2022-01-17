import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import base64
import numpy as np
import yfinance as yf
from numpy import random

st.title('S&P500 Data Filtering')
st.subheader('This App uses pandas webscraping to filter and produce closing price vs time graphs on select stocks')
plot = st.empty()

@st.cache
def load_data():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    html = pd.read_html(url,header = 0)
    df = html[0]
    return df

df = load_data()
sector = df.groupby('GICS Sector')


# Sidebar - Choosing sector(s) to filter
sorted_sector_unique = sorted(df['GICS Sector'].unique())
selected_sector = st.sidebar.multiselect('Sector', sorted_sector_unique, sorted_sector_unique)


# Filtering the table based on selection
df_selected_sector = df [ df['GICS Sector'].isin(selected_sector) ]
st.header('Display Companies in Selected Sector')
st.write('Data Dimension: ' + str(df_selected_sector.shape[0]) + ' rows  x  ' + str(df_selected_sector.shape[1]) + ' columns')
st.dataframe(df_selected_sector)

# Custom Function to download S&P 500 Data
def downloadCSV(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode( csv.encode() ).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="SP500.csv">Download CSV File</a>'
    return href

st.markdown(downloadCSV(df_selected_sector), unsafe_allow_html=True)

data = yf.download(
    tickers = list(df_selected_sector[:10].Symbol),
    period = "ytd",
    interval = "1d",
    group_by = "ticker",
    auto_adjust = True,
    prepost = True,
    threads = True,
    proxy = None
)


# Show plots of Closing Prices
def price_plot(symbol):
    c = 'lightsteelblue'
    df = pd.DataFrame(data[symbol].Close)
    df['Date'] = df.index
    fig,ax = plt.subplots()
    plt.fill_between(df.Date, df.Close, color=c, alpha=0.3)
    plt.plot(df.Date, df.Close, color = c, alpha = 0.8)
    plt.xticks(rotation = 90)
    plt.title(symbol, fontweight = 'bold')
    plt.xlabel('Date', fontweight = 'bold')
    plt.ylabel('Closing Price', fontweight = 'bold')
    return st.pyplot(fig)

def merge_plot(symbol):
    colors = np.random.rand(1,3)
    for i in symbol:
        df = pd.DataFrame(data[i].Close)
        df['Date'] = df.index
        fig,ax = plt.subplots()
        plt.plot(df.Date,df.Close, color = colors)
    return st.pyplot(fig)

num_company = st.sidebar.slider('First N number of Companies to plot', 1, 10)

if st.button('Show Plots'):
    st.header('Stock Closing Price')
    for i in list(df_selected_sector.Symbol)[:num_company]:
        price_plot(i)


# Sidebar - Producing an Overlay of selected stocks
selection = st.sidebar.multiselect('For Plot Overly', list(df_selected_sector.Symbol)[:] )

if st.sidebar.button('Plot Overlay'):
    st.header('Overlayed Plots')
    fig,ax = plt.subplots()

    # for every selected stock in selection, assign it a random color and plot
    for i in selection:
        colors = [np.random.rand(), np.random.rand(), np.random.rand() ]
        df = pd.DataFrame(data[i].Close)
        df['Date'] = df.index
        plt.plot(df.Date, df.Close, color = colors, alpha = 0.8, label=str(i))
        plt.legend()

    plt.xticks(rotation = 90)
    plt.title('Overlay of '+ str(selection), fontweight = 'bold')
    plt.xlabel('Date', fontweight = 'bold')
    plt.ylabel('Closing Price', fontweight = 'bold')
    plt.legend()
    st.pyplot(fig)

fig, ax = plt.subplots()




