import boto3
import search

#  Lambda-specific code for search engine
#  Convention is the handler is named lambda_handler and the file is named lambda_function.py

def lambda_handler(event, context):
    query = event['queryStringParameters']['query']
    items = search.search(query)
    return format_html_query_results(query, items)

# format_html_query_response -- format output from the fcall to search to pretty HTML.
#   Inputs are
#   * the original query string, unedited
#   * a sequence of pairs of the form (docname, int-relevance) in proper order to be rendered

def format_html_query_results(query, items):
    html = f"<html><body>{format_banner_html(query)} {format_item_html(items)}</body></html>"    
    return {'statusCode': 200, 'headers': {'Content-Type': 'text/html'},'body': html}

# Produce HTML with banner information, like the query string
def format_banner_html(query):
  return f"<b>Search Results for Query: {query}</b>"

# Produce HTML with formatted version of the items    
def format_item_html(items): 
  html = "<ul>"
  for title, relevance in items:
    html += f"<li>{title}: {relevance}</li>"
  html += "</ul>"
  return html
    