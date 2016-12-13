# read through gigaword.sgml and write out articles that are relevant financial articles
# if the article mentions a company, write it out as well as XML tags for datestamp and ticker information for easy access later

import string
import csv, re
import sys
from dateutil import parser as dtparser

from bs4 import BeautifulSoup

company_names = list()
company_tickers = list()

def populate_companies(filename):
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for line in reader:
            company = line['Name'] # full company name
            company_names.append(company)
            company_tickers.append(line['Symbol'])


def write_condensed_file(source, destination):
    with open(source) as f:
        num_lines = sum(1 for line in f)
    print("number of lines in file:", num_lines)

    end_of_article_re = re.compile('^\<\/DOC\>$', flags=re.IGNORECASE)
    article_lines = list() # will join to str later for efficiency

    company_patterns = dict()
    relevant_articles_count = 0

    outfile = open(destination, 'w')
    prev_percent = 0
    printable_chars = set(string.printable)
    num_unicode_errors = 0

    with open(source) as infile:
        for index, line in enumerate(infile):
            percent_processed = int(float(index) / num_lines * 100)
            if percent_processed > prev_percent:
                print("%s%% processed" % percent_processed)
                sys.stdout.write("\033[F") # Cursor up one line
                prev_percent = percent_processed

            article_lines.append(line)

            # article_lines now contains a complete article
            if re.search(end_of_article_re, line):

                # get one large string of the text of the articles
                # give this string to Beautiful Soup
                article_text = ''.join(article_lines)

                # remove any unicode characters
                article_text = filter(lambda x: x in printable_chars, article_text)
                prev_company_index = None

                soup = None

                try: 
                    soup = BeautifulSoup(article_text, 'lxml', from_encoding="utf-8")

                    for article in soup('doc'):
                        # extract the date stamp from the article
                        article_id = article['id']
                        article_date_list = list()
                        for char in article_id:
                            if char == '.':
                                break
                            elif char.isdigit():
                                article_date_list.append(char)

                        # add a new datestamp tag to the article
                        article_date_string = ''.join(article_date_list)
                        date_stamp_string = dtparser.parse(article_date_string).isoformat()
                        date_stamp_tag = soup.new_tag("datestamp", datetime=date_stamp_string)
                        article.append(date_stamp_tag)

                        headline_soup = BeautifulSoup(str(article.headline), 'lxml')
                        headline_text = headline_soup.get_text('headline').strip()

                        # check if the article's title mentions an S&P 500 company
                        for company_index, company_name in enumerate(company_names):
                            # regex here, if it is financial, write the date and set flag --> break
                            if company_name not in company_patterns:
                                pattern = re.compile("(\\b" + company_name + "\\b)", flags=re.IGNORECASE)
                                company_patterns[company_name] = pattern

                            pattern = company_patterns[company_name]

                            # if the article is about a company in the S&P 500
                            if re.search(pattern, headline_text):
                                prev_company_index = company_index
                                relevant_articles_count += 1
                                ticker_tag = soup.new_tag("ticker", ticker=company_tickers[company_index])
                                article.append(ticker_tag)
                                outfile.write(article.prettify() + '\n')
                                outfile.flush()
                                break

                except UnicodeEncodeError as e:
                    print(e)
                    print("Unicode exception occured")
                    print("Relevant company name/ticker:", company_names[prev_company_index], company_tickers[prev_company_index])
                    print("Article:")
                    print(article_text)
                    num_unicode_errors += 1
                    print('Number of unicode errors:', num_unicode_errors)


                # cleanup
                article_lines = list()


    outfile.close()
    print("%s relevant articles found" % relevant_articles_count)


if __name__ == "__main__":
    populate_companies("constituents.csv")
    # write_condensed_file("sample.sgml", "gigaword-condensed.sgml")
    # write_condensed_file("gigaword.sgml", "gigaword-condensed.sgml")
    write_condensed_file("gigaword.sgml", "gigaword-condensed.sgml")
    # write_condensed_file("unicode_sample.sgml", "unicode_sample_ouput.sgml")
