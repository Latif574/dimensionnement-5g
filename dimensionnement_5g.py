import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math

# =============================================
# MOTEUR DE CALCUL
# =============================================

def calculer_bilan_et_dimensionnement(params):
    """
    params : dictionnaire contenant toutes les valeurs saisies
    Retourne : un dictionnaire avec tous les résultats
    """
    # Extraction des paramètres
    f = params['frequence']          # MHz
    BW = params['bande_passante']    # MHz
    P_tx = params['puissance']       # dBm
    G_BS = params['gain_antenne']    # dBi
    G_UT = params['gain_ut']         # dBi
    L_cable = params['perte_cable']  # dB
    h_BS = params['hauteur_bs']      # m
    h_UT = params['hauteur_ut']      # m
    SINR_target = params['sinr']     # dB
    M_shadow = params['marge_shadow']  # dB
    M_pen = params['marge_penetration'] # dB
    M_interf = params['marge_interf']   # dB
    surface_totale = params['surface']  # km²
    n_utilisateurs = params['nb_utilisateurs']
    debit_user = params['debit_user']   # Mbps
    activite = params['activite']
    efficacite_spectrale = params['efficacite_spectrale']  # bits/s/Hz
    nb_couches_mimo = params['couches_mimo']
    overhead = params['overhead']  # en % (ex: 0.30)

    # 1. Calcul du bruit thermique N0 (dBm)
    k = 1.38e-23
    T = 290
    BW_hz = BW * 1e6
    N0 = 10 * math.log10(k * T * BW_hz * 1000)  # dBm

    # 2. Bilan de liaison (MAPL sans marges)
    MAPL = P_tx - L_cable + G_BS + G_UT - (N0 + SINR_target)

    # 3. Application des marges
    MAPL_effectif = MAPL - M_shadow - M_pen - M_interf

    # 4. Modèle de propagation 3GPP UMa (LOS) : PL = 28 + 22*log10(d) + 20*log10(fc)
    fc_GHz = f / 1000.0
    # On isole d :
    # MAPL = 28 + 22*log10(d) + 20*log10(fc)  => log10(d) = (MAPL - 28 - 20*log10(fc)) / 22
    d_max = math.pow(10, (MAPL_effectif - 28.0 - 20 * math.log10(fc_GHz)) / 22.0)

    # 5. Surface couverte par un site (en km²)
    # On considère une cellule circulaire de rayon d_max (en mètres)
    rayon_km = d_max / 1000.0
    surface_par_site = math.pi * (rayon_km ** 2)
    N_cov = surface_totale / surface_par_site
    if N_cov < 1:
        N_cov = 1  # au moins un site

    # 6. Capacité d'un site (débit total en Mbps)
    debit_site = BW * efficacite_spectrale * nb_couches_mimo * (1 - overhead)
    # Nombre d'utilisateurs supportés par site
    n_users_par_site = (debit_site * 1000) / (debit_user * activite)
    if n_users_par_site < 1:
        n_users_par_site = 1
    N_cap = n_utilisateurs / n_users_par_site
    if N_cap < 1:
        N_cap = 1

    # 7. Nombre final de sites
    N_final = max(N_cov, N_cap)

    # 8. Résultats intermédiaires (pour le rapport)
    resultats = {
        'N0_dBm': round(N0, 2),
        'MAPL_dB': round(MAPL, 2),
        'MAPL_effectif_dB': round(MAPL_effectif, 2),
        'd_max_m': round(d_max, 2),
        'd_max_km': round(rayon_km, 3),
        'surface_par_site_km2': round(surface_par_site, 3),
        'N_cov': round(N_cov, 2),
        'N_cap': round(N_cap, 2),
        'N_final': round(N_final, 2),   # On arrondit à l'entier supérieur pour le déploiement
        'N_final_arrondi': math.ceil(N_final),
        'debit_site_Mbps': round(debit_site, 2),
        'n_users_par_site': round(n_users_par_site, 0),
        'fc_GHz': fc_GHz
    }
    return resultats


# =============================================
# INTERFACE UTILISATEUR (Tkinter)
# =============================================

class Application5G:
    def __init__(self, root):
        self.root = root
        self.root.title("Dimensionnement NG-RAN 5G")
        self.root.geometry("850x750")
        self.root.resizable(False, False)

        # Variables de contrôle (valeurs par défaut réalistes)
        self.var_freq = tk.DoubleVar(value=3500.0)
        self.var_bw = tk.DoubleVar(value=100.0)
        self.var_puiss = tk.DoubleVar(value=46.0)
        self.var_gain_bs = tk.DoubleVar(value=25.0)   # avec beamforming 64T64R
        self.var_gain_ut = tk.DoubleVar(value=0.0)
        self.var_cable = tk.DoubleVar(value=2.0)
        self.var_hbs = tk.DoubleVar(value=30.0)
        self.var_hut = tk.DoubleVar(value=1.5)
        self.var_sinr = tk.DoubleVar(value=18.0)
        self.var_shadow = tk.DoubleVar(value=9.0)
        self.var_pen = tk.DoubleVar(value=15.0)
        self.var_interf = tk.DoubleVar(value=2.0)
        self.var_surface = tk.DoubleVar(value=10.0)   # km²
        self.var_nb_users = tk.IntVar(value=500)
        self.var_debit_user = tk.DoubleVar(value=50.0)
        self.var_activite = tk.DoubleVar(value=0.5)
        self.var_eff_spect = tk.DoubleVar(value=4.5)
        self.var_couches = tk.IntVar(value=4)
        self.var_overhead = tk.DoubleVar(value=0.30)

        # Widgets
        self.creer_interface()

    def creer_interface(self):
        # Cadre principal avec scrolling (optionnel)
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Titre
        ttk.Label(main_frame, text="Paramètres de dimensionnement 5G", font=('Arial', 14, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)

        # --- Section 1 : Généraux ---
        ttk.Label(main_frame, text="1. Paramètres généraux", font=('Arial', 12, 'bold')).grid(row=1, column=0, columnspan=2, sticky='w', pady=(10,5))

        row = 2
        self.ajouter_ligne(main_frame, row, "Fréquence porteuse (MHz) :", self.var_freq)
        row += 1
        self.ajouter_ligne(main_frame, row, "Bande passante (MHz) :", self.var_bw)
        row += 1
        self.ajouter_ligne(main_frame, row, "Hauteur gNB (m) :", self.var_hbs)
        row += 1
        self.ajouter_ligne(main_frame, row, "Hauteur UE (m) :", self.var_hut)
        row += 1
        self.ajouter_ligne(main_frame, row, "Gain antenne gNB (dBi) :", self.var_gain_bs)
        row += 1
        self.ajouter_ligne(main_frame, row, "Gain antenne UE (dBi) :", self.var_gain_ut)
        row += 1
        self.ajouter_ligne(main_frame, row, "Pertes dans les câbles (dB) :", self.var_cable)

        # --- Section 2 : Couverture ---
        row += 1
        ttk.Label(main_frame, text="2. Paramètres de couverture (Link Budget)", font=('Arial', 12, 'bold')).grid(row=row, column=0, columnspan=2, sticky='w', pady=(10,5))
        row += 1
        self.ajouter_ligne(main_frame, row, "Puissance d'émission (dBm) :", self.var_puiss)
        row += 1
        self.ajouter_ligne(main_frame, row, "SINR cible (dB) :", self.var_sinr)
        row += 1
        self.ajouter_ligne(main_frame, row, "Marge shadowing (dB) :", self.var_shadow)
        row += 1
        self.ajouter_ligne(main_frame, row, "Marge pénétration (dB) :", self.var_pen)
        row += 1
        self.ajouter_ligne(main_frame, row, "Marge interférences (dB) :", self.var_interf)

        # --- Section 3 : Capacité et trafic ---
        row += 1
        ttk.Label(main_frame, text="3. Paramètres de capacité et trafic", font=('Arial', 12, 'bold')).grid(row=row, column=0, columnspan=2, sticky='w', pady=(10,5))
        row += 1
        self.ajouter_ligne(main_frame, row, "Surface totale à couvrir (km²) :", self.var_surface)
        row += 1
        self.ajouter_ligne(main_frame, row, "Nombre total d'utilisateurs :", self.var_nb_users)
        row += 1
        self.ajouter_ligne(main_frame, row, "Débit moyen par utilisateur (Mbps) :", self.var_debit_user)
        row += 1
        self.ajouter_ligne(main_frame, row, "Facteur d'activité :", self.var_activite)
        row += 1
        self.ajouter_ligne(main_frame, row, "Efficacité spectrale (bits/s/Hz) :", self.var_eff_spect)
        row += 1
        self.ajouter_ligne(main_frame, row, "Nombre de couches MIMO :", self.var_couches)
        row += 1
        self.ajouter_ligne(main_frame, row, "Surcharge (Overhead) :", self.var_overhead)

        # --- Boutons ---
        row += 1
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        ttk.Button(btn_frame, text="Lancer le calcul", command=self.lancer_calcul).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Exporter le rapport", command=self.exporter_rapport).pack(side=tk.LEFT, padx=10)

        # --- Zone d'affichage des résultats ---
        row += 1
        ttk.Label(main_frame, text="Résultats :", font=('Arial', 12, 'bold')).grid(row=row, column=0, columnspan=2, sticky='w', pady=(10,0))
        row += 1
        self.txt_resultats = tk.Text(main_frame, height=15, width=90, wrap=tk.WORD, state=tk.DISABLED)
        self.txt_resultats.grid(row=row, column=0, columnspan=2, pady=5)

        # Stockage des résultats pour l'export
        self.derniers_resultats = None

    def ajouter_ligne(self, parent, row, label, variable):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky='e', padx=5, pady=2)
        entry = ttk.Entry(parent, textvariable=variable, width=15)
        entry.grid(row=row, column=1, sticky='w', padx=5, pady=2)

    def lancer_calcul(self):
        try:
            # Récupération des paramètres dans un dictionnaire
            params = {
                'frequence': self.var_freq.get(),
                'bande_passante': self.var_bw.get(),
                'puissance': self.var_puiss.get(),
                'gain_antenne': self.var_gain_bs.get(),
                'gain_ut': self.var_gain_ut.get(),
                'perte_cable': self.var_cable.get(),
                'hauteur_bs': self.var_hbs.get(),
                'hauteur_ut': self.var_hut.get(),
                'sinr': self.var_sinr.get(),
                'marge_shadow': self.var_shadow.get(),
                'marge_penetration': self.var_pen.get(),
                'marge_interf': self.var_interf.get(),
                'surface': self.var_surface.get(),
                'nb_utilisateurs': self.var_nb_users.get(),
                'debit_user': self.var_debit_user.get(),
                'activite': self.var_activite.get(),
                'efficacite_spectrale': self.var_eff_spect.get(),
                'couches_mimo': self.var_couches.get(),
                'overhead': self.var_overhead.get()
            }

            # Calcul
            res = calculer_bilan_et_dimensionnement(params)
            self.derniers_resultats = (params, res)

            # Affichage
            self.txt_resultats.config(state=tk.NORMAL)
            self.txt_resultats.delete(1.0, tk.END)

            affichage = f"""
==================== RÉSULTATS DU DIMENSIONNEMENT 5G ====================

1. BILAN DE LIAISON
   - Bruit thermique (N0)            : {res['N0_dBm']} dBm
   - MAPL (sans marges)              : {res['MAPL_dB']} dB
   - MAPL effectif (avec marges)     : {res['MAPL_effectif_dB']} dB

2. COUVERTURE
   - Portée maximale d'une cellule   : {res['d_max_km']} km (soit {res['d_max_m']} m)
   - Surface couverte par site       : {res['surface_par_site_km2']} km²
   - Sites nécessaires (couverture)  : {res['N_cov']} sites

3. CAPACITÉ
   - Débit total d'un site           : {res['debit_site_Mbps']} Mbps
   - Utilisateurs supportés par site : {res['n_users_par_site']}
   - Sites nécessaires (capacité)    : {res['N_cap']} sites

4. RECOMMANDATION FINALE
   >>> NOMBRE DE SITES À DÉPLOYER : {res['N_final_arrondi']} sites (arrondi à l'entier supérieur)
   (Calculé à partir du max entre couverture et capacité)
"""
            self.txt_resultats.insert(tk.END, affichage)
            self.txt_resultats.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue lors du calcul :\n{str(e)}")

    def exporter_rapport(self):
        if self.derniers_resultats is None:
            messagebox.showwarning("Avertissement", "Veuillez d'abord lancer un calcul.")
            return

        params, res = self.derniers_resultats

        # Choix du fichier
        fichier = filedialog.asksaveasfilename(defaultextension=".txt",
                                               filetypes=[("Fichier texte", "*.txt"), ("Tous les fichiers", "*.*")])
        if not fichier:
            return

        try:
            with open(fichier, 'w', encoding='utf-8') as f:
                f.write("===== RAPPORT DE DIMENSIONNEMENT NG-RAN 5G =====\n\n")
                f.write("1. PARAMÈTRES D'ENTRÉE\n")
                f.write("   - Fréquence porteuse        : {} MHz\n".format(params['frequence']))
                f.write("   - Bande passante            : {} MHz\n".format(params['bande_passante']))
                f.write("   - Puissance d'émission      : {} dBm\n".format(params['puissance']))
                f.write("   - Gain antenne gNB          : {} dBi\n".format(params['gain_antenne']))
                f.write("   - Gain antenne UE           : {} dBi\n".format(params['gain_ut']))
                f.write("   - Pertes câbles             : {} dB\n".format(params['perte_cable']))
                f.write("   - Hauteur gNB               : {} m\n".format(params['hauteur_bs']))
                f.write("   - Hauteur UE                : {} m\n".format(params['hauteur_ut']))
                f.write("   - SINR cible                : {} dB\n".format(params['sinr']))
                f.write("   - Marge shadowing           : {} dB\n".format(params['marge_shadow']))
                f.write("   - Marge pénétration         : {} dB\n".format(params['marge_penetration']))
                f.write("   - Marge interférences       : {} dB\n".format(params['marge_interf']))
                f.write("   - Surface totale            : {} km²\n".format(params['surface']))
                f.write("   - Nb total d'utilisateurs   : {}\n".format(params['nb_utilisateurs']))
                f.write("   - Débit moyen par user      : {} Mbps\n".format(params['debit_user']))
                f.write("   - Facteur d'activité        : {}\n".format(params['activite']))
                f.write("   - Efficacité spectrale      : {} bits/s/Hz\n".format(params['efficacite_spectrale']))
                f.write("   - Couches MIMO              : {}\n".format(params['couches_mimo']))
                f.write("   - Surcharge (overhead)      : {}\n".format(params['overhead']))

                f.write("\n\n2. RÉSULTATS DU CALCUL\n")
                f.write("   - Bruit thermique (N0)      : {} dBm\n".format(res['N0_dBm']))
                f.write("   - MAPL (sans marges)        : {} dB\n".format(res['MAPL_dB']))
                f.write("   - MAPL effectif             : {} dB\n".format(res['MAPL_effectif_dB']))
                f.write("   - Portée maximale           : {} km ({} m)\n".format(res['d_max_km'], res['d_max_m']))
                f.write("   - Surface couverte/site     : {} km²\n".format(res['surface_par_site_km2']))
                f.write("   - Débit d'un site           : {} Mbps\n".format(res['debit_site_Mbps']))
                f.write("   - Utilisateurs/site         : {}\n".format(res['n_users_par_site']))
                f.write("   - Sites pour couverture     : {}\n".format(res['N_cov']))
                f.write("   - Sites pour capacité       : {}\n".format(res['N_cap']))

                f.write("\n\n3. CONCLUSION\n")
                f.write(f"   Le nombre de sites recommandé est de : {res['N_final_arrondi']}\n")
                f.write("   Ce nombre est basé sur le critère le plus contraignant (couverture ou capacité).\n")

            messagebox.showinfo("Succès", f"Rapport exporté avec succès vers :\n{fichier}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export : {str(e)}")


# =============================================
# LANCEMENT DE L'APPLICATION
# =============================================
if __name__ == "__main__":
    root = tk.Tk()
    app = Application5G(root)
    root.mainloop()