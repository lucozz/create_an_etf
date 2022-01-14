import yfinance as yf
import streamlit as st
import pandas as pd

#import libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import squarify
import sys
import datetime
import yfinance as yf
from yahoo_fin import stock_info as si

#set pandas to show all the columns in a data frama
pd.set_option('max_columns', None)

def create_etf(name,tickers,start_date,end_date): #method returns the a dataframe with the returns of the companies and the etf
  with st.spinner('Creating ETF...'):
      ticker_marketcap = calc_marketcap(tickers)
      tickers_prices = prices(tickers)
      ticker_weights = calc_weight(ticker_marketcap)
      etf_returns = calc_return(name,tickers_prices,ticker_weights)
      etf_returns = corrections(etf_returns)
  st.success("ETF "+name+" created!")
  return(etf_returns)

def calc_marketcap(tickers): #calculates de marketcap for each companies and returns it in a dictionaty
  marketcap = []
  for ticker in tickers:
    marketcap.append(yf.Ticker(ticker).info['marketCap'])
  ticker_marketcap = dict(zip(tickers,marketcap))#zipping tickers and marketcap into a dictionary with the format "ticker":marketcap
  return(ticker_marketcap)

def prices(tickers):
  #loop to fill the marketcap list with the "marketCap" column from the yfinance library
  tickers_price = yf.download(' '.join(tickers), start=start_date, end=end_date)["Adj Close"]
  tickers_price = tickers_price.fillna(method="ffill")#fills NaN values with the previous value
  return(tickers_price)

def calc_weight(ticker_marketcap):
  #loop to sum the total market cap of all the companies listed
  total_cap = 0 
  for ticker in ticker_marketcap:
    total_cap += ticker_marketcap[ticker]
  #creates a dictionary from the individual weights of each companies in the etf
  weights = {}
  for ticker in ticker_marketcap:
    weights[ticker] = ticker_marketcap[ticker]/total_cap
  return(weights)

def calc_return(name,tickers_prices,weights):
  #calculates the weighted price of each day
  tickers_prices[name] = 0
  for ticker in weights:
    tickers_prices[name] += weights[ticker]*tickers_prices[ticker]
  #calculates the returns
  etf_return = ((tickers_prices*100) / tickers_prices.iloc[0])-100
  return(etf_return)

def corrections(etf_returns): #excluding from teh results São Paulo anniversary and Rescheduled holiday due covid
  etf_returns.drop(etf_returns.loc[etf_returns.index == '2018-01-25 00:00:00'].index, inplace=True)
  etf_returns.drop(etf_returns.loc[etf_returns.index == '2021-04-02 00:00:00'].index, inplace=True)
  return(etf_returns)

def plot_weights(tickers):  #plot pie chart of the weights
  weights = calc_weight(calc_marketcap(tickers.iloc[:, :-1]))
  plt.pie(weights.values(), labels=weights.keys(), labeldistance=1.15,wedgeprops = {'linewidth' : 3, 'edgecolor' : 'white'});
  plt.show();
  #plot treemap of the weights
  squarify.plot(sizes=weights.values(), label=weights.keys(), alpha=.8, pad = True )
  plt.axis('off')
  plt.show()

def plot_correlation(etf):#plot heatmap and the correlation between from each company and the ETF 
  plt.subplots(figsize=(10,5))
  sns.heatmap(etf.corr(), annot=True)
  #list corrlations
  print(etf.corr()[etf.columns[-1]].sort_values(ascending=False))
    
def plot_all(etf): #plot line chart with the returns of all the companies and the etf value
  st.line_chart(etf)

def plot_etf(etf):#plot line chart with the returns of the etf value only
  #plt.subplots(figsize=(22, 8))
  #plt.plot(etf.index,etf.columns[-1], data=etf)
  st.line_chart(etf.iloc[:,-1:])

def plot_compare(etfs,start,end,benchmark=0): #plot the returns of all the given etfs and the benchmark
  plt.subplots(figsize=(22, 8))
  for etf in etfs:
    plt.plot(etf.index,etf.columns[-1], data=etf)
  if benchmark != 0:
    #download the benchmark values
    bench = yf.download(benchmark, start=start_date, end=end_date)["Adj Close"]
    bench_return = ((bench*100) / bench.iloc[0])-100  #calculates the benchmark returns
    bench_return = bench_return.to_frame()
    plt.plot(bench_return.index,str(bench_return.columns[-1]), data=bench_return,label=benchmark)
  plt.legend()
  plt.show()
    


#start_date="2018-01-01" #setting start and end date
#end_date="2021-04-30"
finc11_tickers=["ITUB3.SA","BBDC3.SA","SANB11.SA","BBAS3.SA", "BPAC11.SA", "BNBR3.SA", "BRSR3.SA"] #set the tickers
#finc11 = create_etf("FINC11",finc11_tickers,start_date,end_date) #calls method that returns the etf and companies returns

test_date="2018-01-01"

#teste
tickers_list = pd.DataFrame(si.tickers_ibovespa())[0].values.tolist()

side = st.sidebar
side.header('Create your own ETF!')

tickers = side.multiselect(
     'Select the tickers',
     tickers_list)

tickers = [ticker + '.SA' for ticker in tickers]

start_date = side.date_input(
    'Start date')

end_date = side.date_input(
    'End date')

etf_name = side.text_input(
    'Give your ETF a name:')

submit_button = side.button('Submit')
if submit_button:
    st.write('You selected:', tickers)
    st.write(start_date)
    st.write(end_date)
    st.write(etf_name)
    etf_returns = create_etf(etf_name,tickers,start_date,end_date) #calls method that returns the etf and companies returns
    plot_all(etf_returns)
    plot_etf(etf_returns)