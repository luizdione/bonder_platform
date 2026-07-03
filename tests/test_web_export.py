#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes do exportador do bundle estatico (bonder.web.export).

Nucleo CPU: monta um diretorio de corrida minimo e verifica que o bundle
publicavel sai completo e coerente (viewer + libs + runs/index + docs + config).
"""
import json
from pathlib import Path

from bonder.config import load_config
from bonder.web.export import export_bundle


def _fake_run(runs_dir: Path, run_id: str) -> Path:
    d = runs_dir / run_id
    d.mkdir(parents=True, exist_ok=True)
    results = {
        "run_id": run_id,
        "contrast": {"name": "NSs_vs_CTRL", "bait_id": "NSs_ICOARACI", "strategy": "subtractive"},
        "summary": {"engine": "maxquant", "acquisition": "DDA", "n_proteins": 3, "n_samples": 6},
        "qc": {"median_valid_values": 3},
        "top_interactors": [{"prey": "P12345", "gene": "Prey1", "confidence": "alta"}],
        "artifacts": {"volcano_png": None},
    }
    (d / "results.json").write_text(json.dumps(results), encoding="utf-8")
    (d / "interactors.tsv").write_text(
        "prey\tgene\tconfidence\tobserved_ip\tobserved_ctrl\n"
        "P12345\tPrey1\talta\t3\t0\n", encoding="utf-8")
    (d / "network.json").write_text(json.dumps({"elements": []}), encoding="utf-8")
    (d / "status.json").write_text(json.dumps({"run_id": run_id, "status": "done",
                                               "contrast": "NSs_vs_CTRL"}), encoding="utf-8")
    return d


def test_export_bundle_is_complete(tmp_path: Path):
    cfg = load_config()
    runs_dir = tmp_path / "runs"
    _fake_run(runs_dir, "run_demo")
    out = tmp_path / "dist_web"

    summary = export_bundle(out, cfg=cfg, runs_dir=runs_dir)

    # viewer + libs + assets de deploy
    assert (out / "index.html").exists()
    assert (out / "lib" / "cytoscape.min.js").exists()
    assert (out / "lib" / "marked.min.js").exists()
    assert (out / ".htaccess").exists()
    assert (out / "README_DEPLOY.md").exists()

    # dados da corrida
    assert (out / "runs" / "run_demo" / "results.json").exists()
    assert (out / "runs" / "run_demo" / "interactors.tsv").exists()
    idx = json.loads((out / "runs" / "index.json").read_text(encoding="utf-8"))
    assert summary["n_runs"] == 1
    assert idx["runs"][0]["run_id"] == "run_demo"
    assert idx["runs"][0]["contrast"] == "NSs_vs_CTRL"
    assert idx["runs"][0]["status"] == "done"

    # config + docs
    cfg_json = json.loads((out / "config.json").read_text(encoding="utf-8"))
    assert cfg_json["version"]
    assert any(c["name"] == "NSs_vs_CTRL" for c in cfg_json["contrasts"])
    docs = json.loads((out / "docs" / "index.json").read_text(encoding="utf-8"))
    assert "docs" in docs and len(docs["docs"]) >= 1


def test_export_include_runs_filter(tmp_path: Path):
    cfg = load_config()
    runs_dir = tmp_path / "runs"
    _fake_run(runs_dir, "run_a")
    _fake_run(runs_dir, "run_b")
    out = tmp_path / "dist_web"

    summary = export_bundle(out, cfg=cfg, runs_dir=runs_dir, include_runs=["run_a"])
    assert summary["n_runs"] == 1
    assert (out / "runs" / "run_a").exists()
    assert not (out / "runs" / "run_b").exists()


def test_export_no_viewer_only_data(tmp_path: Path):
    cfg = load_config()
    runs_dir = tmp_path / "runs"
    _fake_run(runs_dir, "run_demo")
    out = tmp_path / "dist_data"

    export_bundle(out, cfg=cfg, runs_dir=runs_dir, with_viewer=False)
    assert not (out / "index.html").exists()          # sem viewer
    assert (out / "runs" / "index.json").exists()     # mas com dados
    assert (out / "config.json").exists()
