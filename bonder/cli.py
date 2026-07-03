#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cli.py - interface de linha de comando do bonder (headless / CI).

Subcomandos:
  bonder db sync              baixa e verifica os bancos murinos (databases.yaml)
  bonder db digest            digere in silico o proteoma murino (base peptideo->proteina)
  bonder baits check          valida iscas e monta o FASTA de busca combinado
  bonder qc --input F         resumo de QC de uma saida de busca
  bonder run --input F [...]  roda o pipeline para um contraste (isca vs controle)
  bonder list-contrasts       lista os contrastes definidos em samples.yaml
  bonder export --out DIR     empacota o viewer estatico publicavel (Hostinger)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from bonder import __version__
from bonder.config import load_config


def _run_id(prefix: str = "run") -> str:
    return "%s_%s" % (prefix, time.strftime("%Y%m%d_%H%M%S"))


def cmd_db_sync(args) -> int:
    from bonder.db.downloader import Downloader
    cfg = load_config()
    dl = Downloader(cfg.data_root, offline=cfg.offline)
    sources = cfg.databases.get("sources", {})
    plan = [
        ("uniprot_fasta", sources.get("uniprot_mouse", {}).get("fasta_url"), "uniprot/mouse.fasta",
         sources.get("uniprot_mouse", {}).get("sha256_fasta")),
        ("uniprot_idmap", sources.get("uniprot_mouse", {}).get("tsv_url"), "uniprot/mouse_idmap.tsv",
         sources.get("uniprot_mouse", {}).get("sha256_tsv")),
        ("string_links", sources.get("string_mouse", {}).get("links_url"),
         "string/10090.links.txt.gz", sources.get("string_mouse", {}).get("sha256_links")),
        ("string_aliases", sources.get("string_mouse", {}).get("aliases_url"),
         "string/10090.aliases.txt.gz", sources.get("string_mouse", {}).get("sha256_aliases")),
        ("contaminants", sources.get("contaminants", {}).get("url"), "contaminants/crap.fasta",
         sources.get("contaminants", {}).get("sha256")),
    ]
    ok = 0
    for name, url, dest, sha in plan:
        if not url:
            print("[skip] %s: url nao definida" % name)
            continue
        try:
            p = dl.fetch(name, url, dest, expected_sha256=sha)
            print("[ok]   %s -> %s" % (name, p))
            ok += 1
        except Exception as e:
            print("[erro] %s: %s" % (name, e))
    print("Sincronizacao: %d/%d fontes prontas em %s" % (ok, len(plan), cfg.data_root))
    return 0 if ok else 1


def _proteome_murine_out_root(cfg, override=None) -> Path:
    """Resolve a raiz da base digerida: --out > BONDER_PROTEOME_MURINE > yaml."""
    pm = cfg.databases.get("proteome_murine", {}) or {}
    raw = override or os.environ.get("BONDER_PROTEOME_MURINE") or pm.get("out_root") \
        or str(cfg.data_root / "proteome_murine")
    return Path(raw).expanduser()


def cmd_db_digest(args) -> int:
    """Digere in silico o proteoma murino -> base peptideo->proteina em out_root.

    1) garante o FASTA do proteoma (reusa cache/E: ou baixa e verifica);
    2) roda a digestao triptica (parametros de databases.yaml -> proteome_murine);
    3) grava peptides.tsv, protein_index.tsv, digest_profile.json e manifest.
    """
    from bonder.db.downloader import Downloader, sha256_of
    from bonder.db import digest as digest_mod

    cfg = load_config()
    pm = cfg.databases.get("proteome_murine", {}) or {}
    dig_cfg = dict(pm.get("digestion", {}) or {})
    out_root = _proteome_murine_out_root(cfg, getattr(args, "out", None))
    out_root.mkdir(parents=True, exist_ok=True)

    # --- 1) fonte: FASTA do proteoma murino -------------------------------
    src_name = pm.get("source", "uniprot_mouse")
    src = cfg.databases.get("sources", {}).get(src_name, {}) or {}
    fasta_url = src.get("fasta_url")
    source_fasta = out_root / "source" / "uniprot_mouse.fasta"

    # reusa uma copia ja baixada no cache do bonder, se existir (evita re-download)
    cache_fasta = cfg.cache_path("uniprot", "mouse.fasta")
    if not source_fasta.exists() and Path(cache_fasta).exists():
        source_fasta.parent.mkdir(parents=True, exist_ok=True)
        import shutil as _sh
        _sh.copyfile(cache_fasta, source_fasta)
        print("[ok]   fonte reusada do cache -> %s" % source_fasta)
    elif not source_fasta.exists():
        if not fasta_url:
            print("[erro] sem fasta_url para a fonte %r em databases.yaml" % src_name, file=sys.stderr)
            return 2
        dl = Downloader(out_root, offline=cfg.offline)
        try:
            source_fasta = dl.fetch("uniprot_mouse_fasta", fasta_url, "source/uniprot_mouse.fasta",
                                    expected_sha256=src.get("sha256_fasta"))
            print("[ok]   proteoma baixado -> %s" % source_fasta)
        except Exception as e:
            print("[erro] download do proteoma: %s" % e, file=sys.stderr)
            return 1
    else:
        print("[ok]   fonte ja presente -> %s" % source_fasta)

    # --- 2) parametros de digestao ----------------------------------------
    params = digest_mod.DigestParams(
        enzyme=dig_cfg.get("enzyme", "trypsin"),
        missed_cleavages=int(dig_cfg.get("missed_cleavages", 2)),
        min_length=int(dig_cfg.get("min_length", 7)),
        max_length=int(dig_cfg.get("max_length", 50)),
        min_mass=dig_cfg.get("min_mass"),
        max_mass=dig_cfg.get("max_mass"),
        fixed_cys_carbamidomethyl=bool(dig_cfg.get("fixed_cys_carbamidomethyl", True)),
    )
    max_proteins = getattr(args, "max_proteins", None)
    print("[..]   digerindo %s (enzima=%s, missed=%d, len=%d-%d%s) ..."
          % (source_fasta.name, params.enzyme, params.missed_cleavages,
             params.min_length, params.max_length,
             ", limite=%d proteinas" % max_proteins if max_proteins else ""))
    res = digest_mod.digest_proteome(source_fasta, params=params, max_proteins=max_proteins)

    # --- 3) gravacao ------------------------------------------------------
    source_info = {
        "fasta": str(source_fasta),
        "sha256": sha256_of(source_fasta),
        "source_name": src_name,
        "release": src.get("release") or src.get("version"),
        "include_trembl": bool(pm.get("include_trembl", False)),
    }
    paths = digest_mod.write_digest(res, out_root, source_info=source_info)
    print("[ok]   proteinas: %d | peptideos unicos: %d | proteotipicos: %d (%.1f%%)"
          % (res.n_proteins, res.n_peptides(), res.n_proteotypic(),
             100.0 * res.n_proteotypic() / res.n_peptides() if res.n_peptides() else 0.0))
    for k, p in paths.items():
        print("        %-13s -> %s" % (k, p))
    return 0


def cmd_baits_check(args) -> int:
    from bonder.db.baits import validate_baits, build_search_fasta
    cfg = load_config()
    warns = validate_baits(cfg.baits, cfg.config_dir)
    for w in warns:
        print("[aviso] %s" % w)
    fasta = cfg.cache_path("uniprot", "mouse.fasta")
    contam = cfg.cache_path("contaminants", "crap.fasta")
    out = build_search_fasta(
        cfg.baits, cfg.config_dir, cfg.data_root / "search_db.fasta",
        mouse_fasta=fasta if Path(fasta).exists() else None,
        contaminants_fasta=contam if Path(contam).exists() else None,
    )
    print("FASTA de busca: %s" % out)
    return 0


def cmd_qc(args) -> int:
    from bonder.io import load_search_output
    from bonder.stats import qc
    cfg = load_config()
    ds = load_search_output(args.input, samples_cfg=cfg.samples.get("samples", []),
                            baits_cfg=cfg.baits, report_tsv=args.report)
    print(json.dumps(qc.qc_summary(ds), indent=2, ensure_ascii=True))
    return 0


def cmd_list_contrasts(args) -> int:
    cfg = load_config()
    for c in cfg.contrasts():
        print("%-16s bait=%-14s test=%-12s control=%s"
              % (c.get("name"), c.get("bait_id"), c.get("test"), c.get("control")))
    return 0


def cmd_selftest(args) -> int:
    """Autoteste do pipeline (dados sinteticos). Exit 0 se PASSOU, 1 se FALHOU.

    Dentro da imagem de analise (SAINT + R presentes), os passos saint/dep rodam
    de verdade; em CPU puro eles aparecem como 'pulado'.
    """
    from bonder.web import health
    r = health.self_test()
    print("AUTOTESTE:", "PASSOU" if r.get("ok") else "FALHOU",
          "| candidatos:", r.get("n_candidates"), "| tempo:", r.get("elapsed_s"), "s")
    print("passos:", {s["step"]: s["status"] for s in r.get("steps", [])})
    for c in r.get("checks", []):
        print("  [%s] %s" % ("OK" if c["ok"] else "X ", c["artifact"]))
    if r.get("error"):
        print("erro:", r["error"])
    return 0 if r.get("ok") else 1


def cmd_export(args) -> int:
    """Empacota o bundle estatico publicavel (Bonder Viewer) para hospedar."""
    from bonder.web.export import export_bundle
    cfg = load_config()
    summary = export_bundle(
        args.out, cfg=cfg,
        runs_dir=args.runs_dir,
        include_runs=args.run or None,
        with_viewer=not args.no_viewer,
    )
    print("Bundle gerado em %s" % summary["out_dir"])
    print("  corridas: %d %s" % (summary["n_runs"], summary["runs"]))
    print("  documentos: %d" % summary["n_docs"])
    print("Envie o conteudo para a pasta do subdominio (ver README_DEPLOY.md).")
    return 0


def cmd_run(args) -> int:
    from bonder.pipeline import run_pipeline
    cfg = load_config()
    contrasts = cfg.contrasts()
    if args.contrast:
        contrasts = [c for c in contrasts if c.get("name") == args.contrast]
    elif args.bait:
        contrasts = [c for c in contrasts if c.get("bait_id") == args.bait]
    if not contrasts:
        print("Nenhum contraste correspondente em samples.yaml.", file=sys.stderr)
        return 2
    for c in contrasts:
        rid = args.run_id or _run_id(c.get("name", "run"))
        print("== rodando contraste %s (run_id=%s) ==" % (c.get("name"), rid))
        run_dir = run_pipeline(args.input, c, rid, cfg=cfg, report_tsv=args.report)
        print("saida: %s" % run_dir)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="bonder", description="Plataforma CoIP-MS / AP-MS (proteoma murino).")
    p.add_argument("--version", action="version", version="bonder %s" % __version__)
    sub = p.add_subparsers(dest="command", required=True)

    db = sub.add_parser("db", help="bancos de referencia")
    dbsub = db.add_subparsers(dest="db_command", required=True)
    dbsub.add_parser("sync", help="baixa e verifica os bancos murinos").set_defaults(func=cmd_db_sync)
    dg = dbsub.add_parser("digest", help="digere in silico o proteoma murino (base peptideo->proteina)")
    dg.add_argument("--out", default=None, help="raiz de saida (default: databases.yaml proteome_murine.out_root)")
    dg.add_argument("--max-proteins", dest="max_proteins", type=int, default=None,
                    help="limita o numero de proteinas (teste rapido)")
    dg.set_defaults(func=cmd_db_digest)

    bc = sub.add_parser("baits", help="iscas")
    bcsub = bc.add_subparsers(dest="baits_command", required=True)
    bcsub.add_parser("check", help="valida iscas e monta o FASTA de busca").set_defaults(func=cmd_baits_check)

    q = sub.add_parser("qc", help="resumo de QC")
    q.add_argument("--input", required=True)
    q.add_argument("--report", default=None, help="report.tsv do DIA-NN (opcional)")
    q.set_defaults(func=cmd_qc)

    lc = sub.add_parser("list-contrasts", help="lista contrastes de samples.yaml")
    lc.set_defaults(func=cmd_list_contrasts)

    ex = sub.add_parser("export", help="empacota o viewer estatico publicavel (Hostinger)")
    ex.add_argument("--out", required=True, help="diretorio de saida do bundle (ex.: dist_web)")
    ex.add_argument("--runs-dir", dest="runs_dir", default=None, help="diretorio de corridas (default: runs/)")
    ex.add_argument("--run", action="append", default=None, help="exporta apenas esta corrida (repetivel)")
    ex.add_argument("--no-viewer", dest="no_viewer", action="store_true",
                    help="nao copia o viewer/libs (so os dados runs/docs/config)")
    ex.set_defaults(func=cmd_export)

    st = sub.add_parser("selftest", help="autoteste do pipeline (valida SAINT/R quando presentes)")
    st.set_defaults(func=cmd_selftest)

    r = sub.add_parser("run", help="roda o pipeline")
    r.add_argument("--input", required=True, help="saida do motor de busca")
    r.add_argument("--report", default=None, help="report.tsv do DIA-NN (opcional)")
    g = r.add_mutually_exclusive_group()
    g.add_argument("--contrast", default=None, help="nome do contraste (samples.yaml)")
    g.add_argument("--bait", default=None, help="id da isca (samples.yaml)")
    r.add_argument("--run-id", dest="run_id", default=None)
    r.set_defaults(func=cmd_run)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
