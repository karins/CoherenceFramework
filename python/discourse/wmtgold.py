"""
This module contains the rankings from the WMT shared task.

@author: wilkeraziz
"""

WMT14_DE_EN = {
'newstest2014.de-en.ref': 0,
'newstest2014.de-en.onlineB.0': 1,
'newstest2014.de-en.uedin-syntax.3035': 2,
'newstest2014.de-en.onlineA.0': 2,
'newstest2014.de-en.LIMSI-KIT-Submission.3359': 3,
'newstest2014.de-en.uedin-wmt14.3025': 3,
'newstest2014.de-en.eubridge.3569': 3,
'newstest2014.de-en.kit.3109': 4,
'newstest2014.de-en.RWTH-primary.3266': 4,
'newstest2014.de-en.DCU-ICTCAS-Tsinghua-L.3444': 5,
'newstest2014.de-en.CMU.3461': 5,
'newstest2014.de-en.rbmt4.0': 5,
'newstest2014.de-en.rbmt1.0': 6,
'newstest2014.de-en.onlineC.0': 7}

WMT14_FR_EN = {
'newstest2014.fr-en.ref': 0,
'newstest2014.fr-en.uedin-wmt14.3024': 1,
'newstest2014.fr-en.kit.3112': 2,
'newstest2014.fr-en.onlineB.0': 2,
'newstest2014.fr-en.Stanford-University.3496': 2,
'newstest2014.fr-en.onlineA.0': 3,
'newstest2014.fr-en.rbmt1.0': 4,
'newstest2014.fr-en.rbmt4.0': 5,
'newstest2014.fr-en.onlineC.0': 6}

WMT14_RU_EN = {
'newstest2014.ru-en.ref': 0,
'newstest2014.ru-en.AFRL-Post-edited.3431': 1,
'newstest2014.ru-en.onlineB.0': 2,
'newstest2014.ru-en.onlineA.0': 3,
'newstest2014.ru-en.PROMT-Hybrid.3084': 3,
'newstest2014.ru-en.PROMT-Rule-based.3085': 3,
'newstest2014.ru-en.uedin-wmt14.3364': 3,
'newstest2014.ru-en.shad-wmt14.3464': 3,
'newstest2014.ru-en.onlineG.0': 3,
'newstest2014.ru-en.AFRL.3349': 4,
'newstest2014.ru-en.uedin-syntax.3166': 5,
'newstest2014.ru-en.kaznu1.3549': 6,
'newstest2014.ru-en.rbmt1.0': 7,
'newstest2014.ru-en.rbmt4.0': 8}

WMT14_RANKINGS = {'de-en': WMT14_DE_EN, 'fr-en': WMT14_FR_EN, 'ru-en': WMT14_RU_EN}
