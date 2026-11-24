import math

class GorevNoktası:
    def __init__(self, ad, aciklama, boylam, enlem):
        self.ad = ad
        self.aciklama = aciklama
        self.boylam = boylam
        self.enlem = enlem

    def __str__(self):
        return f"{self.ad} - {self.aciklama} (Boylam: {self.boylam}, Enlem {self.enlem})"

def haversine(n1, n2):

    dünya_çevresi = 6371000

    phi1 = math.radians(n1.enlem)
    phi2 = math.radians(n2.enlem)
    delta_phi = math.radians(n2.enlem - n1.enlem)
    delta_lambda = math.radians(n2.boylam - n1.boylam)

    merkez_aci_haversine = math.sin(delta_phi / 2.0)**2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0)**2
    
    mesafe = 2 * dünya_çevresi * math.asin(math.sqrt(merkez_aci_haversine))
    return mesafe

def en_yakin_noktayi_bul(hedef_konum, noktalar_listesi):
    
    if not noktalar_listesi:
        return None

    return min(noktalar_listesi, key=lambda nokta: haversine(hedef_konum, nokta))