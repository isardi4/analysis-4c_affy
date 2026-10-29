"""Exact land-only development, validated by a small Monte Carlo pilot.

Two stages: land count ignoring colors/tappedness; then tapped/untapped ratio.
This does not simulate the Affinity spell/draw engine or choose its best list.
"""

import argparse
from collections import defaultdict, Counter
import csv
import hashlib
import json
from math import comb, sqrt
from pathlib import Path
import random
import time

from src.opening_pilot import ROOT, choose, read_json, wilson

# State: hand bridges, hand untapped, board bridges, board untapped,
#        remaining bridges, remaining untapped, remaining nonlands in the top.


def natural_draw(mode, turn):
    if mode not in ("OTP", "OTD") or turn < 1:
        raise ValueError("Invalid mode or turn")
    return int(mode == "OTD" or turn > 1)


def kept_counts(b, u, spells, mulligans):
    if b+u < 2:
        return None
    if mulligans == 0:
        return b, u, spells
    size = 7-mulligans
    target = 3 if size >= 5 else 2
    low = max(2, size-spells)
    keep_lands = max(low, min(target, b+u, size))
    keep_u = min(u, keep_lands)
    return keep_lands-keep_u, keep_u, size-keep_lands


def opening_exact(lands, bridges, floor=4):
    if not 0 <= bridges <= lands <= 60 or floor not in (4, 5, 6, 7):
        raise ValueError("Invalid land composition or floor")
    untapped, spells = lands-bridges, 60-lands
    states = defaultdict(float)
    p_lt2 = (choose(60-lands, 7)+lands*choose(60-lands, 6))/comb(60, 7)
    sizes = {7-m: p_lt2**m*(1-p_lt2) for m in range(8-floor)}
    for b in range(8):
        for u in range(8-b):
            s = 7-b-u
            probability = choose(bridges, b)*choose(untapped, u)*choose(spells, s)/comb(60, 7)
            if not probability or b+u < 2:
                continue
            for m in range(8-floor):
                kb, ku, _ = kept_counts(b, u, s, m)
                # The bottomed cards remain outside the first 53 library cards.
                state = (kb, ku, 0, 0, bridges-b, untapped-u, spells-s)
                states[state] += p_lt2**m*probability
    return dict(states), {"initial_lt2": p_lt2, "failed": p_lt2**(8-floor),
                          "hand_sizes": sizes, "mean_cards_unconditional": sum(k*p for k, p in sizes.items())}


def play_land(state, policy):
    hb, hu, bp, up, db, du, ds = state
    capacity = bp+up
    if policy not in ("untapped_first", "bridge_t1_then_untapped"):
        raise ValueError("Unknown sequencing policy")
    if hb and ((policy == "bridge_t1_then_untapped" and bp+up == 0) or not hu):
        hb, bp = hb-1, bp+1
    elif hu:
        hu, up = hu-1, up+1
        capacity += 1
    return (hb, hu, bp, up, db, du, ds), capacity


def draw_branches(state, draw):
    if not draw:
        return [(state, 1.0)]
    hb, hu, bp, up, db, du, ds = state
    total = db+du+ds
    if total <= 0:
        raise ValueError("No cards left in the drawable top")
    branches = []
    if db:
        branches.append(((hb+1, hu, bp, up, db-1, du, ds), db/total))
    if du:
        branches.append(((hb, hu+1, bp, up, db, du-1, ds), du/total))
    if ds:
        branches.append(((hb, hu, bp, up, db, du, ds-1), ds/total))
    return branches


def turn_events(state, capacity, turn):
    hb, hu, bp, up, *_ = state
    return {"lands_on_curve": bp+up >= turn,
            "capacity_on_curve": capacity >= turn,
            "capacity_ge1": capacity >= 1,
            "capacity_ge2": capacity >= 2,
            "capacity_ge3": capacity >= 3,
            "screw_le2": bp+up <= 2,
            "six_or_more_lands_seen_proxy": hb+hu+bp+up >= 6}


def develop_exact(lands, bridges, mode, policy, floor=4, horizon=6):
    states, opening = opening_exact(lands, bridges, floor)
    success = 1-opening["failed"]
    turns = []
    for turn in range(1, horizon+1):
        updated, events = defaultdict(float), defaultdict(float)
        capacity_mean, land_mean, hand_land_mean = 0.0, 0.0, 0.0
        for state, weight in states.items():
            for drawn, p in draw_branches(state, natural_draw(mode, turn)):
                after, capacity = play_land(drawn, policy)
                mass = weight*p
                updated[after] += mass
                for name, event in turn_events(after, capacity, turn).items():
                    if event:
                        events[name] += mass
                land_mean += mass*(after[2]+after[3])
                capacity_mean += mass*capacity
                hand_land_mean += mass*(after[0]+after[1])
        states = updated
        draws = turn-int(mode == "OTP")
        turns.append({"turn": turn, "probabilities_unconditional": dict(events),
                      "screw_le2_conditional_on_kept": events["screw_le2"]/success,
                      "failure_or_screw_unconditional": opening["failed"]+events["screw_le2"],
                      "mean_lands_in_play_unconditional": land_mean,
                      "mean_capacity_unconditional": capacity_mean,
                      "mean_lands_in_hand_unconditional": hand_land_mean,
                      "mean_nonlands_seen_unconditional": opening["mean_cards_unconditional"]+draws*success-land_mean-hand_land_mean})
        if abs(sum(states.values())-success) > 1e-10:
            raise AssertionError("Probability mass lost")
    return {"opening": opening, "turns": turns}


def sample_opening(lands, bridges, rng, floor=4):
    template = ["B"]*bridges+["U"]*(lands-bridges)+["S"]*(60-lands)
    for m in range(8-floor):
        deck = list(template)
        rng.shuffle(deck)
        seven = Counter(deck[:7])
        kept = kept_counts(seven["B"], seven["U"], seven["S"], m)
        if kept:
            kb, ku, _ = kept
            bottom = ["B"]*(seven["B"]-kb)+["U"]*(seven["U"]-ku)+["S"]*(seven["S"]-kept[2])
            return {"hand": kept, "library": deck[7:]+bottom, "size": 7-m, "mulligans": m}
    return None


def develop_sample(opening, mode, policy, horizon=6):
    hb, hu, _ = opening["hand"]
    state = (hb, hu, 0, 0, 0, 0, 0)
    library, cursor, turns = opening["library"], 0, []
    for turn in range(1, horizon+1):
        if natural_draw(mode, turn):
            card = library[cursor]
            cursor += 1
            values = list(state)
            if card == "B":
                values[0] += 1
            if card == "U":
                values[1] += 1
            state = tuple(values)
        state, capacity = play_land(state, policy)
        turns.append({"turn": turn, "state": state[:4], "capacity": capacity,
                      "events": turn_events(state, capacity, turn)})
    return turns


def simulate_cell(lands, bridges, mode, policy, n, seed, floor, horizon):
    totals = [Counter() for _ in range(horizon)]
    failures, sizes, traces = 0, Counter(), []
    for trial in range(n):
        seed_value = int.from_bytes(hashlib.sha256(f"structural:{seed}:{trial}".encode()).digest()[:16], "big")
        opening = sample_opening(lands, bridges, random.Random(seed_value), floor)
        if opening is None:
            failures += 1
            continue
        sizes[opening["size"]] += 1
        turns = develop_sample(opening, mode, policy, horizon)
        for turn in turns:
            totals[turn["turn"]-1].update({k: int(v) for k, v in turn["events"].items()})
        if trial < 2:
            traces.append({"trial": trial, "opening": opening, "turns": turns})
    return {"n": n, "failures": failures, "hand_sizes": dict(sizes),
            "turns": [{key: {"count": counts[key], "denominator": n,
                              "rate": counts[key]/n, "wilson95": wilson(counts[key], n)}
                       for key in ("lands_on_curve", "capacity_on_curve", "capacity_ge1", "capacity_ge2", "capacity_ge3", "screw_le2", "six_or_more_lands_seen_proxy")}
                      for counts in totals], "traces": traces}


def report(result, out):
    pct = lambda p: f"{100*p:.2f}%"
    lines = ["# Parte 1 y 2: cantidad de tierras y coste de entrar giradas", "",
             "**Modelo estructural, no recomendación final del mazo.** Solo robos naturales y tierras. Sin colores, spells, scry, robos extra, afinidad ni rival. Cada no tierra es un marcador inerte. La capa siguiente incorporará el motor real y puede cambiar decisiones provisionales.", "",
             "Las probabilidades centrales son exactas por enumeración de estados. El Monte Carlo de 2.000 intentos por celda verifica la implementación; no decide entre resultados exactos.", "",
             "## Mano inicial y mulligan", "",
             "Ambos modos deciden el mulligan con siete cartas. OTD roba una al inicio de T1; OTP no. Conservar requiere al menos dos tierras desde la primera mano; el piso de cuatro y la selección del fondo son propuestas explícitas en la configuración. Con la misma regla, el mulligan tiene la misma distribución en OTP y OTD.", "",
             "| Tierras en las siete originales | Base de 19 | Base de 20 |",
             "| ---: | ---: | ---: |"]
    for k in range(8):
        lines.append(f"| {k} | {pct(result['opening_distribution']['19'][k])} | {pct(result['opening_distribution']['20'][k])} |")
    lines += ["", "## Parte 1: 19 contra 20, control ideal de tierras enderezadas", "",
              "Este control elimina el tipo de tierra para aislar su cantidad. No propone jugar cero bridges. Lands on curve es ≥3/4/5 tierras en mesa al terminar T3/T4/T5. Screw es ≤2 en mesa al terminar T4, condicionado a haber conservado mano. Los land drops usan todos los intentos como denominador, incluidos fallos de política.", "",
              "| Base | Modo | Curve T3 | Curve T4 | Curve T5 | Screw T4 entre keeps | Fallo mulligan |",
              "| --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    for cell in result["cells"]:
        if cell["part"] != 1:
            continue
        t = cell["exact"]["turns"]
        lines.append(f"| {cell['lands']} | {cell['mode']} | {pct(t[2]['probabilities_unconditional'].get('lands_on_curve',0))} | {pct(t[3]['probabilities_unconditional'].get('lands_on_curve',0))} | {pct(t[4]['probabilities_unconditional'].get('lands_on_curve',0))} | {pct(t[3]['screw_le2_conditional_on_kept'])} | {pct(cell['exact']['opening']['failed'])} |")
    lines += ["", "20 mejora indicadores de cantidad de tierras en este control. Eso no establece que sea mejor para Affinity: no hay motor de robo ni utilidad de las cartas que reemplaza. El JSON conserva también la cantidad de no tierras vistas y un proxy explícito de ≥6 tierras vistas a T5; no llamarlo derrota por flood.", "",
              "## Parte 2: bridges frente a tierras artefacto enderezadas", "",
              "Se mantienen ambos totales como control, para no cerrar 19/20 por adelantado. Las dos políticas son priorizar siempre enderezadas, o abrir con bridge T1 y después priorizar enderezadas. No usan información futura ni colores. La selección del fondo es común y prefiere conservar enderezadas.", "",
              "Capacidad es el maná disponible tras jugar tierra y antes de spells. Una tierra que acaba de entrar girada cuenta como tierra en mesa pero no como maná utilizable en ese turno. No es maná gastado ni desperdiciado.", "",
              "| Tierras | Bridges | Enderezadas | Modo | Política | ≥1 maná T1 | ≥2 manás T2 | ≥3 manás T3 | Capacidad acumulada media T1–T3 |",
              "| ---: | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: |"]
    for cell in result["cells"]:
        if cell["part"] != 2:
            continue
        t = cell["exact"]["turns"]
        lines.append(f"| {cell['lands']} | {cell['bridges']} | {cell['lands']-cell['bridges']} | {cell['mode']} | {cell['policy']} | {pct(t[0]['probabilities_unconditional'].get('capacity_ge1',0))} | {pct(t[1]['probabilities_unconditional'].get('capacity_ge2',0))} | {pct(t[2]['probabilities_unconditional'].get('capacity_ge3',0))} | {sum(x['mean_capacity_unconditional'] for x in t[:3]):.3f} |")
    lines += ["", "## Lectura correcta", "",
              "- Esta etapa cuantifica el coste de velocidad de 8–12 bridges. Al omitir fixing y resiliencia, entrar girado pierde sus compensaciones; no se puede descubrir un equilibrio interior completo con esta capa sola.",
              "- Las políticas pueden repartir capacidad de manera distinta entre T1 y T2. Más capacidad en un turno no prueba que se lanzaran más hechizos.",
              "- Una elección de 19/20 y ratio queda provisional hasta añadir colores, Boulder y robos. No trasladar automáticamente el resultado Grixis del video.",
              "- All four colours by T3 y Needed colours met quedan para la etapa de composición y spells. No hay resultados simulados de esos indicadores aquí.",
              "- Los CSV y JSON separan OTP/OTD, mantienen denominadores y guardan trazas. Los fallos del mulligan no se excluyen silenciosamente.", "",
              f"Controles de depuración Monte Carlo: {result['checks_passed']}/{result['checks_total']} dentro de seis errores estándar + 1/N. No es una banda del 95% ni una selección de ganadores.", ""]
    (out/"informe.md").write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT/"results/structural_stages")
    args = parser.parse_args()
    config_path = ROOT/"configs/structural_stages.json"
    config = read_json(config_path)
    specs = [(1,l,0,m,"untapped_first") for l in config['land_totals'] for m in config['modes']]
    specs += [(2,l,b,m,p) for l in config['land_totals'] for b in config['part_2']['bridge_counts']
              for m in config['modes'] for p in config['part_2']['policies']]
    cells, rows, passed, total = [], [], 0, 0
    began = time.perf_counter()
    for part, lands, bridges, mode, policy in specs:
        exact = develop_exact(lands, bridges, mode, policy, config['mulligan_floor'], config['horizon'])
        mc = simulate_cell(lands, bridges, mode, policy, config['trials_per_cell'], config['seed'], config['mulligan_floor'], config['horizon'])
        for turn, empirical in zip(exact['turns'], mc['turns']):
            for name, observed in empirical.items():
                p = turn['probabilities_unconditional'].get(name, 0)
                tolerance = 6*sqrt(p*(1-p)/mc['n'])+1/mc['n']
                passed += abs(observed['rate']-p) <= tolerance
                total += 1
                rows.append({"part":part,"lands":lands,"bridges":bridges,"mode":mode,"policy":policy,
                             "turn":turn['turn'],"metric":name,"exact":p,"mc_count":observed['count'],
                             "n":mc['n'],"mc_rate":observed['rate'],"wilson95_low":observed['wilson95'][0],
                             "wilson95_high":observed['wilson95'][1]})
        cells.append({"part":part,"lands":lands,"bridges":bridges,"mode":mode,"policy":policy,"exact":exact,"monte_carlo":mc})
    distribution = {str(l): [choose(l,k)*choose(60-l,7-k)/comb(60,7) for k in range(8)] for l in config['land_totals']}
    result = {"config":config,"opening_distribution":distribution,"cells":cells,"checks_passed":passed,
              "checks_total":total,"elapsed_seconds":time.perf_counter()-began,
              "source_sha256": {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in (config_path,Path(__file__))}}
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/"results.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    with (args.output/"metrics.csv").open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    report(result,args.output)
    print(f"{len(cells)} celdas exactas, {len(cells)*config['trials_per_cell']:,} trayectorias de control; {result['elapsed_seconds']:.2f} s")
    print(f"Controles: {passed}/{total}. Informe: {args.output/'informe.md'}")
    if passed != total:
        raise SystemExit("Revisar discrepancias antes de usar resultados")


if __name__ == "__main__":
    main()
