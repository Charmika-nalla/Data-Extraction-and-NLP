# -*- coding: utf-8 -*-
"""blackcoffer.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1EUnR7vcTE8WsISWGK_g7Ac9ptGNvHy-c
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

def extract_article(url):
    try:

        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else 'No Title'

        # Find the content within <div> elements containing both classes 'td-post-content' and 'tagdiv-type'
        post_content = soup.find('div', class_=lambda c: c and 'td-post-content' in c.split() and 'tagdiv-type' in c.split())
        if not post_content:
            return title, None

        # Extract the text from post_content
        article_content = post_content.get_text().strip()

        return title, article_content

    except Exception as e:
        print(f"Extraction failed for URL: {url}")
        print(e)  # Print the exception for debugging
        return None, None

def save_article(url_id, title, article_content, folder_path):
    if not article_content:
        return

    file_name = f"{url_id}.txt"
    file_path = os.path.join(folder_path, file_name)

    # Open the file in write mode, which clears the existing content
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(f"{title}\n\n{article_content}")

def main(input_file, folder_path):
    df = pd.read_excel(input_file)

    for index, row in df.iterrows():
        url_id = row['URL_ID']
        url = row['URL']

        print(f"Processing URL_ID: {url_id}, URL: {url}")

        title, article_content = extract_article(url)

        if title and article_content:
            save_article(url_id, title, article_content, folder_path)
        else:
            print(f"Failed to extract content for URL_ID: {url_id}")

if __name__ == "__main__":
    input_file = 'input.xlsx'  # Assuming input.xlsx is in the same directory as the notebook
    folder_path = 'articles'  # Current directory
    main(input_file, folder_path)

import pandas as pd
import os
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import string
import re

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

# Function to load stop words from multiple files
def load_stop_words(stop_words_folder):
    stop_words = set()
    for file_name in os.listdir(stop_words_folder):
        if file_name.endswith('.txt'):
            with open(os.path.join(stop_words_folder, file_name), 'r') as file:
                words = file.read().splitlines()
                stop_words.update(words)
    return stop_words

# Load stop words
stop_words_folder = 'StopWords'
stop_words = load_stop_words(stop_words_folder)

# Load punctuation
punctuation = set(string.punctuation)

# Function to clean and tokenize text
def clean_and_tokenize(text, stop_words, punctuation):
    # Tokenize text into words
    tokens = word_tokenize(text)

    # Remove stop words and punctuation
    tokens = [word.lower() for word in tokens if word.lower() not in stop_words and word.lower() not in punctuation]

    # Stemming
    porter = PorterStemmer()
    tokens = [porter.stem(word) for word in tokens]

    return tokens

# Function to load positive and negative words from multiple files
def load_master_dictionary(master_dict_folder):
    positive_words = set()
    negative_words = set()
    for file_name in os.listdir(master_dict_folder):
        if file_name.endswith('.txt'):
            with open(os.path.join(master_dict_folder, file_name), 'r') as file:
                for line in file:
                    word = line.strip()
                    if word:
                        if file_name.startswith('positive'):
                            positive_words.add(word.lower())
                        elif file_name.startswith('negative'):
                            negative_words.add(word.lower())
    return positive_words, negative_words

# Load positive and negative words
master_dict_folder = 'MasterDictionary'
positive_words, negative_words = load_master_dictionary(master_dict_folder)

# Function to calculate sentiment scores
def calculate_sentiment_scores(tokens, positive_words, negative_words):
    positive_score = sum(1 for word in tokens if word in positive_words)
    negative_score = sum(1 for word in tokens if word in negative_words)
    polarity_score = (positive_score - negative_score) / ((positive_score + negative_score) + 0.000001)
    subjectivity_score = (positive_score + negative_score) / (len(tokens) + 0.000001)
    return positive_score, negative_score, polarity_score, subjectivity_score

# Function to analyze readability
def analyze_readability(text, punctuation):
    sentences = sent_tokenize(text)
    total_words = sum(len(word_tokenize(sentence)) for sentence in sentences)
    total_sentences = len(sentences)
    average_sentence_length = total_words / total_sentences
    complex_word_count = sum(1 for sentence in sentences for word in word_tokenize(sentence) if len(word) > 2)
    percentage_complex_words = complex_word_count / total_words
    fog_index = 0.4 * (average_sentence_length + percentage_complex_words)
    average_words_per_sentence = total_words / total_sentences
    syllable_per_word = calculate_syllables_per_word(text)
    personal_pronoun_count = calculate_personal_pronouns(text)
    average_word_length = calculate_average_word_length(text)
    return (average_sentence_length, percentage_complex_words, fog_index, average_words_per_sentence, complex_word_count, total_words, syllable_per_word, personal_pronoun_count, average_word_length)

# Function to calculate the number of syllables in a word
def count_syllables(word):
    vowels = 'aeiouy'
    word = word.lower()
    count = 0
    if word[0] in vowels:
        count += 1
    for index in range(1, len(word)):
        if word[index] in vowels and word[index - 1] not in vowels:
            count += 1
    if word.endswith('e'):
        count -= 1
    if count == 0:
        count += 1
    return count

# Function to calculate the number of syllables per word in the text
def calculate_syllables_per_word(text):
    tokens = word_tokenize(text)
    total_syllables = sum(count_syllables(word) for word in tokens)
    total_words = len(tokens)
    syllables_per_word = total_syllables / total_words
    return syllables_per_word
import re
# Function to count personal pronouns in the text
def calculate_personal_pronouns(text):
    personal_pronouns = ['I', 'we', 'my', 'ours', 'us']
    pronoun_regex = re.compile(r'\b(?:I|we|my|ours|us)\b', re.IGNORECASE)
    # Find all matches in the text
    matches = pronoun_regex.findall(text)
    # Return the count of matches
    personal_pronoun_count=len(matches)
    return personal_pronoun_count

# Function to calculate average word length
def calculate_average_word_length(text):
    tokens = word_tokenize(text.lower())
    total_characters = sum(len(word) for word in tokens)
    total_words = len(tokens)
    average_word_length = total_characters / total_words
    return average_word_length

# Function to perform sentiment analysis and readability analysis on a given file
def analyze_file(file_path, stop_words, punctuation, positive_words, negative_words):
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()

        # Clean and tokenize text
        tokens = clean_and_tokenize(text, stop_words, punctuation)

        # Calculate sentiment scores
        positive_score, negative_score, polarity_score, subjectivity_score = calculate_sentiment_scores(tokens, positive_words, negative_words)

        average_sentence_length, percentage_complex_words, fog_index, average_words_per_sentence, complex_word_count, total_words, syllable_per_word, personal_pronoun_count, average_word_length = analyze_readability(text, punctuation)

        return {
            'POSITIVE SCORE': positive_score,
            'NEGATIVE SCORE': negative_score,
            'POLARITY SCORE': polarity_score,
            'SUBJECTIVITY SCORE': subjectivity_score,
            'AVG SENTENCE LENGTH': average_sentence_length,
            'PERCENTAGE OF COMPLEX WORDS': percentage_complex_words,
            'FOG INDEX': fog_index,
            'AVG NUMBER OF WORDS PER SENTENCE': average_words_per_sentence,
            'COMPLEX WORD COUNT': complex_word_count,
            'WORD COUNT': total_words,
            'SYLLABLE PER WORD': syllable_per_word,
            'PERSONAL PRONOUNS': personal_pronoun_count,
            'AVG WORD LENGTH': average_word_length
        }
    except Exception as e:
        print(f"Failed to analyze file: {file_path}")
        print(e)
        return None

import os
import pandas as pd

def store_results(output_file, url_id, analysis_results):
    try:
        # Load the existing data from the Excel file
        df = pd.read_excel(output_file, engine='openpyxl')

        # Find the row corresponding to the current file_id
        row_index = df[df['URL_ID'] == url_id].index

        if row_index.empty:
            print(f"URL_ID not found for file_id: {file_id}")
            return

        row_index = row_index[0]  # Get the actual index value from the Index object
        # Update the row with the analysis results
        for key, value in analysis_results.items():
            df.at[row_index, key] = value


        # Save the updated DataFrame back to the Excel file
        df.to_excel(output_file, index=False, engine='openpyxl')
    except Exception as e:
        print(f"Error updating the DataFrame for file_id: {file_id}")
        print(e)

# Assuming the analyze_file function and other necessary functions are defined

folder_path = 'articles'
output_file = 'Output Data Structure.xlsx'


for file_name in os.listdir(folder_path):
    if file_name.startswith('blackassign') and file_name.endswith('.txt'):
        file_path = os.path.join(folder_path, file_name)
        print(f"Analyzing file: {file_path}")
        results = analyze_file(file_path, stop_words, punctuation, positive_words, negative_words)
        if results:
            # Strip off the file extension if present
            file_id = os.path.splitext(file_name)[0]
            store_results(output_file, file_id, results)







