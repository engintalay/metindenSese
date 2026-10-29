# Metinden Sese

Metni sese çeviren, yerelde çalışan ücretsiz bir web uygulaması. Bireysel kullanım için tasarlandı.

- **Diller:** Türkçe, Almanca, İspanyolca, İngilizce
- **Motorlar:**
  - **Piper:** Hızlı, CPU'da çalışır. Varsayılan olarak yanında tutulur.
  - **XTTS v2:** Daha doğal ses. CPU'da yavaştır, NVIDIA GPU varsa CUDA ile hızlanır.
- **Çıktı:** WAV (tarayıcıda oynatma ve indirme)
- **Port:** 10001, ağdaki diğer makinelerden de erişilebilir

## Hızlı başlangıç

```bash
scripts/install.sh          # Python 3.11 ortamı ve bağımlılıklar
scripts/download_models.sh  # Piper ve XTTS v2 modelleri
scripts/run.sh              # Sunucuyu başlatır
```

`install.sh` [uv](https://docs.astral.sh/uv/) varsa onu, yoksa sistemdeki `python3.11`'i kullanır. Betikler tekrar çalıştırılabilir, var olan dosyaları atlar.

## Ses modelleri

`scripts/download_models.sh` aşağıdakileri `models/` altına indirir:

- Piper: `tr_TR-dfki-medium`, `de_DE-thorsten-medium`, `es_ES-davefx-medium`, `en_US-lessac-medium` (`.onnx` + `.onnx.json`)
- XTTS v2: `models/xtts_v2/`

XTTS v2 lisansı (Coqui Public Model License) ticari olmayan kullanım içindir.

## Çalıştırma

```bash
scripts/run.sh
```

Port ve adres ortam değişkeniyle değiştirilebilir: `PORT=10002 HOST=127.0.0.1 scripts/run.sh`. Varsayılan `0.0.0.0:10001`.

- Bu makineden: `http://localhost:10001`
- Ağdaki diğer makinelerden: `http://<bu-makinenin-IP>:10001`

## Ayarlar

`app/config.py` içinde:

- `DEVICE`: `"auto"` (varsayılan), `"cpu"` veya `"cuda"`. `auto` modunda NVIDIA GPU algılanırsa CUDA kullanılır, yoksa CPU.
- `PORT`, `HOST`: Sunucu portu ve adresi.
- `LANGUAGES`: Dil kodlarından model dosyalarına eşleme.
- `XTTS_SPEAKER`: XTTS için kullanılan yerleşik konuşmacı.

Not: AMD APU (Vulkan) desteklenmiyor. Bu tür donanımda CPU kullanılır.

## API

| Yöntem | Uç | Açıklama |
|---|---|---|
| GET | `/` | Web arayüzü |
| GET | `/api/languages` | Desteklenen diller |
| GET | `/api/engines` | Motorlar ve çalışma cihazı |
| POST | `/api/speak` | `{"text": "...", "lang": "tr", "engine": "piper"}` → WAV (senkron) |
| POST | `/api/jobs` | Aynı gövde. Arka planda üretim başlatır, `id` döner |
| GET | `/api/jobs/{id}` | Durum: `queued`, `loading`, `running`, `done`, `error`. İlerleme (`done`/`total`), geçen süre ve tahmini kalan süre |
| GET | `/api/jobs/{id}/audio` | Tamamlanan WAV dosyası |

İstek gövdesindeki `settings` alanı isteğe bağlıdır. Verilmeyen ayarlar varsayılanla çalışır:

| Ayar | Aralık | Varsayılan | Motor | Açıklama |
|---|---|---|---|---|
| `speed` | 0.5 – 1.5 | 1.0 | İkisi de | Konuşma hızı |
| `noise_scale` | 0 – 1.5 | 0.667 | Piper | Ses doğallığı çeşitliliği |
| `noise_w_scale` | 0 – 1.5 | 0.8 | Piper | Konuşma ritmi çeşitliliği |
| `temperature` | 0.1 – 1.5 | 0.75 | XTTS | Yaratıcılık |
| `top_p` | 0.1 – 1.0 | 0.85 | XTTS | Örnekleme genişliği |

Örnek: `{"text": "...", "lang": "tr", "engine": "piper", "settings": {"speed": 1.2}}`

Üretilen dosyalar `outputs/` klasörüne kaydedilir.

## Notlar

- XTTS v2 CPU'da uzun metinlerde birkaç dakika sürebilir. İlk istekte model yüklenir.
- Metin en fazla 50 000 karakter olabilir (`app/config.py` içinde `MAX_TEXT_LENGTH`). Uzun metinler cümle bazlı parçalara bölünür, parça parça üretilip tek WAV'da birleştirilir.
- Arayüzde ilerleme; parça sayısı, geçen süre ve tahmini kalan süre gösterilir.
- Üretim tek bir işçi üzerinden sıralı yapılır, aynı anda birden fazla iş bekleyebilir.
- Modeller ve çıktılar git'e eklenmez.
