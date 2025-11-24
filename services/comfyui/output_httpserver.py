import os
import threading
import http.server
import socketserver


# -----------------------------
# 設定
# -----------------------------
PORT = 8888

OUTPUT_DIR = os.path.abspath(
    "/workspace/output"  # ComfyUI の出力フォルダパスに合わせる
)


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
        # ギャラリーページを返すカスタムハンドラ
        class GalleryHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, directory=None, **kwargs):
                super().__init__(*args, directory=directory, **kwargs)

            def list_images_html(self):
                try:
                    files = sorted(
                        f for f in os.listdir(os.getcwd())
                        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))
                    )
                except Exception:
                    files = []

                # シンプルなギャラリー（遅延読み込みは IntersectionObserver を使用）
                imgs_html = "\n".join(
                    f'<a href="{file}" target="_blank"><img data-src="{file}" alt="{file}" class="lazy"></a>'
                    for file in files
                ) or "<p>No images found.</p>"

                html = f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>ComfyUI Output Gallery</title>
  <style>
    body{{font-family:system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial; padding:16px;}}
    .grid{{display:grid; grid-template-columns:repeat(auto-fill,minmax(180px,1fr)); gap:12px;}}
    .grid a{{display:block; overflow:hidden; border-radius:8px; background:#111; padding:4px;}}
    .grid img{{width:100%; height:180px; object-fit:cover; display:block; background:#222;}}
  </style>
</head>
<body>
  <h1>ComfyUI Output Gallery</h1>
  <p>Images are lazy-loaded. Click to open full image.</p>
  <div class="grid">
    {imgs_html}
  </div>
  <script>
    // IntersectionObserver を使った遅延読み込み
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
      // フォールバック: すべてロード
      lazyImgs.forEach(img => img.src = img.dataset.src);
    }}
  </script>
</body>
</html>
"""
                return html

            def do_GET(self):
                # ルートまたは index.html へのアクセスでギャラリーページを返す
                if self.path in ('/', '/index.html'):
                    content = self.list_images_html().encode('utf-8')
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.send_header('Content-Length', str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                    return
                # それ以外は通常のファイル配信
                return super().do_GET()

        handler_factory = lambda *args, **kwargs: GalleryHTTPRequestHandler(*args, directory=self.directory, **kwargs)

        with socketserver.TCPServer(("127.0.0.1", self.port), handler_factory) as httpd:
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
    start_server_if_needed.server_started = True # type: ignore


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
