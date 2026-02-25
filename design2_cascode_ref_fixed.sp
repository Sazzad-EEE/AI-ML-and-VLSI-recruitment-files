* ============================================================
* Design 2: Self-Biased Cascode Current Reference (Illustrative)
* Generated from Python design script (equation-calibrated)
* Target: Iref1 = Iref2 = 10 uA, VDD = 2.0 - 3.0 V
* ============================================================

.param VDD_val=2.5
.param R_val=15692

VDD VDD 0 DC {VDD_val}

* -------- PMOS CASCODE MIRROR --------
M1C net_m1a Vbiasp VDD VDD PMOS W=20u L=1u
M1A Vbias  Vbias  net_m1a VDD PMOS W=20u L=1u

M2C net_m2a Vbiasp VDD VDD PMOS W=20u L=1u
M2A net_ref Vbias  net_m2a VDD PMOS W=20u L=1u

* -------- NMOS CASCODE MIRROR --------
M3C net_m1a Vncas Vbiasn 0 NMOS W=40u L=1u
M3A Vbiasn Vbiasn 0      0 NMOS W=10u L=1u

M4C net_ref Vncas net_casc 0 NMOS W=40u L=1u
M4A net_casc Vbiasn net_R   0 NMOS W=40u L=1u

R1 net_R 0 {R_val}

* -------- STARTUP (simple) --------
Mstart  Vbias_st VDD VDD VDD PMOS W=1u L=10u
Mstart2 Vbias    Vbias_st 0 0 NMOS W=2u L=1u
Rstart  Vbias_st Vbias 10Meg

* -------- MODELS (illustrative) --------
.model NMOS NMOS (LEVEL=3 VTO=0.5 KP=20.305u LAMBDA=0.08 GAMMA=0.5 PHI=0.6)
.model PMOS PMOS (LEVEL=3 VTO=-0.5 KP=8.122u LAMBDA=0.08 GAMMA=0.5 PHI=0.6)

.op
.dc VDD VDD_val 2.0 3.0 0.01

.end
