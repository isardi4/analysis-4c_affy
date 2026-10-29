"""Opening-hand controls only; intentionally not a Magic turn engine.

Run from the project root: python3 -m src.opening_pilot
Uses only the Python standard library. All probabilities retain failed trials.
"""

import argparse
from collections import Counter
from datetime import datetime, timezone
import csv
import hashlib
from itertools import combinations
import json
from math import comb, sqrt
from pathlib import Path
import platform
import random
import time


ROOT = Path(__file__).resolve().parents[1]
BOULDER = "Giant's Boulder"
DRAW = {"Thoughtcast", "Cryogen Relic", "Reckoner's Bargain"}
THREATS = {"Refurbished Familiar", "Utrom Monitor", "Myr Enforcer", "Glint Hawk"}


def read_json(path):
    return json.loads(path.read_text())


def validate_deck(cards, catalog):
    if sum(cards.values()) != 60:
        raise ValueError("A composition must have exactly 60 cards")
    for name, count in cards.items():
        if name not in catalog or not isinstance(count, int) or count < 0:
            raise ValueError(f"Invalid card or count: {name}")
        if count > 4 and not catalog[name].get("basic", False):
            raise ValueError(f"More than four copies: {name}")


def inventory(cards, catalog):
    lands = {name: n for name, n in cards.items() if catalog[name]["land"]}
    return {
        "lands": sum(lands.values()),
        "untapped_lands": sum(n for name, n in lands.items() if not catalog[name]["tapped"]),
        "bridges": sum(n for name, n in lands.items() if name.endswith("Bridge")),
        "citadels": lands.get("Darksteel Citadel", 0),
        "boulders": cards.get(BOULDER, 0),
        "artifacts": sum(n for name, n in cards.items() if catalog[name]["artifact"]),
        "natural_sources": {c: sum(n for name, n in lands.items() if c in catalog[name]["colors"]) for c in "WUBR"},
    }


def build_variants(reference, catalog, config):
    variants = []
    for family in config["land_families"]:
        for boulders in config["boulder_counts"]:
            cards = dict(reference["cards"])
            for name, delta in family["changes"].items():
                cards[name] = cards.get(name, 0) + delta
            cards[BOULDER] = boulders
            spare = 60 - sum(cards.values())
            if spare < 0:
                cards["Nihil Spellbomb"] += spare
            else:
                for name in ("Nihil Spellbomb", "Myr Enforcer", "Glint Hawk"):
                    added = min(4 - cards[name], spare)
                    cards[name] += added
                    spare -= added
                if spare:
                    raise ValueError("Insufficient named replacement slots")
            cards = {name: n for name, n in sorted(cards.items()) if n}
            validate_deck(cards, catalog)
            changes = {name: cards.get(name, 0) - reference["cards"].get(name, 0)
                       for name in sorted(set(cards) | set(reference["cards"]))
                       if cards.get(name, 0) != reference["cards"].get(name, 0)}
            variants.append({"id": f"{family['id']}_b{boulders}", "family": family["id"],
                             "description": family["description"], "cards": cards,
                             "changes": changes, "inventory": inventory(cards, catalog)})
    return variants


def hand_features(hand, catalog):
    lands = [name for name in hand if catalog[name]["land"]]
    return {"lands": len(lands), "boulders": hand.count(BOULDER),
            "untapped": sum(not catalog[name]["tapped"] for name in lands),
            "colors": len(set("".join(catalog[name]["colors"] for name in lands)))}


def eligible(hand, catalog, minimum_lands=2):
    return hand_features(hand, catalog)["lands"] >= minimum_lands


def bottom_seven(seven, size, catalog, minimum_lands=2):
    """Return kept cards and ordered bottom, using no library information."""
    if not 2 <= size <= 7:
        raise ValueError("Hand size must allow at least two lands")
    if not eligible(seven, catalog, minimum_lands):
        return None
    if size == 7:
        return list(seven), []
    best = None
    for indices in combinations(range(7), size):
        kept = [seven[i] for i in indices]
        f = hand_features(kept, catalog)
        if f["lands"] < minimum_lands:
            continue
        score = (bool(f["boulders"] and f["untapped"]), bool(f["boulders"]),
                 -abs(f["lands"] - (3 if size >= 5 else 2)), f["colors"],
                 -max(0, f["boulders"] - 1), sum(n in DRAW for n in kept),
                 sum(n in THREATS for n in kept), tuple(sorted(kept)))
        if best is None or score > best[0]:
            chosen = set(indices)
            best = (score, kept, [n for i, n in enumerate(seven) if i not in chosen])
    if best is None:
        return None
    return best[1], best[2]


def should_keep(kept, catalog, policy, mulligans):
    if not eligible(kept, catalog):
        return False
    if policy == "min_two":
        return True
    if policy == "seek_boulder_once":
        return mulligans > 0 or BOULDER in kept
    raise ValueError(f"Unknown policy: {policy}")


def starting_hand(deck, catalog, policy, floor, rng):
    if floor not in range(2, 8):
        raise ValueError("Floor must be between 2 and 7")
    attempts = []
    for mulligans in range(8 - floor):
        library = list(deck)
        rng.shuffle(library)
        seven = library[:7]
        selection = bottom_seven(seven, 7 - mulligans, catalog)
        keep = selection is not None and should_keep(selection[0], catalog, policy, mulligans)
        attempts.append({"size_if_kept": 7 - mulligans, "seven": seven, "kept": keep})
        if keep:
            kept, bottom = selection
            return {"kept": kept, "bottom": bottom, "library": library[7:] + bottom,
                    "mulligans": mulligans, "attempts": attempts, "failed": False}
    return {"kept": [], "bottom": [], "library": [], "mulligans": 7 - floor,
            "attempts": attempts, "failed": True}


def choose(n, k):
    return comb(n, k) if 0 <= k <= n else 0


def exact_opening(lands, untapped, boulders):
    """Enumerate disjoint hand categories for exact seven-card events."""
    result = dict.fromkeys(("initial_lt2", "initial_boulder", "initial_boulder_untapped",
                            "initial_eligible_boulder", "initial_eligible_boulder_untapped"), 0.0)
    denom = comb(60, 7)
    tapped, other = lands - untapped, 60 - lands - boulders
    for l in range(8):
        for u in range(l + 1):
            for b in range(8 - l):
                p = choose(untapped, u) * choose(tapped, l-u) * choose(boulders, b) * choose(other, 7-l-b) / denom
                for name, event in (("initial_lt2", l < 2), ("initial_boulder", b > 0),
                                    ("initial_boulder_untapped", b > 0 and u > 0),
                                    ("initial_eligible_boulder", l >= 2 and b > 0),
                                    ("initial_eligible_boulder_untapped", l >= 2 and b > 0 and u > 0)):
                    if event:
                        result[name] += p
    return result


def exact_mulligan(raw, policy, floor):
    p_two = 1 - raw["initial_lt2"]
    p_first = p_two if policy == "min_two" else raw["initial_eligible_boulder"]
    reach, sizes = 1.0, {}
    for size in range(7, floor - 1, -1):
        p = p_first if size == 7 else p_two
        sizes[size] = reach * p
        reach *= 1 - p
    return {"failed": reach, "sizes": sizes,
            "cards_unconditional": sum(size*p for size, p in sizes.items())}


def wilson(successes, n):
    z = 1.959963984540054
    p = successes / n
    d = 1 + z*z/n
    center = (p + z*z/(2*n)) / d
    half = z * sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return [0.0 if successes == 0 else max(0, center-half),
            1.0 if successes == n else min(1, center+half)]


def run_cell(variant, catalog, policy, floor, n, seed):
    deck = [name for name, count in variant["cards"].items() for _ in range(count)]
    counts, sizes, traces = Counter(), Counter(), []
    total_cards, total_mulligans = 0, 0
    inv = variant["inventory"]
    exact = exact_opening(inv["lands"], inv["untapped_lands"], inv["boulders"])
    exact_m = exact_mulligan(exact, policy, floor)
    for trial in range(n):
        # Reset per trial so different mulligan counts cannot shift later trials.
        rng_seed = int.from_bytes(hashlib.sha256(f"{seed}:{trial}".encode()).digest()[:16], "big")
        outcome = starting_hand(deck, catalog, policy, floor, random.Random(rng_seed))
        initial = hand_features(outcome["attempts"][0]["seven"], catalog)
        flags = {"initial_lt2": initial["lands"] < 2,
                 "initial_boulder": initial["boulders"] > 0,
                 "initial_boulder_untapped": initial["boulders"] > 0 and initial["untapped"] > 0,
                 "initial_eligible_boulder": initial["lands"] >= 2 and initial["boulders"] > 0,
                 "initial_eligible_boulder_untapped": initial["lands"] >= 2 and initial["boulders"] > 0 and initial["untapped"] > 0}
        counts.update({key: int(value) for key, value in flags.items()})
        counts["failed"] += outcome["failed"]
        total_cards += len(outcome["kept"])
        total_mulligans += outcome["mulligans"]
        if not outcome["failed"]:
            f = hand_features(outcome["kept"], catalog)
            if f["lands"] < 2:
                raise AssertionError("Kept a hand with fewer than two lands")
            sizes[len(outcome["kept"])] += 1
            counts["kept_boulder"] += f["boulders"] > 0
            counts["kept_boulder_untapped"] += f["boulders"] > 0 and f["untapped"] > 0
            counts["kept_all_lands_tapped"] += f["untapped"] == 0
            counts["kept_duplicate_boulders"] += f["boulders"] > 1
            if Counter(outcome["kept"] + outcome["library"]) != Counter(deck):
                raise AssertionError("Cards lost or duplicated during bottoming")
        if trial < 2:
            traces.append({"trial": trial, **{k: v for k, v in outcome.items() if k != "library"}})
    events = {}
    checks = []
    all_exact = {**exact, "failed": exact_m["failed"]}
    for key in list(exact) + ["failed", "kept_boulder", "kept_boulder_untapped", "kept_all_lands_tapped", "kept_duplicate_boulders"]:
        entry = {"count": counts[key], "denominator": n, "rate": counts[key]/n,
                 "wilson95": wilson(counts[key], n)}
        if key in all_exact:
            expected = all_exact[key]
            # Broad, preregistered bug detector across many correlated checks;
            # not the 95% interval and not a hypothesis test selecting winners.
            tolerance = 6*sqrt(expected*(1-expected)/n) + 1/n
            checks.append({"metric": key, "passed": abs(entry["rate"]-expected) <= tolerance,
                           "error_pp": 100*(entry["rate"]-expected), "tolerance_pp": 100*tolerance})
            entry["exact"] = expected
        events[key] = entry
    return {"variant": variant["id"], "policy": policy, "floor": floor, "n": n,
            "events": events, "hand_size_counts": dict(sorted(sizes.items(), reverse=True)),
            "exact_hand_size_probabilities": exact_m["sizes"],
            "mean_cards_unconditional": total_cards/n,
            "exact_mean_cards_unconditional": exact_m["cards_unconditional"],
            "mean_cards_conditional_on_kept": total_cards/(n-counts["failed"]) if n > counts["failed"] else None,
            "mean_mulligans": total_mulligans/n, "checks": checks, "traces": traces}


def pct(value):
    return f"{100*value:.2f}%"


def write_report(result, output):
    variants = {v["id"]: v for v in result["variants"]}
    lines = ["# Piloto 01: manos iniciales y mulligans", "",
             "Este piloto valida aperturas y mulligans. No simula turnos, scry, robos de hechizos, filtrado operativo ni hate; no determina todavía la mejor base de maná.", "",
             f"Semilla: {result['seed']}. {len(result['cells'])} celdas de {result['n_per_cell']:,} intentos: {result['total_trials']:,} aperturas completas. Tiempo de cálculo: {result['elapsed_seconds']:.2f} s. No se duplica play/draw porque todavía no hay turnos.", "",
             "Lista de referencia candidata del mismo jugador/torneo; la exportación original de Goldfish sigue sin contrastar. Ver procedencia en `data/reference_deck.json`.", "",
             "## Regla del jugador y políticas de control", "",
             "Toda mano conservada, incluida la primera de siete y la mano final después de poner cartas al fondo, debe tener al menos dos tierras. Boulder no cuenta como tierra.", "",
             "- `min_two`: conservar cualquier mano con al menos dos tierras; control sencillo, no recomendación de keep para todo matchup.",
             "- `seek_boulder_once`: con siete exigir también Boulder; desde seis, exigir únicamente las dos tierras. Como máximo un mulligan voluntario por falta de Boulder.",
             "- Piso principal propuesto: cuatro cartas. Si no se logra una mano admisible al llegar al piso, se registra fallo de política; nunca se remuestrea gratis ni se excluye ese intento del denominador. También se prueba el piso de tres y dos sobre la lista original.",
             "- Al elegir el fondo se preservan al menos dos tierras y se favorece Boulder + tierra enderezada. Es una política explícita de control; todavía no optimiza secuencias de juego.", "",
             "## Controles exactos de las primeras siete", "",
             "Los porcentajes siguientes son analíticos y no están condicionados a conservar la mano. «Boulder + enderezada» solo indica posibilidad de lanzarlo T1 sin interacción: no significa poder filtrar T1, ni siquiera que la mano cumpla las dos tierras mínimas.", "",
             "| Composición | Tierras | Enderezadas | Bridges | Boulder | <2 tierras | Boulder | Boulder + enderezada | ≥2 tierras + Boulder + enderezada |",
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for v in result["variants"]:
        i = v["inventory"]
        e = exact_opening(i["lands"], i["untapped_lands"], i["boulders"])
        lines.append(f"| {v['id']} | {i['lands']} | {i['untapped_lands']} | {i['bridges']} | {i['boulders']} | {pct(e['initial_lt2'])} | {pct(e['initial_boulder'])} | {pct(e['initial_boulder_untapped'])} | {pct(e['initial_eligible_boulder_untapped'])} |")
    lines += ["", "## Piloto Monte Carlo", "",
              "Todos los porcentajes de esta tabla usan todos los intentos de la celda, incluidos los fallos. Los datos JSON/CSV incluyen recuentos, denominadores e intervalos Wilson al 95%. Los intervalos son de proporciones individuales; no sirven por sí solos para declarar diferencias entre variantes.", "",
              "| Composición | Política | Piso | Fallo de política | Boulder conservado | Boulder + enderezada conservados | Cartas medias, fallo=0 |",
              "| --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    for cell in result["cells"]:
        e = cell["events"]
        lines.append(f"| {cell['variant']} | {cell['policy']} | {cell['floor']} | {pct(e['failed']['rate'])} | {pct(e['kept_boulder']['rate'])} | {pct(e['kept_boulder_untapped']['rate'])} | {cell['mean_cards_unconditional']:.3f} |")
    lines += ["", "## Cambios exactos y límites", ""]
    for v in variants.values():
        delta = "; ".join(f"{n:+d} {name}" for name, n in v["changes"].items()) or "Sin cambios"
        lines.append(f"- **{v['id']}**: {delta}.")
    checks = [check for cell in result["cells"] for check in cell["checks"]]
    lines += ["", f"Controles Monte Carlo frente a fórmulas exactas: {sum(c['passed'] for c in checks)}/{len(checks)} dentro de la tolerancia predefinida de depuración (seis errores estándar + 1/N). No es una banda de confianza al 95% ni prueba de precisión fina.", "",
              "Se conserva la distribución completa de cartas finales y una muestra de trazas. La biblioteca conserva todas las cartas y el orden del fondo. La misma semilla por intento comparte azar entre celdas, pero aquí no se calculan intervalos de diferencias emparejadas.", "",
              "Citadel se prueba reemplazando Vault, reemplazando Drossforge y como tierra 20. Las comparaciones mezclan velocidad potencial y cambios de colores; todavía no se evalúa cuál funciona mejor durante la partida. La resistencia de indestructible frente a destrucción es una propiedad de las cartas, no un resultado simulado en esta etapa.", "",
              "Los reemplazos de Boulder por Spellbomb tampoco son neutrales. Este piloto puede medir manos, pero su efecto en robos, afinidad y jugadas debe evaluarse en el motor de turnos.", "",
              "## Siguiente etapa", "",
              "Verificar textos y legalidad del catálogo completo; implementar mesa, recursos y secuenciación T1–T6 con Boulder/scry, Cryogen, Thoughtcast, afinidad, Glint Hawk y sacrificios. Solo entonces medir el primer turno de acceso a W/U/B/R y después agregar escenarios de exilio/destrucción y recuperación.", ""]
    (output / "informe_piloto.md").write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=None)
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "pilot_01")
    args = parser.parse_args()
    paths = [ROOT/"data/reference_deck.json", ROOT/"data/opening_catalog.json", ROOT/"configs/opening_pilot.json"]
    reference, catalog_document, config = map(read_json, paths)
    if config["minimum_lands"] != 2:
        parser.error("This experiment requires at least two lands in every kept hand")
    catalog = catalog_document["cards"]
    n = args.trials if args.trials is not None else config["trials_per_cell"]
    if n < 1:
        parser.error("--trials must be positive")
    variants = build_variants(reference, catalog, config)
    cells = []
    started = time.perf_counter()
    for variant in variants:
        floors = [config["default_floor"]]
        sens = config["floor_sensitivity"]
        if variant["family"] == sens["family"] and variant["inventory"]["boulders"] == sens["boulder_count"]:
            floors += sens["additional_floors"]
        for floor in floors:
            for policy in config["policies"]:
                cells.append(run_cell(variant, catalog, policy, floor, n, config["seed"]))
    result = {"stage": config["stage"], "created_at_utc": datetime.now(timezone.utc).isoformat(),
              "python": platform.python_version(), "seed": config["seed"], "n_per_cell": n,
              "total_trials": n*len(cells), "elapsed_seconds": time.perf_counter()-started,
              "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                                for path in paths + [Path(__file__)]},
              "config": config, "reference_verification_status": reference["verification_status"],
              "variants": variants, "cells": cells}
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output/"results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False)+"\n")
    rows = []
    for cell in cells:
        for metric, event in cell["events"].items():
            rows.append({"variant": cell["variant"], "policy": cell["policy"], "floor": cell["floor"],
                         "metric": metric, "count": event["count"], "n": event["denominator"],
                         "rate": event["rate"], "wilson95_low": event["wilson95"][0],
                         "wilson95_high": event["wilson95"][1], "exact": event.get("exact", "")})
    with (args.output/"metrics.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    write_report(result, args.output)
    failures = [c for cell in cells for c in cell["checks"] if not c["passed"]]
    print(f"{len(variants)} composiciones, {len(cells)} celdas, {n*len(cells):,} intentos; {result['elapsed_seconds']:.2f} s")
    print(f"Informe: {args.output / 'informe_piloto.md'}")
    if failures:
        raise SystemExit(f"{len(failures)} controles fuera de tolerancia; revisar antes de continuar")
    print("Todos los controles exactos dentro de tolerancia; toda mano conservada tiene >=2 tierras.")


if __name__ == "__main__":
    main()
