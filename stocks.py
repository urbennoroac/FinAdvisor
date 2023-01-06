def runStocks():
    import streamlit as st
    from urllib.request import urlopen, Request
    from bs4 import BeautifulSoup
    import pandas as pd
    import plotly
    import plotly.express as px
    import json # for graph plotting in website
    # NLTK VADER for sentiment analysis
    import nltk 
    # Esta libreria permite conocer el sentimiento de las noticias con las que se va a analizar las notas para predecir
    # el sentimiento de los stocks.
    nltk.downloader.download('vader_lexicon')
    from nltk.sentiment.vader import SentimentIntensityAnalyzer

    import subprocess
    from datetime import datetime
    import os

    st.markdown('<style>' + open('./style.css').read() + '</style>', unsafe_allow_html=True)

    def get_news(ticker):
        url = finviz_url + ticker
        req = Request(url=url,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}) 
        response = urlopen(req)    
        # Read the contents of the file into 'html'
        html = BeautifulSoup(response)
        # Find 'news-table' in the Soup and load it into 'news_table'
        news_table = html.find(id='news-table')
        return news_table
        
    # parse news into dataframe
    def parse_news(news_table):
        parsed_news = []
        
        for x in news_table.findAll('tr'):
            # occasionally x (below) may be None when the html table is poorly formatted, skip it in try except instead of throwing an error and exiting
            # may also use an if loop here to check if x is None first	
            try:
                # read the text from each tr tag into text
                # get text from a only
                text = x.a.get_text() 
                # splite text in the td tag into a list 
                date_scrape = x.td.text.split()
                # if the length of 'date_scrape' is 1, load 'time' as the only element

                if len(date_scrape) == 1:
                    time = date_scrape[0]				
                # else load 'date' as the 1st element and 'time' as the second    
                else:
                    date = date_scrape[0]
                    time = date_scrape[1]
                
                # Append ticker, date, time and headline as a list to the 'parsed_news' list
                parsed_news.append([date, time, text])        
                
                
            except:
                pass
                
        # Set column names
        columns = ['date', 'time', 'Encabezado']
        # Convert the parsed_news list into a DataFrame called 'parsed_and_scored_news'
        parsed_news_df = pd.DataFrame(parsed_news, columns=columns)        
        # Create a pandas datetime object from the strings in 'date' and 'time' column
        parsed_news_df['datetime'] = pd.to_datetime(parsed_news_df['date'] + ' ' + parsed_news_df['time'])
                
        return parsed_news_df
            
        
            
    def score_news(parsed_news_df):
        # Instantiate the sentiment intensity analyzer
        vader = SentimentIntensityAnalyzer()
        
        # Iterate through the headlines and get the polarity scores using vader
        scores = parsed_news_df['Encabezado'].apply(vader.polarity_scores).tolist()

        # Convert the 'scores' list of dicts into a DataFrame
        scores_df = pd.DataFrame(scores)

        # Join the DataFrames of the news and the list of dicts
        parsed_and_scored_news = parsed_news_df.join(scores_df, rsuffix='_right')             
        parsed_and_scored_news = parsed_and_scored_news.set_index('datetime')    
        parsed_and_scored_news = parsed_and_scored_news.drop(['date', 'time'], 1)          
        parsed_and_scored_news = parsed_and_scored_news.rename(columns={"compound": "sentiment_score"})

        return parsed_and_scored_news

    def plot_hourly_sentiment(parsed_and_scored_news, ticker):
    
        # Group by date and ticker columns from scored_news and calculate the mean
        mean_scores = parsed_and_scored_news.resample('H').mean()

        # Plot a bar chart with plotly
        fig = px.bar(mean_scores, x=mean_scores.index, y='sentiment_score', title = ticker + ' Sentiment Scores por Hora')
        return fig # instead of using fig.show(), we return fig and turn it into a graphjson object for displaying in web page later

    def plot_daily_sentiment(parsed_and_scored_news, ticker):
    
        # Group by date and ticker columns from scored_news and calculate the mean
        mean_scores = parsed_and_scored_news.resample('D').mean()

        # Plot a bar chart with plotly
        fig = px.bar(mean_scores, x=mean_scores.index, y='sentiment_score', title = ticker + ' Sentiment Scores por Dia')
        return fig # instead of using fig.show(), we return fig and turn it into a graphjson object for displaying in web page later

    # for extracting data from finviz
    finviz_url = 'https://finviz.com/quote.ashx?t='


    st.header("Ánalisis de Sentimientos en Noticias")

    ticker = st.text_input('Ingresa el Ticker de la acción', 'AAPL').upper()

    df = pd.DataFrame({'datetime': datetime.now(), 'ticker': ticker}, index = [0])


    try:
        st.subheader("Valor de Sentimientos (Hora/Día) - {} Stock".format(ticker))
        description = """
            La gráfica obtiene un promedio del sentimient score de la accion {} por hora y por dia 
            La tabla por otro lado obtiene los encabezados mas reientes de las acciones y el sentiment score, tanto positivo, negativo o neutral y su promedio.
            Los encabezados de noticias se obtienen a traves de la pagina de noticias FinVizS
            Para el análisis de los sentimientos se utilizo la libreria de Python nltk.sentiment.vader
            """.format(ticker)
        st.write(description)
        tab1, tab2, tab3 = st.tabs(["Encabezados Noticias", "Sentimientos por Hora", "Sentimientos por Día"])
        news_table = get_news(ticker)
        parsed_news_df = parse_news(news_table)
        #print(parsed_news_df)
        parsed_and_scored_news = score_news(parsed_news_df)
        fig_hourly = plot_hourly_sentiment(parsed_and_scored_news, ticker)
        fig_daily = plot_daily_sentiment(parsed_and_scored_news, ticker) 
        
        with tab1:
            with st.container():
                st.header("Encabezados Noticias")
                st.dataframe(parsed_and_scored_news)

        with tab2:
            with st.container():
                st.header("Sentimientos por Hora")
                st.plotly_chart(fig_hourly)

        with tab3:
            with st.container():
                st.header("Sentimientos por Día")
                st.plotly_chart(fig_daily)
                    
    except Exception as e:
        print(str(e))
        st.write("Enter a correct stock ticker, e.g. 'AAPL' above and hit Enter.")	

