import json
import pandas as pd
import matplotlib

def load_json() :

    with open('test/logs/test.json', 'r') as f:
        data = json.load(f)
    
    df = pd.DataFrame(columns=['time', 'process_time', 'face_count', 'resolution'])
    for row in data :
        df = df.append({'time':row['time'], 'process_time': row['process_time'], 
                                'face_count' :row['face_count'], 'resolution':row['resolution']}, ignore_index=True)
    
    return df

if __name__ == "__main__" :

    df = load_json()
    print(df)
    df.to_csv('test.csv')
    