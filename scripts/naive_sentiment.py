import nltk
import csv
import sys, os
from collections import defaultdict, Counter
from nltk.corpus import movie_reviews
from bs4 import BeautifulSoup

class NaiveSentiment(object):
    def __init__(self):
        nltk.download('movie_reviews')
        self.model = defaultdict(Counter)
        self.docs_per_sentiment = Counter() # {'pos': 18271, 'neg': 15623}
        self.train_model()

    def train_model(self):
        documents = [(list(movie_reviews.words(fileid)), category) 
                for category in movie_reviews.categories()
                for fileid in movie_reviews.fileids(category)]
        for doc, tag in documents:
            self.docs_per_sentiment[tag] += 1
            for word in doc:
                self.model[word][tag] += 1

    def classify_article(self, article):
        sentiment_counts = Counter() # count of positive and negative words in article
        article = article.split()
        for word in article:
            if word in self.model: # only tag the word if we have seen it before
                word_sentiments = self.model[word]
                tag = max(word_sentiments.iterkeys(), key=(lambda key: word_sentiments[key]))
                sentiment_counts[tag] += 1
        article_tag = max(sentiment_counts.iterkeys(), key=(lambda key: sentiment_counts[key]))
        sentiment_strength = sentiment_counts[article_tag] / float(sum(sentiment_counts.itervalues()))
        print("This article was tagged as: " + article_tag + " with strength: " + str(sentiment_strength))
        return (article_tag, sentiment_strength)

    def extract_news_sentiment(self, filename):
        with open(filename) as infile:
            raw_text = infile.read()
        soup = BeautifulSoup(raw_text, 'lxml')
        docs = soup.findAll('doc')
        for doc in docs:
            print(soup.datestamp)
            break


if __name__ == "__main__":
    naive_sent = NaiveSentiment()
    naive_sent.extract_news_sentiment('../data/gigaword-condensed.sgml')
