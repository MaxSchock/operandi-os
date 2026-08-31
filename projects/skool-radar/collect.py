"""Collect posts, threads and classroom lessons from Skool communities.

    python3 collect.py --community <slug> [--pages 5] [--comments] [--classroom]
    python3 collect.py --whoami            # check the saved session
    python3 collect.py --list              # communities the session belongs to

Read-only. It never posts, comments, votes or messages anyone.
"""
import argparse
import asyncio
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lib import db  # noqa: E402
from lib.skool import Skool, SkoolUnavailable  # noqa: E402

STATE = os.path.join(HERE, "state", "skool-session.json")


def session_arg():
    return STATE if os.path.exists(STATE) else None


async def run(args):
    con = db.connect()
    state = session_arg()
    if not state and not args.public:
        print("Sin sesion guardada. Ejecuta primero: python3 login.py")
        print("(o pasa --public para una comunidad abierta)")
        return 1

    async with Skool(storage_state=state) as sk:
        who = await sk.whoami()
        if who["logged_in"]:
            # the endpoint returns the groups, not the profile: report what it does say
            quien = who.get("name") or f"{who.get('communities', 0)} comunidades"
            print(f"sesion: activa ({quien})")
        else:
            print(f"sesion: anonima ({who.get('error')})")

        if args.whoami:
            print(json.dumps(who, ensure_ascii=False, indent=2))
            return 0

        if args.list:
            for c in await sk.my_communities():
                print(f"  {c['slug']:<40} {c['title']}")
            return 0

        community = args.community
        run_id = db.start_run(con, community)
        known = db.known_post_ids(con, community)
        gid = await sk.group_id(community)
        print(f"comunidad {community} (group {gid}) · {len(known)} posts ya en la base")

        new_rows = []
        async for row in sk.feed(community, max_pages=args.pages, stop_ids=known):
            db.upsert_post(con, row)
            new_rows.append(row)
            vids = json.loads(row["videos"] or "[]")
            mark = f" [{len(vids)} video]" if vids else ""
            print(f"  + {row['created_at'][:10]} {str(row['title'])[:70]}{mark}")
        con.commit()
        print(f"posts nuevos: {len(new_rows)}")

        errores = 0
        if args.comments and new_rows:
            print("bajando hilos de comentarios...")
            for row in new_rows:
                if not row["n_comments"]:
                    continue
                rows = await sk.comments(row["id"], gid)
                if rows:
                    db.save_comments(con, row["id"], rows)
                    print(f"  {len(rows):>4} comentarios · {str(row['title'])[:60]}")
                elif sk.last_error:
                    errores += 1
                    print(f"  fallo al bajar el hilo ({sk.last_error}) · {str(row['title'])[:50]}")
            con.commit()
            if errores:
                print(f"AVISO: {errores} hilos no se pudieron bajar; no estan en la base")

        if args.classroom:
            print("classroom:")
            courses = await sk.classroom(community)
            for c in courses:
                access = "abierto" if c.get("has_access") else "sin acceso"
                print(f"  [{access}] {c['title']} ({c.get('modules')} modulos)")
            n = 0
            for c in courses:
                if not c.get("has_access"):
                    continue
                lessons, _ = await sk.course_tree(community, c["id"])
                for les in lessons:
                    res = les.pop("resources", [])
                    db.upsert_post(con, les)
                    if res:
                        db.save_resources(con, les["id"], res)
                    n += 1
                print(f"    {c['title']}: {len(lessons)} lecciones")
            con.commit()
            print(f"lecciones guardadas: {n}")

        db.end_run(con, run_id, len(new_rows))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--community", help="slug de la comunidad, p.ej. ai-automation-society")
    ap.add_argument("--pages", type=int, default=5)
    ap.add_argument("--comments", action="store_true")
    ap.add_argument("--classroom", action="store_true")
    ap.add_argument("--whoami", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--public", action="store_true", help="permite correr sin sesion")
    args = ap.parse_args()
    if not (args.whoami or args.list) and not args.community:
        ap.error("hace falta --community")
    raise SystemExit(asyncio.run(run(args)))


main()
