import json
import argparse
from pathlib import Path
import matplotlib.pyplot as plt

try:
    from hafta1.gorev import GorevNoktası, haversine, en_yakin_noktayi_bul
except ImportError:
    from gorev import GorevNoktası, haversine, en_yakin_noktayi_bul

def main():
    varsayilan_klasor = Path(__file__).resolve().parent / "gun1_kombinasyonlari"

    parser = argparse.ArgumentParser(description="Görev Noktası Okuyucu")
    parser.add_argument(
        "klasor_yolu",
        nargs="?",
        default=str(varsayilan_klasor),
        help="Okunacak GeoJSON dosyalarının bulunduğu klasör yolu"
    )
    args = parser.parse_args()

    klasor = Path(args.klasor_yolu)

    if not klasor.exists() or not klasor.is_dir():
        print(f"Hata: '{klasor}' geçerli bir klasör değil.")
        return

    geojson_dosyalari = sorted(klasor.rglob("*.geojson"))

    if not geojson_dosyalari:
        print(f"Uyarı: '{klasor}' klasöründe hiç .geojson dosyası bulunamadı.")
        return

    noktalar = []

    for dosya_yolu in geojson_dosyalari:
        try:
            with open(dosya_yolu, 'r', encoding='utf-8') as file:
                veri = json.load(file)

                for feature in veri.get("features", []):
                    props = feature.get("properties", {})
                    ad = props.get("ad", "Bilinmeyen")
                    aciklama = props.get("aciklama", "")

                    koordinatlar = feature.get("geometry", {}).get("coordinates", [0, 0])
                    boylam = koordinatlar[0]
                    enlem = koordinatlar[1]

                    nokta = GorevNoktası(ad, aciklama, boylam, enlem)
                    noktalar.append(nokta)

        except json.JSONDecodeError:
            print(f"Hata: '{dosya_yolu.name}' geçerli bir JSON formatında değil, atlanıyor.")

    if not noktalar:
        print("Uyarı: Dosyalar okundu ancak içinde hiç görev noktası bulunamadı.")
        return

    toplam_mesafe = 0
    mesafe_sonuclari = []

    print(f"\nOkunan dosya sayısı: {len(geojson_dosyalari)}")
    print("\n--- Rota Bilgileri ---")
    for i in range(len(noktalar) - 1):
        n1 = noktalar[i]
        n2 = noktalar[i + 1]
        mesafe = haversine(n1, n2)
        toplam_mesafe += mesafe

        print(f"{n1.ad} -> {n2.ad} arası mesafe: {mesafe:.2f} metre")

        mesafe_sonuclari.append({
            "baslangic": n1.ad,
            "bitis": n2.ad,
            "mesafe_metre": round(mesafe, 2)
        })

    print(f"Toplam Rota Uzunluğu: {toplam_mesafe:.2f} metre")

    ornek_hedef = GorevNoktası("Hedef", "Aracın anlık konumu", 29.0, 41.0)
    en_yakin = en_yakin_noktayi_bul(ornek_hedef, noktalar)
    print(f"\nAracın konumuna en yakın nokta: {en_yakin.ad}")

    ozet_verisi = {
        "okunan_dosyalar": [d.name for d in geojson_dosyalari],
        "toplam_mesafe_metre": round(toplam_mesafe, 2),
        "mesafeler": mesafe_sonuclari
    }

    cikti_yolu = Path(__file__).resolve().parent / "rota_ozeti.json"
    with open(cikti_yolu, "w", encoding="utf-8") as f:
        json.dump(ozet_verisi, f, ensure_ascii=False, indent=4)
    print(f"\nSonuçlar '{cikti_yolu.name}' dosyasına başarıyla kaydedildi.")

    boylamlar = [n.boylam for n in noktalar]
    enlemler = [n.enlem for n in noktalar]

    plt.figure(figsize=(10, 6))
    plt.plot(boylamlar, enlemler, marker='o', linestyle='-', color='b')

    for n in noktalar:
        plt.annotate(n.ad, (n.boylam, n.enlem), textcoords="offset points", xytext=(0, 10), ha='center')

    plt.title("Görev Noktaları Rotası")
    plt.xlabel("Boylam")
    plt.ylabel("Enlem")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()