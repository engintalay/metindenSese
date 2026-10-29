# Metinden Sese (TTS) Uygulaması - Plan

## Amaç
Metni sese çeviren, tamamen yerelde ücretsiz çalışan, web arayüzlü bir uygulama.
Bireysel kullanım. Aynı ağdaki makinelerden erişilebilir.

## Gereksinimler
- Ücretsiz, yerel çalışma (API ücreti yok)
- Diller: Türkçe (tr), Almanca (de), İspanyolca (es), İngilizce (en)
- Motor seçimi: Piper (varsayılan) ve XTTS v2 (isteğe bağlı, daha doğal ses)
- Web arayüzü: metin girişi, dil ve motor seçimi, üret, tarayıcıda oynat, WAV indir
- MP3 zorunlu değil (sonraki aşamaya bırakıldı)
- Port: 10001
- Ağdaki diğer makinelerden erişilebilir (host 0.0.0.0)

## Donanım (tespit edildi)
- GPU: AMD Phoenix1 APU (entegre Radeon). NVIDIA yok, ROCm ile PyTorch güvenilir değil. Hesaplama CPU'da yapılacak.
- CPU: 16 çekirdek
- RAM: 58 GB toplam. Üretim sırasında boş RAM'in yeterli olduğundan emin olunmalı (XTTS v2 için ~4-6 GB).

## Donanım algılama (otomatik)
- Uygulama açılışında NVIDIA GPU var mı kontrol edilir (`nvidia-smi` veya `torch.cuda.is_available()`).
- NVIDIA varsa:
  - XTTS v2: CUDA üzerinde çalışır (`torch` CUDA sürümü).
  - Piper: `onnxruntime-gpu` ile CUDA sağlayıcısı kullanılır, yoksa CPU'ya düşer.
- NVIDIA yoksa (AMD APU dahil): CPU kullanılır. AMD entegre GPU kullanılmaz.
- Seçilen cihaz (cpu/cuda) `GET /api/engines` yanıtında gösterilir, arayüzde bilgi olarak yazılır.
- Ayar `app/config.py` içinde `DEVICE = "auto"` olarak tutulur. Elle `cpu` veya `cuda` seçilebilir.
- Not: `onnxruntime` ile `onnxruntime-gpu` aynı ortamda çakışır. Kurulum buna göre yapılır.

## Vulkan (ertelendi)
- Vulkan destekli TTS araştırıldı (vox-tts/Qwen3-TTS, Kokoro.cpp, OuteTTS). Hiçbiri dört dili (tr, de, es, en) birlikte güvenle karşılamıyor.
- Karar: Şimdilik sadece CPU ve NVIDIA (CUDA) kullanılacak. Vulkan ileride Almanca/İspanyolca/İngilizce için ek motor olarak düşünülebilir.

## Motorlar
| Motor | Kullanım | Notlar |
|---|---|---|
| Piper | Varsayılan | CPU'da hızlı, MIT lisanslı. Modeller: tr_TR, de_DE, es_ES, en_US. Paket: `pip install piper-tts` (OHF-Voice/piper1-gpl). `rhasspy/piper` deposu arşivlenmiş. |
| XTTS v2 | İsteğe bağlı | CPU'da yavaş, uzun metinlerde dakikalar sürebilir. Lisans: CPML (ticari olmayan) |

## Mimari
```
metindenSese/
├── app/
│   ├── main.py          # FastAPI uygulaması, port 10001
│   ├── engines.py       # Piper ve XTTS v2 sarmalayıcıları (ortak arayüz)
│   ├── config.py        # Dil -> model eşlemesi, port, host
│   └── static/
│       └── index.html   # Web arayüzü
├── models/              # Piper ses modelleri (indirilir, git'e eklenmez)
├── outputs/             # Üretilen WAV dosyaları (git'e eklenmez)
├── requirements.txt
├── README.md
├── .gitignore
└── plan.md              # Bu plan (isteğe bağlı olarak repoda tutulabilir)
```

### API uçları
- `GET /` : Web arayüzü
- `GET /api/languages` : Desteklenen diller
- `GET /api/engines` : Kullanılabilir motorlar
- `POST /api/speak` : `{ "text": "...", "lang": "tr", "engine": "piper" }` -> WAV döner

## Çalıştırma
```
uvicorn app.main:app --host 0.0.0.0 --port 10001
```
Erişim: `http://localhost:10001` veya `http://<makine-IP>:10001`

## Aşamalar (her aşama sonunda git commit + push)
1. **Git ve iskelet:** `git init`, `.gitignore`, klasör yapısı, `requirements.txt`, uzak depo bağlantısı
2. **Piper motoru:** Kurulum, 4 dil için modellerin indirilmesi, `engines.py` içinde Piper sarmalayıcı
3. **API:** FastAPI uçları, WAV üretimi, hata yönetimi
4. **Web arayüzü:** `index.html`, motor ve dil seçimi, oynatma ve indirme
5. **XTTS v2:** Kurulum, model indirme, `engines.py` içine ikinci sarmalayıcı, arayüzde motor seçimi
6. **Ağ erişimi ve test:** `0.0.0.0` ile yerel ağdan erişim testi, güvenlik duvarı notu
7. **README ve son kontrol:** Kurulum ve kullanım talimatları

## Kararlar
- Parola/token koruması şimdilik yok. Gerekirse sonra eklenir.
- Güvenlik duvarı ayarlarına dokunulmayacak.
- Uzak depo (remote) şimdilik yok. Kullanıcı adresi sonra ekleyecek. Bu süre içinde commit'ler yerel olarak atılır, push ertelenir. Remote eklendiğinde bekleyen commit'ler push edilir.

## Açık noktalar
- Uzak depo adresi (kullanıcı sonra ekleyecek)
- Uygulamanın ne zaman "olgun" sayılıp paylaşılacağı (kullanıcı kararı)

## Riskler
- XTTS v2 CPU'da yavaş. Arayüzde süre uyarısı gösterilecek.
- Makinede RAM yoğun. Kullanılmayan programlar kapatılmalı.
- Piper'ın Türkçe sesleri doğal sesli motorlara göre daha robotik olabilir.
