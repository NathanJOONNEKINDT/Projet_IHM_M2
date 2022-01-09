# Ce dashboard a été fait dans le cadre d'un projet IHM du Master 2 Data Science pour la Santé de l'ILIS de Lille
# Il est destiné au professeur Djamel Zitouni qui l'a demandé pour la première semaine de 2022
# Ce projet a commencé comme étant une application de dash mais le déploiement posait des problèmes
# En effet, ce projet ne devait pas demander de téléchargements ou installations supplémentaires
# Heroku a été envisagé pour héberger le dashboard mais la découverte de streamlit a changé les choses
# L'utilisation de ce qui est différent de ce qui nous a été enseigné dans le Master semblait intéressant
# Je suis relativement satisfait du produit final que je trouve meilleur que ce que fait dash

# Ce projet utilise une enquête sur les bénéficiaires de minima sociaux (BMS) de 2018 de la DREES
# Le fichier excel correspondant est disponible sur l'entrepôt de données Datalib d'Antoine Lamer

# Il contient des éléments de statistiques, des graphiques et de l'interactivité
# Il permet aussi d'extraire les graphiques et les pages de l'excel en csv

# Dashboard
import streamlit as st

# Dataframes
import pandas as pd

# Générations de rapports sur les données, à peu près équivalent au summary de R mais en plus poussé
import pandas_profiling
from streamlit_pandas_profiling import st_profile_report

# Visu
import altair as alt

# Création d'une liste pour les pages de l'excel
liste = [
    "Lisezmoi",
    "Caractéristiques_BMS",
    "État_santé_declaré",
    "Maladies_chroniques",
    "Limitations_d'activité",
    "Indice_bien_être"
    ]

# Import de données
# On utilise un cache pour accélérer le temps de traitement de l'utilisateur
@st.cache
# On utilise un argument pour cibler la page de l'excel
def load_sante(n):
    # Des problèmes ont été rencontrés avec l'extraction directe depuis le gitlab donc le fichier a été placé dans un github
    data = pd.read_excel(
        'https://github.com/NathanJOONNEKINDT/Projet_IHM_M2/blob/main/etat_sante_beneficiaires_minima_sociaux.xlsx?raw=true',
        sheet_name = liste[n]
        )
    return data

# Création d'une fonction d'affichage de tableaux avec le bon format et en HTML
# On retire le numéro de ligne, on dit que les décimales sont des virgules
# On veut deux chiffres après la virgule
# On convertit la table en HTML pour un meilleur affichage et on autorise son affichage
def affiche_table(tableau):
    st.write(tableau.style.hide_index().format(decimal = ',', precision = 2).to_html(),
             unsafe_allow_html = True)

# On crée une fonction de conversion de table pour permettre le téléchargement
def converter(dataframe):
    return dataframe.to_csv().encode('utf-8')

# Titre dans le menu de côté pour les df bruts
st.sidebar.header("Renseignements :")
# Case à cocher pour afficher la première page de l'excel
# On y remplace les 'nan' par un string vide
if st.sidebar.checkbox('Afficher la table "lisezmoi"'):
    affiche_table(load_sante(0).fillna(''))

# Titre
st.sidebar.header("Options du graphique")

# Nommer le fichier qui sera téléchargé
dl_input = st.sidebar.text_input("Nom du prochain fichier téléchargé (UTF-8):",
                                 'Nom temporaire')

# Choix du DF en donnant une manière d'extraire l'index
# Nous n'utilisons pas le 0 pour ne pas charger une page posant problème
choix_df = st.sidebar.selectbox("Tableau Etudié", 
                                range(1,6), 
                                format_func=lambda x: liste[x])

# J'aurais probablement pu faire de la section du dessous une fonction aussi maintenant que je regarde mais ça fonctionne bien sans quand même
# Premiers filtres dans le menu de côté
# On commence avec la quatrième colonne qui permet de filtrer le mieux
# On vérifie qu'un choix de dataframe a bel et bien été fait (normalement fait par défaut)
if choix_df:
    # On récupère le choix et on l'insère en tant que variable dans notre fonction de chargement de feuille excel
    df = load_sante(choix_df)
    # On crée une checkbox pour permettre de regarder notre table
    if st.sidebar.checkbox('Aperçu table'):
        # On utilise notre fonction d'affichage
        affiche_table(df)
    # Checkbox encore une fois mais cette fois-ci pour générer un profile report de pandas
    if st.sidebar.checkbox('Rapport sur la table'):
        # On utilise la variante streamlit de ce rapport pour permettre un affichage acceptable
        # /!\ Peut être long
        st_profile_report(df.profile_report())
        
        # Bouton de téléchargement de la page de l'excel non filtrée
        st.sidebar.download_button('Télécharger la table revenus', 
                                   # Utilise la fonction de conversion en csv
                                   data = converter(df),
                                   # Ajoute .csv au nom entré dans le text input
                                   file_name = str(dl_input + '.csv'),
                                   mime = 'text/csv')
        
    # On crée une boîte de sélection du type de minima social qu'on veut étudier
    # Pour ça, on récupère tous les revenus uniques dans la quatrième colonne du dataframe et on les donne en option
    revenus = st.sidebar.multiselect("Revenu étudié", 
                                     df.iloc[:,3].unique())
    
    # On filtre le tableau avec les choix du dessus et on assigne à df_rev
    df_rev = df[df.iloc[:,3].isin(revenus)]
    
    # Si checkbox checkée, changer le format du tableau et l'écrire comme du HTML
    if st.sidebar.checkbox('Aperçu table revenus'):
        affiche_table(df_rev)
    if st.sidebar.checkbox('Rapport sur la table revenus'):
        st_profile_report(df_rev.profile_report())
    
    st.sidebar.download_button('Télécharger la table revenus', 
                               data = converter(df_rev),
                               file_name = str(dl_input + '.csv'),
                               mime = 'text/csv')

# Seconde couche
# On vérifie qu'un type de revenus a été choisi
if 'revenus' in globals():
    if revenus:
        # On filtre la première colonne
        categories = st.sidebar.multiselect('Catégories étudiées',
                                            df_rev.iloc[:,0].unique())
        df_cat = df_rev[df_rev.iloc[:,0].isin(categories)]
        # Afficher la table
        if st.sidebar.checkbox('Aperçu table catégories'):
            affiche_table(df_cat)
        # Afficher le rapport
        if st.sidebar.checkbox('Rapport sur la table catégorie'):
            st_profile_report(df_cat.profile_report())
        
        # Télécharger
        st.sidebar.download_button('Télécharger la table categorie', 
                                   data = converter(df_cat),
                                   file_name = str(dl_input + '.csv'),
                                   mime = 'text/csv')
    
# Troisième couche
if 'categories' in globals():
    if categories:
        libelle = st.sidebar.multiselect('Libellés étudiés', 
                                         df_cat.iloc[:,1].unique())
        df_lib = df_cat[df_cat.iloc[:,1].isin(libelle)]
        if st.sidebar.checkbox('Aperçu table libellé'):
            affiche_table(df_lib)
        if st.sidebar.checkbox('Rapport sur la table libellé'):
            st_profile_report(df_lib.profile_report())
            
        st.sidebar.download_button('Télécharger la table libelle', 
                                   data = converter(df_lib),
                                   file_name = str(dl_input + '.csv'),
                                   mime = 'text/csv')
                
# Dernière couche
if 'libelle' in globals():
    if libelle:
        sexe = st.sidebar.multiselect('Sexe étudié', 
                                       df_cat.iloc[:,2].unique())
        df_sex = df_lib[df_lib.iloc[:,2].isin(sexe)]
        if st.sidebar.checkbox('Aperçu table sexe'):
            affiche_table(df_sex)
        if st.sidebar.checkbox('Rapport sur la table sexe'):
            st_profile_report(df_sex.profile_report())
            
        st.sidebar.download_button('Télécharger la table sexe', 
                                   data = converter(df_sex),
                                   file_name = str(dl_input + '.csv'),
                                   mime = 'text/csv')

# Peut clairement être améliorée si j'y reviens dans le futur
# Ce serait bien aussi d'ajouter un support pour la première page
# On marque la séparation
st.sidebar.header("Section Graph")
# On élimine la première page
if choix_df == 1:
    st.sidebar.markdown("Graphique avec Caractéristiques BMS pas encore supporté")
# On demande à l'utilisateur de filtrer jusqu'au sexe
elif 'sexe' not in globals():
    st.sidebar.text("Veuillez filtrer jusqu'au sexe")
else:
    # Une fois que c'est fait on passe au graphique
    if sexe:
        # On explique une particularité de Vega
        st.sidebar.markdown("*Note* : Les graphiques utilisent Vega qui possède sa propre manière d'exporter qui se situe en haut à droite")
        # On donne l'option d'afficher le graphique
        if st.sidebar.checkbox('Afficher le graphique'):
            # On copie df_sex
            df_graph = df_sex
            # On concatène tous les colonnes non chiffrées
            # C'est très moche mais les tooltips de Vega arrangent les choses
            df_graph["Lib Graph"] = df_graph['Type de bénéficiaire de revenus minima garantis'] + \
                                    ' chez les ' + \
                                    df_graph['Sexe'] + 's' + \
                                    ' selon ' + \
                                    df_graph['Caractéristiques'] + \
                                    ' : ' + \
                                    df_graph['Libellés']
            # On fait de la concaténation la colonne index pour qu'elle s'affiche en tant que légende
            # On remplace les na par des 0 (affiche une colonne vide au lieu de pas de colonne du tout)
            # On retire les colonnes ayant servi à la concaténation
            df_graph = df_graph.set_index('Lib Graph').fillna(0).drop(df_graph.columns[[0,1,2,3]], axis = 1)
            # On affiche le graph avec une longueur arbitraire de 500
            st.bar_chart(df_graph, height = 500)