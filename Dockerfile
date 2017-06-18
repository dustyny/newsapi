FROM python:3.5.2

MAINTAINER Dustin Williams

# Hug applications run on port 8000 as default
# so allow hosts to bind to that port
EXPOSE 8000

RUN apt-get update -y && apt-get upgrade -y && \
    apt-get -y install apt-utils libxml2-dev libxslt-dev python-dev \
    libjpeg-dev zlib1g-dev libpng12-dev 


# https://github.com/python-pillow/Pillow/issues/1763
ENV LIBRARY_PATH=/lib:/usr/lib


# install AWS cli tools
RUN pip install awscli
RUN pip install boto3
RUN pip install newspaper3k


# Download corpora
RUN python -m nltk.downloader brown punkt maxent_treebank_pos_tagger movie_reviews wordnet stopwords averaged_perceptron_tagger


# Hug simple high performance python APIs - www.hug.rest
RUN pip install hug

RUN mkdir /root/.aws/
ADD config /root/.aws/config
ADD credentials /root/.aws/credentials

# Add in the startup script & run it as the entrypoint
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# moved to the end, so app can be updated without completely rebuilding the docker image
RUN mkdir /api_app
ADD /src/app.py /api_app

#/usr/local/lib/python3.5/runpy.py:125: RuntimeWarning: 'nltk.downloader' found in sys.modules #after import of package 'nltk', but prior to execution of 'nltk.downloader'; this may result in #unpredictable behaviour
#  warn(RuntimeWarning(msg))

