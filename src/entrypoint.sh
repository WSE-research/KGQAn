#!/bin/bash

data_dir="/app/kgqan/model"
data_name="output_pred21_8_30"

echo "downloading $data_name"

if [ -d $data_dir ]; then
    if [ -z "$(ls -A $data_dir)" ]; then
        echo "$data_dir exists but is empty!"
    else
        echo "$data_dir is not empty!"
        echo "skipping download"
        exec "$@"
    fi
else
    echo "$data_dir does not exist!"
    mkdir -p $data_dir
fi

echo "downloading data - this can take a few minutes ..."
wget -q --load-cookies /tmp/cookies.txt "https://drive.usercontent.google.com/download?id=1QbT5FDOJtdVd7AqZ-ekwUh2_pn6nNpb3&export=download&confirm=t" -O "$data_dir/$data_name.zip"
unzip "$data_dir/$data_name.zip" -d $data_dir
mv $data_dir/$data_name/* $data_dir
rm "$data_dir/$data_name.zip" # remove zip file
rm -r $data_dir/$data_name # remove empty dir
echo "download finished"

# run CMD from Dockerfile and start the service
exec "$@"
