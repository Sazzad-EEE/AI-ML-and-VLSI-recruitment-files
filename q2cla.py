"""
Design 2: Self-Biased Cascode Current Reference
Complete Analysis, Design, and Simulation (Behavioral / Assumption-Based)
=========================================================
Circuit: Beta-multiplier with PMOS/NMOS cascode mirrors (modeled behaviorally)
Target: Iref1 = Iref2 = 10 uA, VDD = 2.0 to 3.0 V

This version includes:
✅ Correct beta-multiplier factor a = (1 - 1/sqrt(K)) everywhere
✅ Consistent ΔVGS = I*R check
✅ Consistent constant-gm: gm = 2*a/R and gm*R = 2*a
✅ Improved headroom estimate (rough but realistic)
✅ FIXED Windows image saving:
   - forces output folder creation
   - uses safe path handling (no backslash escape bugs)
   - prints absolute save path + existence check
✅ Same plots + SPICE netlist generation

NOTE:
- This is NOT PDK-accurate SPICE. It is a compact equation model for coursework/analysis.
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# OUTPUT DIRECTORY (Windows-safe)
# ============================================================
OUTPUT_DIR = r"V:\DT 2"  # <-- change if you want
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# PROCESS PARAMETERS (calibrated from your simulation point)
# ============================================================
I_sim   = 394e-6    # A  (calibration current)
R_sim   = 2.5e3     # ohm (calibration resistor)
K_ratio = 4         # size ratio (M4A/M3A)
VT_n    = 0.5       # V (assumed)
VT_p    = 0.5       # V magnitude (assumed)

WL_ref  = 10        # "unit" W/L for M3A (arbitrary reference scaling)

# Correct beta-multiplier factor:
a = (1.0 - 1.0 / np.sqrt(K_ratio))   # IMPORTANT

# Ideal beta-multiplier: I = 2*a^2 / (beta_WL * R^2)
# => beta_WL = 2*a^2 / (I*R^2)
KPn_WL_eff = 2.0 * (a**2) / (I_sim * (R_sim**2))     # A/V^2 for (W/L = WL_ref)
KPn_eff    = KPn_WL_eff / WL_ref                      # A/V^2 per "1" W/L

print("="*65)
print("  DESIGN 2: CASCODE CURRENT REFERENCE - CALIBRATED ANALYSIS")
print("="*65)
print(f"\nCalibrated from simulation (R={R_sim/1e3:.1f}k, Iref={I_sim*1e6:.0f}uA):")
print(f"  a = (1 - 1/sqrt(K)) = {a:.3f}")
print(f"  Effective KP_n = {KPn_eff*1e6:.2f} uA/V^2")
print(f"  KP_n * (W/L)   = {KPn_WL_eff*1e6:.2f} uA/V^2")

# ============================================================
# DESIGN EQUATIONS (target 10 uA)
# ============================================================
I_target = 10e-6

# From I = 2*a^2/(KPn_WL*R^2) => R = sqrt(2*a^2/(I*KPn_WL))
R_design = np.sqrt(2.0 * (a**2) / (I_target * KPn_WL_eff))

# Overdrives:
Veff_M3A = np.sqrt(2.0 * I_target / KPn_WL_eff)                 # Vov for "unit" NMOS
Veff_M4A = np.sqrt(2.0 * I_target / (K_ratio * KPn_WL_eff))     # Vov for Kx device

Vgs_M3A  = VT_n + Veff_M3A
Vgs_M4A  = VT_n + Veff_M4A

delta_Vgs = Vgs_M3A - Vgs_M4A
IR_drop   = I_target * R_design

# gm of M3A from square law: gm = 2I/Vov
gm_ref   = 2.0 * I_target / Veff_M3A

# constant-gm relation: gm ≈ 2*a/R
gm_const = 2.0 * a / R_design

print(f"\n{'='*65}")
print(f"  DESIGN PARAMETERS FOR Iref = 10 uA")
print(f"{'='*65}")
print(f"  K ratio (M4A/M3A)  = {K_ratio}")
print(f"  R_design           = {R_design/1e3:.3f} kOhm")
print(f"  Veff_M3A           = {Veff_M3A*1e3:.1f} mV")
print(f"  Veff_M4A           = {Veff_M4A*1e3:.1f} mV")
print(f"  Vgs_M3A            = {Vgs_M3A:.3f} V")
print(f"  Vgs_M4A            = {Vgs_M4A:.3f} V")
print(f"  delta_Vgs          = {delta_Vgs*1e3:.1f} mV  (= Iref*R = {IR_drop*1e3:.1f} mV, check)")
print(f"  gm (from squarelaw)= {gm_ref*1e6:.2f} uA/V = {gm_ref*1e3:.4f} mS")
print(f"  gm (const-gm)      = 2*a/R = {gm_const*1e3:.4f} mS")
print(f"  gm x R             = {gm_ref*R_design:.3f} (expected: 2*a = {2*a:.3f})")

# ============================================================
# TRANSISTOR SIZING (illustrative)
# ============================================================
WL_M3A = WL_ref
WL_M4A = K_ratio * WL_ref

# PMOS mirrors sized stronger to reduce Vovp (illustrative choice)
WL_M1A = WL_ref * 2
WL_M2A = WL_ref * 2

# Cascodes: choose similar scale to their branch devices
WL_M1C = WL_M2C = WL_M1A
WL_M3C = WL_M4C = WL_M4A

VDD_nom = 2.5

# Rough PMOS strength assumption (illustrative)
KPp_eff = KPn_eff * 0.4

# PMOS overdrive estimates
Veff_M1A = np.sqrt(2.0 * I_target / (KPp_eff * WL_M1A))
Veff_M1C = Veff_M1A

# Headroom estimate (rough, saturation-only style)
Vov_n  = Veff_M3A
Vov_nC = Veff_M3A      # assume similar for NMOS cascode
Vov_p  = Veff_M1A
Vov_pC = Veff_M1C
VDD_headroom = (Vov_p + Vov_pC) + (Vov_n + Vov_nC) + IR_drop

print(f"\n{'='*65}")
print(f"  TRANSISTOR SIZES (illustrative)")
print(f"{'='*65}")
print(f"  M1A, M2A (PMOS core mirror):    W/L = {WL_M1A}/1")
print(f"  M1C, M2C (PMOS cascode):        W/L = {WL_M1C}/1")
print(f"  M3A      (NMOS ref, K=1):       W/L = {WL_M3A}/1")
print(f"  M3C      (NMOS cascode ref):    W/L = {WL_M3C}/1")
print(f"  M4A      (NMOS mirror, K=4):    W/L = {WL_M4A}/1")
print(f"  M4C      (NMOS mirror cascode): W/L = {WL_M4C}/1")
print(f"  R        (current setter):      R   = {R_design/1e3:.2f} kOhm")
print(f"  Estimated min VDD (rough):      ~{VDD_headroom:.2f} V")

# ============================================================
# SIMULATION 1: VDD SWEEP (behavioral CLM sensitivity)
# ============================================================
lam_no_cas  = 0.08      # larger effective lambda
lam_cascode = 0.0004    # smaller effective lambda

VDD_range = np.linspace(2.0, 3.0, 100)

def beta_mult_current(VDD, R, KPn_WL, K, lam, VT=0.5):
    """
    Behavioral iterative solve:
    - Uses square-law to compute Vgs3, Vgs4 from I guess
    - Uses delta Vgs across R to update I
    - Adds a crude CLM effect via (1 + lam*VDS_eff)
    """
    I = I_target
    for _ in range(200):
        Vov3 = np.sqrt(max(2.0*I / KPn_WL, 0.0))
        Vov4 = np.sqrt(max(2.0*I / (K*KPn_WL), 0.0))
        Vgs3 = VT + Vov3
        Vgs4 = VT + Vov4

        V_R = Vgs3 - Vgs4
        I_R = V_R / R

        VDS_eff = 0.4 * VDD
        I_with_lam = I_R * (1.0 + lam * VDS_eff)

        I_new = 0.5*I + 0.5*I_with_lam
        if abs(I_new - I) < 1e-14:
            break
        I = I_new

    return max(I, 1e-12)

Iref_no_cas  = np.array([beta_mult_current(v, R_design, KPn_WL_eff, K_ratio, lam_no_cas)  for v in VDD_range])
Iref_cascode = np.array([beta_mult_current(v, R_design, KPn_WL_eff, K_ratio, lam_cascode) for v in VDD_range])

var_no_cas  = (Iref_no_cas.max()  - Iref_no_cas.min())  / Iref_no_cas.mean()  * 100.0
var_cascode = (Iref_cascode.max() - Iref_cascode.min()) / Iref_cascode.mean() * 100.0

print(f"\n{'='*65}")
print(f"  VDD SENSITIVITY (2.0 to 3.0 V)")
print(f"{'='*65}")
print(f"  Without cascodes: {var_no_cas:.2f}% variation")
print(f"  With cascodes:    {var_cascode:.3f}% variation")
print(f"  Improvement:      {var_no_cas/max(var_cascode,1e-12):.0f}x better")

# ============================================================
# SIMULATION 2: TEMPERATURE SWEEP (mu(T), R(T); Vth drift as non-ideality)
# ============================================================
T_range   = np.linspace(-40, 125, 100)
T_nom     = 25.0
T_K_range = T_range + 273.15
T_K_nom   = T_nom + 273.15

alpha_VT = 2e-3  # V/°C (illustrative)

TC_values = [0, 1000, 2000, 3000]
colors_tc = ["#d62728", "#ff7f0e", "#2ca02c", "#1f77b4"]

Iref_temp_dict = {}
for TC in TC_values:
    Iref_T = []
    for T, T_K in zip(T_range, T_K_range):
        mu_factor = (T_K_nom / T_K)**1.5
        VT_T      = VT_n - alpha_VT*(T - T_nom)
        R_T       = R_design * (1.0 + TC*1e-6*(T - T_nom))
        KPn_T     = KPn_WL_eff * mu_factor

        I = I_target
        for _ in range(200):
            Vgs3 = VT_T + np.sqrt(max(2.0*I / KPn_T, 0.0))
            Vgs4 = VT_T + np.sqrt(max(2.0*I / (K_ratio*KPn_T), 0.0))
            V_R  = Vgs3 - Vgs4
            I_new = max(V_R / R_T, 1e-12)
            if abs(I_new - I) < 1e-15:
                break
            I = 0.5*I + 0.5*I_new

        Iref_T.append(I)

    Iref_temp_dict[TC] = np.array(Iref_T)

TC_fine = np.arange(0, 5000, 50)
variations = []
for TC in TC_fine:
    Iref_T = []
    for T, T_K in zip(T_range, T_K_range):
        mu_factor = (T_K_nom / T_K)**1.5
        VT_T      = VT_n - alpha_VT*(T - T_nom)
        R_T       = R_design * (1.0 + TC*1e-6*(T - T_nom))
        KPn_T     = KPn_WL_eff * mu_factor

        I = I_target
        for _ in range(100):
            Vgs3 = VT_T + np.sqrt(max(2.0*I / KPn_T, 0.0))
            Vgs4 = VT_T + np.sqrt(max(2.0*I / (K_ratio*KPn_T), 0.0))
            V_R  = Vgs3 - Vgs4
            I_new = max(V_R / R_T, 1e-12)
            if abs(I_new - I) < 1e-15:
                break
            I = 0.5*I + 0.5*I_new

        Iref_T.append(I)

    arr = np.array(Iref_T)
    variations.append((arr.max() - arr.min()) / arr.mean() * 100.0)

opt_TC = int(TC_fine[int(np.argmin(variations))])
min_var = float(np.min(variations))

print(f"\n{'='*65}")
print(f"  TEMPERATURE ANALYSIS (-40 to 125 C)")
print(f"{'='*65}")
for TC in TC_values:
    arr = Iref_temp_dict[TC]
    v = (arr.max()-arr.min())/arr.mean()*100.0
    print(f"  TC = {TC:4d} ppm/C -> Iref variation = {v:.2f}%")
print(f"  Optimal TC ≈ {opt_TC} ppm/C -> minimum variation ≈ {min_var:.3f}% (behavioral)")

# ============================================================
# SIMULATION 3: gm CONSTANCY
# ============================================================
gm_theory = 2.0 * a / R_design

gm_vs_VDD = np.array([
    (2.0*beta_mult_current(v, R_design, KPn_WL_eff, K_ratio, lam_cascode))
    / np.sqrt(max(2.0*beta_mult_current(v, R_design, KPn_WL_eff, K_ratio, lam_cascode) / KPn_WL_eff, 1e-30))
    for v in VDD_range
])

gm_vs_T = []
for T in T_range:
    R_T = R_design * (1.0 + opt_TC*1e-6*(T - T_nom))
    gm_vs_T.append(2.0 * a / R_T)
gm_vs_T = np.array(gm_vs_T)

gm_VDD_var = (gm_vs_VDD.max()-gm_vs_VDD.min())/gm_vs_VDD.mean()*100.0
gm_T_var   = (gm_vs_T.max()-gm_vs_T.min())/gm_vs_T.mean()*100.0

print(f"\n{'='*65}")
print(f"  gm CONSTANCY")
print(f"{'='*65}")
print(f"  gm (theory) = 2*a/R = {gm_theory*1e6:.2f} uA/V = {gm_theory*1e3:.4f} mS")
print(f"  gm variation vs VDD (with cascodes): {gm_VDD_var:.3f}%")
print(f"  gm variation vs T   (opt TC):        {gm_T_var:.2f}%")
print(f"  gm x R = {gm_theory*R_design:.3f}  (expected: 2*a = {2*a:.3f})")

# ============================================================
# BIAS VOLTAGE OUTPUTS (illustrative estimates)
# ============================================================
KPp_eff = KPn_eff * 0.4
Vsg_M1A = VT_p + np.sqrt(max(2.0*I_target/(KPp_eff*WL_M1A), 0.0))
Vsg_M1C = Vsg_M1A

Vbiasp = VDD_nom - Vsg_M1C
Vpcas  = VDD_nom - Vsg_M1C - Vsg_M1A
Vbiasn = Vgs_M3A
Vncas  = Vgs_M3A + Veff_M3A

print(f"\n{'='*65}")
print(f"  BIAS VOLTAGE OUTPUTS (VDD = {VDD_nom} V) [illustrative]")
print(f"{'='*65}")
print(f"  Vbiasp = {Vbiasp:.3f} V  (PMOS cascode gate est.)")
print(f"  Vpcas  = {Vpcas:.3f} V  (PMOS mirror gate est.)")
print(f"  Vncas  = {Vncas:.3f} V  (NMOS cascode gate est.)")
print(f"  Vbiasn = {Vbiasn:.3f} V  (NMOS bias gate = Vgs_M3A)")

# ============================================================
# OUTPUT IMPEDANCE & LINE REGULATION (very rough)
# ============================================================
gm_n = gm_theory
ro_n = 1.0 / max(lam_no_cas * I_target, 1e-30)
ro_p = ro_n * 0.7

Rout_n = gm_n * ro_n**2
Rout_p = gm_n * ro_p**2
Rout   = (Rout_n * Rout_p) / max(Rout_n + Rout_p, 1e-30)

sens = 1.0 / max(Rout, 1e-30)

print(f"\n{'='*65}")
print(f"  OUTPUT IMPEDANCE & PSRR ESTIMATION (very rough)")
print(f"{'='*65}")
print(f"  ro_n (single transistor)     = {ro_n/1e3:.1f} kOhm")
print(f"  Rout_n (NMOS cascode)        = {Rout_n/1e6:.1f} MOhm")
print(f"  Rout_p (PMOS cascode)        = {Rout_p/1e6:.1f} MOhm")
print(f"  Total Rout (parallel)        = {Rout/1e6:.2f} MOhm")
print(f"  dIref/dVDD                   = {sens*1e12:.2f} pA/V")
print(f"  Line regulation              = {sens/max(I_target,1e-30)*100:.4f}% per V")

# ============================================================
# PLOTTING
# ============================================================
fig = plt.figure(figsize=(16, 12))
fig.patch.set_facecolor("white")
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.38, wspace=0.35)
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
ax3 = fig.add_subplot(gs[0, 2])
ax4 = fig.add_subplot(gs[1, 0])
ax5 = fig.add_subplot(gs[1, 1])
ax6 = fig.add_subplot(gs[1, 2])

for ax in [ax1, ax2, ax3, ax4, ax5, ax6]:
    ax.set_facecolor("white")
    ax.tick_params(colors="black", labelsize=8)
    ax.xaxis.label.set_color("black")
    ax.yaxis.label.set_color("black")
    ax.title.set_color("#1a1a2e")
    for sp in ax.spines.values():
        sp.set_color("#cccccc")

def ax_style(ax, title, xlabel, ylabel):
    ax.set_title(title, fontsize=9, fontweight="bold", pad=6)
    ax.set_xlabel(xlabel, fontsize=8)
    ax.set_ylabel(ylabel, fontsize=8)
    ax.grid(True, color="#dddddd", alpha=0.8, linestyle="--", linewidth=0.5)
    ax.legend(fontsize=7, framealpha=0.8, facecolor="white", edgecolor="#cccccc", labelcolor="black")

ax1.plot(VDD_range, Iref_no_cas*1e6,  lw=1.8, label=f"No cascodes ({var_no_cas:.2f}% var)")
ax1.plot(VDD_range, Iref_cascode*1e6, lw=2.2, label=f"With cascodes ({var_cascode:.3f}% var)")
ax1.axhline(10, lw=1, ls="--", alpha=0.7, label="Target 10 uA")
ax_style(ax1, "Iref vs VDD (Supply Rejection)", "VDD (V)", "Iref (uA)")

ax2.axhline(10, lw=1, ls="--", alpha=0.7, label="Target 10 uA")
for TC in TC_values:
    arr = Iref_temp_dict[TC]
    v = (arr.max()-arr.min())/arr.mean()*100.0
    ax2.plot(T_range, arr*1e6, lw=1.8, label=f"TC={TC} ppm ({v:.1f}%)")
ax_style(ax2, "Iref vs Temperature", "Temperature (C)", "Iref (uA)")

ax3.plot(VDD_range, gm_vs_VDD*1e3, lw=2.2, label="gm vs VDD")
ax3.axhline(gm_theory*1e3, lw=1, ls="--", label=f"Theory: {gm_theory*1e3:.3f} mS")
ax_style(ax3, "gm Constancy vs VDD", "VDD (V)", "gm (mS)")
ax3.text(0.05, 0.15, f"Variation: {gm_VDD_var:.3f}%", transform=ax3.transAxes,
         color="black", fontsize=8, fontfamily="monospace")

ax4.plot(T_range, gm_vs_T*1e3, lw=2.2, label=f"gm vs T (TC={opt_TC} ppm)")
ax4.axhline(gm_theory*1e3, lw=1, ls="--", label="Theory")
ax_style(ax4, "gm Constancy vs Temperature", "Temperature (C)", "gm (mS)")
ax4.text(0.05, 0.15, f"Variation: {gm_T_var:.2f}%", transform=ax4.transAxes,
         color="black", fontsize=8, fontfamily="monospace")

ax5.plot(TC_fine, variations, lw=2)
ax5.axvline(opt_TC, lw=1.5, ls="--", label=f"Optimal TC = {opt_TC} ppm/C")
ax5.scatter([opt_TC], [min_var], s=80, zorder=5)
ax5.text(opt_TC+100, min_var+0.05, f"{min_var:.2f}%", fontsize=8)
ax_style(ax5, "Optimal Resistor TC", "Resistor TC (ppm/C)", "Iref Variation (%)")

ax6.axis("off")
summary = [
    ["Parameter", "Value", "Unit"],
    ["Iref target", "10", "uA"],
    ["R design", f"{R_design/1e3:.2f}", "kOhm"],
    ["K ratio", f"{K_ratio}", "-"],
    ["a = 1-1/sqrt(K)", f"{a:.3f}", "-"],
    ["M3A W/L", f"{WL_M3A}/1", "-"],
    ["M4A W/L", f"{WL_M4A}/1", "-"],
    ["M1A W/L", f"{WL_M1A}/1", "-"],
    ["gm (theory)", f"{gm_theory*1e3:.3f}", "mS"],
    ["gm x R", f"{gm_theory*R_design:.3f}", "-"],
    ["Rout (rough)", f"{Rout/1e6:.1f}", "MOhm"],
    ["VDD sensitivity", f"{var_cascode:.3f}", "% (2-3V)"],
    ["Opt resistor TC", f"{opt_TC}", "ppm/C"],
    ["Vbiasp", f"{Vbiasp:.2f}", "V"],
    ["Vpcas", f"{Vpcas:.2f}", "V"],
    ["Vncas", f"{Vncas:.2f}", "V"],
    ["Vbiasn", f"{Vbiasn:.2f}", "V"],
]
x_pos = [0.02, 0.47, 0.77]
ax6.set_xlim(0, 1)
ax6.set_ylim(0, 1)
ax6.set_title("Design Summary", fontsize=9, fontweight="bold", pad=6)
row_h = 1.0 / len(summary)
for i, row in enumerate(summary):
    y = 1 - (i+0.5)*row_h
    bg = "#e8eaf0" if i == 0 else ("#f5f7ff" if i % 2 == 0 else "white")
    rect = plt.Rectangle((0, 1-(i+1)*row_h), 1, row_h, color=bg, transform=ax6.transAxes, clip_on=False)
    ax6.add_patch(rect)
    for j, (txt, xp) in enumerate(zip(row, x_pos)):
        col = "black" if i != 0 else "#1a1a2e"
        ax6.text(xp, y, txt, transform=ax6.transAxes, fontsize=7,
                 color=col, fontfamily="monospace", va="center")

fig.suptitle("Design 2: Self-Biased Cascode Current Reference — Simulation Results",
             fontsize=12, fontweight="bold", color="black", y=0.98)

# --------- SAVE FIGURE (Windows-safe absolute path) ----------
out_plot = os.path.join(OUTPUT_DIR, "design2_simulation_results_fixed.png")
plt.savefig(out_plot, dpi=150, bbox_inches="tight", facecolor="white")
plt.close()

print("\nCWD:", os.getcwd())
print("Plot saved to:", os.path.abspath(out_plot))
print("Exists?", os.path.exists(out_plot))

# ============================================================
# SPICE NETLIST OUTPUT (illustrative; replace models with PDK)
# ============================================================
out_spice = os.path.join(OUTPUT_DIR, "design2_cascode_ref_fixed.sp")

spice = f"""* ============================================================
* Design 2: Self-Biased Cascode Current Reference (Illustrative)
* Generated from Python design script (equation-calibrated)
* Target: Iref1 = Iref2 = 10 uA, VDD = 2.0 - 3.0 V
* ============================================================

.param VDD_val=2.5
.param R_val={R_design:.0f}

VDD VDD 0 DC {{VDD_val}}

* -------- PMOS CASCODE MIRROR --------
M1C net_m1a Vbiasp VDD VDD PMOS W={WL_M1A}u L=1u
M1A Vbias  Vbias  net_m1a VDD PMOS W={WL_M1A}u L=1u

M2C net_m2a Vbiasp VDD VDD PMOS W={WL_M1A}u L=1u
M2A net_ref Vbias  net_m2a VDD PMOS W={WL_M1A}u L=1u

* -------- NMOS CASCODE MIRROR --------
M3C net_m1a Vncas Vbiasn 0 NMOS W={WL_M4A}u L=1u
M3A Vbiasn Vbiasn 0      0 NMOS W={WL_M3A}u L=1u

M4C net_ref Vncas net_casc 0 NMOS W={WL_M4A}u L=1u
M4A net_casc Vbiasn net_R   0 NMOS W={WL_M4A}u L=1u

R1 net_R 0 {{R_val}}

* -------- STARTUP (simple) --------
Mstart  Vbias_st VDD VDD VDD PMOS W=1u L=10u
Mstart2 Vbias    Vbias_st 0 0 NMOS W=2u L=1u
Rstart  Vbias_st Vbias 10Meg

* -------- MODELS (illustrative) --------
.model NMOS NMOS (LEVEL=3 VTO={VT_n} KP={KPn_eff*1e6:.3f}u LAMBDA={lam_no_cas} GAMMA=0.5 PHI=0.6)
.model PMOS PMOS (LEVEL=3 VTO=-{VT_p} KP={KPn_eff*1e6*0.4:.3f}u LAMBDA={lam_no_cas} GAMMA=0.5 PHI=0.6)

.op
.dc VDD VDD_val 2.0 3.0 0.01

.end
"""

with open(out_spice, "w", encoding="utf-8") as f:
    f.write(spice)

print("SPICE saved to:", os.path.abspath(out_spice))
print("Exists?", os.path.exists(out_spice))

print("\n" + "="*65)
print("  FINAL DESIGN SUMMARY")
print("="*65)
print(f"""
  Output folder: {OUTPUT_DIR}

  R = {R_design/1e3:.2f} kOhm
  K = {K_ratio}
  a = {a:.3f}

  delta_Vgs = {delta_Vgs*1e3:.1f} mV
  Iref*R    = {IR_drop*1e3:.1f} mV

  gm(theory) = {gm_theory*1e3:.4f} mS
  gm*R       = {gm_theory*R_design:.3f} (expected 2*a = {2*a:.3f})

  Plot:  {out_plot}
  SPICE: {out_spice}
""")
print("="*65)