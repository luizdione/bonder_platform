#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""export.py - exporta uma corrida como pagina HTML estatica auto-contida.

Gera um unico arquivo .html (sem servidor, sem dependencias externas) com o
resumo/QC, a tabela de interatores, o volcano e a rede de interacao de UMA
corrida. Feito para publicar a VISUALIZACAO dos resultados (ex.: subir no
hPanel/Hostinger) - as analises continuam rodando no localhost.

Tudo e embutido no proprio HTML: dados (JSON inline), volcano (data URI) e o
cytoscape.min.js vendorizado (apenas quando ha rede). Basta abrir o arquivo.
"""
from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def _read_json(p: Path) -> Optional[Dict[str, Any]]:
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def _embed_json(obj: Any) -> str:
    """Serializa para embutir em <script> com seguranca (fecha-tags, nao-ASCII)."""
    return json.dumps(obj, ensure_ascii=True, default=str).replace("</", "<\\/")


def export_run(run_dir, out_path=None) -> Path:
    """Le os artefatos de uma corrida e escreve um HTML estatico auto-contido.

    run_dir : diretorio da corrida (contem results.json, interactors.tsv, etc.)
    out_path: destino do .html (default: <run_dir>/report.html)
    """
    run_dir = Path(run_dir)
    if not run_dir.exists():
        raise FileNotFoundError("corrida inexistente: %s" % run_dir)
    results = _read_json(run_dir / "results.json") or {}
    network = _read_json(run_dir / "network.json")

    # tabela completa (interactors.tsv) com fallback ao top_interactors do results.json
    interactors: List[Dict[str, Any]] = []
    tsv = run_dir / "interactors.tsv"
    if tsv.exists():
        try:
            import pandas as pd
            interactors = pd.read_csv(tsv, sep="\t").where(lambda d: d.notna(), None).to_dict(orient="records")
        except Exception:
            interactors = results.get("top_interactors", [])
    else:
        interactors = results.get("top_interactors", [])

    # volcano como data URI (self-contained)
    volcano_uri = None
    vp = run_dir / "volcano.png"
    if vp.exists():
        volcano_uri = "data:image/png;base64," + base64.b64encode(vp.read_bytes()).decode("ascii")

    # cytoscape.min.js vendorizado, embutido SO quando ha rede (economiza tamanho)
    cyto_js = ""
    if network:
        cyto = Path(__file__).resolve().parent / "static" / "vendor" / "cytoscape.min.js"
        if cyto.exists():
            cyto_js = cyto.read_text(encoding="utf-8")

    payload = {
        "results": results,
        "interactors": interactors,
        "volcano_uri": volcano_uri,
        "network": network,
    }
    html = (
        _HTML_TEMPLATE
        .replace("__RUN_ID__", str(results.get("run_id", run_dir.name)))
        .replace("/*__CYTOSCAPE__*/", cyto_js)
        .replace('"__DATA__"', _embed_json(payload))
    )
    out_path = Path(out_path) if out_path else run_dir / "report.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    return out_path


_HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>bonder - resultados __RUN_ID__</title>
<style>
  :root{ --bg:#f6f8fa; --panel:#fff; --panel2:#f0f3f6; --line:#d8dee4;
         --fg:#1b1f24; --muted:#5b6572; --accent:#1a56db; --ok:#188038; --warn:#b06000; }
  @media (prefers-color-scheme: dark){
    :root{ --bg:#0f1216; --panel:#171b21; --panel2:#1e242c; --line:#2a323c;
           --fg:#e6e9ee; --muted:#9aa4b2; --accent:#4c8bf5; --ok:#34a853; --warn:#f9ab00; } }
  *{box-sizing:border-box} body{margin:0;font:14px/1.55 system-ui,Segoe UI,Roboto,sans-serif;
    background:var(--bg);color:var(--fg)}
  header{padding:16px 22px;border-bottom:1px solid var(--line);background:var(--panel)}
  header h1{margin:0;font-size:18px} .sub{color:var(--muted);font-size:13px;margin-top:4px}
  main{max-width:1100px;margin:0 auto;padding:18px 22px}
  .card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin:14px 0}
  h2{font-size:15px;margin:0 0 12px;text-transform:uppercase;letter-spacing:.03em;color:var(--muted)}
  .kv{display:grid;grid-template-columns:220px 1fr;gap:5px 14px} .kv div:nth-child(odd){color:var(--muted)}
  .tblwrap{max-height:70vh;overflow:auto;border:1px solid var(--line);border-radius:8px}
  table{width:100%;border-collapse:collapse;font-size:13px}
  th,td{text-align:left;padding:6px 9px;border-bottom:1px solid var(--line);white-space:nowrap}
  th{color:var(--muted);position:sticky;top:0;background:var(--panel)}
  .pill{font-size:11px;padding:1px 8px;border-radius:999px;border:1px solid var(--line)}
  .pill.alta{color:var(--ok);border-color:var(--ok)} .pill.media{color:var(--warn)} .pill.baixa{color:var(--muted)}
  #cy{height:520px;background:var(--panel2);border-radius:10px}
  img.volcano{max-width:640px;width:100%;border-radius:8px}
  .hint{color:var(--muted);font-size:12px} code{background:var(--panel2);padding:1px 5px;border-radius:5px}
  footer{color:var(--muted);font-size:12px;padding:10px 22px;border-top:1px solid var(--line);margin-top:18px}
</style>
</head>
<body>
<header>
  <h1>bonder &middot; resultados</h1>
  <div class="sub" id="sub">corrida __RUN_ID__</div>
</header>
<main>
  <div class="card"><h2>Resumo / QC</h2><div class="kv" id="summary"></div></div>
  <div class="card"><h2>Interatores</h2>
    <div class="tblwrap"><table id="tbl"><thead></thead><tbody></tbody></table></div>
    <p class="hint">Ranqueado por BFDR (SAINT) e FDR (DEP). <b>log2fc*</b>: DEP/limma quando ha R;
    sem R, mostra o descritivo (razao de medias IP/controle, apenas QC).</p></div>
  <div class="card" id="volcanoCard"><h2>Volcano</h2><div id="volcano"></div></div>
  <div class="card" id="redeCard"><h2>Rede de interacao</h2><div id="cy"></div>
    <p class="hint">Cinza = isca; azul = presa detectada; arestas verdes = referencia (STRING/BioGRID).</p></div>
</main>
<footer id="foot">Gerado pelo bonder.</footer>

<script>/*__CYTOSCAPE__*/</script>
<script>
const DATA = "__DATA__";
const $ = s => document.querySelector(s);
const R = DATA.results || {}, S = R.summary || {}, QC = R.qc || {}, C = R.contrast || {};

$('#sub').textContent = 'corrida ' + (R.run_id || '') + (C.name ? (' · contraste ' + C.name) : '');
$('#summary').innerHTML = [
  ['Contraste', (C.name||'-') + (C.bait_id ? (' (isca ' + C.bait_id + ')') : '')],
  ['Motor / aquisicao', (S.engine||'-') + ' / ' + (S.acquisition||'-') + ' (' + (S.quant_type||'-') + ')'],
  ['Proteinas / amostras', (S.n_proteins!=null?S.n_proteins:'-') + ' / ' + (S.n_samples!=null?S.n_samples:'-')],
  ['Contaminantes / iscas', (S.n_contaminants||0) + ' / ' + (S.n_baits||0)],
  ['Valores validos (mediana)', QC.median_valid_values!=null?QC.median_valid_values:'-'],
  ['Candidatos na tabela', (DATA.interactors||[]).length],
].map(([k,v]) => '<div>'+k+'</div><div>'+v+'</div>').join('');

// tabela
const rows = DATA.interactors || [];
const cols = ['prey','gene','confidence','bfdr','saint_score','log2fc','adj_p_value','background_freq','observed_ip','observed_ctrl'];
$('#tbl thead').innerHTML = '<tr>'+cols.map(c=>'<th>'+(c==='log2fc'?'log2fc*':c)+'</th>').join('')+'</tr>';
$('#tbl tbody').innerHTML = rows.map(r=>'<tr>'+cols.map(c=>{
  let v = r[c];
  if(c==='log2fc' && (v===undefined||v===null)) v = r['log2fc_descriptive'];
  if(typeof v === 'number') v = Number.isInteger(v)? v : v.toFixed(3);
  if(c==='confidence') return '<td><span class="pill '+(v||'baixa')+'">'+(v||'')+'</span></td>';
  return '<td>'+(v===undefined||v===null?'':v)+'</td>';
}).join('')+'</tr>').join('') || '<tr><td>Sem candidatos.</td></tr>';

// volcano
if(DATA.volcano_uri){ $('#volcano').innerHTML = '<img class="volcano" alt="volcano" src="'+DATA.volcano_uri+'">'; }
else { $('#volcanoCard').innerHTML = '<h2>Volcano</h2><p class="hint">Requer a etapa DEP/limma (R). Sem R, veja a tabela.</p>'; }

// rede
if(DATA.network && window.cytoscape){
  try{
    cytoscape({ container: $('#cy'), elements: DATA.network.elements,
      style:[
        {selector:'node',style:{'label':'data(label)','font-size':9,'color':getComputedStyle(document.body).color,
          'background-color':'#4c8bf5','width':16,'height':16}},
        {selector:'node[?is_bait]',style:{'background-color':'#9aa4b2','width':30,'height':30,'font-size':12}},
        {selector:'edge',style:{'width':1,'line-color':'#8893a0'}},
        {selector:'edge[edge_type="reference"]',style:{'line-color':'#34a853','width':2}}
      ], layout:{name:'cose',animate:false} });
  }catch(e){ $('#cy').innerHTML = '<p class="hint" style="padding:12px">Rede indisponivel.</p>'; }
} else { $('#redeCard').innerHTML = '<h2>Rede de interacao</h2><p class="hint">Rede nao disponivel nesta corrida.</p>'; }

// rodape com proveniencia
const steps = (R.steps||[]).map(s=>s.step+':'+s.status).join('  ·  ');
$('#foot').innerHTML = 'Gerado pelo bonder' + (steps ? (' &middot; passos: '+steps) : '') + '. Visualizacao estatica; analises rodam no localhost.';
</script>
</body>
</html>
"""
