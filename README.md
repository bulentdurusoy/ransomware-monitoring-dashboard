# Ransomware Monitoring Dashboard

## Proje Hakkinda

**Ransomware Monitoring Dashboard**, fidye yazilimi (ransomware) saldirilarini analiz etmek ve gorsellesstirmek amaciyla gelistirilmis bir **Siber Tehdit Istihbarati (CTI)** dashboard uygulamasidir.

Uygulama; fidye yazilimi gruplari, hedef ulkeler, sektorler, saldiri vektorleri, MITRE ATT&CK teknikleri, siddet seviyeleri ve IOC (Indicator of Compromise) bilgileri hakkinda kapsamli analizler sunar.

> **ONEMLI:** Bu uygulama otomatik olarak sahte/simulasyon veri **uretmez**. Dashboard yalnizca kullanicinin yukledigi veya Docker volume uzerinden saglanan CSV/XLSX veri setini analiz eder.

---

## Kullanilan Teknolojiler

| Teknoloji      | Kullanim Amaci                          |
| -------------- | --------------------------------------- |
| **Python**     | Ana programlama dili                    |
| **Streamlit**  | Web tabanli dashboard arayuzu           |
| **Pandas**     | Veri analizi ve manipulasyonu           |
| **Plotly**     | Interaktif veri gorsellestirme          |
| **NumPy**      | Sayisal islemler                        |
| **openpyxl**   | Excel (XLSX) dosyalari icin destek      |
| **Docker**     | Konteynerizasyon ve dagitim             |

---

## Docker Kullanimi

### Dockerfile

Proje, `python:3.11-slim` tabanli hafif bir Docker imaji kullanir. Uygulama konteyner icinde 8501 portunda calisir.

### Docker ile Calistirma

```bash
# Docker imajini olustur
docker build -t ransomware-dashboard .

# Konteyneri calistir
docker run -p 8501:8501 ransomware-dashboard
```

Veri seti dosyalarini konteyner icine baglamak icin volume kullanin:

```bash
docker run -p 8501:8501 -v ./data:/app/data ransomware-dashboard
```

### Docker Compose ile Calistirma

```bash
docker compose up --build
```

`docker-compose.yml` dosyasi otomatik olarak `./data` klasorunu `/app/data` olarak baglar.

---

## Veri Seti Yukleme Gereksinimleri

### Desteklenen Dosya Formatlari

- `.csv` (Comma-Separated Values)
- `.xlsx` (Microsoft Excel)

### Zorunlu Sutunlar

Yuklenen veri seti asagidaki sutunlari **mutlaka** icermelidir:

| Sutun              | Aciklama                                              |
| ------------------ | ----------------------------------------------------- |
| `date`             | Saldirinin gerceklestigi tarih                        |
| `ransomware_group` | Saldiriyi gerceklestiren fidye yazilimi grubu          |
| `country`          | Saldirinin hedef aldigi ulke                          |
| `target_sector`    | Hedef sektor (orn: Healthcare, Finance, Education)    |
| `attack_vector`    | Saldiri vektoru (orn: Phishing, RDP Brute Force)      |
| `technique`        | MITRE ATT&CK teknigi (orn: T1486, T1566)             |
| `severity`         | Saldirinin siddet seviyesi (1-10 arasi tam sayi)      |
| `ioc_ip`           | Gosterge olarak kullanilan IP adresi                  |
| `ioc_hash`         | Gosterge olarak kullanilan SHA256 hash degeri         |

### Dogrulama Kurallari

- Eksik sutun varsa hata mesaji gosterilir ve dashboard yuklenmez.
- `date` sutunu datetime formatina donusturulur; gecersiz tarihler cikarilir.
- `severity` sutunu sayisal degere donusturulur; 1-10 araligi disindaki degerler cikarilir.
- Gecersiz satirlar hakkinda uyari mesajlari gosterilir.
- Temizleme sonrasi gecerli satir kalmamissa hata mesaji goruntulenir.

> **NOT:** Uygulama Kaggle veya baska bir kaynaktan hazir veri seti kullanmaz. Varsayilan olarak hicbir veri seti yuklu degildir.

---

## Yerel Calistirma (Docker olmadan)

### 1. Gereksinimleri Yukleyin

```bash
pip install -r requirements.txt
```

### 2. Uygulamayi Baslatin

```bash
streamlit run app.py
```

Uygulama varsayilan olarak `http://localhost:8501` adresinde acilacaktir.

---

## Dashboard Ozellikleri

### 1. Hosgeldin Ekrani
Veri seti yuklenmeden once kullaniciya gerekli sutunlar ve desteklenen formatlar hakkinda bilgi veren bir karsilama ekrani gosterilir.

### 2. Veri Seti Yukleme
Sidebar'da iki secenek sunulur:
- **Manuel yukleme:** `st.file_uploader` ile CSV veya XLSX dosyasi yukleyin.
- **Veri klasorunden sec:** Docker volume uzerinden `/app/data` klasorune yerlestirilen dosyalardan birini secin.

### 3. Genel Bakis Ozeti
Toplam saldiri sayisi, benzersiz grup sayisi, en cok hedeflenen ulke ve sektor, ortalama ve maksimum siddet degerleri tek bir bakista goruntulenir.

### 4. Ransomware Grubu Dagilimi
Saldirilarin fidye yazilimi gruplarina gore dagilimini gosteren cubuk ve pasta grafikleri.

### 5. Ulke Bazli Saldiri Dagilimi
Hangi ulkelerin daha fazla saldiriya ugradigini gosteren cubuk grafik.

### 6. Sektor Bazli Saldiri Dagilimi
Saldirilarin hedef sektorlere gore dagilimini gosteren cubuk ve pasta grafikleri.

### 7. Zaman Serisi Trendi
Aylik bazda fidye yazilimi saldiri trendini gosteren alan grafigi.

### 8. Siddet Analizi
- Grup bazinda ortalama siddet seviyesi
- Genel siddet dagilim histogrami

### 9. MITRE ATT&CK Teknik Dagilimi
Saldirilarda kullanilan MITRE ATT&CK tekniklerinin yatay cubuk grafigiyle gosterimi.

### 10. Saldiri Vektoru Analizi
Saldiri vektorlerinin (Phishing, RDP Brute Force vb.) dagilim grafigi.

### 11. Filtreleme
Sol paneldeki filtreler sayesinde verileri asagidaki kriterlere gore daraltabilirsiniz:
- **Tarih araligi**
- **Ransomware grubu**
- **Ulke**
- **Hedef sektor**
- **Siddet araligi**

Tum grafikler ve ozet degerler, secilen filtrelere gore otomatik olarak guncellenir.

---

## IOC Arama Modulu

Dashboard'un alt kisminda yer alan **IOC Search Module** bolumu, kullanicinin belirli bir IP adresi veya SHA256 hash degerini arayarak ilgili saldiri kayitlarini bulmasini saglar.

- Arama, `ioc_ip` ve `ioc_hash` alanlarinin her ikisinde de gerceklestirilir.
- Eslesen kayitlar tum alanlariyla birlikte bir tabloda gosterilir.
- Eslesme bulunamazsa: **"No IOC record found."** mesaji goruntulenir.
- IOC aramasi, filtrelerden bagimsiz olarak yuklenen veri setinin tamami uzerinde calisir.

---

## Proje Yapisi

```
ransomware-monitoring-dashboard/
├── app.py                    # Ana Streamlit dashboard uygulamasi
├── data/                     # Docker volume icin veri klasoru
├── src/
│   ├── __init__.py
│   ├── data_generator.py     # Simulasyon veri uretici (opsiyonel/test)
│   └── utils.py              # Yardimci fonksiyonlar
├── Dockerfile                # Docker imaj tanimi
├── docker-compose.yml        # Docker Compose yapilandirmasi
├── .dockerignore             # Docker build dislamalari
├── README.md                 # Bu dosya
└── requirements.txt          # Python bagimliliklari
```

---



## Lisans

Bu proje egitim ve demonstrasyon amaclidir.

---

## Gelistirici Notlari

- Uygulama **otomatik olarak sahte veri uretmez**.
- Yalnizca kullanicinin yukledigi CSV veya XLSX dosyalari analiz edilir.
- Docker kullanarak uygulamayi herhangi bir ortamda calistirabilirsiniz.
- `src/data_generator.py` dosyasi yalnizca test amacli veri uretimi icin saklanmistir; dashboard tarafindan otomatik olarak cagrilmaz.


## Veri Kaynağı Açıklaması

Bu projede kullanılan veri seti, açık kaynaklardan toplanan ransomware olaylarına ait bilgiler kullanılarak hazırlanmıştır. Ana veri kaynağı olarak **ransomware.live** platformundan yararlanılmıştır. Bu platform üzerinden ransomware grupları, hedef alınan kurumlar, saldırı tarihleri, ülke bilgileri ve sektör bilgileri incelenmiştir.

Veri setindeki ek teknik bilgiler ise internet üzerinde yapılan detaylı açık kaynak araştırmaları sonucunda elde edilmiştir. IOC bilgileri, hash değerleri, IP adresleri, TTP’ler, saldırı vektörleri ve MITRE ATT&CK teknikleri; siber güvenlik haberleri, tehdit istihbaratı raporları, güvenlik blogları ve olay analizleri incelenerek manuel olarak derlenmiştir.

Toplanan veriler proje kapsamında temizlenmiş, standartlaştırılmış ve dashboard üzerinde kullanılabilecek hale getirilmiştir. Farklı kaynaklardan elde edilen bilgiler tek bir Excel dosyasında birleştirilmiş ve aşağıdaki alanlara göre düzenlenmiştir:

- date
- ransomware_group
- country
- target_sector
- attack_vector
- technique
- severity
- ioc_ip
- ioc_hash

MITRE ATT&CK teknikleri ve saldırı vektörleri, olay açıklamalarında geçen teknik detaylara göre eşleştirilmiştir. IOC ve hash bilgileri yalnızca açık kaynaklarda erişilebildiği durumlarda eklenmiştir. Bazı olaylarda tüm teknik detaylara ulaşılamadığı için ilgili alanlar eksik bırakılmış veya yalnızca doğrulanabilen bilgiler kullanılmıştır.

Bu veri seti eğitim, analiz ve ransomware olaylarını görselleştirme amacıyla hazırlanmıştır. Veriler açık kaynaklardan elde edilmiş olup herhangi bir gizli, özel veya yetkisiz bilgi içermemektedir.
