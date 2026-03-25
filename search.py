import boto3
import termify

###############################################
#  Entry point is a function search(line) where line is the 
#    input query.  Output is a sequence of the form (docname, relevance) of 
#    length at most 5, and sorted in descending order of relevance


#  Step 1 -- Make connections to the two dynamodb tables
tfidf_table = boto3.resource('dynamodb').Table('tfidf')
docid_table = boto3.resource('dynamodb').Table('doctitle')

###################################################
#  These three functions do the dynamodb lookups.  
#  There is code missing for all three.

# get_docids_for_terms
# Input is a sequence of terms.  Output is a set of docids -- the set of 
#  all docids that contain one or more of the terms

def get_docids_for_terms(terms):
    docids = set()
    for term in terms:
        #  Make dynamodb call to get all docids for that term, and add them to the set
        query_param = {
            'KeyConditionExpression': 'term = :term',
            'ExpressionAttributeValues': {
                ':term': term
            }
        }
        response = tfidf_table.query(**query_param)
        items = response.get('Items', [])
        for item in items:
            docids.add(item['docid'])
    return docids
 
# get_tfidf
#  Input is a term and docid, output is the stored TF-IDF value for
#  that pair, or 0.0 if there is no stored value

def get_tfidf(term, docid):
    tfidf = tfidf_table.get_item(Key={'term': term, 'docid': docid})
    if 'Item' in tfidf:
        return float(tfidf['Item']['tfidf_score'])
    else:
        return 0.0

# get_doc_title
#   Input is a docid, output is the stored name (title) for the document as stored in Dynamodb, or None if
#     there is no such entry

def get_doc_title(docid):
    doctitle = docid_table.get_item(Key={'docid': docid})
    if 'Item' in doctitle:
        return doctitle['Item']['title']
    else:
        return None

##########################################################

def search(line):
    terms = termify.termify(line)
    docids = get_docids_for_terms(terms)
    return sort_and_limit([(docid, compute_doc_relevance(docid, terms)) for docid in docids])

##  Implements the formula for relevance specified in the assignment -- output is a float.
##    Should return 0.0 if the terms list is empty or none of the terms appear in the document   

def compute_doc_relevance(docid, terms):
  rel_score = 0.0
  if len(terms) > 0:
    for term in terms:
      rel_score += get_tfidf(term, docid)
  return rel_score
   
## Input pairs are (docid, tfidf)
##    Sort in descending order of tfidf, choose the top five, 
##    retrieve the doc title, and truncate tfidf to an integer
##    Output is a list of at most 5 pairs of the form (docname, int-tfidf)
   
def sort_and_limit(pairs):
  final_list = [] 
  for docid, tfidf in sorted(pairs, key=lambda x: x[1], reverse=True)[:5]:
    title = get_doc_title(docid)
    if title is not None:
      final_list.append((title, int(tfidf)))
  return final_list

  