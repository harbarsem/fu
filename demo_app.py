import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import geopandas as gpd
import matplotlib as mpl
from celluloid import Camera
import time

from matplotlib.animation import ArtistAnimation
with st.echo(code_location='below'):
    st.title("Ну и ну!")
    """
    Выборы в США: 1976 - 2020
    """

    """
    Немого общей статистики - голоса за демократов и республиканцев:
    """
    st.set_option('deprecation.showPyplotGlobalUse', False)
    data = pd.read_csv("1976-2020-president.csv")
    data = data.drop(['state_fips', 'state_cen', 'state_ic', 'office', 'writein', 'version', 'notes'], axis='columns')
    data['percentage'] = data["candidatevotes"] / data["totalvotes"]
    geo_states = gpd.read_file("ne_50m_admin_1_states_provinces.shp")
    geo_states = geo_states[geo_states["iso_a2"] == "US"]
    geo_states['name'] = geo_states['name'].apply(lambda x: x.upper())
    geo_states = geo_states[['name', 'geometry']]
    geo_states["rp"] = geo_states['geometry'].representative_point()
    df = geo_states.merge(data, how="right", left_on="name", right_on="state")
    df['area'] = df['geometry'].to_crs({'init': 'epsg:3395'}).map(lambda
                                                                      p: p.area / 10 ** 6)  # (this line - from https://gis.stackexchange.com/questions/218450/getting-polygon-areas-using-geopandas)
    all_years=list(data["year"].unique())

    @st.cache
    def anim_gif(data=df):
        vbr = []
        hhh = []
        for i in range(9):
            vbr.append("{}0M".format(i))
            hhh.append(i * 10 ** 7)
        fig, ax = plt.subplots(figsize=(5, 3))
        camera = Camera(fig)
        for year1 in all_years:
            sample_1 = data[(data["year"] == year1) & (data["candidatevotes"] > 100000)]
            a = sample_1.groupby("party_detailed")["candidatevotes"].sum().reindex(
            index=['DEMOCRAT', 'REPUBLICAN', "LIBERTARIAN"])
            a.plot.bar(color=['#3d50bd', '#e83933', 'black'])
            plt.xticks(rotation=0, horizontalalignment="center")
            ax.text(0.08, 1.03, "Votes for three parties in {}".format(year1), transform=ax.transAxes, fontsize=14, fontweight='bold')
            plt.xlabel("", fontsize=12)
            plt.ylabel("NUMBER OF VOTES", fontsize=12)
            plt.yticks(hhh, vbr)
            camera.snap()
        animation = camera.animate(interval=400, repeat=True, repeat_delay=400)
        time.sleep(2)
        return animation

    data=df
    result=anim_gif(data)
    st.components.v1.html(result.to_jshtml(), height=400, scrolling=True)


    """
    
    Теперь наше естественное желание - понять, как каждый штат менял предпочтения за эти годы. Посмотрим!
    
    """


    simply = df[(df['party_simplified'] == 'DEMOCRAT') | (df['party_simplified'] == 'REPUBLICAN')]
    simply1 = simply.drop(df.columns.difference(['name', 'year', 'percentage', 'party_simplified']), 1).copy()
    dem = simply1[simply1['party_simplified'] == 'DEMOCRAT'].copy()
    rep = simply1[simply1['party_simplified'] == 'REPUBLICAN'].copy()
    df['wh'] = df['name'] + df['year'].astype(str)
    dem['wh'] = dem['name'] + dem['year'].astype(str)
    rep['wh'] = rep['name'] + rep['year'].astype(str)
    margins = dem.merge(rep, left_on='wh', right_on='wh').copy()
    margins['marg'] = -margins["percentage_x"] + margins["percentage_y"]
    margins2 = margins.drop(margins.columns.difference(['wh', 'marg']), 1)
    df = df.merge(margins2, left_on='wh', right_on='wh')
    margins = margins.drop(margins.columns.difference(['wh', 'marg', "name_x", "year_x"]), 1)
    margins_main = margins.pivot_table(index='name_x', columns='year_x', values='marg')
    k = df.copy()
    #lt = ["ALABAMA", "OREGON", "OHIO", "VERMONT", "WISCONSIN", "WYOMING", "RHODE ISLAND", "DISTRICT OF COLUMBIA","TEXAS"]
    selected_states=st.multiselect("Выберите названия штатов (как минимум 4):", list(df['name'].unique()))#, default=lt)
    selected_states=list(selected_states)
    if len(selected_states)>3:
        k=margins_main.loc[selected_states]
        fig = plt.figure(figsize=(15, 0.5 * len(selected_states)))
        sns.heatmap(k, vmin=-0.3, vmax=0.3, center=0, cmap='coolwarm', yticklabels=True, linewidths=3)
        plt.xlabel('Year', fontsize=14, fontweight='bold')
        plt.ylabel('State', fontsize=14, fontweight='bold')
        plt.title('% margin (%Republican - %Democrat) for each state', fontsize=16, fontweight='bold', pad=20)
        st.pyplot()
    else:
        st.write('Пока Вы выбрали меньше 4 штатов!')


    dict_col = {'DEMOCRAT': ["Blues", "демократ!"], 'REPUBLICAN': ["Reds", "республиканец!"]}
    """
   
   
   
   
    """
    selected_year= st.selectbox("Выберите год", df['year'].unique())
    a = int(selected_year)
    sample_zero = df[(df["year"] == a)]
    dem_cand = str(sample_zero[sample_zero['party_detailed'] == 'DEMOCRAT']['candidate'].unique()[0])
    rep_cand = str(sample_zero[sample_zero['party_detailed'] == 'REPUBLICAN']['candidate'].unique()[0])
    st.write("В {} году участвовали политики {} от республиканцев и {} от демократов.".format(a, rep_cand, dem_cand))
    win = sample_zero.groupby("party_simplified")["candidatevotes"].sum().idxmax()
    if a==2000:
        prez = 'GORE, AL'
        st.write(f"В {selected_year!r} году больше всего голосов получил(а) "+ dict_col[win][1]+
             " (хотя президентом стал {}.)".format(prez)+ " Но все же посмотрим, как зовоеывал штаты кандидат, получивший большинство голосов:")
    elif a==2016:
        prez = 'TRUMP, DONALD J.'
        st.write(f"В {selected_year!r} году больше всего голосов получил(а) " + dict_col[win][1] +
                 " (хотя президентом стал {})".format(prez) + ". Но все же посмотрим, как зовоеывал штаты кандидат, получивший большинство голосов:")
    else:
        st.write(f"Победил "+ dict_col[win][1]+ " А вот как голосовали штаты (на графике - разница между результатами республиканца и демократа")

    """
     
     
    """
    sample5 = df[(df["year"] == a) & (df["party_simplified"] == "DEMOCRAT")]
    sample5.plot(column='marg', vmin=-0.3, vmax=0.3, figsize=(25, 15), legend=True, cmap='coolwarm')
    plt.xlim(-130, -65)
    plt.ylim(20, 55)
    title = 'Elections {}: state-level margin'.format(a)
    mpl.pyplot.title(title, fontsize=20, fontweight='bold', loc='center', pad=10)
    for x, y, label in zip(sample5['rp'].x - 1.5, sample5['rp'].y, sample5["state"]):
        if label != 'ALASKA' and label != 'HAWAII' and (sample5[sample5['state'] == label]['area'] > 40000).to_list()[
            0]:
            if label == "MISSISSIPPI" or label == 'VERMONT':
                plt.text(x, y + 0.7, label, fontsize=8, color='black', alpha=1, weight="bold")
            elif label == "IDAHO":
                plt.text(x + 1, y - 1, label, fontsize=8, color='black', alpha=1, weight="bold")
            else:
                plt.text(x, y, label, fontsize=8, color='black', alpha=1, weight="bold")
    plt.text(-56, 35, "Share of votes", fontsize=14, color='black', weight="bold", rotation='vertical')
    st.pyplot()






