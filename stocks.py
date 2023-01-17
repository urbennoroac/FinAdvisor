def runStocks():
    import streamlit as st
    from urllib.request import urlopen, Request
    from bs4 import BeautifulSoup
    import altair as alt
    import yfinance as yf
    import pandas as pd
    import matplotlib.pyplot as plt   # Para la generación de gráficas a partir de los datos
    import seaborn as sns    
    from datetime import date, timedelta
    import plotly
    import plotly.express as px
    # NLTK VADER para realizar el analisis de sentimientos
    import nltk 
    # Esta libreria permite conocer el sentimiento de las noticias con las que se va a analizar las notas para predecir
    # el sentimiento de los stocks.
    nltk.downloader.download('vader_lexicon')
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    from datetime import datetime


    st.markdown('<style>' + open('./style.css').read() + '</style>', unsafe_allow_html=True)

    def get_news(ticker):
        url = finviz_url + ticker
        req = Request(url=url,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}) 
        response = urlopen(req)    
        # Lee los contenidos en el archivo 'HTML'
        # Read the contents of the file into 'html'
        html = BeautifulSoup(response)
        news_table = html.find(id='news-table')
        return news_table
        
    # parse news into dataframe
    def parse_news(news_table):
        parsed_news = []
        
        for x in news_table.findAll('tr'):
           
            try:
                text = x.a.get_text() 
                date_scrape = x.td.text.split()

                if len(date_scrape) == 1:
                    time = date_scrape[0]				
            
                else:
                    date = date_scrape[0]
                    time = date_scrape[1]
                
                parsed_news.append([date, time, text])        
                
                
            except:
                pass
                
        columns = ['date', 'time', 'Encabezado']
 
        parsed_news_df = pd.DataFrame(parsed_news, columns=columns)        
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
        tab1, tab2, tab3, tab4 = st.tabs(["Encabezados Noticias", "Sentimientos por Hora", "Sentimientos por Día", "Correlaciones"])
        news_table = get_news(ticker)
        parsed_news_df = parse_news(news_table)
        
        print('Hola')
        today = date.today()

        d1 = today.strftime("%Y-%m-%d")
        end_date = d1
        d2 = date.today() - timedelta(days=360)
        d2 = d2.strftime("%Y-%m-%d")
        start_date = d2

        data = yf.download('AAPL', 
                            start=start_date, 
                            end=end_date, 
                            progress=False)
        data = data.tz_localize(None)
        data = data.reset_index(drop = False)
        print(data.head())

        #print(parsed_news_df)
        parsed_and_scored_news = score_news(parsed_news_df)
        print(parsed_and_scored_news)
        
        parsed_and_scored_news2 = parsed_and_scored_news.reset_index(drop=False)
        data2 = pd.concat([parsed_and_scored_news2, data], axis=1, keys=['parsed_and_scored_news2', 'data']).corr().loc['parsed_and_scored_news2', 'data']
        data3 = pd.concat([parsed_and_scored_news2, data], axis=1, keys=['parsed_and_scored_news2', 'data'])
        print(data2)
        print('Data 3')
        print(data3)
      
        fig_hourly = plot_hourly_sentiment(parsed_and_scored_news, ticker)
        fig_daily = plot_daily_sentiment(parsed_and_scored_news, ticker) 
        
        with tab1:
            with st.container():
                st.header("Encabezados Noticias")
                st.dataframe(parsed_and_scored_news)

        with tab2:
            with st.container():
                st.header("Mapa de Calor Correlación Scores - Precio Stocks")
                st.plotly_chart(fig_hourly)

        with tab3:
            with st.container():
                st.header("Sentimientos por Día")
                st.plotly_chart(fig_daily)
        
        with tab4:
            with st.container():
                st.header("Correlaciones")
                fig, ax = plt.subplots()
                sns.heatmap(data2, ax=ax)
                st.write(fig)
                
        
        
                    
    except Exception as e:
        print(str(e))
        st.write("Enter a correct stock ticker, e.g. 'AAPL' above and hit Enter.")	

