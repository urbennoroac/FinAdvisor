from st_on_hover_tabs import on_hover_tabs
import streamlit as st
import yfinance as yf
import pandas as pd

from datetime import date
import base64
from stocks import runStocks
from sentiment_twitter import runSentiment
from predicciones import runPredicciones
from PIL import Image

from subplots import get_candlestick_plot
img2 = Image.open('logos/logo-no-background2.png')
img_nltk= Image.open('logos/nltk.png')
st.set_page_config(page_title = 'FinAdvisor', page_icon = img2, layout="wide")

st.markdown('<style>' + open('./style.css').read() + '</style>', unsafe_allow_html=True)


def set_bg_hack(main_bg):
    
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
    tabs = on_hover_tabs(tabName=['Intro', 'Acciones', 'Noticias', 'Twitter', 'Predicciones'], 
                         iconName=['home', 'price_check', 'newspaper', 'flutter_dash', 'trending_up'], default_choice=0)



if tabs =='Intro':
    col1, col2 = st.columns(2)
    with col1:
        st.image(img2)
    with col2:
        st.title("FinAdvisor")
        st.header('Introducción')
        st.markdown('<div style="text-align: justify;">FinAdvisor es una herramienta que permite generar conclusiones acerca del comportamiento de diferentes acciones a traves del análisis de sentimiento en diferentes plataformas, como plataformas de noticias y twitter, a tráves de este análisis los usuarios podran determinar cual podria ser el comportamiento de las acciones en los próximos días.</div>', unsafe_allow_html=True)
    

    st.subheader('¿Por qué usar el análisis de sentimientos para las finanzas?')
    st.markdown('<div style="text-align: justify;">Las finanzas son el estudio de la gestión del dinero, las inversiones y otros instrumentos financieros. Es un aspecto crucial de cualquier negocio u organización, ya que ayuda a garantizar que haya suficiente capital disponible para satisfacer las diversas necesidades y objetivos financieros de la entidad. El análisis de sentimientos, por otro lado, es una rama de la minería de datos que se ocupa de la identificación y análisis de emociones, opiniones y actitudes expresadas en texto o lenguaje hablado. A menudo se usa en finanzas para medir el sentimiento del mercado o de acciones individuales. Hay muchas maneras diferentes de realizar análisis de sentimiento en finanzas. Un método común es usar técnicas de procesamiento de lenguaje natural (NLP) para analizar grandes cantidades de datos de texto, como artículos de noticias o publicaciones en redes sociales, para identificar tendencias y patrones en la forma en que las personas hablan sobre una empresa o mercado en particular. Esto puede hacerse manualmente, por analistas capacitados o con el uso de algoritmos automatizados y modelos de aprendizaje automático. Otro método de análisis de sentimiento en las finanzas es utilizar indicadores financieros y análisis técnico para identificar patrones en el movimiento de los precios de las acciones u otros instrumentos financieros. Esto se puede hacer analizando el volumen de la actividad comercial, el número de compradores y vendedores y la dirección general del mercado. El análisis de sentimiento puede ser una herramienta poderosa en finanzas, ya que permite a los inversores y analistas comprender mejor el mercado y tomar decisiones más informadas sobre dónde asignar su capital. También puede ayudar a identificar riesgos y oportunidades potenciales, y puede usarse para desarrollar estrategias para mitigar o aprovechar estas tendencias. Sin embargo, es importante tener en cuenta que el análisis de sentimientos no es una ciencia perfecta, y siempre es importante considerar múltiples fuentes de información y realizar una debida diligencia exhaustiva antes de tomar cualquier decisión de inversión.</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader('¿Comó se realiza el análisis de sentimientos?')
        st.markdown('<div style="text-align: justify;">Se realiza mediante el uso de la libreria NLTK. El kit de herramientas de lenguaje natural (NLTK) es una biblioteca popular de Python para trabajar con datos de lenguaje humano. Proporciona una amplia gama de herramientas y recursos para tareas como tokenización, derivación, lematización, etiquetado de partes del discurso y análisis. Una de las características principales de NLTK es su extensa colección de corpus (grandes cuerpos de datos lingüísticos), que se pueden utilizar para entrenar y evaluar modelos de procesamiento de lenguaje natural. NLTK también incluye una gama de herramientas de preprocesamiento y visualización, así como interfaces para otras bibliotecas y herramientas como WordNet y Treebank. NLTK se usa ampliamente en investigación y educación, y también es una opción popular para proyectos de procesamiento de lenguaje natural en la industria. Está bien documentado y tiene una comunidad de usuarios grande y activa, lo que facilita encontrar ayuda y recursos en línea. En general, NLTK es una biblioteca poderosa y flexible que facilita el trabajo con datos de lenguaje humano en Python. Ya sea que sea un investigador, un estudiante o un desarrollador profesional, NLTK es un recurso valioso para cualquier proyecto de procesamiento de lenguaje natural.</div>', unsafe_allow_html=True)
    with col2:
        st.image(img_nltk)

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

                df = tickerDf
                df[f'{ma1}_ma'] = df['Close'].rolling(ma1).mean()
                df[f'{ma2}_ma'] = df['Close'].rolling(ma2).mean()
                df = df[-days_to_plot:]
                
                st.plotly_chart(
                get_candlestick_plot(df, ma1, ma2, tickerSymbol),
                use_container_width = True,
                )

                df_new = tickerDf[['Date', 'Dividends']]
                df_new.Date = df.Date.astype(str)
                df_new = df_new.rename(columns={'Date' : 'index'}).set_index('index')
                
                #st.area_chart(df_new)
                st.line_chart(tickerDf.Dividends)
                df_new = tickerDf[['Date', 'Stock Splits']]
                st.line_chart(tickerDf['Stock Splits'])

    

elif tabs == 'Noticias':
    runStocks()

elif tabs == 'Twitter':
    runSentiment()

elif tabs == 'Predicciones':
    runPredicciones()
    