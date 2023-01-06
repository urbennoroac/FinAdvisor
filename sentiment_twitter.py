def runSentiment():
    from attr import has
    import pandas as pd
    import streamlit as st
    from helper import preprocessing_data, graph_sentiment, analyse_mention, analyse_hastag, download_data
    import altair as alt
    


    st.title("Twitter Sentimental Analysis")

    
    col11, col22 = st.columns(2)
    with col11:
        function_option = st.selectbox("Selecciona el metodo por el cual deseas buscar los tweets: ", ["Buscar por #Hashtag o Palabra", "Buscar por usuario"])
    with col22:
        lengua = st.radio(
        "Selecciona el idioma con el cual deseas hacer el análisis",
        ('Español', 'Ingles'), horizontal=True)

        if lengua == 'Español':
            var_idiom='es'
        else:
            var_idiom='en'

    if function_option == "Buscar por #Hashtag o Palabra":
            word_query = st.text_input("Ingresa un Hashtag o cualquier otra palabra")
    if function_option == "Buscar por usuario":
        word_query = st.text_input("Ingresa el nombre de usuario (sin @)")

    number_of_tweets = st.slider("¿Cuál es el número de tweets {}".format(word_query), min_value=100, max_value=10000)
    st.info("1 Tweets toma aprox 0.05 segundos por lo que el tiempo de espera es de {} minutos para {} Tweets.".format(round((number_of_tweets*0.05/60),2), number_of_tweets))

    if st.button("Análisis de Sentimientos"):

        data = preprocessing_data(word_query, number_of_tweets, function_option, var_idiom)
        analyse = graph_sentiment(data)
        mention = analyse_mention(data)
        hastag = analyse_hastag(data)
        

        st.write(" ")
        st.write(" ")
        st.header("Dataset que contiene los twits")
        tab1, tab2, tab3 = st.tabs(["Tabla con Tweets", "Top Apariciones", "Análisis de Sentimientos"])
        with tab1:
            st.subheader("Tabla con Tweets")
            st.write(data)
            download_data(data, label="twitter_sentiment_filtered")
            st.write(" ")
        
        with tab2:
            st.subheader("Top Apariciones")
            col1, col2, col3 = st.columns(3)
            with col2:
                st.markdown("### Análisis de Datos")

            
            col1, col2 = st.columns(2)

            with col1:
                st.text("Top 10 @Mentions en {} tweets".format(number_of_tweets))
                df_graph_p=(data["mentions"].value_counts().head(10).reset_index())
                c = alt.Chart(df_graph_p).mark_arc().encode(
                    theta=alt.Theta(field="mentions", type="quantitative"),
                    color=alt.Color(field="index", title='Mentions', type="nominal"),
                ).interactive()
                st.altair_chart(c, use_container_width=True)

            with col2:
                st.text("Top 10 Hashtags usados en {} tweets".format(number_of_tweets))
                df = pd.DataFrame(hastag).reset_index()
                c = alt.Chart(df).mark_bar(color='firebrick').encode(
                    alt.Y('index', title='Hastags', type='nominal'),
                    alt.X('0', title='Número de apariciones', type='quantitative')
                ).interactive()
                st.altair_chart(c, use_container_width=True)
    

        
            st.text("Top 10 Links utiliados en {} tweets".format(number_of_tweets))
            df_graph=(data["links"].value_counts().head(10).reset_index())
            c = alt.Chart(df_graph).mark_bar(color='firebrick').encode(
                alt.Y('index', title='Número de apariciones', type='nominal'),
                alt.X('links', type='quantitative')
            ).interactive()
            st.altair_chart(c, use_container_width=True)
            
       
        with tab3:
            st.subheader("Twitter Sentiment Analysis")
            df_sentiment=data.drop(columns=['Tweets', 'mentions', 'hastags', 'retweets', 'links'])
            c = alt.Chart(df_sentiment).mark_circle(size=60).encode(
                x='Subjectivity:Q',
                y='Polarity:Q',
                color='Analysis:N',
                tooltip=['Subjectivity', 'Polarity', 'Analysis']
            ).interactive()

            st.altair_chart(c, use_container_width=True)
            #st.bar_chart(analyse)

            c = alt.Chart(analyse).mark_arc().encode(
                    theta=alt.Theta(field="Analysis", type="quantitative"),
                    color=alt.Color(field="index", type="nominal"),
                ).interactive()
            st.altair_chart(c, use_container_width=True)