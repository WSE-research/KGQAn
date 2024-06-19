#!/bin/bash

data_dir="/app/data"
data_name="wiki-news-300d-1M"

echo "downloading $data_name"

if [ -d $data_dir ]; then
    if [ -f "$data_dir/$data_name.txt" ]; then
        echo "$data_dir/$data_name.txt already exists!"
        echo "skipping download"
        exec "$@"
    else
        echo "$data_dir exists but does not contain $data_name.txt!"
    fi
else
    echo "$data_dir does not exist!"
    mkdir -p $data_dir
fi

echo "downloading data - this can take a few minutes ..."
wget -q --load-cookies /tmp/cookies.txt "https://drive.usercontent.google.com/download?id=1UTPGv8QUgqSVQ2JeX9QVW0YhbGRxONLL&export=download&confirm=t" -O "$data_dir/$data_name.zip"
unzip "$data_dir/$data_name.zip" -d $data_dir
rm "$data_dir/$data_name.zip" # remove zip file
echo "download finished"

# run CMD from Dockerfile and start the service
exec "$@"
