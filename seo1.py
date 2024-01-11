from bs4 import BeautifulSoup
import pandas as pd
import requests
import nltk
from nltk.tokenize import word_tokenize
from nltk import ngrams
import streamlit as st
import base64

# nltk.download('stopwords') # stopwords are words like (to,if,the.. etc)
# nltk.download('punkt')

st.title('Article SEO Analyzer')
url = st.text_input('Enter the URL')

def seo_analysis(url):
    if not url:
        st.warning("Please enter a valid URL.")
        return

    try:
        # Send requests to get the URL content
        res = requests.get(url).text

        # Parse the HTML of the URL content using Beautiful Soup
        soup = BeautifulSoup(res, 'html.parser')

        # Create lists to store values
        bad = []  # to list all the missing/bad things from the webpage
        good = []
        keywords = []

        # Title
        title = soup.find('title').text
        if title:
            good.append(f'Title exists: {title}')
        else:
            bad.append('No Title')

        # Meta Description
        meta_d = soup.find('meta', attrs={'name': 'description'})['content']
        if meta_d:
            good.append(f'Meta description exists: {meta_d}')
        else:
            bad.append('No Meta Description')

        # Headings
        headings = ['h1', 'h2', 'h3']
        h_tags = []
        for h in soup.find_all(headings):
            good.append(f'{h.name} --> {h.text.strip()}')
            h_tags.append(h.name)

        if 'h1' not in h_tags:
            bad.append('No H1 found')

        # Image Alt text
        for i in soup.find_all('img', alt=''):
            bad.append(f'No Alt: {i}')

        # Get the keywords
        body = soup.find('body').text
        words = [i.lower() for i in word_tokenize(body)]
        bi_grams = ngrams(words, 2)
        freq_bi_grams = nltk.FreqDist(bi_grams)
        bigrams_common = freq_bi_grams.most_common(10)

        # To fetch all the content from the body tag and tokenize it and store it in the created list
        sw = nltk.corpus.stopwords.words('english')  # creating a list of all English stopwords
        # Creating a list to store only meaningful words and discard the stopwords
        new_words = []
        for i in words:
            if i not in sw and i.isalpha():
                new_words.append(i)

        freq_new = nltk.FreqDist(new_words)
        new_words_common = freq_new.most_common(10)

        # Make sure "good" and "bad" lists have the same length
        max_len = max(len(good), len(bad))
        good += [''] * (max_len - len(good))
        bad += [''] * (max_len - len(bad))


        # Print the results using columns
        tab1,tab2, tab3, tab4 = st.tabs(['Keywords','Keyword Pairs','Good','Warnings'])

        with tab1:
            st.header("Keywords")
            for i in new_words_common:
                st.text(i)

        with tab2:
            st.header("Keyword Pairs")
            for i in bigrams_common:
                st.text(i)

        with tab3:
            st.header("Good")
            for i in good:
                st.success(i)

        with tab4:
            st.header("Warnings")
            for i in bad:
                st.error(i)

        # Generate download button for the report
        df = pd.DataFrame({"Good": good, "Warnings": bad})
        csv_link = get_csv_download_link(df, "seo_report.csv")
        st.markdown(csv_link, unsafe_allow_html=True)

    except requests.exceptions.MissingSchema:
        st.error("Invalid URL. Please enter a valid URL with a scheme (e.g., 'http://' or 'https://').")

# Function to generate the download link
def get_csv_download_link(dataframe, filename):
    csv = dataframe.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download Report</a>'
    return href

# Calling the function
seo_analysis(url)
