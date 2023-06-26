import streamlit as st
import aip

aip.clear_cookie_manager()

# Title
st.title('Logout')
st.info('**You have successfully logged out. For login please click here: [Home page]('
        'https://aip-fyi-budget-tracker.streamlit.app)**', icon="🏠")