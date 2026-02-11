"""
Utility functions per analisi Food Cost ristoranti
Autore: Giovanni Lo Presti
Data: Ottobre 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display


def eda_display(df):
  """
  Automatizzo la visualizzazione delle stats di un dataset

  Args:
      df = dataframe caricato in precedenza

  Return:
      df:
      - head()
      - info()
      - describe()
      - somma NaN values
      - df con % NaN per Serie
      - duplicated()

  Requirements:
  pandas
  """

  print('DATASET HEAD:')
  display(df.head(15))

  print('-' * 70)
  print('-' * 70)
  print('INFO:')
  display(df.info())

  print('-' * 70)
  print('-' * 70)
  print('DESCRIBE:')
  display(df.describe())

  print('-' * 70)
  print('-' * 70)
  print('NAN VALUES:')
  display(df.isna().sum())
  missing = df.isna().sum()
  missing_pct = (df.isna().sum() / len(df) * 100).round(2)
  missing_df = pd.DataFrame({
        'Missing Count': missing,
        'Percentage': missing_pct
    })
  display(missing_df[missing_df['Missing Count'] > 0])

  print('-' * 70)
  print('-' * 70)
  print('DUPLICATED:')
  print(df.duplicated().sum())


def risparmio_foodcost(ds, nome_piatto, fc_target):

  """
  Calcola il risparmio potenziale inserendo il food cost ottimale

  Args:
      nome_piatto (str): Nome del piatto da analizzare
      fc_target (float): Food cost % ottimale da rasggiungere

  Return:
      Dict con tutti i calcoli eseguiti
  """

  # cerco il piatto nel df per accedere ai dati del piatto
  piatto = ds[ds['dish_name'] == nome_piatto]

  #verifico che il piatto esista
  if piatto.empty:
    return f"{nome_piatto} non trovato!"

  # trovo dati di riferimento sul piatto
  prezzo_piatto = piatto['selling_price'].iloc[0]
  costo_piatto = piatto['unit_cost'].iloc[0]
  spreco_piatto = piatto['waste_qty'].iloc[0]
  unit_piatto_vendute = piatto['quantity_sold'].sum()

  # calcolo food cost attuale
  fc_attuale = ((costo_piatto + spreco_piatto) / prezzo_piatto) * 100

  # calcolo il costo target per soddisfare il fc% di riferimento
  costo_target = (fc_target * prezzo_piatto) / 100

  # calcolo il risparmio potenziale
  risparmio = costo_piatto - costo_target
  risparmio_potenziale = risparmio * unit_piatto_vendute

  # aggiungo la colonna category
  categoria = piatto['category'].iloc[0]

  return {
      'nome piatto' : nome_piatto,
      'categoria' : categoria,
      'prezzo piatto' : round(float(prezzo_piatto),2),
      'costo piatto' : round(float(costo_piatto),2),
      'costo target' : round(float(costo_target),2),
      'unità vendute' : int(unit_piatto_vendute),
      'food cost % attuale' : round(float(fc_attuale),2),
      'food cost % target' : round(float(fc_target),2),
      'costo target' : round(float(costo_target),2),
      'risparmio per unità' : round(float(risparmio),2),
      'risparmio potenziale': round(float(risparmio_potenziale),2)
  }



# FUNZIONE PER CREARE LA MATRICE DI MENU ENGINEERING

def create_menu_matrix(df, x_col='sold_qty', y_col='margin_real_€', label_col='item_name', title="Menu Engineering Matrix"):
    """
    Genera una matrice di Menu Engineering professionale.
    
    Args:
        df: Il dataframe contenente i dati.
        x_col: Nome della colonna Popolarità (es. 'qty').
        y_col: Nome della colonna Redditività (es. 'margin_real_€').
        label_col: Nome della colonna con i nomi dei piatti.
    """

    # 1. Provo a importare adjustText per gestier le etichette
    try:
        from adjustText import adjust_text # type: ignore
        HAS_ADJUST_TEXT = True
    except ImportError:
        HAS_ADJUST_TEXT = False
        print("Consiglio: installa 'adjustText' (pip install adjustText) per etichette perfette!")
    
    # 2. Calcolo le Mediane (i confini dei quadranti)
    median_x = df[x_col].median()
    median_y = df[y_col].median()

    # 3. Assegno la categoria a ogni piatto per colorarli
    def get_category(row):
        if row[x_col] >= median_x and row[y_col] >= median_y:
            return 'STAR'
        elif row[x_col] < median_x and row[y_col] >= median_y:
            return 'PUZZLE'
        elif row[x_col] >= median_x and row[y_col] < median_y:
            return 'PLOWHORSE'
        else:
            return 'DOG'

    df['me_category'] = df.apply(get_category, axis=1)
    
    # Mappa colori standard del settore
    palette = {
        'STAR': 'gold',       # Oro/Giallo
        'PUZZLE': 'purple',   # Viola/Blu scuro (Enigma)
        'PLOWHORSE': 'gray',  # Grigio (Lavoro sporco)
        'DOG': 'red'          # Rosso (Pericolo)
    }

    # 4. Setup Grafico
    plt.figure(figsize=(14, 10))
    sns.set_style("whitegrid")
    
    # Scatterplot principale
    sns.scatterplot(
        data=df, 
        x=x_col, 
        y=y_col, 
        hue='me_category',  # Colora in base alla categoria
        palette=palette,
        s=300,              # Dimensione fissa (o puoi renderla dinamica in base al fatturato)
        edgecolor='black',
        alpha=0.2
    )

    # 5. Disegno le linee dei quadranti
    plt.axvline(median_x, color='black', linestyle='-.', alpha=0.2)
    plt.axhline(median_y, color='black', linestyle='-.', alpha=0.2)
    
    # Lista dove raccoglieremo tutti gli oggetti testo
    texts = []
    
    # Ciclo su ogni riga del dataframe
    for i in range(df.shape[0]):
        # Creiamo l'oggetto testo MA non lo stampiamo ancora in via definitiva
        t = plt.text(
            x=df[x_col].iloc[i], 
            y=df[y_col].iloc[i], 
            s=df[label_col].iloc[i],
            fontsize=9, 
            weight='bold', 
            color='black'
        )
        texts.append(t) # Lo aggiungiamo alla lista
    
    # ORA APPLICHIAMO LA MAGIA
    if HAS_ADJUST_TEXT:
        # arrowprops crea quelle belle freccette se l'etichetta viene spostata molto
        adjust_text(texts, arrowprops=dict(arrowstyle='-', color='gray', lw=0.5))

    # 6. FORMATTAZIONE FINALE ---
    # Etichette Quadranti
    x_lims = plt.xlim()
    y_lims = plt.ylim()
    plt.text(x_lims[1], y_lims[1], 'STARS', ha='right', va='top', fontsize=16, color='gold', weight='heavy')
    plt.text(x_lims[0], y_lims[1], 'PUZZLES', ha='left', va='top', fontsize=16, color='purple', weight='heavy')
    plt.text(x_lims[1], y_lims[0], 'PLOWHORSES', ha='right', va='bottom', fontsize=16, color='gray', weight='heavy')
    plt.text(x_lims[0], y_lims[0], 'DOGS', ha='left', va='bottom', fontsize=16, color='red', weight='heavy')

    # Titoli
    plt.title(title, fontsize=18, weight='bold')
    plt.xlabel('Popolarità (Quantità Venduta)', fontsize=12)
    plt.ylabel('Redditività (Margine Unitario €)', fontsize=12)
    
    # Sposto la legenda fuori
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0, title="Categoria ME")
    
    plt.tight_layout()
    plt.show()





# FUNZIONE PER FARE AUGMENTATION DEI DATI DEL DATAFRAME


def inject_realism_full(sales_df, inventory_df, menu_df):
    print("--- AVVIO SIMULAZIONE REALISTICA: FULL MENU ---")
    
    # --- 1. CONFIGURAZIONE SCENARIO (La "Regia") ---
    
    # A. SALES MULTIPLIERS: (Qty = Moltiplicatore Vendite, Price = Moltiplicatore Prezzo)
    # Logica: 
    # - > 1.0: Aumento (Successo/Inflazione)
    # - < 1.0: Diminuzione (Flop/Sconto)
    
    sales_scenario = {
        # --- BEVANDE (Le miniere d'oro - Volumi alti) ---
        'Acqua naturale':       {'qty': 4.0, 'price': 1.0}, # Tutti bevono acqua
        'Caffè':                {'qty': 3.5, 'price': 1.0}, # Margine puro
        'Spritz':               {'qty': 2.0, 'price': 1.2}, # Alta vendita, prezzo alzato (STAR)
        'Vino rosso (calice)':  {'qty': 1.5, 'price': 1.1},
        'Birra media':          {'qty': 2.5, 'price': 1.0},
        
        # --- PIZZE (Il motore del locale) ---
        'Margherita':           {'qty': 3.0, 'price': 1.0}, # PLOWHORSE (Vende tantissimo)
        'Diavola':              {'qty': 0.6, 'price': 1.0}, # DOG (Vende poco)
        'Marinara':             {'qty': 0.2, 'price': 1.0}, # DOG estremo (Non la vuole nessuno)
        'Pizza gourmet tartufo':{'qty': 0.4, 'price': 1.5}, # PUZZLE (Poca vendita, prezzo altissimo)
        'Bufala e pachino':     {'qty': 1.2, 'price': 1.2}, # STAR potenziale
        
        # --- CUCINA ROMANA (I Classici) ---
        'Carbonara':            {'qty': 2.2, 'price': 1.0}, # STAR/PLOWHORSE
        'Amatriciana':          {'qty': 1.8, 'price': 1.0},
        'Cacio e pepe':         {'qty': 1.5, 'price': 1.1}, # Leggero hype
        
        # --- SECONDI E LUSSO (Rischio alto) ---
        'Branzino al forno':    {'qty': 0.8, 'price': 1.3}, # PUZZLE (Prezzo alto, vendita media)
        'Tagliata di manzo':    {'qty': 0.7, 'price': 1.4}, # PUZZLE
        'Cotoletta alla milanese': {'qty': 1.5, 'price': 1.1}, # Piatto sicuro
        
        # --- DOLCI ---
        'Tiramisù':             {'qty': 2.0, 'price': 1.0}, # Best seller
        'Panna cotta':          {'qty': 0.5, 'price': 1.0}, # Flop
    }

    # B. WASTE SCENARIO: (Moltiplicatore spreco)
    # Logica: 
    # - Prodotti freschi (Mozzarella, Pesce) = Spreco Alto
    # - Prodotti secchi (Farina, Olio) = Spreco Basso
    
    waste_scenario = {
        # --- ALTO RISCHIO (Deteriorabili) ---
        'Mozzarella (kg)':          3.5, # Scade subito, si butta l'acqua
        'Pesce branzino (kg)':      4.0, # Se non lo vendi oggi, lo butti (Costo enorme)
        'Verdure miste (kg)':       2.5, # Appassiscono
        'Prosciutto crudo (kg)':    1.5, # Si ossida se tagliato prima
        
        # --- MEDIO RISCHIO ---
        'Carne manzo (kg)':         1.2,
        'Salame piccante (kg)':     1.8, # Spreco alto che ucciderà la Diavola
        'Funghi porcini (kg)':      1.3,
        
        # --- BASSO RISCHIO (Stabili) ---
        'Farina tipo 00 (kg)':      0.2, # Quasi zero spreco
        'Olio EVO (lt)':            0.1, # Non scade mai
        'Pomodoro San Marzano (kg)':0.3, # In scatola
    }