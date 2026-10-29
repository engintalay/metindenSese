# Metinden Sese

Metni sese çeviren, yerelde çalışan ücretsiz bir web uygulaması. Bireysel kullanım için tasarlandı.

- **Diller:** Türkçe, Almanca, İspanyolca, İngilizce
- **Motorlar:**
  - **Piper:** Hızlı, CPU'da çalışır. Varsayılan olarak yanında tutulur.
  - **XTTS v2:** Daha doğal ses. CPU'da yavaştır, NVIDIA GPU varsa CUDA ile hızlanır.
- **Çıktı:** WAV (tarayıcıda oynatma ve indirme)
- **Port:** 10001, ağdaki diğer makinelerden de erişilebilir

## Kurulum

Python 3.11 gerekir. Aşağıdaki adımlar [uv](https://docs.astral.sh/uv/) ile örneklenmiştir.

```bash
uv python install 3.11
uv venv --python 3.11 .venv
uv pip install --python .venv/bin/python -r requirements.txt
```

### Ses modelleri

Piper modellerini [rhasspy/piper-voices](https://huggingface.co/rhasspy/piper-voices) deposundan `models/` klasörüne indirin:

- `tr/tr_TR/dfki/medium/tr_TR-dfki-medium.onnx` (+ `.onnx.json`)
- `de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx` (+ `.onnx.json`)
- `es/es_ES/davefx/medium/es_ES-davefx-medium.onnx` (+ `.onnx.json`)
- `en/en_US/lessac/medium/en_US-lessac-medium.onnx` (+ `.onnx.json`)

XTTS v2 modelini `models/xtts_v2/` klasörüne indirin:

```bash
COQUI_TOS_AGREED=1 .venv/bin/python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='coqui/XTTS-v2', local_dir='models/xtts_v2', allow_patterns=['*.json','*.pth','*.pth.tar','*.wav'])"
```

XTTS v2 lisansı (Coqui Public Model License) ticari olmayan kullanım içindir.

## Çalıştırma

```bash
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 10001
```

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
| POST | `/api/speak` | `{"text": "...", "lang": "tr", "engine": "piper"}` → WAV |

Üretilen dosyalar `outputs/` klasörüne kaydedilir.

## Notlar

- XTTS v2 CPU'da uzun metinlerde birkaç dakika sürebilir. İlk istekte model yüklenir.
- Metin en fazla 5000 karakter olabilir.
- Modeller ve çıktılar git'e eklenmez.
