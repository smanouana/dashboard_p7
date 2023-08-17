
import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import shap
import plotly.graph_objects as go
st.set_option('deprecation.showPyplotGlobalUse', False)


def main():
    st.title("PRET A DEPENSER")
    st.markdown("## Dashboard")
    with st.expander("Enter data"):
        client_id = st.number_input("Entrée Client ID")
        activity = ['EXT_SOURCE_3','EXT_SOURCE_2','AMT_GOODS_PRICE','EXT_SOURCE_1','AMT_CREDIT','AMT_ANNUITY']
        variable = st.selectbox("Selection Activité", activity)
   
    if st.button("Analyser"):
        with st.spinner('Fetching data and performing analysis...'):
            # Client information
            response = requests.post("http://localhost:9000/infos_client", json={"client_id":client_id})
            data = response.json()
            st.write('Tableau des données du client ID')
            st.table(data)
           
            # Credit score information
            response = requests.post("http://localhost:9000/score_credit", json={"client_id":client_id})    
            data = response.json()    
            st.write("Infos sur le score")
            score = data['SCORE ID CLIENT']
            st.write("score :", score)  
            seuil = 0.5
            st.write("SEUIL : 0.5")
           
            # Gauge chart for credit score
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                gauge = {
                    'axis': {'range': [0, 1]},
                    'steps' : [{'range': [0, 0.5], 'color': "red"},
                               {'range': [0.5, 1], 'color': "green"}]}))

            st.plotly_chart(fig)

            if score > seuil:
                st.success("crédit accordé")
            else:
                st.error("crédit non accordé")
           
            # Graph
            response = requests.post("http://localhost:9000/analyze_variable", json={"client_id":client_id,"variable":variable})    
            data = response.json()
            variable_data = data['variable_data']
            variable_client_id = data['variable_client_id']
            st.write("valeur variable_client_id", variable_client_id)
            valeurs = variable_data
            variable = variable_client_id
            plt.hist(valeurs, bins=10)
            plt.plot([variable, variable], [0, max(plt.gca().get_ylim())], 'r--')
            st.pyplot()

            # Shap plot
            response = requests.post('http://localhost:9000/shap_plot2', json={"client_id":client_id})
            data = response.json()
            content_html = data['key']
            st.components.v1.html(content_html)
            st.write("shapley POSITIVE contribue à augmenter la probabilté de prediction du risque de défaut de crédit")
            st.write("shapley NEGATIVE permet à réduire la probabilité de prédiction du risque défaut de crédit")
        st.balloons()

if __name__ == '__main__':
    main()