import streamlit as st
import numpy as np
import matplotlib.pylab as plt
import base64
from stocks import runStocks
from main import runSentiment
from PIL import Image


hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

padding = 0
padding2 = 4
st.markdown(f""" <style>
    .reportview-container .main .block-container{{
        padding-top: {padding}rem;
        padding-right: {padding2}rem;
        padding-left: {padding2}rem;
        padding-bottom: {padding}rem;
    }} </style> """, unsafe_allow_html=True)




st.markdown(""" <style>
MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

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

def main():
    

    menu = ["Intro", "Twitter Sentiment", "Stock Sentiment"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Stock Sentiment":
        runStocks()
    elif choice == "Twitter Sentiment":
        runSentiment()
    
    



if __name__ == '__main__':
    set_bg_hack('./image/bg_main.png')
    main()