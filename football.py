import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

# Configurazione della pagina Streamlit
st.set_page_config(
    page_title="Statistiche Calcio Avanzate",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Stile personalizzato CSS
st.markdown("""
    <style>
    .main {
        background-color: #f4f6f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    h1, h2, h3 {
        color: #1b263b;
    }
    </style>
""", unsafe_allow_html=True)

# Dizionario globale di traduzione delle intestazioni in italiano
traduzioni_colonne = {
    'Date': 'Data',
    'Time': 'Ora',
    'HomeTeam': 'Squadra Casa',
    'AwayTeam': 'Squadra Ospite',
    'FTHG': 'Gol Casa (Finale)',
    'FTAG': 'Gol Ospiti (Finale)',
    'FTR': 'Risultato Finale (1X2)',
    'HTHG': 'Gol Casa (Primo Tempo)',
    'HTAG': 'Gol Ospiti (Primo Tempo)',
    'HTR': 'Risultato Primo Tempo',
    'HxG': 'xG Casa',
    'AxG': 'xG Ospiti',
    'HS': 'Tiri Casa',
    'AS': 'Tiri Ospiti',
    'HST': 'Tiri in Porta Casa',
    'AST': 'Tiri in Porta Ospiti',
    'HF': 'Falli Casa',
    'AF': 'Falli Ospiti',
    'HC': 'Calci d\'Angolo Casa',
    'AC': 'Calci d\'Angolo Ospiti',
    'HY': 'Cartellini Gialli Casa',
    'AY': 'Cartellini Gialli Ospiti',
    'HR': 'Cartellini Rossi Casa',
    'AR': 'Cartellini Rossi Ospiti'
}

# Titolo Principale
st.title("⚽ Statistiche Calcio")
st.markdown("Carica il file CSV scaricandolo da https://www.football-data.co.uk/")
st.markdown("<p style='font-size: 13px; font-style: italic; color: #555555;'>realizzato da Giacomo Bertè, Fabio Bertè e Luca Bertè - tutti i diritti riservati</p>", unsafe_allow_html=True)

# Sidebar per il caricamento del file
st.sidebar.header("📁 Caricamento Dati CSV")
uploaded_file = st.sidebar.file_uploader("Carica il file CSV settimanale", type=["csv"])

if uploaded_file is not None:
    @st.cache_data
    def load_data(file):
        return pd.read_csv(file)

    df = load_data(uploaded_file)

    # Conversione della data se presente e formattazione in stringa italiana gg/mm/aaaa
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce').dt.strftime('%d/%m/%Y')

    # Estrazione lista squadre
    squadre = sorted(list(set(df['HomeTeam'].dropna().unique()).union(set(df['AwayTeam'].dropna().unique()))))

    # --- FILTRO SQUADRA ---
    st.sidebar.markdown("---")
    st.sidebar.header("🔍 Filtro Squadra Dedicato")
    squadra_selezionata = st.sidebar.selectbox("Seleziona una squadra per il focus analitico", ["Tutte le squadre"] + squadre)

    # ---------------------------------------------------------
    # CASO 1: È SELEZIONATA UNA SQUADRA SPECIFICA
    # ---------------------------------------------------------
    if squadra_selezionata != "Tutte le squadre":
        st.subheader(f"🛡️ Profilo e Statistiche Dettagliate per: {squadra_selezionata} 🛡️")
        
        df_sq_casa = df[df['HomeTeam'] == squadra_selezionata]
        df_sq_fuori = df[df['AwayTeam'] == squadra_selezionata]
        df_sq_tot = pd.concat([df_sq_casa, df_sq_fuori])

        giocate = len(df_sq_tot)
        giocate_casa = len(df_sq_casa)
        giocate_fuori = len(df_sq_fuori)

        # Gol fatti e subiti
        tot_gf = int(df_sq_casa['FTHG'].sum() + df_sq_fuori['FTAG'].sum()) if ('FTHG' in df.columns and 'FTAG' in df.columns) else 0
        tot_gs = int(df_sq_casa['FTAG'].sum() + df_sq_fuori['FTHG'].sum()) if ('FTAG' in df.columns and 'FTHG' in df.columns) else 0

        # Calcolo Punti, Vinte, Pareggiate, Perse
        punti = 0
        vinte = pareggi = perse = 0
        vinte_casa = pareggi_casa = perse_casa = 0
        vinte_fuori = pareggi_fuori = perse_fuori = 0

        for _, r in df_sq_casa.iterrows():
            res = r.get('FTR')
            if res == 'H':
                punti += 3; vinte += 1; vinte_casa += 1
            elif res == 'D':
                punti += 1; pareggi += 1; pareggi_casa += 1
            elif res == 'A':
                perse += 1; perse_casa += 1

        for _, r in df_sq_fuori.iterrows():
            res = r.get('FTR')
            if res == 'A':
                punti += 3; vinte += 1; vinte_fuori += 1
            elif res == 'D':
                punti += 1; pareggi += 1; pareggi_fuori += 1
            elif res == 'H':
                perse += 1; perse_fuori += 1

        # KPI Cards Principali
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Partite", giocate)
        c2.metric("Punti", punti)
        c3.metric("Vinte", vinte)
        c4.metric("Pareggi", pareggi)
        c5.metric("Perse", perse)
        c6.metric("Diff. Reti", tot_gf - tot_gs)

        st.markdown("---")

        # Sezione Statistiche Approfondite in Schede
        tab_sq1, tab_sq2, tab_sq3 = st.tabs([
            f"🛡️ Storico Partite ({squadra_selezionata})", 
            "📈 Dettaglio Statistico Completo", 
            "📊 Analisi Grafica e Trend"
        ])

        with tab_sq1:
            st.markdown(f"#### 🛡️ Elenco di tutti gli incontri disputati da {squadra_selezionata}")
            partite_mostra = []
            for _, r in df_sq_tot.iterrows():
                casa = r.get('HomeTeam')
                ospite = r.get('AwayTeam')
                incontro = f"{casa} vs {ospite}"
                
                fthg = r.get('FTHG')
                ftag = r.get('FTAG')
                risultato = f"{int(fthg)}-{int(ftag)}" if pd.notna(fthg) and pd.notna(ftag) else "N/D"
                
                data_formattata = r.get('Date') if pd.notna(r.get('Date')) else "N/D"
                ora_formattata = r.get('Time') if pd.notna(r.get('Time')) else ""

                partite_mostra.append({
                    "Data": data_formattata,
                    "Ora": ora_formattata,
                    "Incontro": incontro,
                    "Risultato (Casa - Ospiti)": risultato,
                    "xG Casa": r.get('HxG'),
                    "xG Ospiti": r.get('AxG')
                })
            
            df_partite_sto = pd.DataFrame(partite_mostra)
            df_partite_sto.index = range(1, len(df_partite_sto) + 1)
            st.dataframe(df_partite_sto, use_container_width=True)

        with tab_sq2:
            st.markdown(f"### 📋 Tabella Analitica Completa: {squadra_selezionata} (Valori Medi)")
            
            tiri_fatti = (df_sq_casa['HS'].sum() if 'HS' in df_sq_casa.columns else 0) + (df_sq_fuori['AS'].sum() if 'AS' in df_sq_fuori.columns else 0)
            tiri_subiti = (df_sq_casa['AS'].sum() if 'AS' in df_sq_casa.columns else 0) + (df_sq_fuori['HS'].sum() if 'HS' in df_sq_fuori.columns else 0)
            
            tirip_fatti = (df_sq_casa['HST'].sum() if 'HST' in df_sq_casa.columns else 0) + (df_sq_fuori['AST'].sum() if 'AST' in df_sq_fuori.columns else 0)
            tirip_subiti = (df_sq_casa['AST'].sum() if 'AST' in df_sq_casa.columns else 0) + (df_sq_fuori['HST'].sum() if 'HST' in df_sq_fuori.columns else 0)
            
            angoli_fatti = (df_sq_casa['HC'].sum() if 'HC' in df_sq_casa.columns else 0) + (df_sq_fuori['AC'].sum() if 'AC' in df_sq_fuori.columns else 0)
            angoli_subiti = (df_sq_casa['AC'].sum() if 'AC' in df_sq_casa.columns else 0) + (df_sq_fuori['HC'].sum() if 'HC' in df_sq_fuori.columns else 0)

            falli_fatti = (df_sq_casa['HF'].sum() if 'HF' in df_sq_casa.columns else 0) + (df_sq_fuori['AF'].sum() if 'AF' in df_sq_fuori.columns else 0)
            gialli = (df_sq_casa['HY'].sum() if 'HY' in df_sq_casa.columns else 0) + (df_sq_fuori['AY'].sum() if 'AY' in df_sq_fuori.columns else 0)
            rossi = (df_sq_casa['HR'].sum() if 'HR' in df_sq_casa.columns else 0) + (df_sq_fuori['AR'].sum() if 'AR' in df_sq_fuori.columns else 0)

            xg_fatti = (df_sq_casa['HxG'].sum() if 'HxG' in df_sq_casa.columns else 0) + (df_sq_fuori['AxG'].sum() if 'AxG' in df_sq_fuori.columns else 0)
            xg_subiti = (df_sq_casa['AxG'].sum() if 'AxG' in df_sq_casa.columns else 0) + (df_sq_fuori['HxG'].sum() if 'HxG' in df_sq_fuori.columns else 0)

            div = giocate if giocate > 0 else 1

            col_stat1, col_stat2 = st.columns(2)

            with col_stat1:
                st.markdown("#### ⚽ Rendimento e Gol")
                df_rendimento = pd.DataFrame({
                    "Metrica": [
                        "Partite Giocate (Casa / Trasferta)", 
                        "Vittorie (Casa / Trasferta)", 
                        "Pareggi (Casa / Trasferta)", 
                        "Sconfitte (Casa / Trasferta)", 
                        "Gol Fatti (Totali / Media)", 
                        "Gol Subiti (Totali / Media)",
                        "Media Punti per Partita"
                    ],
                    "Valore": [
                        f"{giocate} ({giocate_casa} / {giocate_fuori})",
                        f"{vinte} ({vinte_casa} / {vinte_fuori})",
                        f"{pareggi} ({pareggi_casa} / {pareggi_fuori})",
                        f"{perse} ({perse_casa} / {perse_fuori})",
                        f"{tot_gf} ({round(tot_gf/div, 2)})",
                        f"{tot_gs} ({round(tot_gs/div, 2)})",
                        f"{round(punti/div, 2)}"
                    ]
                })
                df_rendimento.index = range(1, len(df_rendimento) + 1)
                st.dataframe(df_rendimento, use_container_width=True)

            with col_stat2:
                st.markdown("#### 🎯 Statistiche di Gioco e xG (Valori Medi)")
                df_gioco = pd.DataFrame({
                    "Metrica di Gioco (Media Partita)": [
                        "Tiri Totali (Effettuati / Subiti)",
                        "Tiri in Porta (Effettuati / Subiti)",
                        "Calci d'Angolo (Favore / Contro)",
                        "Expected Goals xG (Prodotti / Concessi)",
                        "Falli Commessi (Media)",
                        "Cartellini Gialli / Rossi (Media)"
                    ],
                    "Valore Medio": [
                        f"{round(tiri_fatti/div, 2)} / {round(tiri_subiti/div, 2)}",
                        f"{round(tirip_fatti/div, 2)} / {round(tirip_subiti/div, 2)}",
                        f"{round(angoli_fatti/div, 2)} / {round(angoli_subiti/div, 2)}",
                        f"{round(xg_fatti/div, 2)} / {round(xg_subiti/div, 2)}",
                        f"{round(falli_fatti/div, 2)}",
                        f"{round(gialli/div, 2)} 🟨 / {round(rossi/div, 2)} 🟥"
                    ]
                })
                df_gioco.index = range(1, len(df_gioco) + 1)
                st.dataframe(df_gioco, use_container_width=True)

        with tab_sq3:
            st.markdown(f"#### 📊 Trend e Grafici Avanzati (Media Progressiva per Giornata): {squadra_selezionata}")
            
            x_vals = np.array(range(1, len(df_sq_tot) + 1))
            
            # --- GRAFICO xG A BARRE VERTICALI (MEDIA PROGRESSIVA FINO ALLA GIORNATA N) ---
            if 'HxG' in df.columns and 'AxG' in df.columns:
                fig, ax = plt.subplots(figsize=(4.5, 2.3))
                
                xg_prodotti_raw = np.array([r.get('HxG') if r['HomeTeam'] == squadra_selezionata else r.get('AxG') for _, r in df_sq_tot.iterrows()], dtype=float)
                xg_concessi_raw = np.array([r.get('AxG') if r['HomeTeam'] == squadra_selezionata else r.get('HxG') for _, r in df_sq_tot.iterrows()], dtype=float)
                
                xg_prodotti = np.cumsum(xg_prodotti_raw) / x_vals
                xg_concessi = np.cumsum(xg_concessi_raw) / x_vals
                
                width = 0.4
                
                ax.bar(x_vals - width/2, xg_prodotti, width, label='Media xG Prodotto', color='#2a9d8f', edgecolor='black', linewidth=0.4)
                ax.bar(x_vals + width/2, xg_concessi, width, label='Media xG Concesso', color='#e76f51', edgecolor='black', linewidth=0.4)
                
                ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
                ax.set_xticks(x_vals)
                ax.set_xticklabels(x_vals, fontsize=7)
                ax.set_title(f"Media Progressiva xG per Giornata - {squadra_selezionata}", fontsize=8, fontweight='bold')
                ax.set_xlabel("Giornata", fontsize=6)
                ax.set_ylabel("Media xG", fontsize=6)
                ax.tick_params(axis='both', labelsize=6)
                ax.grid(True, linestyle=':', alpha=0.5, axis='y')
                ax.legend(fontsize=6, loc='upper left', frameon=True)
                
                plt.tight_layout()
                st.pyplot(fig)

                # Spiegazione del calcolo matematico dell'Expected Goals (xG)
                with st.expander("🧮 Come viene calcolato l'Expected Goals (xG) — Clicca per approfondire", expanded=False):
                    st.markdown("""
                    ### 🎯 Che cos'è l'Expected Goals (xG)?

                    L'**Expected Goals (xG)** misura quanto sono state **pericolose le occasioni da gol** create da una squadra.

                    Ad ogni tiro viene assegnata una **probabilità di trasformarsi in gol**, espressa con un numero compreso tra **0 e 1**.

                    Per esempio:

                    - **xG = 0,05** → il tiro ha circa il **5%** di probabilità di diventare gol
                    - **xG = 0,20** → circa il **20%**
                    - **xG = 0,50** → circa il **50%**
                    - **xG = 0,90** → circa il **90%**

                    Quindi **più è alto il valore xG di un tiro, più l'occasione è considerata pericolosa**.

                    ---

                    ### ⚽ Come si calcola l'xG di una squadra?

                    L'xG della squadra è ottenuto **sommando il valore xG di tutti i suoi tiri**.

                    La formula è:

                    **xG = xG₁ + xG₂ + xG₃ + ... + xGₙ**

                    oppure, in forma matematica:

                    **xG = Σᵢ₌₁ⁿ P(Gol | tiroᵢ)**

                    Dove:

                    - **n** = numero totale di tiri effettuati
                    - **xGᵢ** = valore xG assegnato al singolo tiro
                    - **P(Gol | tiroᵢ)** = probabilità che quel determinato tiro diventi gol

                    ---

                    ### 📌 Esempio pratico

                    Immaginiamo che una squadra effettui **5 tiri** durante una partita:

                    | Tiro | Valore xG | Probabilità |
                    |------|-----------|-------------|
                    | Tiro 1 | 0,05 | 5% |
                    | Tiro 2 | 0,10 | 10% |
                    | Tiro 3 | 0,25 | 25% |
                    | Tiro 4 | 0,30 | 30% |
                    | Tiro 5 | 0,20 | 20% |

                    Il calcolo sarà:

                    **0,05 + 0,10 + 0,25 + 0,30 + 0,20 = 0,90 xG**

                    La squadra ha quindi prodotto **0,90 Expected Goals**.

                    Questo significa che, considerando la qualità complessiva delle occasioni create, ci si aspetterebbe **circa 0,90 gol**.

                    ⚠️ **Attenzione:** 0,90 xG non significa che la squadra debba necessariamente segnare 0,90 gol.

                    In una singola partita può segnare **0, 1, 2 o più gol**. L'xG è una **stima probabilistica della qualità delle occasioni**, non una previsione esatta del risultato.

                    ---

                    ### 🟢 xG Prodotto

                    **xG Prodotto** indica la qualità complessiva delle occasioni create dalla squadra.

                    È la somma dei valori xG di **tutti i tiri effettuati dalla squadra**.

                    **xG Prodotto = Σ xG dei tiri effettuati**

                    Esempio:

                    **0,10 + 0,25 + 0,40 + 0,15 = 0,90 xG**

                    ---

                    ### 🔴 xG Concesso

                    **xG Concesso** indica invece la qualità complessiva delle occasioni che la squadra ha permesso agli avversari di creare.

                    In pratica, si sommano i valori xG di **tutti i tiri effettuati dagli avversari**.

                    **xG Concesso = Σ xG dei tiri degli avversari**

                    Esempio:

                    **0,20 + 0,10 + 0,35 + 0,05 = 0,70 xG**

                    La squadra ha quindi concesso **0,70 xG**.

                    ---

                    ### 📊 How to read the chart

                    - 🟢 **xG Prodotto** → quanto sono state pericolose le occasioni create dalla squadra.
                    - 🔴 **xG Concesso** → quanto sono state pericolose le occasioni concesse agli avversari.
                    - **Differenza xG** → **xG Prodotto − xG Concesso**.

                    Per esempio:

                    **1,80 xG prodotti − 0,70 xG concessi = +1,10 xG**

                    La squadra ha creato occasioni complessivamente più pericolose rispetto a quelle concesse.

                    Al contrario:

                    **0,60 xG prodotti − 1,40 xG concessi = −0,80 xG**

                    significa che gli avversari hanno creato occasioni complessivamente più pericolose.

                    ---

                    ### 🧠 Da cosa dipende il valore xG di un tiro?

                    Il valore xG di ogni tiro viene normalmente stimato da un **modello statistico** che considera caratteristiche dell'occasione, come:

                    - 📍 **posizione del tiro**
                    - 📐 **angolo rispetto alla porta**
                    - 🦶 **parte del corpo utilizzata**
                    - ⚽ **tipo di azione**
                    - 🏃 **situazione di gioco**
                    - 🎯 **eventuale assist o cross**
                    - 🚩 **calcio d'angolo o punizione**
                    - 🥅 **distanza dalla porta**

                    Per questo motivo, **due tiri non hanno necessariamente lo stesso valore xG**.

                    Un tiro ravvicinato davanti alla porta può avere un xG molto elevato, mentre un tiro dalla lunga distanza può avere un xG molto basso.

                    ### In sintesi

                    **xG Prodotto = qualità delle occasioni create**

                    **xG Concesso = qualità delle occasioni concesse**

                    **Differenza xG = qualità delle occasioni create − qualità delle occasioni concesse**

                    👉 **Più alto è l'xG prodotto, maggiori sono state le occasioni create.**

                    👉 **Più basso è l'xG concesso, meno pericolose sono state le occasioni concesse agli avversari.**
                    """)

            else:
                st.info("Dati xG non disponibili nel dataset per generare il grafico.")

            st.markdown("---")
            
            # --- ULTERIORI GRAFICI E TENDENZE (MEDIA PROGRESSIVA PER GIORNATA) ---
            col_gr1, col_gr2 = st.columns(2)
            
            with col_gr1:
                st.markdown("##### 🎯 Media Tiri Totali vs Tiri in Porta")
                if 'HS' in df.columns and 'HST' in df.columns:
                    fig2, ax2 = plt.subplots(figsize=(4.5, 2.3))
                    tiri_t_raw = np.array([r.get('HS') if r['HomeTeam'] == squadra_selezionata else r.get('AS') for _, r in df_sq_tot.iterrows()], dtype=float)
                    tiri_p_raw = np.array([r.get('HST') if r['HomeTeam'] == squadra_selezionata else r.get('AST') for _, r in df_sq_tot.iterrows()], dtype=float)
                    
                    tiri_t = np.cumsum(tiri_t_raw) / x_vals
                    tiri_p = np.cumsum(tiri_p_raw) / x_vals
                    
                    width = 0.35
                    # Utilizziamo direttamente x_vals come posizioni (da 1 a N)
                    ax2.bar(x_vals - width/2, tiri_t, width, label='Media Tiri Totali', color='#457b9d')
                    ax2.bar(x_vals + width/2, tiri_p, width, label='Media Tiri in Porta', color='#1d3557')
                    
                    ax2.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
                    ax2.set_xticks(x_vals)
                    ax2.set_xticklabels(x_vals, fontsize=6)
                    ax2.set_xlabel("Giornata", fontsize=6)
                    ax2.set_ylabel("Media Tiri", fontsize=6)
                    ax2.set_title("Media Progressiva Tiri per Giornata", fontsize=8, fontweight='bold')
                    ax2.legend(fontsize=6, loc='upper left')
                    ax2.grid(True, linestyle='--', alpha=0.3)
                    plt.tight_layout()
                    st.pyplot(fig2)
                else:
                    st.info("Dati tiri non sufficienti per il grafico.")

            with col_gr2:
                st.markdown("##### 🚩 Andamento Media Calci d'Angolo")
                if 'HC' in df.columns and 'AC' in df.columns:
                    fig3, ax3 = plt.subplots(figsize=(4.5, 2.3))
                    angoli_fav_raw = np.array([r.get('HC') if r['HomeTeam'] == squadra_selezionata else r.get('AC') for _, r in df_sq_tot.iterrows()], dtype=float)
                    angoli_con_raw = np.array([r.get('AC') if r['HomeTeam'] == squadra_selezionata else r.get('HC') for _, r in df_sq_tot.iterrows()], dtype=float)
                    
                    angoli_fav = np.cumsum(angoli_fav_raw) / x_vals
                    angoli_con = np.cumsum(angoli_con_raw) / x_vals
                    
                    ax3.plot(x_vals, angoli_fav, marker='s', markersize=3, color='#2a9d8f', label="Media Angoli Favore", linewidth=1.5)
                    ax3.plot(x_vals, angoli_con, marker='^', markersize=3, color='#e76f51', label="Media Angoli Contro", linewidth=1.5, linestyle=':')
                    
                    ax3.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
                    ax3.set_xticks(x_vals)
                    
                    ax3.set_xlabel("Giornata", fontsize=6)
                    ax3.set_ylabel("Media Corner", fontsize=6)
                    ax3.tick_params(axis='both', labelsize=6)
                    ax3.set_title("Media Progressiva Calci d'Angolo per Giornata", fontsize=8, fontweight='bold')
                    ax3.legend(fontsize=6, loc='upper left')
                    ax3.grid(True, linestyle='--', alpha=0.3)
                    plt.tight_layout()
                    st.pyplot(fig3)
                else:
                    st.info("Dati corner non sufficienti per il grafico.")

    # ---------------------------------------------------------
    # CASO 2: VISUALIZZAZIONE GENERALE (TUTTE LE SQUADRE)
    # ---------------------------------------------------------
    else:
        st.subheader("📊 Panoramica Globale del Campionato")
        
        col1, col2, col3, col4 = st.columns(4)
        tot_partite = len(df)
        tot_gol = int(df['FTHG'].sum() + df['FTAG'].sum()) if 'FTHG' in df.columns and 'FTAG' in df.columns else 0
        media_gol = round(tot_gol / tot_partite, 2) if tot_partite > 0 else 0
        
        col1.metric("Partite Analizzate", tot_partite)
        col2.metric("Gol Totali", tot_gol)
        col3.metric("Media Gol / Partita", media_gol)
        col4.metric("Totale Colonne Dataset", len(df.columns))

        st.markdown("---")

        tab_generale, tab_tiri_xg, tab_raw = st.tabs([
            "🏆 Classifica e Gol", 
            "🎯 Tiri, xG e Angoli (Medie per Squadra)", 
            "📋 Tabella Completa"
        ])

        with tab_generale:
            st.markdown("### Classifica Generale")
            def calcola_classifica(dataframe):
                classifica = {}
                for s in squadre:
                    classifica[s] = {'Punti': 0, 'Giocate': 0, 'Vinte': 0, 'Pareggiate': 0, 'Perse': 0, 'GolFatti': 0, 'GolSubiti': 0}
                for _, row in dataframe.iterrows():
                    casa, ospite = row.get('HomeTeam'), row.get('AwayTeam')
                    gf_casa, gf_ospite = row.get('FTHG'), row.get('FTAG')
                    ftr = row.get('FTR')
                    if pd.isna(casa) or pd.isna(ospite) or pd.isna(gf_casa) or pd.isna(gf_ospite): continue
                    classifica[casa]['Giocate'] += 1; classifica[ospite]['Giocate'] += 1
                    classifica[casa]['GolFatti'] += int(gf_casa); classifica[casa]['GolSubiti'] += int(gf_ospite)
                    classifica[ospite]['GolFatti'] += int(gf_ospite); classifica[ospite]['GolSubiti'] += int(gf_casa)
                    if ftr == 'H':
                        classifica[casa]['Punti'] += 3; classifica[casa]['Vinte'] += 1; classifica[ospite]['Perse'] += 1
                    elif ftr == 'A':
                        classifica[ospite]['Punti'] += 3; classifica[ospite]['Vinte'] += 1; classifica[casa]['Perse'] += 1
                    elif ftr == 'D':
                        classifica[casa]['Punti'] += 1; classifica[casa]['Pareggiate'] += 1
                        classifica[ospite]['Punti'] += 1; classifica[ospite]['Pareggiate'] += 1
                df_c = pd.DataFrame.from_dict(classifica, orient='index')
                df_c['Differenza Reti'] = df_c['GolFatti'] - df_c['GolSubiti']
                df_c = df_c.sort_values(by=['Punti', 'Differenza Reti', 'GolFatti'], ascending=False).reset_index().rename(columns={'index': 'Squadra'})
                df_c.index = range(1, len(df_c) + 1)
                return df_c

            df_class = calcola_classifica(df)
            st.dataframe(df_class, use_container_width=True)

            st.markdown("### Distribuzione Gol Segnati per Squadra")
            fig, ax = plt.subplots(figsize=(12, 5))
            df_class_sorted = df_class.sort_values(by='GolFatti', ascending=False)
            ax.bar(df_class_sorted['Squadra'], df_class_sorted['GolFatti'], label='Gol Fatti Totali', color='#2a9d8f')
            ax.set_xticklabels(df_class_sorted['Squadra'], rotation=45, ha='right')
            ax.set_ylabel("Gol")
            ax.set_title("Totale Gol per Squadra", fontsize=12, fontweight='bold')
            ax.legend()
            st.pyplot(fig)

        with tab_tiri_xg:
            st.markdown("### Analisi Approfondita")
            
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                st.markdown("#### 🎯 Tiri Totali per Squadra")
                if 'HS' in df.columns and 'AS' in df.columns:
                    tiri_casa = df.groupby('HomeTeam')['HS'].sum()
                    tiri_fuori = df.groupby('AwayTeam')['AS'].sum()
                    tiri_tot = (tiri_casa.add(tiri_fuori, fill_value=0)).sort_values(ascending=False)
                    
                    fig, ax = plt.subplots(figsize=(8, 5))
                    tiri_tot.head(10).plot(kind='bar', color='#e76f51', ax=ax)
                    ax.set_title("Top 10 Squadre per Tiri Totali (Casa + Trasferta)")
                    plt.xticks(rotation=45, ha='right')
                    st.pyplot(fig)
                else:
                    st.info("Colonne tiri non trovate.")

            with col_g2:
                st.markdown("#### ⚡ Expected Goals (HxG / AxG)")
                if 'HxG' in df.columns and 'AxG' in df.columns:
                    xg_c = df.groupby('HomeTeam')['HxG'].sum()
                    xg_f = df.groupby('AwayTeam')['AxG'].sum()
                    xg_tot = (xg_c.add(xg_f, fill_value=0)).sort_values(ascending=False)

                    fig, ax = plt.subplots(figsize=(8, 5))
                    xg_tot.head(10).plot(kind='bar', color='#457b9d', ax=ax)
                    ax.set_title("Top 10 Squadre per xG (Expected Goals) Totale")
                    plt.xticks(rotation=45, ha='right')
                    st.pyplot(fig)
                else:
                    st.info("Colonne xG non presenti.")

            st.markdown("#### Tabella Statistiche di Gioco (Medie AVG per Squadra)")
            
            mapping_colonne_medie = {
                'HomeTeam': 'Squadra',
                'HS': 'Tiri Totali',
                'AS': 'Tiri Subiti (Avg)',
                'HST': 'Tiri in Porta',
                'AST': 'Tiri in Porta Subiti (Avg)',
                'HF': 'Falli Commessi',
                'AF': 'Falli Subiti (Avg)',
                'HC': 'Calci d\'Angolo',
                'AC': 'Angoli Subiti (Avg)',
                'HY': 'Cartellini Gialli',
                'AY': 'Gialli Avversari (Avg)',
                'HR': 'Cartellini Rossi',
                'AR': 'Rossi Avversari (Avg)'
            }
            
            game_metrics = [c for c in ['HS', 'AS', 'HST', 'AST', 'HF', 'AF', 'HC', 'AC', 'HY', 'AY', 'HR', 'AR'] if c in df.columns]
            if len(game_metrics) > 0:
                stats_summary = df.groupby('HomeTeam')[game_metrics].mean().reset_index()
                stats_summary = stats_summary.rename(columns=mapping_colonne_medie)
                stats_summary.index = range(1, len(stats_summary) + 1)
                st.dataframe(stats_summary, use_container_width=True)

        with tab_raw:
            st.markdown("### 📋 Tabella Completa")
            
            df_display = df.copy()
            parole_chiave_quote = ['B365', 'BFD', 'BV', 'BW', 'PP', 'SKB', 'Max', 'Avg', 'BFE', 'AHh', 'AHCh', 'Div']
            
            colonne_valide = [col for col in df_display.columns if not any(k in col for k in parole_chiave_quote)]
            df_display = df_display[colonne_valide]
            df_display = df_display.drop(columns=['FTR', 'HTR'], errors='ignore')
            df_display = df_display.rename(columns=traduzioni_colonne)
            df_display.index = range(1, len(df_display) + 1)
            
            configurazione_colonne = {
                "Data": st.column_config.TextColumn("Data", pinned=True),
                "Ora": st.column_config.TextColumn("Ora", pinned=True),
                "Squadra Casa": st.column_config.TextColumn("Squadra Casa", pinned=True),
                "Squadra Ospite": st.column_config.TextColumn("Squadra Ospite", pinned=True),
            }
            
            st.dataframe(df_display, column_config=configurazione_colonne, use_container_width=True)

else:
    st.info("👈 Per iniziare, carica il file CSV aggiornato della settimana tramite la barra laterale.")
