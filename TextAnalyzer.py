import nltk
from transformers import pipeline
import streamlit as st
import docx
from PyPDF2 import PdfReader
import streamlit as st
from textly import load_model, sentiment, summarize, extract_text_from_txt, extract_text_from_docx, extract_text_from_pdf
from nltk.sentiment import SentimentIntensityAnalyzer
pos = "color: green; font-weight: bold;"
neg = "color: red; font-weight: bold;"
def main():  
    st.markdown(
    f"<h1 style='text-align: center;'>DocuAnalyzer</h1>", 
    unsafe_allow_html=True
) 
    summarizer=load_model()
    user_input=st.text_area('Enter text here')
    uploaded_file=st.file_uploader("Choose a file", type=["txt", "docx", "pdf"])
    if uploaded_file is not None:
        file_extension=uploaded_file.name.split(".")[-1]
        if file_extension=="txt":
            text=extract_text_from_txt(uploaded_file)
        elif file_extension=="docx":
            text=extract_text_from_docx(uploaded_file)
        elif file_extension == "pdf":
            text=extract_text_from_pdf(uploaded_file)

    # Button to trigger summarization
    if st.button("Generate Summary"):
        if user_input:
            summary=summarize(user_input, summarizer, max_value=350, min_value=90)
            st.subheader("Generated Summary:")
            st.write(summary)
        elif uploaded_file is not None:
            summar =summarize(text, summarizer, max_value=350, min_value=80)
            st.write(summary)

    
    if st.button("Perform Sentiment Analysis"):
        sentiment_result=sentiment(user_input)
        if sentiment_result=='Positive':
            style=pos
        elif sentiment_result=="Negative":
            style=neg
        else: 
            style=""
        st.subheader("Sentiment Analysis Result:")
        st.markdown(f"**Sentiment:** <span style='{style}'>{sentiment_result}</span>", unsafe_allow_html=True)
if __name__ == '__main__':
    main()
@st.cache_resource
def load_model():
    return pipeline('summarization')

def extract_text_from_txt(file):
    text=str(file.read())
    return text

def extract_text_from_docx(file):
    doc=docx.Document(file)
    full_text=""
    for para in doc.paragraphs:
        full_text+=para.text + "\n"
    return full_text

def extract_text_from_pdf(file):
    pdf_reader=PdfReader(file)
    full_text=""
    for page_num in range(len(pdf_reader.pages)):
        page=pdf_reader.pages[page_num]
        full_text+=page.extract_text() + "\n"
    return full_text

def summarize(text, summarizer, max_value=350, min_value=50):
    text=text.replace('.', '.<eos>')
    text=text.replace('?', '?<eos>')
    text=text.replace('!', '!<eos>')
    max_chunk=600
    sentences=text.split('<eos>')
    current_chunk=0 
    chunks=[]
    for sentence in sentences:
        if len(chunks)==current_chunk + 1: 
            if len(chunks[current_chunk]) + len(sentence.split(' ')) < max_chunk:
                chunks[current_chunk].extend(sentence.split(' '))
            else:
                current_chunk+= 1
                chunks.append(sentence.split(' '))
        else:
            chunks.append(sentence.split(' '))
    for chunk_id in range(len(chunks)):
        chunks[chunk_id] = ' '.join(chunks[chunk_id])
    summary=[]
    for i in chunks:
        sumr=summarizer(i, max_length=max_value, min_length=min_value, do_sample=False)[0]['summary_text']
        summary.append(sumr)
    return ' '.join(summary)

def sentiment(text):
    nltk.download('vader_lexicon')
    text=str(text)
    sia=SentimentIntensityAnalyzer()
    sent=sia.polarity_scores(text)
    if sent['pos'] > 0.15 and (sent['pos']>sent['neg']):
        sentiment_label='Positive'
    elif (sent['neg'] > 0.15) and (sent['neg']>sent['pos']):
        sentiment_label='Negative'
    elif sent['neu'] > 0.8:
        sentiment_label='Neutral'
    else:
        sentiment_label='Neutral'
    return sentiment_label
