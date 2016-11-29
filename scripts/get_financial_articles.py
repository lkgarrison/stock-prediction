import csv, re

company_names = list()
tickers = list()

def populate_companies(filename):
	with open(filename) as csvfile:
		reader = csv.DictReader(csvfile)
		for line in reader:
			tickers.append(line['Symbol']) # ticker
			company = line['Name'] # full company name
			company_names.append(company)

def write_condensed_file(source, destination):
    outfile = open(destination, "wb")
    with open(source) as infile:
        prev_line = ""
        currently_writing_article = False
        for line in infile:
            is_date = re.search("(.+?), [A-Z][a-z]* ?\. ?[1-3]*[0-9]* \( [A-Z]* \)", line)
            if is_date: # if it is a formatted date, check the title against company names and tickers
                title = prev_line
                currently_writing_article = False
                found_financial = False
                for company_name in company_names:
                    # regex here, if it is financial, write title and date and set flag --> break
                    pattern = re.compile("\\b" + company_name + "\\b", flags=re.IGNORECASE)
                    if re.search(pattern, title):
                        outfile.write(line)
                        currently_writing_article = True
                        found_financial = True
                        break

                if found_financial:
                    continue
                for ticker in tickers:
                    # regex here, if it is financial, write title and date and set flag --> break
                    pattern = re.compile("(\b" + ticker + "\b)", flags=re.IGNORECASE)
                    if re.search(pattern, title):
                        outfile.write(line)
                        currently_writing_article = True
                        break
                    
            else:
                if currently_writing_article:
                    # write this line
                    outfile.write(prev_line)
                
                prev_line = line

        # print the last line if the last article was being writen
        if currently_writing_article:
            outfile.write(prev_line)


if __name__ == "__main__":
    populate_companies("constituents.csv")
    write_condensed_file("sample.txt", "gigaword-condensed.eng.tok")

