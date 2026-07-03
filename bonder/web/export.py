#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""export.py - empacota um BUNDLE ESTATICO publicavel (Bonder Viewer).

Gera um diretorio 100% estatico (HTML/JS/JSON) que reproduz o dashboard em modo
**somente visualizacao + curadoria (edicao)**, sem nenhuma dependencia de Python,
R, GPU ou Redis no servidor. E o que se hospeda na Hostinger (ou qualquer host
estatico), atras de senha, em `bonder.<seu-dominio>`.

Ideia: a analise pesada roda LOCAL (dashboard em localhost:8080, pipeline, SAINT,
DEP/limma, GPU). Este exportador copia os RESULTADOS ja gerados de cada corrida e
o viewer estatico, montando um pacote que so precisa ser enviado por FTP/hPanel.

Estrutura do bundle:
  index.html            viewer estatico (bonder/web/viewer/index.html)
  lib/*.js              cytoscape + marked (vendorizados; sem CDN)
  .htaccess             MIME + no-indexes (+ bloco de Basic Auth comentado)
  README_DEPLOY.md      passo a passo do deploy na Hostinger
  config.json           versao, contrastes, iscas (contexto para o viewer)
  runs/index.json       lista de corridas
  runs/<id>/...         results.json, interactors.tsv, network.json, volcano.png, ...
  docs/index.json       lista dos documentos (.md)
  docs/<id>.md          documentos de ajuda/metodologia

O viewer le tudo como arquivo estatico (fetch relativo), entao NAO ha API.
"""
from __future__ import annotations

import json
import shutil
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from bonder import __version__
from bonder.config import BonderConfig, load_config

# Arquivos de cada corrida que fazem sentido no viewer (os que existirem sao copiados).
RUN_FILES = [
    "results.json", "status.json", "interactors.tsv", "network.json",
    "network.graphml", "volcano.png", "manifest.json", "qc.json",
]


def _viewer_dir() -> Path:
    return Path(__file__).resolve().parent / "viewer"


def _run_contrast(run_dir: Path) -> Optional[str]:
    rj = run_dir / "results.json"
    if rj.exists():
        try:
            data = json.loads(rj.read_text(encoding="utf-8"))
            return (data.get("contrast") or {}).get("name")
        except Exception:
            return None
    return None


def _copy_runs(runs_dir: Path, out: Path, include_runs: Optional[List[str]]) -> List[Dict[str, Any]]:
    index: List[Dict[str, Any]] = []
    if not runs_dir.exists():
        return index
    for d in sorted(runs_dir.iterdir()):
        if not d.is_dir():
            continue
        if include_runs and d.name not in include_runs:
            continue
        # so exporta corridas com algum resultado
        if not (d / "results.json").exists() and not (d / "status.json").exists():
            continue
        dest = out / "runs" / d.name
        dest.mkdir(parents=True, exist_ok=True)
        for fname in RUN_FILES:
            src = d / fname
            if src.exists():
                shutil.copyfile(src, dest / fname)
        status: Dict[str, Any] = {}
        sj = d / "status.json"
        if sj.exists():
            try:
                status = json.loads(sj.read_text(encoding="utf-8"))
            except Exception:
                status = {}
        index.append({
            "run_id": d.name,
            "status": status.get("status", "done"),
            "contrast": _run_contrast(d) or status.get("contrast"),
            "updated": status.get("updated"),
        })
    return index


def _copy_docs(out: Path) -> List[Dict[str, Any]]:
    from bonder.web import docs as docs_mod
    docs_out = out / "docs"
    docs_out.mkdir(parents=True, exist_ok=True)
    doc_index: List[Dict[str, Any]] = []
    for d in docs_mod.list_docs():
        full = docs_mod.get_doc(d["id"])
        if not full:
            continue
        fname = "%s.md" % d["id"]
        (docs_out / fname).write_text(full["markdown"], encoding="utf-8")
        doc_index.append({"id": d["id"], "title": d["title"],
                          "category": d["category"], "file": fname})
    (docs_out / "index.json").write_text(
        json.dumps({"docs": doc_index}, indent=2, ensure_ascii=True), encoding="utf-8")
    return doc_index


def export_bundle(
    out_dir,
    cfg: Optional[BonderConfig] = None,
    runs_dir=None,
    include_runs: Optional[List[str]] = None,
    with_viewer: bool = True,
) -> Dict[str, Any]:
    """Monta o bundle estatico em out_dir. Retorna um resumo (contagens/caminhos)."""
    cfg = cfg or load_config()
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # 1) viewer estatico + libs + assets de deploy (copia a arvore inteira)
    if with_viewer:
        vd = _viewer_dir()
        if not vd.exists():
            raise FileNotFoundError("viewer nao encontrado em %s" % vd)
        shutil.copytree(vd, out, dirs_exist_ok=True)

    # 2) corridas
    rd = Path(runs_dir) if runs_dir else cfg.runs_dir
    index = _copy_runs(rd, out, include_runs)
    (out / "runs").mkdir(parents=True, exist_ok=True)
    (out / "runs" / "index.json").write_text(
        json.dumps({"runs": index}, indent=2, ensure_ascii=True), encoding="utf-8")

    # 3) documentos (.md)
    doc_index = _copy_docs(out)

    # 4) config.json (contexto para o viewer)
    config = {
        "title": "CoIP-MS / AP-MS - parceiros no proteoma murino",
        "version": __version__,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "contrasts": [
            {"name": c.get("name"), "bait_id": c.get("bait_id"), "strategy": c.get("strategy")}
            for c in cfg.contrasts()
        ],
        "baits": cfg.bait_ids(),
        "n_runs": len(index),
    }
    (out / "config.json").write_text(
        json.dumps(config, indent=2, ensure_ascii=True), encoding="utf-8")

    return {
        "out_dir": str(out),
        "n_runs": len(index),
        "runs": [r["run_id"] for r in index],
        "n_docs": len(doc_index),
        "viewer": with_viewer,
    }
