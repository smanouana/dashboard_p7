
import pandas as pd
from time import sleep
import streamlit as st
import requests
import matplotlib.pyplot as plt
import plotly.graph_objects as go

st.set_option('deprecation.showPyplotGlobalUse', False)


def fetch_data(endpoint, payload):
    try:
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error fetching data from {endpoint}: {e}")
        return None


def display_client_data(client_id):
    data = fetch_data("https://creditapi-joqlneigka-uc.a.run.app/infos_client", {"client_id": client_id})
    
    if data:
        df = pd.DataFrame([data])  # Convert dictionary to dataframe with one row
        st.write('Tableau des données du client ID')
        st.table(df)


def display_credit_score(client_id):
    data = fetch_data("https://creditapi-joqlneigka-uc.a.run.app/score_credit", {"client_id": client_id})
    if data:
        score = data.get('SCORE ID CLIENT', 0)
        st.write("Infos sur le score")
        st.write("score :", score)
        st.write("SEUIL : 0.5")
        display_gauge_chart(score)


def display_gauge_chart(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 1]},
            'steps': [{'range': [0, 0.5], 'color': "red"},
                      {'range': [0.5, 1], 'color': "green"}]
        }
    ))
    st.plotly_chart(fig)
    if score > 0.5:
        st.success("crédit accordé")
    else:
        st.error("crédit non accordé")


def display_variable_analysis(client_id, variable):
    data = fetch_data("https://creditapi-joqlneigka-uc.a.run.app/analyze_variable", {
        "client_id": client_id, "variable": variable
    })
    if data:
        variable_data = data.get('variable_data', [])
        variable_client_id = data.get('variable_client_id', 0)
        st.write("valeur variable_client_id", variable_client_id)
        plt.hist(variable_data, bins=10)
        plt.plot([variable_client_id, variable_client_id], [0, max(plt.gca().get_ylim())], 'r--')
        st.pyplot()


def display_shap_plot(client_id):
    data = fetch_data("https://creditapi-joqlneigka-uc.a.run.app/shap_plot2", {"client_id": client_id})
    if data:
        content_html = data.get('key', '')
        st.components.v1.html(content_html)
        st.write("shapley POSITIVE contribue à augmenter la probabilté de prediction du risque de défaut de crédit")
        st.write("shapley NEGATIVE permet à réduire la probabilité de prédiction du risque défaut de crédit")


def main():
    st.title("PRET A DEPENSER")
    st.markdown("## Dashboard")
    with st.expander("Enter data"):
        client_id = st.number_input("Entrée Client ID", value=0.0)
        activity = ['EXT_SOURCE_3', 'EXT_SOURCE_2', 'AMT_GOODS_PRICE', 'EXT_SOURCE_1', 'AMT_CREDIT', 'AMT_ANNUITY']
        default_index = activity.index("EXT_SOURCE_3")
        variable = st.selectbox("Selection Activité", activity, index=default_index)

    if st.button("Analyser"):
        with st.spinner('Fetching data and performing analysis...'):
            display_client_data(client_id)
            sleep(5)
            display_credit_score(client_id)
            display_variable_analysis(client_id, variable)
            sleep(10)
            display_shap_plot(client_id)
            st.balloons()


if __name__ == '__main__':
    main()
