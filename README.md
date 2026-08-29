# 📱 Kaydırma Arkeolojisi (Feed-to-Life)

**Samsung Innovation Campus Generative AI Hackathon Projesi**

Bu proje, dijital bağımlılık sorununa odaklanmaktadır. Kullanıcıların kaydettiği/beğendiği içerikleri bir "tüketim" değil, **"karşılanmamış bir ihtiyaç kanıtı"** olarak okur ve yapay zeka desteğiyle bu ihtiyacı ekran dışında karşılayacak **tek bir yapıcı mikro-eylem** önerir.

---

## 👥 Ekip Rolleri ve Branch (Dal) Yapısı

Çakışmaları (merge conflict) önlemek için herkes kendi branch'inde çalışacaktır:

- **`main`**: Yalnızca onaylanmış, çalışan kodlar burada durur. Doğrudan bu branch'e kod yazmak **YASAKTIR**.
- **`feature/ui`**: Kişi B (Streamlit UI)
- **`feature/data`**: Kişi A (Veri manipülasyonu, Mock JSON, Backend)
- **`feature/ai`**: Kişi C (Prompt yönetimi, API çağrıları)

---

## 🛠 Git Kullanım Rehberi (Adım Adım)

### 1. Repoyu Bilgisayarına İndir (Klonla)

İlk defa projeye başlarken terminali (Command Prompt / VS Code Terminal) açıp şu komutu çalıştırın:

```bash
git clone https://github.com/yusufcanzdemir/sic_hackathon_14
cd sic_hackathon_14
```

---

### 2. Kendi Çalışma Alanını (Branch) Oluştur

`main` dalında çalışmadığından emin olmak için kendi dalını oluştur ve oraya geç:

```bash
# Sadece ilk seferde oluşturmak için (-b):
git checkout -b feature/kendi-rolun

# Örneğin:
git checkout -b feature/data
```

---

### 3. Kodunu Yaz ve Değişiklikleri Kaydet

Kendi kodlarını yazdın, test ettin ve her şey çalışıyor. Şimdi bunları GitHub'a gönderme zamanı:

```bash
# 1. Tüm değişiklikleri sahneye ekle
git add .

# 2. Ne yaptığını anlatan kısa bir mesajla kaydet
git commit -m "feat: Ornek mock datalar eklendi"

# VEYA:
git commit -m "fix: Buton hatasi duzeltildi"

# 3. Kendi branch'ini GitHub'a (uzak sunucuya) gönder
git push origin feature/kendi-rolun
```

---

### 4. Kodları Birleştirme (Pull Request)

Kendi işini bitirdiğinde kodlarını `main` ile birleştirmek için **terminali kullanma**.

1. GitHub web sitesine gir.
2. **"Compare & pull request"** butonuna bas.
3. Ekip arkadaşlarına haber ver.
4. Kodunu ekip arkadaşlarının incelemesine (code review) gönder.
5. Onaylandıktan sonra Pull Request'i `main` branch'ine birleştirin.

> **Önemli:** `main` branch'ine doğrudan `push` yapılmayacaktır.

---

### 5. Başkasının Yazdığı Yeni Kodları Kendi Bilgisayarına Alma

Diyelim ki arayüz kodları `main` branch'ine eklendi. Bu yeni kodları kendi bilgisayarına çekmek için şu adımları izle:

```bash
# 1. Ana branch'e geç
git checkout main

# 2. En güncel kodları indir
git pull origin main

# 3. Kendi branch'ine geri dön
git checkout feature/kendi-rolun

# 4. Main'deki yenilikleri kendi branch'ine entegre et
git merge main
```

> **Not:** Eğer çakışma (conflict) çıkarsa VS Code üzerinden kabul edilecek kodları seçip dosyaları kaydedin. Ardından:

```bash
git add .
git commit -m "fix: merge conflict cozuldu"
```

---

## 🚀 Projeyi Bilgisayarda Çalıştırma (Kurulum)

Projeyi local ortamınızda çalıştırmak için aşağıdaki adımları sırasıyla uygulayın.

### 1. Sanal ortam (venv) oluştur

Proje klasörünün terminalde açık olduğundan emin olun:

```bash
python -m venv venv
```

### 2. Sanal ortamı aktif et

**Windows (CMD):**

```bash
venv\Scripts\activate
```

**Windows (PowerShell):**

```powershell
venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
source venv/bin/activate
```

> Sanal ortam başarıyla aktif olduğunda terminal satırının başında genellikle `(venv)` ibaresini görürsünüz.

### 3. Gerekli kütüphaneleri yükle

Sanal ortam aktifken:

```bash
pip install -r requirements.txt
```

### 4. Streamlit arayüzünü başlat

```bash
streamlit run app.py
```

### 5. İşiniz bittiğinde sanal ortamı kapat

```bash
deactivate
```

> **Not:** Projeyi her tekrar açtığınızda `venv` oluşturmanız gerekmez. Sadece sanal ortamı tekrar aktif edip projeyi çalıştırmanız yeterlidir.

---

## 📁 Önerilen Proje Yapısı

Projenin ilerleyen aşamalarında aşağıdaki yapının kullanılması önerilir:

```text
sic_hackathon_14/
│
├── app.py
├── requirements.txt
├── README.md
│
├── data/
│   └── mock_data.json
│
├── ai/
│   ├── prompts.py
│   └── api.py
│
└── utils/
    └── data_processing.py
```

---

## 🎯 Projenin Temel Akışı

```text
Kullanıcının Kaydettiği / Beğendiği İçerikler
                    ↓
              Veri Analizi
                    ↓
          Ortak İlgi / İhtiyaç Tespiti
                    ↓
             Yapay Zeka Analizi
                    ↓
       Ekran Dışı Mikro-Eylem Önerisi
                    ↓
          Kullanıcıya Tek Öneri
```

Amaç, kullanıcıya daha fazla içerik tüketmesini önermek değil; **ekran başında oluşan ilgiyi gerçek hayattaki küçük ve uygulanabilir bir eyleme dönüştürmektir.**