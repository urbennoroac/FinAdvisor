import json
import streamlit as st
from attr import has
from helper import preprocessing_data, graph_sentiment, analyse_mention, analyse_hastag, download_data

from pathlib import Path
from streamlit import session_state as state
from streamlit_elements import elements, sync, event
from types import SimpleNamespace

from dashboard import Dashboard, Editor, Card, DataGrid, Radar, Pie, Player


def main():
    st.write(
        """
        FinAdvisor
        =====================
        Create a draggable and resizable dashboard in Streamlit, featuring Material UI widgets,
        Monaco editor (Visual Studio Code), Nivo charts, and more!
        [github_badge]: https://badgen.net/badge/icon/GitHub?icon=github&color=black&label
        [github_link]: https://github.com/okld/streamlit-elements
        [pypi_badge]: https://badgen.net/pypi/v/streamlit-elements?icon=pypi&color=black&label
        [pypi_link]: https://pypi.org/project/streamlit-elements
        """
    )

    with st.expander("GETTING STARTED"):
        st.write((Path(__file__).parent/"README.md").read_text())

    st.title("Twitter Sentimental Analysis")

    function_option = st.sidebar.selectbox("Select The Funtionality: ", ["Search By #Tag and Words", "Search By Username"])

    if function_option == "Search By #Tag and Words":
        word_query = st.text_input("Enter the Hastag or any word")

    if function_option == "Search By Username":
        word_query = st.text_input("Enter the Username ( Don't include @ )")

    number_of_tweets = st.slider("How many tweets You want to collect from {}".format(word_query), min_value=100, max_value=10000)
    st.info("1 Tweets takes approx 0.05 sec so you may have to wait {} minute for {} Tweets, So Please Have Patient.".format(round((number_of_tweets*0.05/60),2), number_of_tweets))

    if st.button("Analysis Sentiment"):

        data = preprocessing_data(word_query, number_of_tweets, function_option)
        analyse = graph_sentiment(data)
        mention = analyse_mention(data)
        hastag = analyse_hastag(data)

        st.write(" ")
        st.write(" ")
        st.header("Extracted and Preprocessed Dataset")
        st.write(data)
        download_data(data, label="twitter_sentiment_filtered")
        #st.write(" ")
        
        col1, col2, col3 = st.columns(3)
        with col2:
            st.markdown("### EDA On the Data")


        col1, col2 = st.columns(2)

        with col1:
            st.text("Top 10 @Mentions in {} tweets".format(number_of_tweets))
            st.bar_chart(mention)
        with col2:
            st.text("Top 10 Hastags used in {} tweets".format(number_of_tweets))
            st.bar_chart(hastag)
        
        col3, col4 = st.columns(2)
        with col3:
            st.text("Top 10 Used Links for {} tweets".format(number_of_tweets))
            st.bar_chart(data["links"].value_counts().head(10).reset_index())
        
        with col4:
            st.text("All the Tweets that containes top 10 links used")
            filtered_data = data[data["links"].isin(data["links"].value_counts().head(10).reset_index()["index"].values)]
            st.write(filtered_data)

        st.subheader("Twitter Sentment Analysis")
        st.bar_chart(analyse)

        if "w" not in state:
            board = Dashboard()
            w = SimpleNamespace(
                dashboard=board,
                editor=Editor(board, 0, 0, 6, 11, minW=3, minH=3),
                player=Player(board, 0, 12, 6, 10, minH=5),
                pie=Pie(board, 6, 0, 6, 7, minW=3, minH=4),
                radar=Radar(board, 12, 7, 3, 7, minW=2, minH=4),
                card=Card(board, 6, 7, 3, 7, minW=2, minH=4),
                data_grid=DataGrid(board, 6, 13, 6, 7, minH=4),
            )
            state.w = w

            w.editor.add_tab("Card content", Card.DEFAULT_CONTENT, "plaintext")
            result = data.to_json(orient="split")
            parsed = json.loads(result)
            #st.write(parsed)
            w.editor.add_tab("Data grid", json.dumps(DataGrid.DEFAULT_ROWS, indent=2), "json")
            w.editor.add_tab("Radar chart", json.dumps(Radar.DEFAULT_DATA, indent=2), "json")
            w.editor.add_tab("Pie chart", json.dumps(Pie.DEFAULT_DATA, indent=2), "json")
        else:
            w = state.w

        with elements("demo"):
            event.Hotkey("ctrl+s", sync(), bindInputs=True, overrideDefault=True)

            with w.dashboard(rowHeight=57):
                w.editor()
                w.player()
                w.pie(w.editor.get_content("Pie chart"))
                w.radar(w.editor.get_content("Radar chart"))
                w.card(w.editor.get_content("Card content"))
                w.data_grid(w.editor.get_content("Data grid"))


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    main()