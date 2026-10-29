"""Exact coverage of a bounded mana domain, without full-turn simulation."""

import argparse
import csv
from functools import lru_cache
import hashlib
import json
from pathlib import Path

from src.opening_pilot import ROOT, exact_opening, read_json


@lru_cache(maxsize=None)
def bounded_count(types, total, cap=4):
    """Coefficient of x**total in (1+x+...+x**cap)**types."""
    if types < 0 or total < 0 or total > types*cap:
        return 0
    if types == 0:
        return int(total == 0)
    return sum(bounded_count(types-1, total-n, cap) for n in range(cap+1))


def domain_count(scope, lands, cap=4, bridge_min=0, bridge_max=None):
    types = len(scope["ordinary_artifact_lands"])+len(scope["citadel"])
    maximum = min(lands, len(scope["bridges"])*cap) if bridge_max is None else min(lands, bridge_max)
    return sum(bounded_count(len(scope["bridges"]), b, cap) * (
        bounded_count(types, lands-b, cap)
        + len(scope["basics"])*bounded_count(types, lands-b-1, cap))
        for b in range(bridge_min, maximum+1))


def bounded_vectors(types, total, cap=4):
    """Lazy enumeration with exact remaining-capacity pruning."""
    if types == 0:
        if total == 0:
            yield ()
        return
    for n in range(min(cap, total), max(0, total-(types-1)*cap)-1, -1):
        for rest in bounded_vectors(types-1, total-n, cap):
            yield (n,) + rest


def land_bases(scope, lands, cap=4, bridge_min=0, bridge_max=None):
    """Every permitted base once; excluded bridge bands are never generated."""
    bridges = scope["bridges"]
    others = scope["ordinary_artifact_lands"]+scope["citadel"]
    maximum = min(lands, len(bridges)*cap) if bridge_max is None else min(lands, bridge_max)
    for basic in [None]+scope["basics"]:
        total = lands-int(basic is not None)
        for b in range(bridge_min, min(total, maximum)+1):
            if not bounded_count(len(others), total-b, cap):
                continue
            for bv in bounded_vectors(len(bridges), b, cap):
                for ov in bounded_vectors(len(others), total-b, cap):
                    base = {name: n for name, n in zip(bridges+others, bv+ov) if n}
                    if basic is not None:
                        base[basic] = 1
                    yield base


def exact_profiles(scope, lands, cap=4, bridge_min=0, bridge_max=None):
    """Exact equivalence only for total-land / untapped opening events."""
    maximum = lands if bridge_max is None else min(lands, bridge_max)
    for basic in (0, 1):
        choices = 1 if basic == 0 else len(scope["basics"])
        if not choices:
            continue
        for bridges in range(bridge_min, min(lands-basic, maximum)+1):
            ways = bounded_count(len(scope["bridges"]), bridges, cap)
            for citadel in range(cap+1):
                ordinary = lands-basic-bridges-citadel
                count = ways*bounded_count(len(scope["ordinary_artifact_lands"]), ordinary, cap)*choices
                if count:
                    yield {"lands": lands, "bridges": bridges, "citadels": citadel,
                           "ordinary_artifact_lands": ordinary, "basics": basic,
                           "untapped_lands": lands-bridges, "distinct_bases": count}


def write_search(output):
    path = ROOT/"configs/mana_search_space.json"
    catalog_path = ROOT/"data/opening_catalog.json"
    config, catalog = read_json(path), read_json(catalog_path)["cards"]
    if config["maximum_basic_lands_total"] != 0:
        raise ValueError("The active study excludes basic lands")
    cap = config["nonbasic_copy_limit"]
    low, high = config["bridge_range"]
    if not 0 <= low <= high:
        raise ValueError("Invalid bridge range")
    rows, counts, per_bridge, cache = [], {}, [], {}
    for name, scope in config["scopes"].items():
        names = sum((scope[k] for k in ("bridges", "ordinary_artifact_lands", "citadel", "basics")), [])
        if scope["basics"] or len(scope["citadel"]) != 1:
            raise ValueError("Expected no basics and one Citadel card type")
        if len(names) != len(set(names)) or any(n not in catalog for n in names):
            raise ValueError("Missing or repeated land in the pool")
        counts[name] = {}
        for lands in config["land_totals"]:
            total = domain_count(scope, lands, cap, low, high)
            groups = list(exact_profiles(scope, lands, cap, low, high))
            bands = {band: domain_count(scope, lands, cap, a, b)
                     for band, (a, b) in config["bridge_bands"].items()}
            if sum(g["distinct_bases"] for g in groups) != total or sum(bands.values()) != total:
                raise AssertionError("Incomplete or overlapping profile/band partition")
            counts[name][lands] = {"all_bases": total, "bands": bands, "profiles": len(groups)}
            for bridges in range(low, high+1):
                per_bridge.append({"scope": name, "lands": lands, "bridges": bridges,
                                   "untapped": lands-bridges,
                                   "distinct_bases": domain_count(scope, lands, cap, bridges, bridges)})
            for group in groups:
                for boulder in config["boulder_counts"]:
                    key = (lands, group["untapped_lands"], boulder)
                    if key not in cache:
                        cache[key] = exact_opening(*key)
                    p = cache[key]
                    rows.append({"scope": name, **group, "boulders": boulder,
                                 "p_initial_lt2_lands": p["initial_lt2"],
                                 "p_initial_boulder": p["initial_boulder"],
                                 "p_initial_eligible_boulder_untapped": p["initial_eligible_boulder_untapped"]})
    totals = {name: sum(d["all_bases"] for d in block.values()) for name, block in counts.items()}
    output.mkdir(parents=True, exist_ok=True)
    manifest = {"status": "Active bounded domain counted; exact opening profiles only; no new turn/hate simulation",
                "config": config, "counts": counts, "per_bridge_counts": per_bridge, "scope_totals": totals,
                "base_boulder_pairs": {name: n*len(config["boulder_counts"]) for name, n in totals.items()},
                "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in (path, catalog_path, Path(__file__), ROOT/"src/opening_pilot.py")}}
    (output/"manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False)+"\n")
    with (output/"exact_opening_profiles.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    lines = [f"# Universo activo: {low}–{high} bridges, sin básicas", "",
             f"19/20 tierras, {low}–{high} bridges totales, ninguna básica y 0–4 copias de cada tierra del catálogo W/U/B/R, incluyendo Citadel. El resto son tierras artefacto enderezadas. Boulder se cruza en cantidades 0–4, con reemplazos explícitos para mantener 60 cartas.", "",
             "Todas las cantidades del rango activo se incluyen sin anticipar cuál será mejor.", "",
             "| Tierras | Bridges | Enderezadas | Bases distintas |",
             "| ---: | ---: | ---: | ---: |"]
    for r in per_bridge:
        lines.append(f"| {r['lands']} | {r['bridges']} | {r['untapped']} | {r['distinct_bases']:,} |")
    lines += ["", "## Totales por rango", "",
              "| Tierras | " + " | ".join(f"{a}–{b} ({band})" for band, (a,b) in config['bridge_bands'].items()) + " | Total |",
              "| ---: | " + " | ".join('---:' for _ in config['bridge_bands']) + " | ---: |"]
    for name, block in counts.items():
        for lands, d in block.items():
            lines.append(f"| {lands} | " + " | ".join(f"{d['bands'][band]:,}" for band in config['bridge_bands']) + f" | {d['all_bases']:,} |")
        lines += ["", f"Total activo **{name}: {totals[name]:,} bases**. El conteo anterior de 32.205.701 incluía básicas y cantidades de bridges excluidas ahora; ya no es el alcance activo.", ""]
    lines += ["## Qué se evaluó", "",
              "Conteo exhaustivo y controles exactos de aperturas por perfiles con multiplicidad: menos de dos tierras en siete, Boulder en siete y al menos dos tierras + Boulder + tierra enderezada en siete. Para estas métricas la partición representa exactamente todas las bases del dominio.", "",
              "No se simularon aquí turnos, acceso W/U/B/R, scry, robos adicionales, mulligans estratégicos ni hate. Bases con igual total de bridges pueden ser distintas en esos resultados. No se añadieron partidas Monte Carlo.", "",
              "El generador aplica el límite de bridges durante la generación; no materializa primero bases excluidas. Se contrastó contra fuerza bruta en dominios pequeños.", "",
              "## Alcance y continuación", "",
              "- Seis bridges W/U/B/R, Ancient Den, Seat of the Synod, Vault of Whispers, Great Furnace y Darksteel Citadel. La extensión verde previa queda inactiva, no demostrada inferior.",
              f"- Todas las distribuciones dentro de {low}–{high}, sin fijar cantidades de Vault/Synod/Furnace/Citadel.",
              "- Básicas y su análisis de Cleansing Wildfire excluidos por indicación del jugador.",
              "- El motor debe separar cantidad de bridges, identidad/colores y política de juego dentro del rango activo.",
              "- Publicar cobertura y distinguir conteo/evaluación exacta de partidas simuladas; confirmar candidatos con nuevas semillas.", ""]
    (output/"universo_busqueda.md").write_text("\n".join(lines))
    print("Bases activas:", totals)
    print(f"{len(rows)} perfiles exactos; informe: {output / 'universo_busqueda.md'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT/"results/search_space")
    write_search(parser.parse_args().output)
