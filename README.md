# Ba Nghìn Từ

Ứng dụng học từ vựng tiếng Anh cho người Việt. Một bản build phục vụ **cả web lẫn app**:
mở bằng trình duyệt là web, cài ra màn hình chính là app chạy toàn màn hình và offline.

- **3.669 mục từ** — phủ **100% danh sách Oxford 3000** (A1 897 · A2 792 · B1 691 · B2 598),
  cộng 566 từ mở rộng có gắn nhãn riêng
- **40 chủ đề, chia nhỏ thành 192 chủ đề con theo nghĩa** (mỗi chủ đề con 9–30 từ) để dễ học,
  dễ tập trung — ví dụ *Con người & ngoại hình* → Con người & giới tính · Tuổi tác · Dáng người ·
  Khuôn mặt · Tóc & làn da · Nhận xét vẻ ngoài · Ăn mặc & chăm chút
- **4 kỹ năng**: thẻ ghi nhớ, nghe hiểu, luyện nói (nhận dạng giọng), luyện viết
- **Lặp lại ngắt quãng** kiểu Anki: từ mới học theo bước 1 phút / 10 phút ngay trong phiên, thuộc rồi ôn theo ngày (Khó < Tốt < Dễ)
- **50 chuyên đề ngữ pháp** A1→C1, 300 bài tập 4 dạng
- **Lộ trình luyện thi** TOEIC / IELTS sinh theo mục tiêu và quỹ thời gian
- **Hội thoại theo chủ đề** lấy nguyên văn từ kho DailyDialog: đọc & nghe hai giọng, đóng vai
  nói vào micro, điền từ. Mỗi đoạn mang thêm từ mới, ít lặp (hiện có chủ đề 1: 44 đoạn, 96/102 từ)
- **869 ảnh minh hoạ** thật, phần còn lại dùng biểu tượng
- Chạy hoàn toàn phía trình duyệt — **không cần máy chủ ứng dụng, không có cơ sở dữ liệu**

---

## Chạy thử tại chỗ

```bash
cd pwa
python -m http.server 8777        # hoặc: npx serve -l 8777
# mở http://localhost:8777
```

`localhost` được trình duyệt coi là nguồn an toàn, nên service worker và nút cài app
hoạt động đầy đủ ngay cả khi chưa có HTTPS.

## Dựng lại từ nguồn

```bash
./build.sh            # Linux / macOS
build.bat             # Windows
```

Chuỗi việc: `get_fonts.py` (lần đầu, tải phông về tự host) → `sprites.py` (ghép ảnh) →
`build.py` (nhúng dữ liệu vào HTML) → `make_icons.py` → `make_pwa.py` (xuất `pwa/`).

---

## Deploy lên server

Thư mục cần đưa lên là **`pwa/`** — 9,7 MB, toàn tệp tĩnh. Không cần Node, PHP hay
database. Không cần rewrite rule cho SPA vì app không dùng định tuyến theo URL.

### Ba điều bắt buộc

| Việc | Vì sao |
|---|---|
| **Phải có HTTPS** | Thiếu HTTPS thì service worker không đăng ký được, không cài được app, và micro (luyện nói) bị chặn. Ngoại lệ duy nhất là `localhost`. |
| **`sw.js` không được cache** | Trình duyệt cache service worker thì app sẽ **không bao giờ nhận bản cập nhật**. |
| **Bật gzip/brotli** | `index.html` nặng 1.144 KB, nén xuống còn **384 KB** — giảm 66%. |

### nginx

```nginx
server {
    listen 443 ssl http2;
    server_name vocab.example.com;
    root /var/www/banghintu;      # trỏ vào nội dung thư mục pwa/
    index index.html;

    gzip on;
    gzip_types text/html text/css application/javascript application/manifest+json image/svg+xml;
    gzip_min_length 1024;

    # Service worker: tuyệt đối không cache
    location = /sw.js {
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        expires off;
    }

    # Trang chính: luôn hỏi lại server
    location = /index.html {
        add_header Cache-Control "no-cache";
    }

    # Manifest cần đúng kiểu nội dung
    location = /manifest.webmanifest {
        types { }
        default_type application/manifest+json;
        add_header Cache-Control "public, max-age=3600";
    }

    # Ảnh, icon và phông chữ đều có tên gắn mã băm -> cache dài
    location ~* ^/(img|icons|fonts)/ {
        expires 30d;
        add_header Cache-Control "public, max-age=2592000, immutable";
    }

    location / { try_files $uri $uri/ =404; }
}
```

### Apache (`.htaccess` đặt trong `pwa/`)

```apache
AddType application/manifest+json .webmanifest

<Files "sw.js">
    Header set Cache-Control "no-cache, no-store, must-revalidate"
</Files>
<Files "index.html">
    Header set Cache-Control "no-cache"
</Files>
<FilesMatch "\.(jpg|png|woff2)$">
    Header set Cache-Control "public, max-age=2592000, immutable"
</FilesMatch>

<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html application/javascript application/manifest+json
</IfModule>
```

### Caddy

```
vocab.example.com {
    root * /var/www/banghintu
    encode gzip zstd
    header /sw.js Cache-Control "no-cache, no-store, must-revalidate"
    header /index.html Cache-Control "no-cache"
    header /img/* Cache-Control "public, max-age=2592000, immutable"
    header /icons/* Cache-Control "public, max-age=2592000, immutable"
    header /fonts/* Cache-Control "public, max-age=2592000, immutable"
    file_server
}
```

### Cài lên điện thoại sau khi deploy

- **Android / Chrome** — mở trang, Chrome hiện thanh *"Cài ứng dụng"*, hoặc vào
  **Cài đặt → Cài ra màn hình chính** trong chính app.
- **iPhone / Safari** — bắt buộc dùng Safari: **Chia sẻ → Thêm vào MH chính**.
  (iOS không cho trình duyệt khác cài PWA.)

Cài xong: có icon riêng, mở toàn màn hình không thanh địa chỉ, và **chạy được khi mất mạng**
vì service worker đã lưu sẵn 138 tệp gồm cả ảnh và phông chữ.

### Đặt ở thư mục con cũng được

`start_url` và `scope` trong manifest đều là đường dẫn tương đối (`./`), nên đặt tại
`https://ten-mien/vocab/` vẫn chạy, không cần sửa gì.

---

## Dữ liệu người học

### Không gọi ra bên ngoài

Bản trong `pwa/` **không gửi request nào ra ngoài tên miền của bạn**: không CDN, không
Google Fonts, không analytics. Phông chữ đã tải về `pwa/fonts/` (15 tệp woff2, 334 KB,
chỉ giữ bộ chữ Latin và tiếng Việt). Nhờ vậy mất mạng app vẫn hiển thị đúng phông, và
trình duyệt người dùng không kết nối tới máy chủ bên thứ ba nào.

Muốn tải lại phông: `python build/get_fonts.py`.

Tiến độ lưu bằng `localStorage`, ảnh người dùng tự thêm lưu bằng IndexedDB — **nằm
trong máy người học, không gửi đi đâu**. Vì thế server không cần database và không giữ
dữ liệu cá nhân nào.

Đồng bộ nhiều thiết bị chỉ hoạt động ở bản chạy trên claude.ai. Trên server riêng, app tự
lui về lưu cục bộ. Muốn chuyển máy thì dùng **Cài đặt → Sao lưu tiến độ** để tải tệp
JSON, rồi **Khôi phục** ở máy kia.

---

## Cấu trúc

```
app/shell.html        Vỏ ứng dụng: giao diện + toàn bộ logic (mẫu, chưa có dữ liệu)
data/topics/t01..t40  40 chủ đề gốc (3.669 mục từ) — dữ liệu từ, không đổi khi chia lại
build/subtopics.json  Cách tách mỗi chủ đề thành chủ đề con theo nghĩa (sửa ở đây để chia lại)
data/ex2/             Câu ví dụ thứ hai + bản dịch, kèm nhãn nguồn
data/grammar/         50 chuyên đề ngữ pháp, 300 bài tập
data/exam.json        Cấu trúc TOEIC / IELTS, mẹo từng phần, thư viện nhiệm vụ
data/dialogues/       Hội thoại theo chủ đề (DailyDialog) + bản dịch + từ đúng nghĩa từng đoạn
build/*.py            Script dựng, tải ảnh, đối chiếu Oxford, chọn câu ví dụ
build/smoke*.js       Kiểm thử tự động (101 mục)
pwa/                  ★ Bản deploy — đây là thứ đưa lên server
```

### Kiểm thử

```bash
npm install            # chỉ cần jsdom
node build/smoke.js            # 46 mục: từ vựng, lặp lại ngắt quãng, đọc chậm, 4 kỹ năng, tra từ
node build/smoke_grammar.js    # 10 mục: ngữ pháp, 4 dạng bài, chấm điểm
node build/smoke_plan.js       # 13 mục: lộ trình, kiểm tra trình độ
node build/smoke_dialog.js     # 34 mục: hội thoại, chọn giọng A/B, từ mới không lặp, đóng vai, điền từ
```

### Tải lại dữ liệu nguồn (đã loại khỏi git vì nặng)

```bash
python build/get_corpus.py     # kho câu Tatoeba (~106 MB)
python build/get_oxford.py     # PDF Oxford 3000 gốc
python build/compare_oxford.py # đối chiếu độ phủ danh sách Oxford
```

### Chia chủ đề con

Sửa `build/subtopics.json` (mỗi chủ đề con là một danh sách từ, cách nhau bằng `|`), rồi kiểm tra:

```bash
python build/lessons.py            # báo lỗi nếu có từ chưa xếp, xếp hai lần hoặc viết sai
```

Chủ đề không có trong tệp đó (các danh sách danh từ / động từ / tính từ B1–B2 xếp theo vần) được
chia đều, mỗi phần ≤ 25 từ.

### Thêm hội thoại cho một chủ đề

```bash
python build/pick_dialogs.py t02   # chọn đoạn: nhiều từ mới nhất, ít lặp nhất (tự tải kho ~4 MB)
# đọc build/dlg_review/t02.txt, ghi đoạn loại / từ sai nghĩa vào build/dlg_review/t02.json, chạy lại
python build/dialogues.py t02      # xuất data/dialogues/t02.json (giữ bản dịch đã có)
```

---

## Nguồn và giấy phép

| Thành phần | Nguồn |
|---|---|
| Danh sách 3000 từ | **The Oxford 3000™** — Oxford University Press. Dùng làm danh sách đối chiếu và nhãn cấp độ; nghĩa tiếng Việt, IPA và chú giải trong app là nội dung riêng. |
| Câu ví dụ thứ hai | **Tatoeba** — CC BY 2.0 FR. Câu tiếng Anh lấy nguyên từ kho; bản dịch tiếng Việt được đối chiếu lại, mỗi câu có ghi nhãn nguồn trong app. |
| Hội thoại | **DailyDialog** (Li và cộng sự, IJCNLP 2017) — **CC BY-NC-SA 4.0, chỉ dùng phi thương mại**. Câu tiếng Anh giữ nguyên (chỉ chuẩn hoá dấu câu và sửa vài lỗi gõ ghi trong `build/dialogues.py`); bản dịch tiếng Việt do dự án biên dịch. |
| Ảnh minh hoạ | **Wikipedia / Wikimedia** — ảnh đại diện bài viết, có ghi tên bài trong bảng chi tiết từ. |
| Phông chữ | **Bricolage Grotesque, IBM Plex Mono, Source Sans 3** — SIL Open Font License, tải về tự host trong `pwa/fonts/`. |
| Giọng đọc | Web Speech API — giọng cài sẵn trong trình duyệt và hệ điều hành người dùng. |

Bộ ngữ pháp, lộ trình luyện thi và toàn bộ mã nguồn là nội dung riêng của dự án.
