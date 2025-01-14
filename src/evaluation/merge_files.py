import pandas as pd
import os

file_dir = os.path.dirname(os.path.abspath(__file__))

csv_files = [
    "output/qald_response_time.csv",
    "output/lcquad_response_time.csv",
    "output/yago_response_time.csv",
    "output/dblp_response_time.csv",
    "output/mag_response_time.csv",
]

dataframes = []
for csv_file in csv_files:
    df = pd.read_csv(os.path.join(file_dir, csv_file))
    dataset_name = csv_file.split("/")[-1].split("_")[0]
    df.insert(0, "Dataset", dataset_name)
    dataframes.append(df)

merged_dataframe = pd.concat(dataframes)

output_file = "output/evaluation_response_time.csv"
merged_dataframe.to_csv(os.path.join(file_dir, output_file), index=False)
