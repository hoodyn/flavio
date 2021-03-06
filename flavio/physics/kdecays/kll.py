r"""Functions for $K^0\to \ell^+\ell^-$ decays"""

import flavio
from flavio.config import config
from flavio.physics.bdecays.common import lambda_K
from flavio.physics import ckm
from flavio.physics.kdecays.wilsoncoefficients import wilsoncoefficients_sm_sl
from flavio.physics.common import add_dict
from math import pi, sqrt


def amplitudes_weak_eigst(par, wc, l1, l2):
    r"""Amplitudes P and S for the decay $\bar K^0\to\ell_1^+\ell_2^-$.

    Parameters
    ----------

    - `par`: parameter dictionary
    - `wc`: Wilson coefficient dictionary
    - `l1` and `l2`: should be `'e'` or `'mu'`
    """
    # masses
    ml1 = par['m_'+l1]
    ml2 = par['m_'+l2]
    mK = par['m_K0']
    # Wilson coefficient postfix 
    qqll = 'sd' + l1 + l2
    # For LFV expressions see arXiv:1602.00881 eq. (5)
    C9m = wc['C9_'+qqll] - wc['C9p_'+qqll]  # only relevant for l1 != l2
    C10m = wc['C10_'+qqll] - wc['C10p_'+qqll]
    CPm = wc['CP_'+qqll] - wc['CPp_'+qqll]
    CSm = wc['CS_'+qqll] - wc['CSp_'+qqll]
    P = (ml2 + ml1)/mK * C10m + mK * CPm  # neglecting mu, md
    S = (ml2 - ml1)/mK * C9m  + mK * CSm  # neglecting mu, md
    # Include complex part of the eff. operator prefactor. Phases matter.
    xi_t = ckm.xi('t', 'sd')(par)
    return xi_t * P, xi_t * S


def amplitudes(par, wc, K, l1, l2):
    r"""Amplitudes P and S entering the $K_{L,S}\to\ell_1^+\ell_2^-$ observables.
    
    Parameters
    ----------
    
    - `par`: parameter dictionary
    - `wc`: Wilson coefficient dictionary
    - `K`: should be `'KL'` or `'KS'`
    - `l1` and `l2`: should be `'e'` or `'mu'`
    """
    # KL, KS are linear combinations of K0, K0bar. So are the amplitudes.
    # Normalization differs by sqrt(2) from `amplitudes_weak_eigst`.
    P_K0bar, S_K0bar = amplitudes_weak_eigst(par, wc, l1, l2)
    if l1 != l2:
        P_aux, S_aux = amplitudes_weak_eigst(par, wc, l2, l1)
        S_K0 = -S_aux.conjugate()
        P_K0 = P_aux.conjugate()
        if K == 'KL':
            sig = +1
        elif K == 'KS':
            sig = -1
        S = (S_K0 + sig * S_K0bar) / 2
        P = (P_K0 + sig * P_K0bar) / 2
    # Simplified expressions for special cases. See also arXiv:1711.11030.
    elif l1 == l2:
        if K == 'KL':
            S = -1j * S_K0bar.imag 
            P = P_K0bar.real
        elif K == 'KS':
            S = -S_K0bar.real
            P = -1j * P_K0bar.imag
    return P, S


def amplitudes_LD(par, K, l):
    r"""Long-distance amplitudes entering the $K\to\ell^+\ell^-$ observables."""
    ml = par['m_' + l]
    mK = par['m_K0']
    s2w = par['s2w']
    pre = 2 * ml / mK / s2w
    # numbers extracted from arXiv:1711.11030
    flavio.citations.register("Chobanova:2017rkj")
    if K == 'KS':
        ASgaga = 2.49e-4 * (-2.821 + 1.216j)
        SLD = pre * ASgaga
        PLD = 0
    elif K == 'KL':
        ALgaga = 2.02e-4 * (par['chi_disp(KL->gammagamma)'] - 5.21j)
        SLD = 0
        PLD = pre * ALgaga
    return SLD, PLD


def amplitudes_eff(par, wc, K, l1, l2, ld=True):
    r"""Effective amplitudes entering the $K\to\ell_1^+\ell_2^-$ observables."""
    P, S = amplitudes(par, wc, K, l1, l2)
    if l1 != l2 or not ld:
        SLD = 0
        PLD = 0
    else:
        SLD, PLD = amplitudes_LD(par, K, l1)
    # The relative sign due to different conventions. Cf. my notes.
    Peff = P - PLD
    Seff = S - SLD
    return Peff, Seff


def get_wc(wc_obj, par, l1, l2):
    scale = config['renormalization scale']['kdecays']
    if l1 == l2:   # (l1,l2) == ('e','e') or ('mu','mu')
        label = 'sd' + l1 + l2
        wcnp = wc_obj.get_wc(label, scale, par)
        # include SM contributions for LF conserving decay
        _c = wilsoncoefficients_sm_sl(par, scale)
        xi_t = ckm.xi('t', 'sd')(par)
        xi_c = ckm.xi('c', 'sd')(par)
        wcsm = {'C10_sd' + l1 + l2: _c['C10_t'] + xi_c / xi_t * _c['C10_c']}
    elif {l1,l2} == {'e','mu'}:
        # Both flavor combinations relevant due to K0-K0bar mixing
        wcnp = {**wc_obj.get_wc('sdemu', scale, par),
                **wc_obj.get_wc('sdmue', scale, par)}
        wcsm = {}

    return add_dict((wcsm, wcnp))


def br_kll(par, wc_obj, K, l1, l2, ld=True):
    r"""Branching ratio of $K\to\ell_1^+\ell_2^-$"""
    # parameters
    wc = get_wc(wc_obj, par, l1, l2)
    GF = par['GF']
    alphaem = par['alpha_e']
    ml1 = par['m_'+l1]
    ml2 = par['m_'+l2]
    mK = par['m_K0']
    tauK = par['tau_'+K]
    fK = par['f_K0']
    # CKM part of the eff. operator prefactor N is included in Peff and Seff
    N = 4 * GF / sqrt(2) * alphaem / (4 * pi)
    beta = sqrt(lambda_K(mK**2, ml1**2, ml2**2)) / mK**2
    beta_p = sqrt(1 - (ml1 + ml2)**2 / mK**2)
    beta_m = sqrt(1 - (ml1 - ml2)**2 / mK**2)
    prefactor = 2 * abs(N)**2 / 32. / pi * mK**3 * tauK * beta * fK**2
    Peff, Seff = amplitudes_eff(par, wc, K, l1, l2, ld=ld)
    return prefactor * (beta_m**2 * abs(Peff)**2 + beta_p**2 * abs(Seff)**2)


# function returning function needed for prediction instance
def br_kll_fct(K, l1, l2):
    def f(wc_obj, par):
        return br_kll(par, wc_obj, K, l1, l2)
    return f

def br_kll_fct_lsum(K, l1, l2):
    def f(wc_obj, par):
        # Neglecting indirect CPV in kaons, BR(KL,KS->e+mu-) = BR(KL,KS->mu+e-) 
        return 2 * br_kll(par, wc_obj, K, l1, l2)
    return f


_tex = {'e': 'e', 'mu': r'\mu'}
_tex_p = {'KL': r'K_L', 'KS': r'K_S',}

for l in ['e', 'mu']:
    for P in _tex_p:
        _obs_name = "BR({}->{}{})".format(P, l, l)
        _obs = flavio.classes.Observable(_obs_name)
        _process_tex = _tex_p[P] + r"\to "+_tex[l]+r"^+"+_tex[l]+r"^-"
        _process_taxonomy = r'Process :: $s$ hadron decays :: FCNC decays :: $K\to \ell\ell$ :: $' + _process_tex + r'$'
        _obs.add_taxonomy(_process_taxonomy)
        _obs.set_description(r"Branching ratio of $" + _process_tex +r"$")
        _obs.tex = r"$\text{BR}(" + _process_tex + r")$"
        flavio.classes.Prediction(_obs_name, br_kll_fct(P, l, l))


# LFV decay
for P in _tex_p:
    _obs_name = "BR({}->emu,mue)".format(P)
    _obs = flavio.classes.Observable(_obs_name)
    _process_tex = _tex_p[P] + r"\to e^\pm\mu^\mp"
    _process_taxonomy = r'Process :: $s$ hadron decays :: FCNC decays :: $K\to \ell\ell$ :: $' + _process_tex + r'$'
    _obs.add_taxonomy(_process_taxonomy)
    _obs.set_description(r"Branching ratio of $" + _process_tex +r"$")
    _obs.tex = r"$\text{BR}(" + _process_tex + r")$"
    flavio.classes.Prediction(_obs_name, br_kll_fct_lsum(P, 'e', 'mu'))
