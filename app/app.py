import streamlit as st
import pickle
import pandas as pd
import plotly.graph_objects as go
import numpy as np



def get_clean_data():
  data = pd.read_csv("data/data.csv")
  
  data = data.drop(['Unnamed: 32', 'id'], axis=1)
  
  data['diagnosis'] = data['diagnosis'].map({ 'M': 1, 'B': 0 })
  
  return data 



def add_sidebar():
  st.sidebar.header("Cell Nuclei Measurements")
  
  ## RECEIVING THE ACTUAL PREPROCESSED DATA
  data = get_clean_data()
  
  slider_labels = [
        ## "KEY"->"VALUE" -> LABEL IS THAT WILL BE DISPLAYED ON STREAMLIT: KEY IS THE ACTUAL COLUMN I
        ("Radius (mean)", "radius_mean"),
        ("Texture (mean)", "texture_mean"),
        ("Perimeter (mean)", "perimeter_mean"),
        ("Area (mean)", "area_mean"),
        ("Smoothness (mean)", "smoothness_mean"),
        ("Compactness (mean)", "compactness_mean"),
        ("Concavity (mean)", "concavity_mean"),
        ("Concave points (mean)", "concave points_mean"),
        ("Symmetry (mean)", "symmetry_mean"),
        ("Fractal dimension (mean)", "fractal_dimension_mean"),
        ("Radius (se)", "radius_se"),
        ("Texture (se)", "texture_se"),
        ("Perimeter (se)", "perimeter_se"),
        ("Area (se)", "area_se"),
        ("Smoothness (se)", "smoothness_se"),
        ("Compactness (se)", "compactness_se"),
        ("Concavity (se)", "concavity_se"),
        ("Concave points (se)", "concave points_se"),
        ("Symmetry (se)", "symmetry_se"),
        ("Fractal dimension (se)", "fractal_dimension_se"),
        ("Radius (worst)", "radius_worst"),
        ("Texture (worst)", "texture_worst"),
        ("Perimeter (worst)", "perimeter_worst"),
        ("Area (worst)", "area_worst"),
        ("Smoothness (worst)", "smoothness_worst"),
        ("Compactness (worst)", "compactness_worst"),
        ("Concavity (worst)", "concavity_worst"),
        ("Concave points (worst)", "concave points_worst"),
        ("Symmetry (worst)", "symmetry_worst"),
        ("Fractal dimension (worst)", "fractal_dimension_worst"),
    ]

  input_dict = {}

  for label, key in slider_labels:
    ## STORING THE KEYS(COLUMN NAMES) IN INPUT_DICT AND CREATING SLIDER:
    input_dict[key] = st.sidebar.slider(
       ## ACTUAL LABELS:
       label,
       min_value=float(0),
       ## DATA KE KEY MAI JO VALUE(ACTUAL COLUMN)PRESENT HAI USKA MAX VALUE
       max_value=float(data[key].max()),
       value=float(data[key].mean())
    )
    
  return input_dict



def get_scaled_values(input_dict):
  data = get_clean_data()
  
  ## INDEPENDENT FEATURES:
  X = data.drop(['diagnosis'], axis=1)
  ## EMPTY DICT TO STORE THE SCALED VALUE:
  scaled_dict = {}
  
  ## ITERATING THROUGH THE INPUT DICT(WHICH STORES THE VALUE OF EACH COLUMN)
  for key, value in input_dict.items():
    max_val = X[key].max()
    min_val = X[key].min()
    scaled_value = (value - min_val) / (max_val - min_val)
    scaled_dict[key] = scaled_value
  
  return scaled_dict



def get_radar_chart(input_data):
  
  ## the input_data which stores the value of input_dict(values of each 30 columns)
  ## scaling down the values of input data:
  ## get_scaled_values -> Takes input a input_dict and returns a scaled_dict
  input_data = get_scaled_values(input_data)
  
  ## all the 10 columns -> types(mean , se and worst)
  categories = ['Radius', 'Texture', 'Perimeter', 'Area', 
                'Smoothness', 'Compactness', 
                'Concavity', 'Concave Points',
                'Symmetry', 'Fractal Dimension']

  fig = go.Figure()

  fig.add_trace(go.Scatterpolar(
        r=[
          input_data['radius_mean'], input_data['texture_mean'], input_data['perimeter_mean'],
          input_data['area_mean'], input_data['smoothness_mean'], input_data['compactness_mean'],
          input_data['concavity_mean'], input_data['concave points_mean'], input_data['symmetry_mean'],
          input_data['fractal_dimension_mean']
        ],
        theta=categories,
        fill='toself',
        name='Mean Value'
  ))
  fig.add_trace(go.Scatterpolar(
        r=[
          input_data['radius_se'], input_data['texture_se'], input_data['perimeter_se'], input_data['area_se'],
          input_data['smoothness_se'], input_data['compactness_se'], input_data['concavity_se'],
          input_data['concave points_se'], input_data['symmetry_se'],input_data['fractal_dimension_se']
        ],
        theta=categories,
        fill='toself',
        name='Standard Error'
  ))
  fig.add_trace(go.Scatterpolar(
        r=[
          input_data['radius_worst'], input_data['texture_worst'], input_data['perimeter_worst'],
          input_data['area_worst'], input_data['smoothness_worst'], input_data['compactness_worst'],
          input_data['concavity_worst'], input_data['concave points_worst'], input_data['symmetry_worst'],
          input_data['fractal_dimension_worst']
        ],
        theta=categories,
        fill='toself',
        name='Worst Value'
  ))

  fig.update_layout(
    polar=dict(
      radialaxis=dict(
        visible=True,
        ## AS VALUUES ARE SCALED DOWN BTW 0 AND 1 , SO RANGE BETWEEN [0 AND 1]
        range=[0, 1]
      )),
    showlegend=True
  )

  return fig



def add_predictions(input_data):
    model = pickle.load(open('model/model.pkl','rb'))
    scaler = pickle.load(open('model/scaler.pkl','rb'))

    input_array = np.array(list(input_data.values())).reshape(1,-1)
   
    input_array_scaled = scaler.transform(input_array)

    prediction = model.predict(input_array_scaled)

    st.subheader("Cell cluster prediction")
    st.write("The cell cluster is:")
  
    if prediction[0] == 0:
        st.write("<span class='diagnosis benign'>Benign</span>", unsafe_allow_html=True)
    else:
        st.write("<span class='diagnosis malicious'>Malicious</span>", unsafe_allow_html=True)
    
  
    st.write("Probability of being benign: ", model.predict_proba(input_array_scaled)[0][0])
    st.write("Probability of being malicious: ", model.predict_proba(input_array_scaled)[0][1])
  
    st.write("This app can assist medical professionals in making a diagnosis, but should not be used as a substitute for a professional diagnosis.")


def main():

    st.set_page_config(
        page_title = 'Breat Cancer Predictor',
        page_icon=":female-doctor:",
        layout="wide",
        initial_sidebar_state="expanded"

    )

    with open("assets/style.css") as f:
        st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)
    ## container acts as a div:
    with st.container():
       st.title("Breast Cancer Predictior")
       st.write("Please connect this app to your cytology lab to help diagnose breast cancer form your tissue sample. This app predicts using a machine learning model whether a breast mass is benign or malignant based on the measurements it receives from your cytosis lab. You can also update the measurements by hand using the sliders in the sidebar.")

    ## CALLING THE ADD_SIDEBAR FUNCTION TO ADD THE SLIDER, IT RETURNS AN DICTIONARY OF INPUT DATA->(INPUT_DICT):
    ## GETTING THE INPUT_DATA AS 'input_data' from 'input_dict'
    input_data = add_sidebar()

    ## col1 is 4 times bigger than col2:
    col1,col2 = st.columns([4,1])

    with col1:
        radar_chart = get_radar_chart(input_data)
        st.plotly_chart(radar_chart)

    with col2:
        add_predictions(input_data)






















if __name__ == '__main__':
  main()