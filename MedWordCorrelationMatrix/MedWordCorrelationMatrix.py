#pip install pymed
#pip install scispacy
#pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.4.0/en_core_sci_sm-0.4.0.tar.gz

import pandas as pd
from pymed import PubMed
import scispacy
import spacy
import spacy_legacy
#import en_core_sci_sm   #The model we are going to use
#nlp = spacy.load("en_core_sci_sm")
from spacy import displacy
from scispacy.abbreviation import AbbreviationDetector
from scispacy.umls_linking import UmlsEntityLinker
from scispacy.linking import EntityLinker
import os
import networkx as nx
import matplotlib.pyplot as plt
from neo4j import GraphDatabase
import nxneo4j as nxn

if __name__ == '__main__':
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = ""
    driver = GraphDatabase.driver(uri=uri,auth=(uri,password))

    pubmed = PubMed(tool="PubMedSearcher", email="saprabhune@usf.edu")

    if os.path.isfile('.\PubMed_JAMA_Data.csv'):
        articlesPD_JAMA = pd.read_csv('.\PubMed_JAMA_Data.csv').dropna(subset = ['abstract'])
    else:
        ## PUT YOUR SEARCH TERM HERE ##
        #search_term = "journal = European journal of medicinal chemistry"
        search_term = "Journal of the American Medical Association"
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
                               u'title':article.get('title'),
                               u'keywords':article.get('keywords'),
                               u'journal':article.get('journal'),
                               u'abstract':article.get('abstract'),
                               u'conclusions':article.get('conclusions'),
                               u'methods':article.get('methods'),
                               u'results': article.get('results'),
                               u'copyrights':article.get('copyrights'),
                               u'doi':article.get('doi'),
                               u'publication_date':article.get('publication_date'), 
                               u'authors':article.get('authors')})

        # Generate Pandas DataFrame from list of dictionaries
        articlesPD_JAMA = pd.DataFrame.from_dict(articleInfo)
        export_csv = articlesPD_JAMA.to_csv (r'.\PubMed_Data.csv', index = None, header=True) 
        #Print first 10 rows of dataframe
        print(articlesPD_JAMA.head(10))

    if os.path.isfile('.\PubMed_The New England journal of medicine _Data.csv'):
        articlesPD_NEJM = pd.read_csv('.\PubMed_The New England journal of medicine _Data.csv').dropna(subset = ['abstract'])
    else:
        search_term = "The New England journal of medicine"
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
                               u'title':article.get('title'),
                               u'keywords':article.get('keywords'),
                               u'journal':article.get('journal'),
                               u'abstract':article.get('abstract'),
                               u'conclusions':article.get('conclusions'),
                               u'methods':article.get('methods'),
                               u'results': article.get('results'),
                               u'copyrights':article.get('copyrights'),
                               u'doi':article.get('doi'),
                               u'publication_date':article.get('publication_date'), 
                               u'authors':article.get('authors')})

        # Generate Pandas DataFrame from list of dictionaries
        articlesPD_NEJM = pd.DataFrame.from_dict(articleInfo)
        export_csv = articlesPD_NEJM.to_csv (r'.\PubMed_The New England journal of medicine _Data.csv', index = None, header=True) 
        #Print first 10 rows of dataframe
        print(articlesPD_NEJM.head(10))

    #Working on JAMA Data here
    #Need to get these columns 'pubmed_id','abstract', 'keywords', 'doi', 'journal', 'publication_date' only in primary data file
    if os.path.isfile('.\PubMed_Data_JAMA_Selected.csv'):
        articlesPD_JAMA_Selected = pd.read_csv('.\PubMed_Data_JAMA_Selected.csv').dropna(subset = ['abstract'])
    else:
        articlesPD_JAMA_Selected = pd.DataFrame(articlesPD_JAMA, columns =['pubmed_id','abstract', 'keywords', 'doi', 'journal', 'publication_date'])
        export_csv = articlesPD_JAMA_Selected.to_csv (r'.\PubMed_Data_JAMA_Selected.csv', index = None, header=True) 

    #rake_nltk_var = Rake()
    #keyword_extracted =[]
    extractedWordAndCUI = []

    articlesPD_original = pd.DataFrame(articlesPD_JAMA_Selected, columns =['pubmed_id','abstract'])

    #Using sciSpacy
    nlp = spacy.load("en_core_sci_sm")

    # Add the abbreviation pipe to the spacy pipeline.
    nlp.add_pipe("abbreviation_detector")

    nlp.add_pipe("scispacy_linker", 
                     config={"resolve_abbreviations": True, "name": "umls"})    
    print("Pipeline: ", nlp.pipe_names)

    linker = nlp.get_pipe("scispacy_linker")

    if os.path.isfile('.\Extracted_Keywords_JAMA.csv'):
        pdExtractedList = pd.read_csv('.\Extracted_Keywords_JAMA.csv').dropna(subset = ['CUIs'])
    else:

        #Just trying out on a sample of 5 abstracts
        articlesPD = articlesPD_original.head(5) #Remove this later to run on the entire resultset of PubMed Abstracts

        #Creating the graph
        G = nx.Graph()

        config = {
                "node_label": "term",
                "relationship_type": "CORRELATED",
                "identifier_property": "term"
            }
        GN = nxn.Graph(driver, config)

        print(GN.number_of_nodes())

        for idx, row in articlesPD.iterrows():
            pubmedId = row.values[0]
            text = row.values[1]

            doc = nlp(text)     
            entity = doc.ents
            #Print the Abbreviation and it's definition
            print("Abbreviation", "\t", "Definition")
            for abrv in doc._.abbreviations:
                print(f"{abrv} \t ({abrv.start}, {abrv.end}) {abrv._.long_form}")
                if abrv._.long_form not in entity:
                    entity= entity+(abrv._.long_form,)
                                  
            print("Name: ", entity)
                
            # Each entity is linked to UMLS with a score
            # (currently just char-3gram matching).        
            for umls_ent in entity:
                if (key.startswith(str(umls_ent)) for key in linker.umls.alias_to_cuis.keys()):
                    extractedWordAndCUI.append({'Keyword':str(umls_ent).lower(), 
                                                        'CUIs': linker.umls.alias_to_cuis.get(str(umls_ent)),
                                                        'pubmed_id':pubmedId})

                    pdExtractedList = pd.DataFrame.from_dict(extractedWordAndCUI)

            pdExtractedList.dropna(subset=['CUIs'], inplace=True) 
            pdExtractedList['CUIs'] = pdExtractedList['CUIs'].astype(str)

            #NetworkX Graph
            for prim_idx, prim_item in pdExtractedList.iterrows():
                #Making a copy by dropping the current node
                pdExtractedList_secondary = pdExtractedList.drop(prim_idx, axis=0)                
                for sec_idx, sec_item in pdExtractedList_secondary.iterrows():
                    prim_node = str(prim_item.values[0]).lower()
                    sec_node = str(sec_item.values[0]).lower()
                    prim_cui = str(prim_item.values[1]).replace('{','').replace('}','').replace('\'','')
                    sec_cui = str(sec_item.values[1]).replace('{','').replace('}','').replace('\'','')
                    #Checking to see if the pair exists
                    if G.has_edge(prim_node, sec_node):
                        # we added this one before, just increase the weight by one
                        G[prim_node][sec_node]['weight'] += 1
                    else:
                        G.add_nodes_from([(prim_item.values[0], {"cui": prim_cui, "pubmed_id": prim_item.values[2]}),
                                      (sec_item.values[0], {"cui": sec_cui, "pubmed_id": sec_item.values[2]})])
                        # new edge. add with weight=1
                        G.add_edge(prim_node, sec_node, weight=1)

            #Neo4j Graph
            for prim_idx, prim_item in pdExtractedList.iterrows():
                #Making a copy by dropping the current node
                pdExtractedList_secondary = pdExtractedList.drop(prim_idx, axis=0) 
                for sec_idx, sec_item in pdExtractedList_secondary.iterrows():
                    prim_node = str(prim_item.values[0]).lower()
                    sec_node = str(sec_item.values[0]).lower()
                    prim_cui = str(prim_item.values[1]).replace('{','').replace('}','').replace('\'','')
                    sec_cui = str(sec_item.values[1]).replace('{','').replace('}','').replace('\'','')
                    prim_pubid = str(prim_item.values[2])
                    sec_pubid = str(sec_item.values[2])
                    #Checking to see if the pair exists
                    query =  " MERGE (u:TERM {name: \'" + prim_node + "\', cui: \'" + prim_cui + "\', pubmed_id: \'" + prim_pubid + "\'})" \
                                " MERGE (v:TERM {name: \'" + sec_node + "\', cui: \'" + sec_cui + "\', pubmed_id: \'" + sec_pubid + "\'})" \
                                " MERGE (u)-[c:CORRELATED]->(v)" \
                                " ON CREATE SET c.weight = 1" \
                                " ON MATCH SET c.weight = c.weight+1" \

                    with driver.session() as session:
                        result = session.run(query)
                   
        #Generating graph diagram for networkx graph
        print(G.number_of_nodes(), G.number_of_edges())
        fig = plt.figure(1, figsize=(200, 80), dpi=20)
        nx.draw(G, with_labels = True, font_weight='normal')
        plt.draw()
        plt.show()
        graph_metric = nx.pagerank(G, weight='weight')
        nx.set_node_attributes(G, graph_metric, 'pagerank')
        nx.write_gml(G, "sample_medcorr.graphml")

        print(GN.number_of_nodes())
        
        #Saving the list of pubmedid, keyword and cuis to csv
        pdExtractedList.to_csv (r'.\Extracted_Keywords_JAMA.csv', index = None, header=True) 