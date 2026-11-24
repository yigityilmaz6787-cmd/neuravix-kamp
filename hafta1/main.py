import json
import argparse
import matplotlib.pyplot as plt
from hafta1.gorev import GorevNoktasi, haversine, en_yakin_noktayi_bul

def main():
    parser = argparse.ArgumentParser(description="Görev Noktası Okuyucu")
    parser.add_argument("dosya_yolu", help="Okunacak GeoJSON dosyasının yolu")
    args = parser.parse_args()

    noktalar = []

    try:
        with open(args.dosya_yolu, 'r', encoding='utf-8') as file:
            veri = json.load(file)

            for feature in veri.get("features", []):
                props = feature.get("properties", {})
                ad = props.get("ad", "Bilinmeyen")
                aciklama = props.get("aciklama", "")
                
                koordinatlar = feature.get("geometry", {}).get("coordinates", [0, 0])
                boylam = koordinatlar[0]
                enlem = koordinatlar[1]

                nokta = GorevNoktasi(ad, aciklama, boylam, enlem)
                noktalar.append(nokta)

    except FileNotFoundError:
        print(f"Hata: '{args.dosya_yolu}' dosyası bulunamadı. Lütfen dosya yolunu kontrol edin.")
        return
    except json.JSONDecodeError:
        print("Hata: Dosya geçerli bir JSON formatında değil.")
        return

    if not noktalar:
        print("Uyarı: Dosya okundu ancak içinde hiç görev noktası bulunamadı.")
        return

    toplam_mesafe = 0
    mesafe_sonuclari = []

    print("\n--- Rota Bilgileri ---")
    for i in range(len(noktalar) - 1):
        n1 = noktalar[i]
        n2 = noktalar[i+1]
        mesafe = haversine(n1, n2)
        toplam_mesafe += mesafe
        
        print(f"{n1.ad} -> {n2.ad} arası mesafe: {mesafe:.2f} metre")
        
        mesafe_sonuclari.append({
            "baslangic": n1.ad,
            "bitis": n2.ad,
            "mesafe_metre": round(mesafe, 2)
        })

    print(f"Toplam Rota Uzunluğu: {toplam_mesafe:.2f} metre")

    ornek_hedef = GorevNoktasi("Hedef", "Aracın anlık konumu", 29.0, 41.0)
    en_yakin = en_yakin_noktayi_bul(ornek_hedef, noktalar)
    print(f"\nAracın konumuna en yakın nokta: {en_yakin.ad}")

    ozet_verisi = {
        "toplam_mesafe_metre": round(toplam_mesafe, 2),
        "mesafeler": mesafe_sonuclari
    }
    
    with open("rota_ozeti.json", "w", encoding="utf-8") as f:
        json.dump(ozet_verisi, f, ensure_ascii=False, indent=4)
    print("\nSonuçlar 'rota_ozeti.json' dosyasına başarıyla kaydedildi.")

    boylamlar = [n.boylam for n in noktalar]
    enlemler = [n.enlem for n in noktalar]

    plt.figure(figsize=(10, 6))
    plt.plot(boylamlar, enlemler, marker='o', linestyle='-', color='b')

    for n in noktalar:
        plt.annotate(n.ad, (n.boylam, n.enlem), textcoords="offset points", xytext=(0,10), ha='center')

    plt.title("Görev Noktaları Rotası")
    plt.xlabel("Boylam")
    plt.ylabel("Enlem")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()