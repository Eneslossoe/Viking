# Zaman Kırığı – Ragnar Zamanında Viking Bir Köylü Olsaydın Hayatın Nasıl Olurdu?

Bu videodaki her şey kodla üretildi: çizimler (SVG), animasyon (Python/PIL), seslendirme
(yerel Türkçe ses modeli), müzik ve ses efektleri (numpy sentezi). Hiçbir hazır görsel ya da
ses dosyası kullanılmadı.

## Çıktılar (`cikti/`)
| Dosya | Açıklama |
|---|---|
| `Ragnar_Zamaninda_Viking_Koylusu.mp4` | 1080p video (git'e eklenmez, boyutu büyük) |
| `Ragnar_Zamaninda_Viking_Koylusu.srt` | YouTube'a yüklenecek Türkçe altyazı |
| `kapak_1280x720.jpg` | Kapak görseli |
| `youtube_bilgileri.md` | Başlık, açıklama (bölüm zamanlarıyla), etiketler, kaynaklar |

## Klasörler
- `senaryo/sahneler.json` – 20 sahnelik metin ve görsel notları
- `cizim/sanat.py`, `cizim/sanat2.py` – çizim kütüphanesi (karakter, hayvanlar, uzun ev, gemi, Paris…)
- `cizim/sahneler.py` – her sahnenin çekimleri (hangi cümlede hangi görüntü, efektler, kamera)
- `cizim/render.js` – SVG → PNG (Playwright/Chromium)
- `video/animasyon.py` – kamera hareketi, nefes, göz kırpma, gemi sallanması, ateş, duman, kar, yağmur, şimşek
- `ses/seslendir.py` – Chatterbox Multilingual (MIT lisanslı) ile Türkçe seslendirme;
  her cümle Whisper ile geri dinlenip yanlış okunursa yeniden üretilir
- `ses/birlestir.py` – sesi sertleştirme (hafif kalınlaştırma, EQ, kompresör) ve zamanlama
- `ses/muzik.py` – Re minör drone/pad, davul, rüzgar, dalga, yağmur, ateş, gök gürültüsü, Viking borusu
- `video/son_kurgu.py` – karışım (müzik konuşmada otomatik kısılır), -14 LUFS, SRT

## Yeniden üretmek
```bash
./kurulum.sh   # tek seferlik
./uret.sh      # tüm video
```
Metni değiştirmek için `senaryo/sahneler.json` dosyasını düzenleyip `./uret.sh` çalıştırmak yeterli;
sadece değişen cümleler yeniden seslendirilir.

## Tarihsel notlar
- Ragnar Lodbrok yarı efsanevidir; 845 Paris saldırısı Frank yıllıklarında "Reginherus" adıyla geçer.
- Kel Charles'ın ödediği 7.000 libre (~2,5 ton) gümüş ve altın, Annales Bertiniani'de kayıtlıdır.
- Soğan çorbası anlatısı Heimskringla'daki Aziz Olaf Destanı'ndan; cumartesi yıkanma ve tarak
  anlatısı Wallingford'lu John kroniğinden.
- Vikingler boynuzlu miğfer takmazdı; çizimlerde burun korumalı yuvarlak miğfer kullanıldı.
