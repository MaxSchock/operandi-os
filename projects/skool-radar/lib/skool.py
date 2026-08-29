"""Skool reader built on Playwright.

Skool is a Next.js app: every page ships its data as JSON inside __NEXT_DATA__,
so we read structured records instead of scraping markup. Comments come from the
internal api2.skool.com endpoint, called from inside the browser context so the
session cookies and headers travel with it.

Everything here is read-only. Nothing posts, comments, votes or DMs.
"""
import json
import re
import sys

sys.path.insert(0, "/home/max/.config")
from playwright_exe import chromium_exe  # noqa: E402

from playwright.async_api import async_playwright  # noqa: E402

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
NEXT_DATA = re.compile(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.S)
BASE = "https://www.skool.com"


class Skool:
    def __init__(self, storage_state=None, headless=True, slow_ms=0):
        self.storage_state = storage_state
        self.headless = headless
        self.slow_ms = slow_ms

    async def __aenter__(self):
        self._pw = await async_playwright().start()
        self._browser = await self._pw.chromium.launch(
            headless=self.headless,
            executable_path=chromium_exe(),
            args=["--no-sandbox", "--disable-dev-shm-usage"],
            slow_mo=self.slow_ms,
        )
        self.ctx = await self._browser.new_context(
            user_agent=UA,
            viewport={"width": 1440, "height": 1000},
            locale="en-US",
            storage_state=self.storage_state,
        )
        self.page = await self.ctx.new_page()
        return self

    async def __aexit__(self, *exc):
        await self._browser.close()
        await self._pw.stop()

    async def page_props(self, url, wait_ms=1200):
        """Load a Skool URL and return its pageProps dict."""
        await self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await self.page.wait_for_timeout(wait_ms)
        html = await self.page.content()
        m = NEXT_DATA.search(html)
        if not m:
            return None
        return json.loads(m.group(1)).get("props", {}).get("pageProps", {})

    async def api(self, path):
        """Call the internal API from inside the page, so the session travels along."""
        url = path if path.startswith("http") else f"https://api2.skool.com{path}"
        if "skool.com" not in (self.page.url or ""):
            await self.page.goto(f"{BASE}/discover", wait_until="domcontentloaded", timeout=60000)
        return await self.page.evaluate(
            """async (u) => {
                try {
                    const r = await fetch(u, {credentials: 'include'});
                    if (!r.ok) return {__error: r.status};
                    return await r.json();
                } catch (e) { return {__error: String(e)}; }
            }""", url)

    async def whoami(self):
        """Logged-in identity, read from the session endpoint the app itself uses.

        Authenticated pages are rendered client-side, so __NEXT_DATA__ comes back
        nearly empty and cannot be used to tell a live session from an anonymous one.
        """
        data = await self.api("/self/groups?limit=1&prefs=false")
        if not data or data.get("__error"):
            return {"logged_in": False, "name": None, "error": (data or {}).get("__error")}
        me = data.get("user") or data.get("self") or {}
        md = me.get("metadata") or {}
        return {"logged_in": True, "name": me.get("name") or md.get("firstName"),
                "id": me.get("id")}

    async def my_communities(self):
        """Communities this account belongs to."""
        data = await self.api("/self/groups?limit=50&prefs=false")
        if not data or data.get("__error"):
            return []
        groups = data.get("groups") or data.get("items") or []
        out = []
        for g in groups:
            grp = g.get("group", g)
            md = grp.get("metadata") or {}
            if grp.get("name"):
                out.append({"slug": grp["name"], "title": md.get("displayName") or grp["name"],
                            "id": grp.get("id"), "members": md.get("totalMembers"),
                            "role": g.get("role") or grp.get("role")})
        return out

    @staticmethod
    def _rich_text(desc):
        """Skool stores lesson bodies as ProseMirror JSON prefixed with [v2]."""
        if not desc:
            return ""
        if isinstance(desc, str):
            raw = desc[4:] if desc.startswith("[v2]") else desc
            try:
                desc = json.loads(raw)
            except Exception:
                return raw
        out = []

        def walk(n):
            if isinstance(n, list):
                for x in n:
                    walk(x)
                return
            if not isinstance(n, dict):
                return
            if n.get("type") == "text":
                out.append(n.get("text", ""))
            elif n.get("type") in ("paragraph", "heading", "listItem", "bulletList"):
                out.append("\n")
            for x in (n.get("content") or []):
                walk(x)

        walk(desc)
        return "\n".join(line.strip() for line in "".join(out).splitlines() if line.strip())

    @staticmethod
    def _resources(md):
        """Attachments and links a lesson carries, as a list of dicts."""
        raw = md.get("resources")
        if not raw:
            return []
        try:
            items = json.loads(raw) if isinstance(raw, str) else raw
        except Exception:
            return []
        return [i for i in items if isinstance(i, dict)]

    @staticmethod
    def _videos(md):
        """Videos of a post or a lesson.

        Posts carry videoLinksData (a JSON list). Classroom lessons carry a bare
        videoLink plus videoLenMs, and in this community those are Loom URLs.
        """
        out = []
        raw = md.get("videoLinksData") or md.get("video_links_data")
        if raw:
            try:
                data = json.loads(raw) if isinstance(raw, str) else raw
            except Exception:
                data = []
            prov = {1: "youtube", 2: "vimeo", 3: "loom", 4: "wistia"}
            out += [{"provider": prov.get(v.get("provider"), str(v.get("provider"))),
                     "video_id": v.get("video_id"), "url": v.get("url"),
                     "len_ms": v.get("len_ms"), "title": v.get("title")} for v in data]
        link = md.get("videoLink")
        if link and not any(v.get("url") == link for v in out):
            host = link.split("/")[2].lower() if "//" in link else ""
            provider = ("loom" if "loom.com" in host else
                        "youtube" if "youtu" in host else
                        "vimeo" if "vimeo" in host else
                        "wistia" if "wistia" in host else host or "desconocido")
            out.append({"provider": provider, "video_id": link.rstrip("/").split("/")[-1],
                        "url": link, "len_ms": md.get("videoLenMs"), "title": md.get("title")})
        return out

    def _post_row(self, community, node):
        p = node.get("post", node)
        md = p.get("metadata") or {}
        user = p.get("user") or {}
        return {
            "id": p.get("id"),
            "community": community,
            "slug": p.get("name"),
            "url": f"{BASE}/{community}/{p.get('name')}" if p.get("name") else None,
            "kind": "post",
            "title": md.get("title"),
            "content": md.get("content"),
            "author": user.get("name"),
            "labels": md.get("labels"),
            "upvotes": md.get("upvotes") or 0,
            "n_comments": md.get("comments") or 0,
            "videos": json.dumps(self._videos(md), ensure_ascii=False),
            "created_at": p.get("createdAt"),
            "updated_at": p.get("updatedAt"),
            "course": None,
            "module": None,
        }

    async def feed(self, community, max_pages=40, stop_ids=None, sort="newest"):
        """Yield posts newest-first, stopping early once we hit known ids."""
        stop_ids = stop_ids or set()
        consecutive_known = 0
        for page_no in range(1, max_pages + 1):
            url = f"{BASE}/{community}?p={page_no}&sort={sort}"
            props = await self.page_props(url)
            if not props:
                return
            trees = props.get("postTrees") or []
            if not trees:
                return
            for node in trees:
                row = self._post_row(community, node)
                if not row["id"]:
                    continue
                if row["id"] in stop_ids:
                    consecutive_known += 1
                    continue
                consecutive_known = 0
                yield row
            # a whole page of already-seen posts means we caught up
            if consecutive_known >= len(trees):
                return

    async def comments(self, post_id, group_id, limit=25):
        """Comment thread for a post, nested.

        Skool's API caps a page at 30 and exposes no working cursor: its own web
        app only ever asks for two blocks, the pinned/top ones and the tail. We
        mirror that, so a very long thread is sampled (top + latest), not
        exhausted. Enough to judge whether a post is worth reading; noted as a
        known limit rather than pretended otherwise.
        """
        base = (f"https://api2.skool.com/posts/{post_id}/comments"
                f"?group-id={group_id}&limit={min(limit, 30)}")
        rows, seen = [], set()
        self.last_error = None
        for variant in ("&pinned=true", "&tail=true"):
            data = await self.page.evaluate(
                """async (u) => {
                    try {
                        const r = await fetch(u, {credentials: 'include'});
                        if (!r.ok) return {__error: r.status};
                        return await r.json();
                    } catch (e) { return {__error: String(e)}; }
                }""", base + variant)
            if not data or data.get("__error"):
                self.last_error = (data or {}).get("__error", "empty")
                continue

            def walk(node, parent, depth):
                for child in (node.get("children") or []):
                    p = child.get("post") or {}
                    md = p.get("metadata") or {}
                    cid = p.get("id")
                    if cid and cid not in seen:
                        seen.add(cid)
                        rows.append((cid, post_id, parent, depth,
                                     (p.get("user") or {}).get("name"),
                                     md.get("content"), md.get("upvotes") or 0,
                                     p.get("created_at")))
                    walk(child, cid, depth + 1)

            walk(data.get("post_tree") or {}, None, 0)
        return rows

    async def group_id(self, community):
        props = await self.page_props(f"{BASE}/{community}") or {}
        g = props.get("currentGroup") or {}
        return (g.get("group") or g).get("id")

    async def classroom(self, community):
        """All courses, modules and lessons the account can actually open."""
        props = await self.page_props(f"{BASE}/{community}/classroom") or {}
        courses = props.get("allCourses") or []
        out = []
        for c in courses:
            md = c.get("metadata") or {}
            out.append({"id": c.get("id"), "title": md.get("title"), "desc": md.get("desc"),
                        "has_access": md.get("hasAccess"), "modules": md.get("numModules")})
        return out

    async def course_tree(self, community, course_id):
        """Modules and lessons of one course, with their video links.

        Shape: pageProps.course = {course: <root>, children: [modules]}, and every
        node repeats that {course, children} nesting. Leaves are the lessons.
        """
        props = await self.page_props(f"{BASE}/{community}/classroom/{course_id}") or {}
        node = props.get("course") or {}
        root = node.get("course") or {}
        course_title = (root.get("metadata") or {}).get("title")
        # Lesson URLs are built from the course's short `name`, not from any id:
        # with the wrong anchor Skool silently ignores ?md= and serves the
        # default lesson, which reads as "this lesson has no text".
        course_slug = root.get("name") or course_id
        lessons = []

        def visit(n, module_title, module_id, depth):
            inner = n.get("course") or n
            md = inner.get("metadata") or {}
            title = md.get("title")
            kids = n.get("children") or []
            if kids:
                for k in kids:
                    visit(k,
                          title if depth == 0 else module_title,
                          inner.get("id") if depth == 0 else module_id,
                          depth + 1)
                return
            lessons.append({
                "id": inner.get("id"),
                "community": community,
                "slug": inner.get("name"),
                "url": (f"{BASE}/{community}/classroom/"
                        f"{course_slug}?md={inner.get('id')}"),
                "kind": "lesson",
                "title": title,
                "content": self._rich_text(md.get("desc")),
                "resources": self._resources(md),
                "author": None,
                "labels": None,
                "upvotes": 0,
                "n_comments": 0,
                "videos": json.dumps(self._videos(md), ensure_ascii=False),
                "created_at": inner.get("createdAt"),
                "updated_at": inner.get("updatedAt"),
                "course": course_title,
                "module": module_title,
            })

        for child in (node.get("children") or []):
            visit(child, None, None, 0)
        return lessons, props
