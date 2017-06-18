#!/usr/bin/env python
import datetime
start_time = datetime.datetime.now()


from newspaper import Article
from boto3 import client
import json
import hug

# s3 bucket connection
s3 = client('s3')


#HAVE TO FIGURE OUT HOW TO SET THE BROWSER USER AGENT!! MIGHT BE IN OLD PROJECT 


@hug.get('/', examples="bucket=tsarticle&folder=newspaper_drop&filename=20171231-sugarcandy-com-23&url=http://www.sugarcandy.com/baby-bites-dingo.html")
def process_article(bucket, folder, filename, url):
	article = get_article(url)
	article_size = len(article.html)
	article_html_file = article.html
	html_save_response = save_html_2_bucket(bucket, folder, filename, article_html_file)
	end_time = datetime.datetime.now()
	start_stop_delta = end_time - start_time
	return ({
		"filename": filename,
		"authors": article.authors,
		"publish_date": article.publish_date.strftime("%s") if article.publish_date else None,
		"title": article.title,
		"text": article.text,
		"summary": article.summary,
		"keywords": article.keywords,
		"images:": list(article.images),
		"movies": article.movies,
		"topimage": article.top_image},
		{'process_article_response': 200},
		{'Content-Type': 'application/json'},
		{'htmlSaveResponse': html_save_response},
		{'article_size': article_size, 
		'start_processing': start_time.isoformat(),
		'end_processing': end_time.isoformat(), 
		'total_processing_time': str(start_stop_delta)})


def get_article(url):
	article = Article(url, keep_article_html=True, request_timeout=20)
	article.download()
	# uncomment this if 200 is desired in case of bad url
	# article.set_html(article.html if article.html else '<html></html>')
	article.parse()
	article.nlp()
	assert isinstance(article, object)
	return article


def save_html_2_bucket(bucket, folder, filename, article_html_file):
	if len(article_html_file) > 0:
		html_file_name = filename + ".html"
		html_deposit = s3.put_object(Bucket=bucket, Body=article_html_file, Key=folder + "/" + html_file_name)
		return html_deposit


@hug.get('/health')
def health_check():
        return "status: up"


@hug.get('/test')
def qa_test():
	url = 'https://www.engadget.com/2017/06/02/grado-labs-hand-built-headphones/'
	filename = "20170602-engadget-com-122"
	bucket = 'tsarticlehtml'
	folder = 'newspaper_drop'
	run_lambda = process_article(bucket, folder, filename, url)
	return run_lambda