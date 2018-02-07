import more_itertools as mit
import numpy as np
import pandas as pd
pd.set_option('expand_frame_repr', False)


def get_data():
    data = pd.read_excel("data/Masked_Employee_Ratings_and_Profile.xlsx", sheetname=None)
    # print("Sheet names in provided excel file:")
    # for key in data:
    #     print(key)
    return data

if __name__ == "__main__":
    input_data = get_data()
    df = input_data['Masked_Employee_Ratings_and_Pro']

    # print(df.head())
    # print(df['Performance Evaluation Rating Desc'].value_counts())

    """ Break multiple deficient elements into its own (hot encode) """
    one_hot = pd.get_dummies(df['Performance Evaluation Rating Desc'])
    df_hot_encoded = df.join(one_hot)
    # print(df_hot_encoded.head())
    # print(df_hot_encoded.shape)

    s = df_hot_encoded['Performance Evaluation Rating Desc'].groupby(df_hot_encoded['Employee Identifier']).value_counts()
    print(s)

    df_minus_outstanding = df_hot_encoded[df_hot_encoded['OUTSTANDING'] == 0]
    print(df_minus_outstanding.shape)
    df_minus_outstanding_commendable = df_minus_outstanding[df_minus_outstanding['COMMENDABLE'] == 0]
    print(df_minus_outstanding_commendable.shape)
    df_minus_outstanding_commendable_fully = \
        df_minus_outstanding_commendable[df_minus_outstanding_commendable['FULLY SUCCESSFUL'] == 0]
    print(df_minus_outstanding_commendable_fully.shape)

    s = df_minus_outstanding_commendable_fully['Performance Evaluation Rating Desc']\
        .groupby(df_minus_outstanding_commendable_fully['Employee Identifier']).value_counts()
    print(s)

    df_minus_outstanding_commendable_fully['UNACCEPTABLE'] = \
        np.where(df_minus_outstanding_commendable_fully['MARGINAL'] == 1,
                 df_minus_outstanding_commendable_fully['MARGINAL'],
                 df_minus_outstanding_commendable_fully['UNSATISFACTORY'])

    print(df_minus_outstanding_commendable_fully)

    def get_consec(df_in):
        # print(df_in)
        years = df_in['Fiscal Year']

        cons_years = [list(group) for group in mit.consecutive_groups(years)]
        # print(cons_years)

        return str(cons_years)
        # for index, row in df_in.iterrows():
        #     print('Employee Identifier: ' + str(row['Employee Identifier']))
        #     print('Fiscal Year: ' + str(row['Fiscal Year']))


    print("total records")
    print(df_minus_outstanding_commendable_fully.shape)

    df_marginals_only = df_minus_outstanding_commendable_fully[df_minus_outstanding_commendable_fully['MARGINAL'] == 1]
    print("Number of marginal records pre")
    print(df_marginals_only.shape)

    df_marginal_years = df_minus_outstanding_commendable_fully[
        df_minus_outstanding_commendable_fully['MARGINAL'] == 1].groupby('Employee Identifier').apply(get_consec)
    df_marginal_years = df_marginal_years.reset_index(name='MARGINAL_YEARS')
    # print("Number of marginal records")
    # print(df_marginal_years.shape)
    df_final_results = pd.merge(df_minus_outstanding_commendable_fully, df_marginal_years, on='Employee Identifier',
                                how='outer')
    print(df_final_results.shape)

    df_unsatisfactory_years = df_minus_outstanding_commendable_fully[
        df_minus_outstanding_commendable_fully['UNSATISFACTORY'] == 1].groupby('Employee Identifier').apply(get_consec)
    df_unsatisfactory_years = df_unsatisfactory_years.reset_index(name='UNSATISFACTORY_YEARS')
    # print("Number of unsatisfactory records")
    # print(df_unsatisfactory_years.shape)
    df_final_results = pd.merge(df_final_results, df_unsatisfactory_years,
                                on='Employee Identifier', how='outer')
    print(df_final_results.shape)

    # print(df_minus_outstanding_commendable.head())
    df_unacceptable_years = df_minus_outstanding_commendable_fully[
        df_minus_outstanding_commendable_fully['UNACCEPTABLE'] == 1].groupby('Employee Identifier').apply(get_consec)
    df_unacceptable_years = df_unacceptable_years.reset_index(name='UNACCEPTABLE_YEARS')
    # print("Number of unacceptable records")
    # print(df_unacceptable_years.shape)
    df_final_results = pd.merge(df_final_results, df_unacceptable_years,
                                on='Employee Identifier', how='outer')
    print(df_final_results.shape)

    import time
    time_str = time.strftime("%Y%m%d-%H%M%S")
    df_final_results.to_csv("output/results-" + time_str + ".csv", index=False, encoding='ISO-8859-1')

    df_final_results['MARGINAL_YEARS'].fillna(value='', inplace=True)
    df_final_results['UNSATISFACTORY_YEARS'].fillna(value='', inplace=True)
    df_final_results['UNACCEPTABLE_YEARS'].fillna(value='', inplace=True)

    df_out = df_final_results.groupby(['Employee Identifier', 'MARGINAL_YEARS', 'UNSATISFACTORY_YEARS', 'UNACCEPTABLE_YEARS'], as_index=False).agg(
        {'MARGINAL': sum, 'UNSATISFACTORY': sum})
    print(df_out)
    df_out.to_csv("output/results-" + time_str + "2.csv", index=False, encoding='ISO-8859-1')



    # result = pd.crosstab(df_final_results['Employee Identifier'], [df_final_results['year'], df_final_results['type']], dropna=False)
    # result.columns = ['type_{}_{}'.format(typ, year) for year, typ in result.columns]
