# /// script
# dependencies = ["playwright>=1.51,<2"]
# ///
import sys, threading
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from playwright.sync_api import sync_playwright
from product.nz_election.tests.screenshots import Handler, check_page
with sync_playwright() as pw:
    exe = next((Path.home()/'Library/Caches/ms-playwright').glob('chromium_headless_shell-*/chrome-headless-shell-mac-arm64/chrome-headless-shell'))
    b = pw.chromium.launch(executable_path=str(exe))
    for site in sys.argv[1:]:
        s = ThreadingHTTPServer(('127.0.0.1',0), partial(Handler, directory=site))
        threading.Thread(target=s.serve_forever, daemon=True).start()
        origin=f'http://127.0.0.1:{s.server_port}'
        c = b.new_context(viewport={'width':390,'height':844}, reduced_motion='reduce')
        p = c.new_page()
        try:
            check_page(p, origin+'/unattended/nz-election/methods/', Path(site), origin); print(site, 'PASS')
        except AssertionError as e: print(site, 'FAIL', str(e)[:200])
