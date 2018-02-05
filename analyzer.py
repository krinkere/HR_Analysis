import matplotlib.pyplot as plt
import datetime
import csv
import time
import pandas as pd
pd.set_option('expand_frame_repr', False)


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

if __name__ == "__main__":
    input_data = get_data()

    """ Get the data off first sheet named: Table for Analysis - OCIO """
    df = input_data['Table for Analysis - OCIO']

    """ Sample data and column names"""
    print(df.head())
    print("Column headings:")
    print(df.columns)

    """ Display breakdown of case types """
    print(df['Case Type'].value_counts())
    """ Visual breakdown of case types """
    display_histogram(df['Case Type'].values, ylabel="count")

    """ Size of the input data """
    print(df.shape)
    print(df['Case Type'].count())

    """ Only interested in case type that is performance or performance (mgmt) """
    df_perf = df[df['Case Type'].isin(['Performance', 'Performance (Mgmt)'])]

    """ Size of the case type filtered data """
    print(df_perf.head())
    print(df_perf.shape)
    print(df_perf['Case Type'].count())

    """ Display breakdown of deficient element """
    print(df['Deficient Element'].value_counts())
    print(df_perf['Deficient Element'].value_counts())

    """ Break multiple deficient elements into its own (hot encode) """
    df_split_dock_mgmt = \
        df_perf['Deficient Element'].str.split('\s*•\s*', expand=True).stack().str.get_dummies().sum(level=0)
    df_dock_mgmt = pd.concat([df_perf, df_split_dock_mgmt], axis=1)

    """ Size of the case type filtered data """
    print(df_dock_mgmt.head(100))
    total = df_dock_mgmt['Docket Management'].sum()
    print(total)
    total = df_dock_mgmt['Production'].sum()
    print(total)
    total = df_dock_mgmt['Quality'].sum()
    print(total)

    df_perf_type_doc_mgmt = df_dock_mgmt[df_dock_mgmt['Quality'] == 1]

    """ Size of the case type filtered data """
    print(df_perf_type_doc_mgmt['Case Type'].count())

    """ 
    at this point we have case type that are either performance or performance mgmt) and deficient element being 
    Quality
    """

    """ convert dates to proper format """
    df_perf_type_doc_mgmt['Proposal Issued to Employee_DT'] = pd.to_datetime(
        df_perf_type_doc_mgmt['Proposal Issued to Employee']).apply(lambda x: x.date())
    df_perf_type_doc_mgmt['Date Resolved_DT'] = pd.to_datetime(
        df_perf_type_doc_mgmt['Date Resolved']).apply(lambda x: x.date())
    df_perf_type_doc_mgmt['Date Received_DT'] = pd.to_datetime(
        df_perf_type_doc_mgmt['Date Received']).apply(lambda x: x.date())

    """ how many null dates we have for Proposal Issued to Employee """
    print(df_perf_type_doc_mgmt['Proposal Issued to Employee'].isnull().sum())

    """ 
    end date for first case is 'Proposal Issued to Employee' unless it is null, in which case use 'Date Resolved'
    """
    df_perf_type_doc_mgmt["end_first_case"] = \
        df_perf_type_doc_mgmt['Proposal Issued to Employee_DT'].fillna(df_perf_type_doc_mgmt["Date Resolved_DT"])

    """ how many null dates we have for Date Received """
    print(df_perf_type_doc_mgmt['Date Received'].isnull().sum())

    """ sample it """
    print(df_perf_type_doc_mgmt.head())

    """ find multiple offenders (if it is only 1 occurrence, discard """
    df_perf_type_doc_mgmt_counts = df_perf_type_doc_mgmt.groupby(
        ['Employee Identifier'])['Quality'].count().reset_index(name='count')  # .sort_values(['count']

    """ sample it """
    print(df_perf_type_doc_mgmt_counts.head(10))
    # print(type(df_perf_type_doc_mgmt_counts))

    """ get a list of employees with more than 1 violation """
    df_offending_employee = df_perf_type_doc_mgmt_counts[df_perf_type_doc_mgmt_counts['count'] > 1]

    """ sample it """
    print(df_offending_employee.head())

    """ filter to get full details only on the above found employees """
    df_full_record_offending_employee = \
        df_perf_type_doc_mgmt[df_perf_type_doc_mgmt['Employee Identifier'].isin(
            df_offending_employee['Employee Identifier'])]

    """ sample it """
    print(df_full_record_offending_employee.head())

    def date_compare(df_in):
        for index, row in df_in.iterrows():
            print('Employee Identifier: ' + str(row['Employee Identifier']))
            end_date_first_case = row.end_first_case
            print('End date of first case: ' + str(end_date_first_case))
            margin = datetime.timedelta(days=154)

            for index2, row2 in df_in.iterrows():
                if end_date_first_case == row2.end_first_case:
                    continue
                start_date_second_case = row2['Date Received_DT']
                print('Start date of second case: ' + str(start_date_second_case))
                print('Within 154 calendar days? ' + str(
                    end_date_first_case <= start_date_second_case <= end_date_first_case + margin))
                if end_date_first_case <= start_date_second_case <= end_date_first_case + margin:
                    with open("output/results" + time_str + ".csv", "a", newline='') as r_file:
                        rlts = csv.writer(r_file)
                        rlts.writerow([str(row['Employee Identifier']), str(end_date_first_case),
                                       row['Final Decisions'], str(start_date_second_case), row2['Final Decisions']])
        return

    time_str = time.strftime("%Y%m%d-%H%M%S")
    with open("output/results" + time_str + ".csv", "a", newline='') as results_file:
        results = csv.writer(results_file)
        results.writerow(['Employee Identifier', 'End of first case', 'Final Decision of first case',
                          'Start of second case', 'Final Decision of second case'])

    """ find offending employees and their violations in a csv file """
    df_full_record_offending_employee.groupby('Employee Identifier').apply(date_compare)

