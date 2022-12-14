import pandas as pd
from pymed import PubMed
from rake_nltk import Rake

if __name__ == '__main__':
    pubmed = PubMed(tool="PubMedSearcher", email="saprabhune@usf.edu")

## PUT YOUR SEARCH TERM HERE ##
search_term = "journal = European journal of medicinal chemistry"
results = pubmed.query(search_term, max_results=500)
articleList = []
articleInfo = []

for article in results:
# Print the type of object we've found (can be either PubMedBookArticle or PubMedArticle).
# We need to convert it to dictionary with available function
    articleDict = article.toDict()
    articleList.append(articleDict)

# Generate list of dict records which will hold all article details that could be fetch from PUBMED API
for article in articleList:
#Sometimes article['pubmed_id'] contains list separated with comma - take first pubmedId in that list - thats article pubmedId
    pubmedId = article['pubmed_id'].partition('\n')[0]
    # Append article info to dictionary 
    articleInfo.append({u'pubmed_id':pubmedId,
                       u'title':article['title'],
                       u'keywords':article['keywords'],
                       u'journal':article['journal'],
                       u'abstract':article['abstract'],
                       u'conclusions':article['conclusions'],
                       u'methods':article['methods'],
                       u'results': article['results'],
                       u'copyrights':article['copyrights'],
                       u'doi':article['doi'],
                       u'publication_date':article['publication_date'], 
                       u'authors':article['authors']})

# Generate Pandas DataFrame from list of dictionaries
articlesPD = pd.DataFrame.from_dict(articleInfo)
export_csv = articlesPD.to_csv (r'.\PubMed_Data.csv', index = None, header=True) 
#Print first 10 rows of dataframe
print(articlesPD.head(10))


abstractList = articlesPD['abstract'].dropna()
rake_nltk_var = Rake()
keyword_extracted =[]
extractedWordAndText = []
for text in abstractList:
    rake_nltk_var.extract_keywords_from_text(text)
    keyword_extracted = rake_nltk_var.get_ranked_phrases()
    extractedWordAndText.append({'Text':text,
                                                'Keywords':keyword_extracted})

    pdExtractedList = pd.DataFrame.from_dict(extractedWordAndText)
    pdExtractedList.to_csv (r'.\Extracted_List.csv', index = None, header=True) 
print(keyword_extracted[1])

