# Geliştirme Kuralları

## Git
- Her aşama tamamlandığında commit atılır, ardından push yapılır.
- Commit mesajları kısa ve açıklayıcı olmalı. Örnek: `feat: piper motoru eklendi`, `chore: git iskeleti`.
- Commit öncesi `git status` ile yalnızca ilgili dosyaların eklendiği kontrol edilir.
- `models/`, `outputs/`, sanal ortam (`.venv/`) ve `__pycache__/` git'e eklenmez (`.gitignore`).
- Doğrudan `main` dalına push yapılır (bireysel proje). Gerekirse dal kuralı sonradan değiştirilebilir.
- Geri alınamaz işlemler (`push --force`, `reset --hard`) kullanıcı onayı olmadan yapılmaz.

## Kod
- Yorumlar yalnızca gerekli olduğunda eklenir.
- Motorlar ortak bir arayüz üzerinden çalışır, yeni motor eklemek kolay olmalı.
- Ayarlar (port, host, dil-model eşlemesi) `app/config.py` içinde tutulur, kodda sabit değer yazılmaz.

## Aşama akışı
1. Aşama için kod yazılır.
2. Uygulama çalıştırılarak test edilir.
3. `git status` kontrol edilir.
4. Commit ve push yapılır.
5. Sonraki aşamaya geçilir.
