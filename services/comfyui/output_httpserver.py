import os
import threading
import http.server
import socketserver
import math
from urllib.parse import urlparse, parse_qs


# -----------------------------
# 設定
# -----------------------------
PORT = 8888

OUTPUT_DIR = os.path.abspath(
    "/workspace/output"  # ComfyUI の出力フォルダパスに合わせる
)

PAGE_SIZE = 64


# -----------------------------
# HTTP サーバスレッド
# -----------------------------
class ThreadedHTTPServer(threading.Thread):
    def __init__(self, directory, port):
        super().__init__()
        self.directory = directory
        self.port = port
        self.daemon = True

    def run(self):
        os.chdir(self.directory)

        class GalleryHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, directory=None, **kwargs):
                super().__init__(*args, directory=directory, **kwargs)

            def list_images_html(self, page=1):
                try:
                    files = sorted(
                        f for f in os.listdir(os.getcwd())
                        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))
                    )
                except Exception:
                    files = []

                # ファイル名降順 (Z→A)
                files = sorted(files, reverse=True)

                total = len(files)
                page = max(1, min(page, max(1, math.ceil(total / PAGE_SIZE) if PAGE_SIZE > 0 else 1)))
                start = (page - 1) * PAGE_SIZE
                end = start + PAGE_SIZE
                page_files = files[start:end]

                imgs_html = "\n".join(
                    f'<a href="{file}" target="_blank"><img data-src="{file}" alt="{file}" class="lazy"></a>'
                    for file in page_files
                ) or "<p>No images found.</p>"

                total_pages = max(1, math.ceil(total / PAGE_SIZE)) if PAGE_SIZE > 0 else 1

                # ページナビ
                def page_link(p, text=None):
                    text = text or str(p)
                    return f'<a href="/?page={p}">{text}</a>'

                nav_parts = []
                if page > 1:
                    nav_parts.append(page_link(page - 1, "Prev"))
                # 簡易に先頭・直近・最後のページリンクを作る（多すぎないように）
                for p in range(max(1, page - 2), min(total_pages, page + 2) + 1):
                    if p == page:
                        nav_parts.append(f'<strong>{p}</strong>')
                    else:
                        nav_parts.append(page_link(p))
                if page < total_pages:
                    nav_parts.append(page_link(page + 1, "Next"))
                nav_html = " | ".join(nav_parts) or ""

                html = f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>ComfyUI Output Gallery</title>
  <style>
    body{{font-family:system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial; padding:16px;}}
    .meta{{margin-bottom:8px;color:#666;}}
    .grid{{display:grid; grid-template-columns:repeat(auto-fill,minmax(180px,1fr)); gap:12px;}}
    .grid a{{display:block; overflow:hidden; border-radius:8px; background:#111; padding:4px;}}
    .grid img{{width:100%; height:180px; object-fit:cover; display:block; background:#222;}}
    .pager{{margin:12px 0;padding:8px;background:#f5f5f5;border-radius:6px;}}
    .pager a{{margin:0 6px;text-decoration:none;color:#06c;}}
    .pager strong{{margin:0 6px;}}
  </style>
</head>
<body>
  <h1>ComfyUI Output Gallery</h1>
  <div class="meta">Total images: {total} — Page {page} / {total_pages}</div>
  <div class="pager">{nav_html}</div>
  <div class="grid">
    {imgs_html}
  </div>
  <div class="pager">{nav_html}</div>
  <script>
    const lazyImgs = [].slice.call(document.querySelectorAll('img.lazy'));
    if ('IntersectionObserver' in window) {{
      let obs = new IntersectionObserver((entries, observer) => {{
        entries.forEach(entry => {{
          if (entry.isIntersecting) {{
            const img = entry.target;
            img.src = img.dataset.src;
            img.classList.remove('lazy');
            observer.unobserve(img);
          }}
        }});
      }}, {{rootMargin: '200px 0px'}});
      lazyImgs.forEach(img => obs.observe(img));
    }} else {{
      lazyImgs.forEach(img => img.src = img.dataset.src);
    }}
  </script>
</body>
</html>
"""
                return html

            def do_GET(self):
                # クエリパラメータから page を取得
                parsed = urlparse(self.path)
                qs = parse_qs(parsed.query)
                page_vals = qs.get("page", [])
                try:
                    page = int(page_vals[0]) if page_vals else 1
                except Exception:
                    page = 1

                # ルートまたは index.html へのアクセスでギャラリーページを返す
                if parsed.path in ('/', '/index.html'):
                    content = self.list_images_html(page=page).encode('utf-8')
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.send_header('Content-Length', str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                    return
                # それ以外は通常のファイル配信（ファイルパスはそのまま）
                # path にクエリが付いている場合は取り除いて渡す
                self.path = parsed.path
                return super().do_GET()

        handler_factory = lambda *args, **kwargs: GalleryHTTPRequestHandler(*args, directory=self.directory, **kwargs)

        with socketserver.TCPServer(("0.0.0.0", self.port), handler_factory) as httpd:
            print(f"[ComfyUI-Output-HTTPServer] Serving '{self.directory}' at http://127.0.0.1:{self.port}")
            httpd.serve_forever()


# -----------------------------
# ComfyUI 起動時に自動実行
# -----------------------------
def start_server_if_needed():
    if getattr(start_server_if_needed, "server_started", False):
        return

    server = ThreadedHTTPServer(OUTPUT_DIR, PORT)
    server.start()
    start_server_if_needed.server_started = True  # type: ignore


# モジュールインポート時に実行
start_server_if_needed()


# -----------------------------
# ダミーノード（表示用）
# -----------------------------
class OutputFolderHTTPServerAuto:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}}

    RETURN_TYPES = ()
    FUNCTION = "noop"
    CATEGORY = "server"

    def noop(self):
        return ()


NODE_CLASS_MAPPINGS = {
    "OutputFolderHTTPServerAuto": OutputFolderHTTPServerAuto
}
