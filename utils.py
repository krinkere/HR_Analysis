import pandas as pd
import matplotlib.pyplot as plt


def get_data():
    data = pd.read_excel("data/FinalTableforAnalysis.xlsx", sheetname=None)
    print("Sheet names in provided excel file:")
    for key in data:
        print(key)
    return data


def display_histogram(histo_input, xlabel="", ylabel=""):
    fig = plt.figure(figsize=(10, 10))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.hist(histo_input)
    plt.show()


def clean_from_duplicates(file_name, extension):
    df_dup = pd.read_csv(file_name + "." + extension, encoding="ISO-8859-1")
    print("generated records")
    print(df_dup.shape)
    print("generated duplicates")
    duplicates = df_dup[df_dup.duplicated(keep=False)]
    print(duplicates)
    print(duplicates.shape)

    df_dup = pd.read_csv(file_name + "." + extension, encoding="ISO-8859-1")
    no_duplicates = df_dup.drop_duplicates()
    print("generated without duplicates")
    print(no_duplicates.shape)
    no_duplicates.to_csv(file_name + "_nodup." + extension, index=False, encoding='ISO-8859-1')
