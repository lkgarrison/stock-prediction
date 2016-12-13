import nltk
import csv
from collections import defaultdict, Counter
from nltk.corpus import movie_reviews
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from bs4 import BeautifulSoup
from dateutil import parser as dtparser
from datetime import timedelta


def get_stock_dates(ticker):
    dates = set()
    with open('../data/historical/' + ticker.upper() + '.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for line in reader:
            isodate = dtparser.parse(line['Date']).isoformat()
            dates.add(isodate)
    return dates

stock_dates = get_stock_dates('IBM')

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
        return (article_tag, sentiment_strength)

    def classify_article_nltk(self, article, sid):
        sentiment_dict = Counter()
        article = article.split('\n\n')
        for line in article:
            line = line.replace('\n', '')
            ss = sid.polarity_scores(line)
            for tag in ss:
                sentiment_dict[tag] += ss[tag]
        for tag in sentiment_dict:
            sentiment_dict[tag] = sentiment_dict[tag] / float(len(article))
        return sentiment_dict


    def extract_news_sentiment(self, filename):
        DAY_FRIDAY = 4  # monday:0, ...,  sunday: 6
        with open('company-sentiment.csv', 'wb') as outfile:
            outfile.write('date,ticker,neg,pos\n')
            sid = SentimentIntensityAnalyzer()
            with open(filename) as infile:
                raw_text = infile.read()
            soup = BeautifulSoup(raw_text, 'lxml')
            docs = soup.findAll('doc')
            for doc in docs:
                datetime = doc.datestamp.get('datetime')
                dateobj = dtparser.parse(datetime)
                while dateobj.isoformat() not in stock_dates:
                    dateobj = dateobj - timedelta(days=1)
                
                datetime = dateobj.isoformat()
                ticker = doc.ticker.get('ticker')
                doc_soup = BeautifulSoup(doc.text, 'lxml')
                doc_text = doc_soup.get_text('text').strip()
                sentiment_dict = self.classify_article_nltk(doc_text, sid)
                neg = sentiment_dict['neg']
                pos = sentiment_dict['pos']
                csv_string = datetime + ',' + ticker + ',' + str(neg) + ',' + str(pos) + '\n'
                outfile.write(csv_string)


if __name__ == "__main__":
    naive_sent = NaiveSentiment()
    naive_sent.extract_news_sentiment('../data/gigaword-condensed.sgml')
