"""Tests for pasar.py with a fake model. Run: python3 -m unittest scripts/revision-cruzada/test_pasar.py"""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pasar  # noqa: E402

LISTA = "# doc\n\n## C. otra\n\nnada\n\n## D. Lista\n\n" + "\n".join(f"{i}. **Punto {i}.** texto" for i in range(1, 16)) + "\n"
BUENO = json.dumps([{"punto": 4, "fichero": "a.ts", "linea": 3, "linea_prueba": "try { b(); } catch {}", "resumen": "catch vacío",
                     "escenario_de_fallo": "si falla la red devuelve [] como si no hubiera datos", "confianza": 0.7}])


class FakeModel:
    """Returns queued answers; each call costs `coste` dollars."""

    def __init__(self, respuestas, coste=0.01):
        self.respuestas = list(respuestas)
        self.coste = coste
        self.llamadas = []

    def __call__(self, modelo, mensajes, max_tokens):
        self.llamadas.append(mensajes)
        r = self.respuestas.pop(0) if self.respuestas else "[]"
        if isinstance(r, Exception):
            raise r
        return r, {"prompt_tokens": 1000, "completion_tokens": 100, "cost": self.coste}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = self.tmp.name
        self.repo = os.path.join(d, "repo")
        self.out = os.path.join(d, "out")
        os.makedirs(os.path.join(self.repo, "lib"))
        self.lista = os.path.join(d, "lista.md")
        with open(self.lista, "w") as f:
            f.write(LISTA)
        self.escribir("a.ts", 'import { b } from "./lib/b";\nexport function a() {\n  try { b(); } catch {}\n}\n')
        self.escribir("lib/b.ts", "export function b() { return 1; }\n")
        self.escribir("c.py", "from .lib import x\n\ndef c():\n    return 1\n")
        self.log = []

    def tearDown(self):
        self.tmp.cleanup()

    def escribir(self, rel, txt):
        with open(os.path.join(self.repo, rel), "w") as f:
            f.write(txt)

    def correr(self, extra, cliente=None, precios=(1e-6, 1e-6)):
        argv = [self.repo, "--ext", ".ts", "--nombre", "prueba", "--salida", self.out,
                "--lista", self.lista, "--fecha", "2026-10-14"] + extra
        return pasar.ejecutar(argv, cliente=cliente, precios_fn=lambda m: precios,
                              clave_fn=lambda: "sk-falsa", log=self.log.append, dormir=lambda s: None)

    def carpeta(self):
        return os.path.join(self.out, "prueba", "2026-10-14")

    def leer_jsonl(self, nombre):
        p = os.path.join(self.carpeta(), nombre)
        if not os.path.exists(p):
            return []
        with open(p) as f:
            return [json.loads(l) for l in f if l.strip()]


class TestTroceado(Base):
    def test_fichero_pequeno_un_trozo_con_import(self):
        trozos, _ = pasar.construir_trozos(self.repo, ["a.ts", "lib/b.ts"], 24000)
        a = [t for t in trozos if t["fichero"] == "a.ts"]
        self.assertEqual(len(a), 1)
        self.assertEqual((a[0]["desde"], a[0]["hasta"]), (1, 4))
        self.assertEqual(a[0]["imports"], ["lib/b.ts"])

    def test_fichero_grande_se_parte_por_funciones(self):
        cuerpo = "  const x = 1; // relleno para pasar de sesenta kilobytes con texto\n" * 30
        partes = ['import { b } from "./lib/b";', ""]
        for i in range(60):
            partes.append(f"export function f{i}() {{\n{cuerpo}}}\n")
        self.escribir("grande.ts", "\n".join(partes))
        self.assertGreater(os.path.getsize(os.path.join(self.repo, "grande.ts")), 60 * 1024)
        trozos, textos = pasar.construir_trozos(self.repo, ["grande.ts"], 24000)
        self.assertGreater(len(trozos), 1)
        n = len(textos["grande.ts"].splitlines())
        # contiguous, complete coverage and every cut on a top-level function
        self.assertEqual(trozos[0]["desde"], 1)
        self.assertEqual(trozos[-1]["hasta"], n)
        for x, y in zip(trozos, trozos[1:]):
            self.assertEqual(y["desde"], x["hasta"] + 1)
            self.assertTrue(textos["grande.ts"].splitlines()[y["desde"] - 1].startswith("export function"))
        # later chunks carry the import header and overlap as context, plus the local import
        self.assertIn('from "./lib/b"', trozos[1]["contexto"])
        self.assertEqual(trozos[1]["imports"], ["lib/b.ts"])
        for t in trozos:
            self.assertLessEqual(len(t["codigo"].encode()), 60 * 1024 + 8 * (t["hasta"] - t["desde"] + 1))

    def test_python_grande_corta_en_definiciones(self):
        defs = ["import os", ""] + [f"def f{i}():\n" + "    x = 'relleno relleno relleno relleno relleno'\n" * 40 for i in range(50)]
        self.escribir("g.py", "\n".join(defs))
        trozos, textos = pasar.construir_trozos(self.repo, ["g.py"], 24000)
        self.assertGreater(len(trozos), 1)
        lineas = textos["g.py"].splitlines()
        for t in trozos[1:]:
            self.assertTrue(lineas[t["desde"] - 1].startswith("def "))
            self.assertIn("import os", t["contexto"])

    def test_barril_sin_imports_adjuntos(self):
        self.escribir("index.ts", 'export * from "./a";\nexport { b } from "./lib/b";\n')
        trozos, _ = pasar.construir_trozos(self.repo, ["index.ts"], 24000)
        self.assertEqual(trozos[0]["imports"], [])

    def test_import_python_relativo(self):
        self.escribir("lib/__init__.py", "")
        self.escribir("lib/x.py", "y = 1\n")
        self.assertIn("lib/x.py", pasar.imports_locales(self.repo, "c.py", "from .lib import x\n"))


class TestSalida(Base):
    def test_json_invalido_reintenta_y_acepta(self):
        m = FakeModel(["Aquí tienes: [", BUENO, "[]"])
        self.assertEqual(self.correr(["--tope", "1"], cliente=m), 0)
        hall = self.leer_jsonl("hallazgos.jsonl")
        self.assertEqual(len(hall), 1)
        self.assertEqual(hall[0]["punto"], 4)
        self.assertEqual(hall[0]["trozo"]["fichero"], "a.ts")
        self.assertEqual(len(m.llamadas[1]), 4)   # retry carries the rejected answer and the correction
        self.assertEqual(self.leer_jsonl("fallos.jsonl"), [])

    def test_dos_salidas_invalidas_guarda_fallo_y_sigue(self):
        m = FakeModel(["no", '{"punto": 1}', "[]"])
        self.assertEqual(self.correr(["--tope", "1"], cliente=m), 0)
        fallos = self.leer_jsonl("fallos.jsonl")
        self.assertEqual(len(fallos), 1)
        self.assertIn("rechazada", fallos[0]["error"])
        self.assertEqual(len(m.llamadas), 3)   # 2 for the failing chunk, 1 for the next
        estado = pasar._leer_json(os.path.join(self.carpeta(), "estado.json"))
        self.assertTrue(estado["completo"])
        self.assertEqual(estado["fallos"], 1)

    def test_validacion_de_esquema(self):
        self.assertEqual(pasar.validar_salida("```json\n[]\n```"), [])
        for malo in ["{}", "[1]", '[{"punto": 16, "fichero": "a", "linea": 1, "resumen": "", "escenario_de_fallo": "", "confianza": 0.5}]',
                     '[] y algo más', '[{"punto": 1}]']:
            with self.assertRaises(ValueError, msg=malo):
                pasar.validar_salida(malo)


class TestLineaPrueba(Base):
    def test_descarta_hallazgo_cuya_linea_no_esta_en_el_trozo(self):
        inventado = json.loads(BUENO)[0] | {"linea": 9, "linea_prueba": "await enviar(todo); // no existe"}
        m = FakeModel([json.dumps(json.loads(BUENO) + [inventado])])
        self.assertEqual(self.correr(["--tope", "1"], cliente=m), 0)
        hall = self.leer_jsonl("hallazgos.jsonl")
        self.assertEqual([h["linea_prueba"] for h in hall], ["try { b(); } catch {}"])
        desc = self.leer_jsonl("descartados.jsonl")
        self.assertEqual(len(desc), 1)
        self.assertIn("no está en el trozo", desc[0]["descartado"])

    def test_filtro_ignora_numeracion_y_espacios_y_corta_a_tres(self):
        codigo = "    3|   try { b(); }   catch {}\n    4| return x;"
        h = {"linea_prueba": "3| try { b(); } catch {}", "confianza": 0.5}
        quedan, fuera = pasar.filtrar_por_prueba([h | {"confianza": c} for c in (0.1, 0.9, 0.5, 0.7)], codigo)
        self.assertEqual([q["confianza"] for q in quedan], [0.9, 0.7, 0.5])
        self.assertEqual(len(fuera), 1)
        self.assertIn("más de 3", fuera[0]["descartado"])

    def test_sin_linea_prueba_es_salida_invalida(self):
        sin = json.loads(BUENO)
        del sin[0]["linea_prueba"]
        with self.assertRaises(ValueError):
            pasar.validar_salida(json.dumps(sin))


class TestTopeYReanudar(Base):
    def test_tope_para_antes_de_pasarse_y_reanuda(self):
        for i in range(5):
            self.escribir(f"m{i}.ts", f"export const m{i} = {i};\n")
        # each chunk: worst case 2*(tin*1e-6 + 4000*1e-6) ~ 0.009 $; real cost 0.01 $ per call
        m = FakeModel([], coste=0.01)
        rc = self.correr(["--tope", "0.035"], cliente=m)
        self.assertEqual(rc, 5)
        estado = pasar._leer_json(os.path.join(self.carpeta(), "estado.json"))
        self.assertFalse(estado["completo"])
        self.assertLessEqual(estado["gastado"], 0.035)
        self.assertIn("tope", estado["parado"])
        hechos = len(estado["hechos"])
        self.assertTrue(0 < hechos < 7)
        with open(os.path.join(self.carpeta(), "coste.txt")) as f:
            self.assertIn("PARADO", f.read())
        # a new run on the same folder refuses to overwrite
        self.assertEqual(self.correr(["--tope", "1"], cliente=FakeModel([])), 3)
        # resume finishes only the pending chunks
        m2 = FakeModel([], coste=0.01)
        self.assertEqual(self.correr(["--tope", "1", "--reanudar"], cliente=m2), 0)
        estado = pasar._leer_json(os.path.join(self.carpeta(), "estado.json"))
        self.assertTrue(estado["completo"])
        self.assertEqual(len(m2.llamadas), estado["total"] - hechos)
        self.assertEqual(len(set(estado["hechos"])), estado["total"])

    def test_reanudar_descarta_hallazgos_de_trozo_no_marcado(self):
        m = FakeModel([BUENO], coste=0.01)
        self.correr(["--tope", "0.012"], cliente=m)   # first chunk done, then stops
        estado_p = os.path.join(self.carpeta(), "estado.json")
        estado = pasar._leer_json(estado_p)
        self.assertEqual(len(estado["hechos"]), 1)
        # simulate a crash after writing a finding but before marking its chunk
        with open(os.path.join(self.carpeta(), "hallazgos.jsonl"), "a") as f:
            f.write(json.dumps({"punto": 1, "trozo": {"id": "fantasma"}}) + "\n")
        self.correr(["--tope", "1", "--reanudar"], cliente=FakeModel([]))
        ids = [h["trozo"]["id"] for h in self.leer_jsonl("hallazgos.jsonl")]
        self.assertNotIn("fantasma", ids)
        self.assertEqual(len(ids), 1)

    def test_reanudar_con_modelo_distinto_se_niega(self):
        self.correr(["--tope", "0.012"], cliente=FakeModel([]))
        self.assertEqual(self.correr(["--tope", "1", "--reanudar", "--modelo", "otro/modelo"], cliente=FakeModel([])), 2)


class TestArgumentosYClave(Base):
    def test_argumento_desconocido_sale_sin_tocar_nada(self):
        for extra in (["--tope", "1", "--sec"], ["--tope", "1", "--nose"], ["--tope", "1", "suelto"],
                      ["--tope", "0"], ["--tope", "1", "--seco", "--reanudar"]):
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as cm:
                self.correr(extra, cliente=FakeModel([]))
            self.assertNotEqual(cm.exception.code, 0, extra)
        self.assertFalse(os.path.exists(self.out))

    def test_sin_clave_no_llama(self):
        m = FakeModel([])
        argv = [self.repo, "--ext", ".ts", "--nombre", "prueba", "--salida", self.out,
                "--lista", self.lista, "--tope", "1"]
        rc = pasar.ejecutar(argv, cliente=m, precios_fn=lambda x: (1e-6, 1e-6),
                            clave_fn=lambda: None, log=self.log.append)
        self.assertEqual(rc, 3)
        self.assertEqual(m.llamadas, [])
        self.assertFalse(os.path.exists(self.out))

    def test_sin_precio_ni_tarifa_no_llama(self):
        m = FakeModel([])
        self.assertEqual(self.correr(["--tope", "1"], cliente=m, precios=None), 3)
        self.assertEqual(m.llamadas, [])

    def test_seco_no_llama_y_estima(self):
        m = FakeModel([])
        self.assertEqual(self.correr(["--tope", "1", "--seco"], cliente=m), 0)
        self.assertEqual(m.llamadas, [])
        with open(os.path.join(self.carpeta(), "seco.txt")) as f:
            txt = f.read()
        self.assertIn("trozos: 2", txt)
        self.assertIn("coste estimado", txt)
        self.assertFalse(os.path.exists(os.path.join(self.carpeta(), "estado.json")))

    def test_seco_con_tarifa_por_argumento_marca_estimada(self):
        self.correr(["--tope", "1", "--seco", "--tarifa-entrada", "0.3", "--tarifa-salida", "1"], precios=None)
        with open(os.path.join(self.carpeta(), "seco.txt")) as f:
            self.assertIn("ESTIMADA", f.read())

    def test_clave_no_aparece_en_errores(self):
        c = pasar.ClienteOpenRouter("sk-secreta-123")
        self.assertEqual(c._limpio("fallo con sk-secreta-123 dentro"), "fallo con *** dentro")


if __name__ == "__main__":
    unittest.main()
