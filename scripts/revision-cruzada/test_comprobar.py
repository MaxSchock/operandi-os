"""Tests for comprobar.py: one positive and one negative case per check, on temporary files.

Run: python3 -m unittest scripts/revision-cruzada/test_comprobar.py
"""
import json
import os
import sys
import tempfile
import textwrap
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comprobar as c  # noqa: E402


class Base(unittest.TestCase):
    def scan(self, files, puntos=None):
        with tempfile.TemporaryDirectory() as root:
            for rel, text in files.items():
                full = os.path.join(root, rel)
                os.makedirs(os.path.dirname(full), exist_ok=True)
                with open(full, "w", encoding="utf-8") as fh:
                    fh.write(textwrap.dedent(text))
            hallazgos, _ = c.run(root, puntos=puntos)
        return hallazgos

    def hits(self, files, punto):
        return [h for h in self.scan(files, {punto}) if h["punto"] == punto]


class P04(Base):
    def test_py_positive(self):
        h = self.hits({"app/x.py": """
            def f():
                try:
                    return load()
                except Exception:
                    return None
        """}, 4)
        self.assertEqual(len(h), 1)
        self.assertEqual(h[0]["gravedad"], "alta")
        self.assertEqual(h[0]["linea"], 5)

    def test_py_negative_logged(self):
        h = self.hits({"app/x.py": """
            def f():
                try:
                    return load()
                except Exception as exc:
                    log.warning("load failed: %s", exc)
                    return None
        """}, 4)
        self.assertEqual(h, [])

    def test_py_negative_narrow(self):
        h = self.hits({"app/x.py": """
            try:
                import foo
            except ImportError:
                pass
        """}, 4)
        self.assertEqual(h, [])

    def test_js_positive(self):
        h = self.hits({"src/a.ts": """
            async function g() {
              const r = await api().catch(() => null);
              try { await send(); } catch {}
              return r;
            }
        """}, 4)
        self.assertEqual(sorted(x["linea"] for x in h), [3, 4])
        self.assertTrue(all(x["gravedad"] == "alta" for x in h))

    def test_js_negative(self):
        h = self.hits({"src/a.ts": """
            async function g() {
              try { await send(); } catch (e) { logger.error(e); throw e; }
              const s = "catch {}";  // catch {} inside a string and a comment
              return api().catch((e) => report(e));
            }
        """}, 4)
        self.assertEqual(h, [])

    def test_js_best_effort_is_low(self):
        h = self.hits({"src/a.ts": "await worker.terminate().catch(() => {});\n"}, 4)
        self.assertEqual([x["gravedad"] for x in h], ["baja"])


class P06(Base):
    def test_empty_compose_default_with_int_cast(self):
        h = self.hits({
            "svc/docker-compose.yml": "services:\n  a:\n    environment:\n"
                                      "      - INVITE_DAILY_CAP=${INVITE_DAILY_CAP:-}\n",
            "svc/app/config.py": "import os\nCAP = int(os.environ.get('INVITE_DAILY_CAP', '20'))\n",
        }, 6)
        self.assertEqual(len(h), 1)
        self.assertEqual(h[0]["gravedad"], "alta")

    def test_compose_negative(self):
        h = self.hits({
            "svc/docker-compose.yml": "services:\n  a:\n    image: app:1.4.2\n    environment:\n"
                                      "      - CAP=${CAP:-20}\n",
            "svc/app/config.py": "import os\nCAP = int(os.environ.get('CAP', '20'))\n",
        }, 6)
        self.assertEqual(h, [])

    def test_force_without_image_and_latest(self):
        h = self.hits({"deploy.sh": "docker service update --force web\n"
                                    "docker build -t web:latest .\n"}, 6)
        self.assertEqual(sorted(x["linea"] for x in h), [1, 2])

    def test_force_with_image_negative(self):
        h = self.hits({"deploy.sh": "docker service update --force \\\n  --image web:abc123 web\n"},
                      6)
        self.assertEqual(h, [])

    def test_journal_repeated_when(self):
        journal = {"entries": [{"tag": "0001_a", "when": 100}, {"tag": "0002_b", "when": 100}]}
        h = self.hits({"drizzle/meta/_journal.json": json.dumps(journal, indent=1)}, 6)
        self.assertEqual(len(h), 1)
        self.assertIn("0002_b", h[0]["regla"])

    def test_journal_negative(self):
        journal = {"entries": [{"tag": "0001_a", "when": 100}, {"tag": "0002_b", "when": 200}]}
        self.assertEqual(self.hits({"drizzle/meta/_journal.json": json.dumps(journal)}, 6), [])


class P07(Base):
    def test_py_requests_and_while(self):
        h = self.hits({"app/x.py": """
            import requests
            def f():
                return requests.get("https://x")
            def loop():
                while True:
                    work()
        """}, 7)
        self.assertEqual(sorted(x["linea"] for x in h), [4, 6])

    def test_py_negative(self):
        h = self.hits({"app/x.py": """
            import requests
            def f():
                return requests.get("https://x", timeout=10)
            def loop():
                while True:
                    if work():
                        break
        """}, 7)
        self.assertEqual(h, [])

    def test_js_fetch(self):
        h = self.hits({"src/a.ts": 'const r = await fetch("https://api.x/y", { method: "POST" });\n'},
                      7)
        self.assertEqual([x["gravedad"] for x in h], ["media"])

    def test_js_fetch_negative(self):
        h = self.hits({"src/a.ts": 'const r = await fetch("https://api.x/y", '
                                   '{ signal: AbortSignal.timeout(5000) });\n'}, 7)
        self.assertEqual(h, [])

    def test_tests_are_excluded(self):
        h = self.hits({"tests/test_x.py": "import requests\nrequests.get('http://x')\n"}, 7)
        self.assertEqual(h, [])


class P10(Base):
    def test_log_secret_and_environ(self):
        h = self.hits({"app/x.py": """
            import os, logging
            log = logging.getLogger()
            def f(api_key):
                log.info("key %s", api_key)
                print(os.environ)
        """}, 10)
        self.assertEqual(sorted((x["linea"], x["gravedad"]) for x in h), [(5, "media"), (6, "alta")])

    def test_log_negative(self):
        h = self.hits({"app/x.py": """
            import os, logging
            log = logging.getLogger()
            def f(api_key, max_tokens):
                log.info("key set: %s, tokens %d", bool(api_key), max_tokens)
                print(os.environ.get("HOME"))
        """}, 10)
        self.assertEqual(h, [])

    def test_hardcoded_key_is_masked(self):
        fake = "sk-" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4"
        h = self.hits({"src/a.ts": f'const k = "{fake}";\n'}, 10)
        self.assertEqual(len(h), 1)
        self.assertEqual(h[0]["fragmento"], "valor omitido")
        self.assertNotIn(fake, json.dumps(h))

    def test_js_console_token(self):
        h = self.hits({"src/a.ts": "console.log('t', accessToken);\nconsole.log(token.length);\n"},
                      10)
        self.assertEqual([x["linea"] for x in h], [1])


class P11(Base):
    def test_scheduler_without_tz(self):
        h = self.hits({"app/main.py": """
            from apscheduler.schedulers.background import BackgroundScheduler
            s = BackgroundScheduler()
        """}, 11)
        self.assertEqual([x["gravedad"] for x in h], ["alta"])

    def test_scheduler_local_tz_negative(self):
        h = self.hits({"app/main.py": """
            from apscheduler.schedulers.background import BackgroundScheduler
            from apscheduler.triggers.cron import CronTrigger
            s = BackgroundScheduler(timezone="Europe/Madrid")
            s.add_job(f, trigger=CronTrigger(hour=9))
        """}, 11)
        self.assertEqual(h, [])

    def test_js_today_utc(self):
        h = self.hits({"app/page.tsx": "const todayKey = new Date().toISOString().slice(0, 10);\n"},
                      11)
        self.assertEqual(len(h), 1)

    def test_js_today_negative(self):
        h = self.hits({"app/page.tsx": "const k = new Intl.DateTimeFormat('sv', "
                                       "{ timeZone: 'Europe/Madrid' }).format(new Date());\n"}, 11)
        self.assertEqual(h, [])


class P12(Base):
    def test_limit_without_pagination(self):
        h = self.hits({"app/x.ts": """
            export async function list(sb) {
              const { data } = await sb.from("leads").select("*").limit(500);
              return data;
            }
        """}, 12)
        self.assertEqual(len(h), 1)

    def test_limit_with_range_negative(self):
        h = self.hits({"app/x.ts": """
            export async function list(sb, from) {
              const { data } = await sb.from("leads").select("*").range(from, from + 499).limit(500);
              return data;
            }
        """}, 12)
        self.assertEqual(h, [])

    def test_py_sql_limit(self):
        h = self.hits({"app/x.py": """
            def rows(cur):
                cur.execute("SELECT * FROM t ORDER BY id LIMIT 200")
                return cur.fetchall()
        """}, 12)
        self.assertEqual(len(h), 1)

    def test_py_sql_limit_one_and_offset_negative(self):
        h = self.hits({"app/x.py": """
            def one(cur):
                cur.execute("SELECT * FROM t LIMIT 1")
            def page(cur, offset):
                cur.execute("SELECT * FROM t LIMIT 200 OFFSET %s", (offset,))
        """}, 12)
        self.assertEqual(h, [])


class P03(Base):
    def test_webhook_without_account(self):
        h = self.hits({"app/main.py": """
            @app.post("/webhook/unipile")
            async def hook(req):
                body = await req.json()
                return await handle(body)
        """}, 3)
        self.assertEqual(len(h), 1)

    def test_webhook_with_account_negative(self):
        h = self.hits({"app/main.py": """
            @app.post("/webhook/unipile")
            async def hook(req):
                body = await req.json()
                if body.get("account_id") != OUR_ACCOUNT:
                    return {"ignored": True}
                return await handle(body)
        """}, 3)
        self.assertEqual(h, [])


class P03FailOpen(Base):
    def test_fail_open_secret(self):
        h = self.hits({"app/main.py": """
            @app.post("/webhook/telegram")
            async def hook(req, tok=None):
                if cfg.telegram_webhook_secret and tok != cfg.telegram_webhook_secret:
                    raise HTTPException(401)
        """}, 3)
        self.assertIn("alta", [x["gravedad"] for x in h])

    def test_fail_closed_negative(self):
        h = self.hits({"app/main.py": """
            @app.post("/webhook/telegram")
            async def hook(req, tok=None):
                if not cfg.telegram_webhook_secret or tok != cfg.telegram_webhook_secret:
                    raise HTTPException(401)
                chat_account_id = 1
        """}, 3)
        self.assertEqual(h, [])


class P14(Base):
    def test_only_in_test(self):
        h = self.hits({"src/a.test.ts": "it.only('x', () => {});\n"}, 14)
        self.assertEqual([x["gravedad"] for x in h], ["alta"])

    def test_only_negative(self):
        h = self.hits({"src/a.test.ts": "it('x', () => {});\n// it.only in a comment\n"}, 14)
        self.assertEqual(h, [])


class P15(Base):
    def test_phone_suffix(self):
        h = self.hits({"src/chat.ts": "if (tel.endsWith(ziffern)) return true;\n"
                                      "return tel.slice(-9) === z.slice(-9);\n"}, 15)
        self.assertEqual(sorted(x["linea"] for x in h), [1, 2])
        self.assertTrue(all(x["gravedad"] == "revisar" for x in h))

    def test_extension_negative(self):
        h = self.hits({"src/f.ts": "if (fileName.endsWith('.pdf')) open();\n"
                                   "if (email.includes('@')) ok();\n"}, 15)
        self.assertEqual(h, [])


class Infra(Base):
    def test_ignore_file_and_inline(self):
        files = {
            "comprobar.ignore": "legacy/*\nscripts/* p07\n",
            "legacy/a.py": "try:\n    x()\nexcept Exception:\n    pass\n",
            "scripts/b.py": "import requests\nrequests.get('http://x')\n"
                            "try:\n    x()\nexcept Exception:\n    pass\n",
            "app/c.py": "try:\n    x()\nexcept Exception:  # comprobar: ignore p04\n    pass\n",
        }
        h = self.scan(files)
        self.assertEqual([(x["fichero"], x["punto"]) for x in h], [("scripts/b.py", 4)])

    def test_excluded_dirs_and_min(self):
        files = {
            "node_modules/x/a.js": "try { a() } catch {}\n",
            "dist/a.js": "try { a() } catch {}\n",
            "web/app.min.js": "try { a() } catch {}\n",
        }
        self.assertEqual(self.scan(files), [])

    def test_js_views_keep_layout(self):
        src = "const a = `x ${b('}')} y`; // c\nconst r = /\"/; f('\"');\n"
        nc, ns = c.js_views(src)
        self.assertEqual(len(nc), len(src))
        self.assertEqual(nc.count("\n"), src.count("\n"))
        self.assertNotIn("// c", nc)
        self.assertIn("b(", ns)


if __name__ == "__main__":
    unittest.main()
