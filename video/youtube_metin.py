"""YouTube başlık/açıklama/etiketlerini, gerçek bölüm zamanlarıyla üretir."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOLUM = {
    "s01_acilis": "Giriş", "s02_ragnar": "Ragnar gerçek mi, efsane mi?", "s03_piramit": "Jarl, Karl, Köle: Viking toplumu",
    "s04_dogum": "Doğum ve isim verme", "s05_uzun_ev": "Uzun ev", "s06_yemek": "Bir gün ve yemekler",
    "s07_tarla": "Tarla, hayvanlar ve kışa hazırlık", "s08_kadinlar": "Viking kadınları", "s09_temizlik": "Vikingler pis miydi?",
    "s10_ting": "Ting: kanun ve kan davası", "s11_din": "Tanrılar ve Valhalla", "s12_cagri": "Akın çağrısı",
    "s13_deniz": "Denizde hayat", "s14_paris": "Paris kuşatması, 845", "s15_salgin": "Salgın ve yaralar",
    "s16_evlilik": "Evlilik", "s17_kis": "Uzun kış", "s18_aclik": "Kıtlık ve kölelik tehlikesi",
    "s19_olum": "Yaşlılık ve ölüm", "s20_kapanis": "Kapanış",
}


def fmt(t):
    t = int(t)
    return f"{t // 60}:{t % 60:02d}"


def main():
    z = json.load(open(os.path.join(ROOT, "build", "video", "sessiz_zaman.json")))
    bolumler = "\n".join(f"{fmt(0 if i == 0 else s['bas'])} {BOLUM[s['sid']]}" for i, s in enumerate(z["sahneler"]))
    metin = f"""# YouTube Yükleme Bilgileri

## Başlık
Ragnar Zamanında Viking Bir Köylü Olsaydın Hayatın Nasıl Olurdu?

## Açıklama
Yıl 845. Ragnar Lodbrok 120 gemiyle Paris'e yelken açıyor... Ama sen o gemilerde değilsin.
Bu bölümde Viking çağında sıradan bir köylünün, yani bir "karl"ın hayatını baştan sona yaşıyoruz:
uzun evde büyümek, kışa hazırlık, Ting meclisi, Thor ve Freyr, Paris seferi, kıtlık ve taş gemi mezarlar.

Sen olsan hangisini seçerdin: tarla mı, kürek mi? Yorumlara yaz!

⏳ Bölümler
{bolumler}

📚 Kaynaklar
- Annales Bertiniani (Frank yıllıkları, 845 Paris saldırısı ve 7.000 libre ödeme)
- Snorri Sturluson, Heimskringla – Aziz Olaf Destanı (soğan çorbası anlatısı)
- Wallingford'lu John kroniği (Danimarkalıların tarak ve cumartesi yıkanma alışkanlığı)
- Ragnars saga loðbrókar (Ragnar efsanesi ve yılan çukuru)

#viking #ragnar #tarih #animasyon #zamankırığı

## Etiketler
viking, vikingler, ragnar lodbrok, viking köylüsü, viking hayatı, tarih, tarih animasyon, 845 paris, paris kuşatması, iskandinav tarihi, karl, jarl, thrall, valhalla, thor, odin, freyr, uzun ev, zaman kırığı, olsaydın ne olurdu

## Video süresi
{fmt(z['toplam'])}
"""
    open(os.path.join(ROOT, "cikti", "youtube_bilgileri.md"), "w", encoding="utf-8").write(metin)
    print(metin)


if __name__ == "__main__":
    main()
