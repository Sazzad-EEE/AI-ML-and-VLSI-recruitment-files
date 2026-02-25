import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

V_DD = 1.0
muCox_n = 500e-6
muCox_p = 100e-6
V_A_prime = 3.0
V_tn = 0.35
V_tp = -0.35

def calculate_lambda(L):
    return 1 / (V_A_prime * L)

def nmos_current(V_DS, V_GS, W, L):
    V_ov = V_GS - V_tn
    I_D = np.zeros_like(V_DS)
    if V_ov <= 0:
        return I_D
    lam = calculate_lambda(L)
    for i, vds in enumerate(V_DS):
        if vds <= V_ov - 1e-9:
            I_D[i] = (W / L) * muCox_n * (V_ov * vds - vds**2 / 2)
        else:
            I_D[i] = (W / L) * muCox_n * (V_ov**2 / 2) * (1 + lam * (vds - V_ov))
    return I_D

def nmos_sat(V_GS, W, L):
    V_ov = V_GS - V_tn
    if V_ov <= 0:
        return 0.0
    lam = calculate_lambda(L)
    return (W / L) * muCox_n * (V_ov**2 / 2) * (1 + lam * V_tn)

def pmos_current_with_negative(V_DS, V_GS, W, L):
    V_Tp_mag = -V_tp
    V_SG = -V_GS
    V_SD = -V_DS
    V_ov = V_SG - V_Tp_mag
    I_D = np.zeros_like(V_DS)
    if V_ov <= 0:
        return I_D
    lam = calculate_lambda(L)
    for i, vsd in enumerate(V_SD):
        if vsd <= V_ov - 1e-9:
            I_D[i] = (W / L) * muCox_p * (V_ov * vsd - vsd**2 / 2)
        else:
            I_D[i] = (W / L) * muCox_p * (V_ov**2 / 2) * (1 + lam * (vsd - V_ov))
    return I_D

def pmos_sat(V_GS, W, L):
    V_SG = -V_GS
    V_ov = V_SG - (-V_tp)
    if V_ov <= 0:
        return 0.0
    lam = calculate_lambda(L)
    return (W / L) * muCox_p * (V_ov**2 / 2) * (1 + lam * (-V_tp))

fig = plt.figure(figsize=(18, 12))

ax1 = plt.subplot(2, 4, 1)
ax2 = plt.subplot(2, 4, 2)
ax3 = plt.subplot(2, 4, 3)
ax4 = plt.subplot(2, 4, 4)
ax5 = plt.subplot(2, 2, (3, 4))

V_DS = np.linspace(0, V_DD, 200)
for V_GS in [0.2, 0.5, 1.0]:
    I_D = nmos_current(V_DS, V_GS, 1, 1)
    ax1.plot(V_DS, I_D * 1e6, linewidth=2, label=f'V_GS = {V_GS}V')
ax1.set_xlabel('V_DS (V)')
ax1.set_ylabel('I_D (μA)')
ax1.set_title('(a) nMOS I_D-V_DS')
ax1.grid(True, alpha=0.3)
ax1.legend()
ax1.set_xlim(0, V_DD)
ax1.set_ylim(bottom=0)

V_GS = np.linspace(0, V_DD, 200)
I_D_vds01 = np.array([nmos_current(np.array([0.1]), vgs, 1, 1)[0] for vgs in V_GS])
I_D_vds_eq_vgs = np.array([nmos_sat(vgs, 1, 1) for vgs in V_GS])
ax2.plot(V_GS, I_D_vds01 * 1e6, 'b-', linewidth=2, label='V_DS = 0.1V')
ax2.plot(V_GS, I_D_vds_eq_vgs * 1e6, 'r-', linewidth=2, label='V_DS = V_GS')
ax2.set_xlabel('V_GS (V)')
ax2.set_ylabel('I_D (μA)')
ax2.set_title('(b) nMOS I_D-V_GS')
ax2.grid(True, alpha=0.3)
ax2.legend()
ax2.set_xlim(0, V_DD)
ax2.set_ylim(bottom=0)

V_DS_neg = np.linspace(0, -V_DD, 200)
for V_GS_neg in [-0.2, -0.5, -1.0]:
    I_D = pmos_current_with_negative(V_DS_neg, V_GS_neg, 1, 1)
    ax3.plot(V_DS_neg, I_D * 1e6, linewidth=2, label=f'V_GS = {V_GS_neg}V')
ax3.set_xlabel('V_DS (V)')
ax3.set_ylabel('I_D (μA)')
ax3.set_title('(c) pMOS I_D-V_DS')
ax3.grid(True, alpha=0.3)
ax3.legend()
ax3.set_xlim(-V_DD, 0)
ax3.set_ylim(bottom=0)

V_GS_neg = np.linspace(0, -V_DD, 200)
I_D_vds01_p = np.zeros_like(V_GS_neg)
I_D_vds_eq_vgs_p = np.zeros_like(V_GS_neg)

for i, vgs in enumerate(V_GS_neg):
    if -vgs >= (-V_tp):
        I_D_vds01_p[i] = pmos_current_with_negative(np.array([-0.1]), vgs, 1, 1)[0]
        I_D_vds_eq_vgs_p[i] = pmos_sat(vgs, 1, 1)

ax4.plot(V_GS_neg, I_D_vds01_p * 1e6, 'b-', linewidth=2, label='V_DS = -0.1V')
ax4.plot(V_GS_neg, I_D_vds_eq_vgs_p * 1e6, 'r-', linewidth=2, label='V_DS = V_GS')
ax4.set_xlabel('V_GS (V)')
ax4.set_ylabel('I_D (μA)')
ax4.set_title('(d) pMOS I_D-V_GS')
ax4.grid(True, alpha=0.3)
ax4.legend()
ax4.set_xlim(-V_DD, 0)
ax4.set_ylim(bottom=0)

V_DS = np.linspace(0, V_DD, 500)
L_values = [5, 1, 0.5]
V_GS_values = [0.5, 1.0]

colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
line_styles = ['-', '--']

for idx_gs, V_GS in enumerate(V_GS_values):
    for idx_L, L in enumerate(L_values):
        I_D = nmos_current(V_DS, V_GS, 1, L)
        ax5.plot(V_DS, I_D * 1e6, 
                linestyle=line_styles[idx_gs], 
                color=colors[idx_L], 
                linewidth=2.5,
                label=f'V_GS={V_GS}V, L={L}μm')

V_ov_05 = V_GS_values[0] - V_tn
V_ov_10 = V_GS_values[1] - V_tn

ax5.axvline(x=V_ov_05, color='gray', linestyle=':', alpha=0.7, linewidth=1.5)
ax5.axvline(x=V_ov_10, color='gray', linestyle=':', alpha=0.7, linewidth=1.5)

ax5.text(V_ov_05 + 0.02, 240, f'Sat boundary\n(V_GS=0.5V)', 
         fontsize=8, color='blue', ha='left', va='top',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.7))

ax5.text(V_ov_10 + 0.02, 240, f'Sat boundary\n(V_GS=1.0V)', 
         fontsize=8, color='green', ha='left', va='top',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.7))

ax5.text(0.07, 20, 'TRIODE REGION', fontsize=9, ha='center', 
         bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgray', alpha=0.5))

ax5.text(0.8, 20, 'SATURATION REGION', fontsize=9, ha='center',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgray', alpha=0.5))

ax5.set_xlabel('V_DS (V)', fontsize=12)
ax5.set_ylabel('I_D (μA)', fontsize=12)
ax5.set_title('(e) nMOS I_D-V_DS: Channel Length Dependence', fontsize=14)

ax5.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
ax5.minorticks_on()
ax5.grid(True, which='minor', alpha=0.1, linestyle=':', linewidth=0.3)

ax5.set_xlim(0, V_DD)
ax5.set_ylim(0, 250)

ax5.legend(fontsize=10, ncol=2, framealpha=0.95, edgecolor='black', fancybox=True, loc='upper left')

lambda_text = "Channel Length Modulation:\n"
for L in L_values:
    lambda_text += f"L = {L}μm: λ = {calculate_lambda(L):.4f} V⁻¹\n"
ax5.text(0.75, 0.45, lambda_text, transform=ax5.transAxes, fontsize=9,
         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))

plt.tight_layout()
plt.suptitle('MOSFET IV Characteristics (Square Law Model with CLM)', fontsize=16, y=1.02)

out = Path.cwd() / "mosfet_iv_plots_final_fixed.png"
plt.savefig(out, dpi=300, bbox_inches="tight")
print("Saved to:", out)

plt.show()

print("\n")
print(f"Overdrive voltages:")
print(f"V_GS = 0.5V: V_OV = {V_ov_05:.2f}V")
print(f"V_GS = 1.0V: V_OV = {V_ov_10:.2f}V")
print("\n")
print("Channel Length Modulation Parameters:")
for L in L_values:
    lam = calculate_lambda(L)
    print(f"L = {L:3.1f}μm: λ = {lam:.4f} V⁻¹  |  V_A = {V_A_prime*L:4.1f}V")