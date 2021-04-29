import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import io
import base64

# con = sqlite3.connect("wildfire_data.sqlite")
# cur = con.cursor()

# df_count = pd.read_sql_query('SELECT STATE, FIRE_YEAR, STAT_CAUSE_DESCR, FIRE_SIZE_CLASS from Fires', con)
df_count = pd.read_pickle("wildfire_df.p")
df_freq=pd.read_csv('./state-freq-data.csv', delimiter=",")
fire_levels=['A','B','C','D','E','F','G']

all_states=df_freq.state.unique()

start_year = 1992
end_year  = 2015
years  = list(range(start_year, end_year+1))

'''
{"label": "A = 0 to 0.25 Acres", "value": "A"},
{"label": "B = 0.26 to 9.9 Acres", "value": "B"},
{"label": "C = 10.0 to 99.9 Acres", "value": "C"},
{"label": "D = 100 to 299 Acres", "value": "D"},
{"label": "E = 300 to 999 Acres", "value": "E"},
{"label": "F = 1000 to 4999 Acres", "value": "F"},
{"label": "G = 5000+ Acres", "value": "G"},
'''

def get_State(state):
    x=df_count[df_count["STATE"] == state]
    y=df_freq[df_freq["state"] == state]
    return x,y

def get_Year(year,x_state,y_state):
    dff_x=x_state[x_state["FIRE_YEAR"] == year]
    dff_y=y_state[y_state['year']==year]

    return dff_x,dff_y



def Data_Preprocess():
    # the input array should be corrsponding to the size of the wildfire
    data_x=[]
    data_y=[]
    empty_input=np.array([0,0,0,0,0,0,0])
    for state in all_states:
        #loop through every state in the dataframe
        x_state,y_state=get_State(state)
        #print(x_state)
        #print(y_state)
        for year in years:
            #print(year)
            x_year,y_year=get_Year(year,x_state,y_state)
            #print(x_year,y_year)
            #print(x_year,y_year)
            if x_year.empty:  #the frame is empty
                data_x.append(empty_input)
                data_y.append([0])


            else:
                tmp_x=x_year.groupby(['FIRE_SIZE_CLASS']).size()
                tmp_y=y_year['wildfire'].iloc[0]
                tmp_df=pd.DataFrame({'count':[0,0,0,0,0,0,0]},index=fire_levels)
                
                for level in tmp_x.index.values:
                    tmp_df.loc[level,['count']]=tmp_x[level]

                #print(tmp_df,tmp_x)
                data_x.append(tmp_df['count'].to_list())
                data_y.append([tmp_y])

    x = np.array(data_x)
    y = np.array(data_y)
    return x, y


def machine_learning():
    x,y=Data_Preprocess()
    X_train, X_test, y_train, y_test = train_test_split(x,y,test_size=0.2)
    model = LogisticRegression(solver='liblinear', random_state=0)
    model.fit(X_train, y_train)
    # print(model.coef_)
    # print(model.score(X_test, y_test))
    # print(confusion_matrix(y_test, model.predict(X_test)))
    cm = confusion_matrix(y_test, model.predict(X_test))
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(cm)
    ax.grid(False)
    ax.xaxis.set(ticks=(0, 1), ticklabels=('Predicted 0s', 'Predicted 1s'))
    ax.yaxis.set(ticks=(0, 1), ticklabels=('Actual 0s', 'Actual 1s'))
    ax.set_ylim(1.5, -0.5)
    for i in range(2):
        for j in range(2):
            ax.text(j, i, cm[i, j], ha='center', va='center', color='red')
    buf = io.BytesIO()
    plt.savefig(buf, format = "png")
    plt.close()
    data = base64.b64encode(buf.getbuffer()).decode("utf8")
    return "data:image/png;base64,{}".format(data)