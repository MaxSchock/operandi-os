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

    async def whoami(self):
        props = await self.page_props(f"{BASE}/discover")
        me = (props or {}).get("self") or {}
        meta = me.get("metadata") or {}
        return {"logged_in": bool(me.get("id")), "name": me.get("name"),
                "first": meta.get("firstName"), "id": me.get("id")}

    async def my_communities(self):
        """Communities the logged-in account belongs to."""
        props = await self.page_props(f"{BASE}/discover") or {}
        out = []
        for key in ("groupCards", "myGroups", "groups"):
            for g in (props.get(key) or []):
                grp = g.get("group", g)
                md = grp.get("metadata") or {}
                if grp.get("name"):
                    out.append({"slug": grp["name"], "title": md.get("displayName") or grp.get("name"),
                                "id": grp.get("id"), "members": md.get("totalMembers")})
        seen, uniq = set(), []
        for c in out:
            if c["slug"] not in seen:
                seen.add(c["slug"])
                uniq.append(c)
        return uniq

    @staticmethod
    def _videos(md):
        raw = md.get("videoLinksData") or md.get("video_links_data")
        if not raw:
            return []
        try:
            data = json.loads(raw) if isinstance(raw, str) else raw
        except Exception:
            return []
        prov = {1: "youtube", 2: "vimeo", 3: "loom", 4: "wistia"}
        return [{"provider": prov.get(v.get("provider"), str(v.get("provider"))),
                 "video_id": v.get("video_id"), "url": v.get("url"),
                 "len_ms": v.get("len_ms"), "title": v.get("title")} for v in data]

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
        """Modules and lessons of one course, with body text and video links."""
        props = await self.page_props(f"{BASE}/{community}/classroom/{course_id}") or {}
        course = props.get("course") or {}
        cmd = (course.get("metadata") or {}) if isinstance(course, dict) else {}
        lessons = []

        def visit(node, module_title):
            md = node.get("metadata") or {}
            title = md.get("title")
            kids = node.get("children") or []
            if kids:
                for k in kids:
                    visit(k, title or module_title)
                return
            lessons.append({
                "id": node.get("id"),
                "community": community,
                "slug": node.get("name"),
                "url": f"{BASE}/{community}/classroom/{course_id}?md={node.get('id')}",
                "kind": "lesson",
                "title": title,
                "content": md.get("description") or md.get("content"),
                "author": None,
                "labels": None,
                "upvotes": 0,
                "n_comments": 0,
                "videos": json.dumps(self._videos(md), ensure_ascii=False),
                "created_at": node.get("createdAt"),
                "updated_at": node.get("updatedAt"),
                "course": cmd.get("title"),
                "module": module_title,
            })

        root = course.get("tree") or course.get("children") or course
        if isinstance(root, dict):
            visit(root, None)
        elif isinstance(root, list):
            for n in root:
                visit(n, None)
        return lessons, props
