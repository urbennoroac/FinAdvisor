from st_on_hover_tabs import on_hover_tabs
import streamlit as st
import yfinance as yf
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
import numpy as np
import matplotlib.pylab as plt
import base64
from stocks import runStocks
from main import runSentiment
from PIL import Image
from subplots import get_candlestick_plot
st.set_page_config(layout="wide")

st.title("FinAdvisor")
st.markdown('<style>' + open('./style.css').read() + '</style>', unsafe_allow_html=True)

def set_bg_hack(main_bg):
    '''
    A function to unpack an image from root folder and set as bg.
 
    Returns
    -------
    The background.
    '''
    # set bg name
    main_bg_ext = "png"
        
    st.markdown(
         f"""
         <style>
         .stApp {{
             background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
    )

with st.sidebar:
    tabs = on_hover_tabs(tabName=['Intro', 'Acciones', 'Noticias', 'Twitter'], 
                         iconName=['home', 'price_check', 'newspaper', 'flutter_dash'], default_choice=0)



if tabs =='Intro':
    st.latex(r'''
    a + ar + a r^2 + a r^3 + \cdots + a r^{n-1} =
    \sum_{k=0}^{n-1} ar^k =
    a \left(\frac{1-r^{n}}{1-r}\right)
    ''')

elif tabs == 'Acciones':
    #st.write('Nombre de la opción {}'.format(tabs))
    
    # Concatena nombres y simbolos y los diccionarios de otra lista
    # que nos permitiran seleccionar differentes opciones
    tickers = pd.read_csv('tickers.csv')
    symbols = tickers['Symbol'].to_list()
    names = tickers['Company Name'].to_list()
    result = list(symbols[i]+' - '+names[i] for i in range(len(names)))

    # Obtiene la fecha del dia de hoy
    today = date.today()
    d1 = today.strftime("%A, %B %d, %Y") # YYYY-mm-dd

    st.subheader( "Precio Acciones"
    )

    # tickerSymbol = "GOOGL"
    # tickerSymbol = st.text_input('Enter ticker')
    tickerSymbol = st.selectbox('Selecciona una nombre Ticker para buscar los precios de la acción', result)

    tickerData = yf.Ticker(symbols[result.index(tickerSymbol)])

    tickerDf = tickerData.history(period='max')
    tickerDfToday = tickerData.history(period='1d')
    tickerDfYes = tickerData.history(period='2d')

    if tickerDfToday.empty:
        df2 = {'Open': ['No data found'], 'Close': ['No data found'], 'High': ['No data found'], 'Low': ['No data found'], 'Volume': ['No data found'], 'Dividends': ['No data found']}
        tickerDfToday = df2

    tickerDf = tickerDf.reset_index(level=0)
    st.write("""
    ### """ + symbols[result.index(tickerSymbol)] + """
    #### """ + names[result.index(tickerSymbol)])

    with open('elements.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


    
    
    
    tab1, tab2, tab3 = st.tabs(["Precios", "Detalles", "Gráficas"])
    with st.container():
        with tab1:
            with st.container():
                st.header("Precios")
                col1, col2, col3 = st.columns(3)
                col1.metric("Precio Apertura", round(tickerDfToday['Open'][0],5), (str((round(100-((round(tickerDfYes['Open'][0],5)*100)/round(tickerDfToday['Open'][0],5)), 5)))+"%") )
                col2.metric("Precio Cierre", round(tickerDfToday['Close'][0],5), (str((round(100-((round(tickerDfYes['Close'][0],5)*100)/round(tickerDfToday['Open'][0],5)), 5)))+"%"))
                col3.metric("Precio Maximo", round(tickerDfToday['High'][0],5), (str((round(100-((round(tickerDfYes['High'][0],5)*100)/round(tickerDfToday['Open'][0],5)), 5)))+"%"))

                col1, col2, col3 = st.columns(3)
                col1.metric("Precio Minimo", round(tickerDfToday['Low'][0],5), (str((round(100-((round(tickerDfYes['Low'][0],5)*100)/round(tickerDfToday['Open'][0],5)), 5)))+"%"))
                col2.metric("Volumen", round(tickerDfToday['Volume'][0],5) , (str((round(100-((round(tickerDfYes['Volume'][0],5)*100)/round(tickerDfToday['Open'][0],5)), 5)))+"%"))
                col3.metric("Precio de Dividendos", round(tickerDfToday['Dividends'][0], 5), (str((round(100-((round(tickerDfYes['Dividends'][0],5)*100)/round(tickerDfToday['Open'][0],5)), 5)))+"%"))
                

        with tab2:
            with st.container():
                st.header("Detalles")
                col1, col2, col3 = st.columns(3)
                col1.metric("Nombre Compañia", names[result.index(tickerSymbol)], "Nombre Completo")
                col2.metric("Symbol", symbols[result.index(tickerSymbol)] , "Simbolo de Ticker")
                col3.metric("Nombre de Security", tickers['Security Name'][result.index(tickerSymbol)], "")
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Categoría de Mercado", tickers['Market Category'][result.index(tickerSymbol)], "")
                col2.metric("Test Issue", tickers['Test Issue'][result.index(tickerSymbol)], "")
                col3.metric("Estado Financiero", tickers['Financial Status'][result.index(tickerSymbol)], "")

                

        with tab3:
            with st.container():
                st.header("Gráficas")

                days_to_plot = st.slider(
                    'Días a Gráficar', 
                    min_value = 1,
                    max_value = 300,
                    value = 120,
                )
                ma1 = st.number_input(
                    'Promedio Modificable 1',
                    value = 10,
                    min_value = 1,
                    max_value = 120,
                    step = 1,    
                )
                ma2 = st.number_input(
                    'Promedio Modificable 2',
                    value = 20,
                    min_value = 1,
                    max_value = 120,
                    step = 1,    
                )

                # Get the dataframe and add the moving averages
                df = tickerDf
                df[f'{ma1}_ma'] = df['Close'].rolling(ma1).mean()
                df[f'{ma2}_ma'] = df['Close'].rolling(ma2).mean()
                df = df[-days_to_plot:]
                
                st.plotly_chart(
                get_candlestick_plot(df, ma1, ma2, tickerSymbol),
                use_container_width = True,
                )

                st.line_chart(tickerDf.Dividends)

                #st.line_chart(tickerDf.Stock)
                st.line_chart(tickerDf['Stock Splits'])

                
        # st.text(tickerDfToday)

    

    # Display the plotly chart on the dashboard
    
   

    
    

elif tabs == 'Noticias':
    runStocks()

elif tabs == 'Twitter':
    runSentiment()
    