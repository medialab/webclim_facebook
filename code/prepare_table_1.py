import os

import pandas as pd 

from create_paper_tables_and_figures import import_data, save_figure


if __name__ == '__main__':
    
    df = import_data(folder="self_declared_repeat_offenders", file_name='alledged-repeat-offenders - Feuille 1.csv')
    
    df = df[df['date_in_screenshot'] & df['page_name_in_screenshot'] & df['is_clearly_reduced']]
    df = df[df['group-or-page']=='page']
    df = df.drop_duplicates(subset=['account-url'], keep='first')
    df = df[['repeat-offender-post-url']]

    df_path = os.path.join('.', 'data', 'self_declared_repeat_offenders', 'table_1.csv')
    df.to_csv(df_path, index=False)