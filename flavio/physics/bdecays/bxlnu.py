r"""Functions for inclusive semi-leptonic $B$ decays.

See arXiv:1107.3100."""


import flavio
from flavio.physics.bdecays.wilsoncoefficients import get_wceff_fccc_std
from math import pi, log, sqrt
from flavio.classes import Observable, Prediction
from flavio.config import config
from functools import lru_cache


def BR_BXclnu(par, wc_obj, lep):
    r"""Total branching ratio of $\bar B^0\to X_c \ell^- \bar\nu_\ell$"""
    GF = par['GF']
    scale = flavio.config['renormalization scale']['bxlnu']
    kinetic_cutoff = 1. # cutoff related to the kinetic definition of mb in GeV
    # mb in the kinetic scheme
    mb = flavio.physics.running.running.get_mb_KS(par, kinetic_cutoff)
    xl = par['m_'+lep]**2/mb**2
    # mc in MSbar at 3 GeV
    mc = flavio.physics.running.running.get_mc(par, 3)
    mb_MSbar = flavio.physics.running.running.get_mb(par, scale)
    xc = mc**2/mb**2
    Vcb = flavio.physics.ckm.get_ckm(par)[1, 2]
    alpha_s = flavio.physics.running.running.get_alpha(par, scale, nf_out=5)['alpha_s']
    # wc: NB this includes the EW correction already
    # the b quark mass is MSbar here as it comes from the definition
    # of the scalar operators
    wc = get_wceff_fccc_std(wc_obj, par, 'bc', lep, mb_MSbar, scale, nf=5)
    Gamma_LO = GF**2 * mb**5 / 192. / pi**3 * abs(Vcb)**2
    r_WC = (   g(xc, xl)      * (abs(wc['V'])**2 + abs(wc['Vp'])**2)
             - gLR(xc, xl)    * (wc['V']*wc['Vp']).real
             + g(xc, xl)/4.   * mb_MSbar**2 * (abs(wc['S'])**2 + abs(wc['Sp'])**2)
             + gLR(xc, xl)/2. * mb_MSbar**2 * (wc['S']*wc['Sp']).real
             + 12*g(xc, xl)   * abs(wc['T'])**2
             # the following terms vanish for vanishing lepton mass
             + gVS(xc, xl)    * mb_MSbar * ((wc['V']*wc['S']).real
                                       + (wc['Vp']*wc['Sp']).real)
             + gVSp(xc, xl)   * mb_MSbar * ((wc['V']*wc['Sp']).real
                                       + (wc['Vp']*wc['S']).real)
             - 12*gVSp(xc, xl)* (wc['V']*wc['T']).real
             + 12*gVS(xc, xl) * (wc['Vp']*wc['T']).real
           )
    # eq. (26) of arXiv:1107.3100 + corrections (P. Gambino, private communication)
    r_BLO = ( 1
                 # NLO QCD
                 + alpha_s/pi * pc1(xc, mb)
                 # NNLO QCD
                 + alpha_s**2/pi**2 * pc2(xc, mb)
                 # power correction
                 - par['mu_pi^2']/(2*mb**2)
                 + (1/2. -  2*(1-xc)**4/g(xc, 0))*(par['mu_G^2'] - (par['rho_LS^3'] + par['rho_D^3'])/mb)/mb**2
                 + d(xc)/g(xc, 0) * par['rho_D^3']/mb**3
                 # O(alpha_s) power correction (only numerically)
                 + alpha_s/pi *  par['mu_pi^2'] * 0.071943
                 + alpha_s/pi *  par['mu_G^2'] * (-0.114774)
            )
    # average of B0 and B+ lifetimes
    return (par['tau_B0']+par['tau_B+'])/2. * Gamma_LO * r_WC * r_BLO

@lru_cache(maxsize=config['settings']['cache size'])
def g(xc, xl):
    if xl == 0:
        return 1 - 8*xc + 8*xc**3 - xc**4 - 12*xc**2*log(xc)
    else:
        return (sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        - 7*xc*sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        - 7*xc**2*sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        + xc**3*sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        - 7*xl*sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        + 12*xc*xl*sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        - 7*xc**2*xl*sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        - 7*xl**2*sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        - 7*xc*xl**2*sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        + xl**3*sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        + 24*xc**2*log(2) - 24*xl**2*log(2) - 24*(-1 + xc**2)*xl**2* log(1 - sqrt(xc))
        + 12*xc**2*log(xc) - 6*xl**2*log(xc) - 6*xc**2*xl**2*log(xc)
        - 12*xl**2*log(sqrt(xc) - 2*xc + xc**1.5)
        + 12*xc**2*xl**2* log(sqrt(xc) - 2*xc + xc**1.5)
        - 12*xl**2*log(xl) + 12*xc**2*xl**2*log(xl)
        - 24*xc**2*log(1 + xc - xl - sqrt(1 + (xc - xl)**2 - 2*(xc + xl)))
        + 12*xl**2* log(1 + xc - xl - sqrt(1 + (xc - xl)**2 - 2*(xc + xl)))
        + 12*xc**2*xl**2* log(1 + xc - xl - sqrt(1 + (xc - xl)**2 - 2*(xc + xl)))
        + 12*xl**2* log(1 + xc**2 - xl + sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        - xc*(2 + xl + sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))))
        - 12*xc**2*xl**2* log(1 + xc**2 - xl
        + sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        - xc*(2 + xl + sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl)))))

@lru_cache(maxsize=config['settings']['cache size'])
def gLR(xc, xl):
    if xl == 0:
        return 4*sqrt(xc)*(1 + 9*xc - 9*xc**2 - xc**3 + 6*xc*(1 + xc)*log(xc))
    else:
        return (4*sqrt(xc)*(sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        + 10*xc*sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        + xc**2*sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        - 5*xl*sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        - 5*xc*xl*sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        - 2*xl**2*sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        - 12*xc*log(2) - 12*xc**2*log(2) + 24*xc*xl*log(2)
        - 12*xl**2*log(2) - 12*(-1 + xc)*xl**2* log(1 - sqrt(xc))
        - 6*xc*log(xc) - 6*xc**2*log(xc) + 12*xc*xl*log(xc) - 3*xl**2*log(xc)
        - 3*xc*xl**2*log(xc) - 6*xl**2*log(sqrt(xc) - 2*xc + xc**1.5)
        + 6*xc*xl**2* log(sqrt(xc) - 2*xc + xc**1.5) - 6*xl**2*log(xl)
        + 6*xc*xl**2*log(xl) + 12*xc*log(1 + xc - xl
        - sqrt(1 + (xc - xl)**2 - 2*(xc + xl)))
        + 12*xc**2*log(1 + xc - xl - sqrt(1 + (xc - xl)**2 - 2*(xc + xl)))
        - 24*xc*xl*log(1 + xc - xl - sqrt(1 + (xc - xl)**2 - 2*(xc + xl)))
        + 6*xl**2*log(1 + xc - xl - sqrt(1 + (xc - xl)**2 - 2*(xc + xl)))
        + 6*xc*xl**2* log(1 + xc - xl - sqrt(1 + (xc - xl)**2 - 2*(xc + xl)))
        + 6*xl**2*log(1 + xc**2 - xl + sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        - xc*(2 + xl + sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))))
        - 6*xc*xl**2* log(1 + xc**2 - xl + sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        - xc*(2 + xl + sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))))))

@lru_cache(maxsize=config['settings']['cache size'])
def gVS(xc, xl):
    if xl == 0:
        return 0
    else:
        return (2*sqrt(xl)*(sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        - 5*xc*sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        - 2*xc**2*sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        + 10*xl*sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        - 5*xc*xl*sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        + xl**2*sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl)) + 12*xc**2*log(2)
        + 12*xl*log(2) - 24*xc*xl*log(2) + 12*xl**2*log(2)
        - 12*xl*(1 - 2*xc + xc**2 + xl)* log(1 - sqrt(xc)) + 6*xc**2*log(xc)
        + 3*xl*log(xc) - 6*xc*xl*log(xc) - 3*xc**2*xl*log(xc) + 3*xl**2*log(xc)
        + 6*xl*log(sqrt(xc) - 2*xc + xc**1.5) - 12*xc*xl*log(sqrt(xc) - 2*xc + xc**1.5)
        + 6*xc**2*xl* log(sqrt(xc) - 2*xc + xc**1.5)
        + 6*xl**2*log(sqrt(xc) - 2*xc + xc**1.5) + 6*xl*log(xl)
        - 12*xc*xl*log(xl) + 6*xc**2*xl*log(xl) + 6*xl**2*log(xl)
        - 12*xc**2*log(1 + xc - xl - sqrt(1 + (xc - xl)**2 - 2*(xc + xl)))
        - 6*xl*log(1 + xc - xl - sqrt(1 + (xc - xl)**2 - 2*(xc + xl)))
        + 12*xc*xl*log(1 + xc - xl - sqrt(1 + (xc - xl)**2 - 2*(xc + xl)))
        + 6*xc**2*xl* log(1 + xc - xl - sqrt(1 + (xc - xl)**2 - 2*(xc + xl)))
        - 6*xl**2*log(1 + xc - xl - sqrt(1 + (xc - xl)**2 - 2*(xc + xl)))
        - 6*xl*log(1 + xc**2 - xl + sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        - xc*(2 + xl + sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))))
        + 12*xc*xl*log(1 + xc**2 - xl + sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        - xc*(2 + xl + sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))))
        - 6*xc**2*xl* log(1 + xc**2 - xl + sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        - xc*(2 + xl + sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))))
        - 6*xl**2*log(1 + xc**2 - xl + sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        - xc*(2 + xl + sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))))))

@lru_cache(maxsize=config['settings']['cache size'])
def gVSp(xc, xl):
    if xl == 0:
        return 0
    else:
        return (2*sqrt(xc*xl)* (2*sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        + 5*xc*sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        - xc**2*sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        + 5*xl*sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        - 10*xc*xl*sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        - xl**2*sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl)) - 12*xc*log(2)
        + 12*xl*log(2) - 12*(1 + xc**2 + xc*(-2 + xl))*xl* log(1 - sqrt(xc))
        - 6*xc*log(xc) + 3*xl*log(xc) + 6*xc*xl*log(xc) - 3*xc**2*xl*log(xc)
        - 3*xc*xl**2*log(xc) + 6*xl*log(sqrt(xc) - 2*xc + xc**1.5)
        - 12*xc*xl*log(sqrt(xc) - 2*xc + xc**1.5)
        + 6*xc**2*xl* log(sqrt(xc) - 2*xc + xc**1.5)
        + 6*xc*xl**2* log(sqrt(xc) - 2*xc + xc**1.5)
        + 6*xl*log(xl) - 12*xc*xl*log(xl) + 6*xc**2*xl*log(xl) + 6*xc*xl**2*log(xl)
        + 12*xc*log(1 + xc - xl - sqrt(1 + (xc - xl)**2 - 2*(xc + xl)))
        - 6*xl*log(1 + xc - xl - sqrt(1 + (xc - xl)**2 - 2*(xc + xl)))
        - 12*xc*xl*log(1 + xc - xl - sqrt(1 + (xc - xl)**2 - 2*(xc + xl)))
        + 6*xc**2*xl* log(1 + xc - xl - sqrt(1 + (xc - xl)**2 - 2*(xc + xl)))
        + 6*xc*xl**2* log(1 + xc - xl - sqrt(1 + (xc - xl)**2 - 2*(xc + xl)))
        - 6*xl*log(1 + xc**2 - xl + sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        - xc*(2 + xl + sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))))
        + 12*xc*xl*log(1 + xc**2 - xl + sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        - xc*(2 + xl + sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))))
        - 6*xc**2*xl* log(1 + xc**2 - xl + sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        - xc*(2 + xl + sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))))
        - 6*xc*xl**2* log(1 + xc**2 - xl + sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))
        - xc*(2 + xl + sqrt(xc**2 + (-1 + xl)**2 - 2*xc*(1 + xl))))))

def d(xc):
    return 8*log(xc) - 10*xc**4/3. + 32*xc**3/3. - 8*xc**2 - 32*xc/3. + 34/3.

def pc1(r, mb):
    # this is an expansion to 2nd order in mb around 4.6 and in r around 0.05
    # P. Gambino,  private communication
    # kinetic scheme cutoff is set to 1 GeV
    return ( 6.486085393242938 - 80.16227770322831*r + 207.37836204469366*r**2
            + mb*(-2.3090743981240274 + 14.029509187000471*r - 36.61694487623083*r**2)
            + mb**2*(0.18126017716432158 - 0.8813205571033417*r + 3.1906139935867635*r**2))

def pc2(r, mb):
    # this is an expansion to 2nd order in mb around 4.6 and in r around 0.05
    # P. Gambino,  private communication
    # kinetic scheme cutoff is set to 1 GeV
    return  ( 63.344451026174276 - 1060.9791881246733*r + 4332.058337615373*r**2
             + mb*(-21.760717863346223 + 273.7460360545832*r - 1032.068345746423*r**2)
             + mb**2*(1.8406501267881998 - 20.26973707297946*r + 73.82649433414315*r**2))


def BR_tot_function(lep):
    if lep == 'l':
        return lambda wc_obj, par: (BR_BXclnu(par, wc_obj, 'e')+BR_BXclnu(par, wc_obj, 'mu'))/2
    else:
        return lambda wc_obj, par: BR_BXclnu(par, wc_obj, lep)

_process_taxonomy = r'Process :: $b$ hadron decays :: Semi-leptonic tree-level decays :: $B\to X\ell\nu$ :: $'

_tex = {'e': 'e', 'mu': '\mu', 'l': r'\ell'}

for l in ['e', 'mu', 'l']:
        _obs_name = "BR(B->Xc"+l+"nu)"
        _process_tex = r"B\to X_c"+_tex[l]+r"^+\nu_"+_tex[l]
        _obs = Observable(_obs_name)
        _obs.set_description(r"Total branching ratio of $" + _process_tex + r"$")
        _obs.tex = r"$\text{BR}(" + _process_tex + r")$"
        _obs.add_taxonomy(_process_taxonomy + _process_tex + r"$")
        Prediction(_obs_name, BR_tot_function(l))
