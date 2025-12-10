
import pandas as pd
import os, time
from datetime import datetime

def save_results(df, prefix='sim'):
    os.makedirs('outputs', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    path = os.path.join('outputs', f"{prefix}_{timestamp}.csv")
    df.to_csv(path, index=False)
    return path

def example_cohort_csv():
    # return a small example cohort as pandas DataFrame
    import pandas as pd
    df = pd.DataFrame([{'name':'Patient 1','age':30,'sex':'male','weight':70,'immune':65},
                       {'name':'Patient 2','age':65,'sex':'female','weight':60,'immune':40}])
    return df
