# Deploy do Bonder Viewer na Hostinger (bonder.ifrj-crj-geneticamolecular.online)

Versao **hospedada** e **leve** do bonder: somente **visualizacao e edicao
(curadoria)** dos resultados. A analise pesada (pipeline, SAINT, DEP/limma, GPU)
continua rodando **local** (dashboard em `localhost:8080`); aqui so publicamos os
resultados ja gerados. E um site 100% **estatico** — funciona em qualquer plano
Hostinger (inclusive o compartilhado), sem Python/Node no servidor.

## 0. Gerar o pacote (na sua maquina)

```bash
# exporta o bundle publicavel a partir das corridas locais (runs/)
python -m bonder.cli export --out dist_web
# opcional: apenas algumas corridas
python -m bonder.cli export --out dist_web --run run_NSs_vs_CTRL_20260702_120000
```

O `dist_web/` gerado ja contem: `index.html`, `lib/`, `.htaccess`,
`config.json`, `runs/` (com `index.json` + uma pasta por corrida) e `docs/`.

## 1. Criar o subdominio (hPanel)

1. hPanel -> **Dominios** -> **Subdominios**.
2. Crie `bonder` para `ifrj-crj-geneticamolecular.online`.
3. Anote a **pasta raiz (document root)**, ex.:
   `domains/ifrj-crj-geneticamolecular.online/public_html/bonder`
   (a Hostinger cria o registro DNS automaticamente; pode levar alguns minutos).

## 2. Enviar os arquivos

- **Gerenciador de Arquivos (hPanel)**: compacte o conteudo de `dist_web/` num
  `.zip`, envie para a pasta raiz do subdominio e **extraia la dentro**.
  Garanta que `index.html` fique na RAIZ do subdominio (nao dentro de uma subpasta).
- ou **FTP/SFTP** (FileZilla/WinSCP): copie tudo de `dist_web/` para a pasta raiz.

Confira: `https://bonder.ifrj-crj-geneticamolecular.online/` deve abrir o viewer.

## 3. Proteger por senha (a "area interna")

**(A) Recomendado - GUI:** hPanel -> **Avancado** ->
**Protecao por senha de diretorios** -> selecione a pasta do subdominio ->
crie usuario e senha. Pronto (a Hostinger cuida do `.htaccess`/`.htpasswd`).

**(B) Manual:** edite o `.htaccess` do bundle, descomente o bloco *Basic Auth* e
aponte `AuthUserFile` para o caminho ABSOLUTO do seu `.htpasswd` no servidor.
Gere o `.htpasswd` pelo hPanel ou com `htpasswd -c .htpasswd usuario`.

> O `.htaccess` incluido ja vem **seguro por padrao** (nao ativa a senha sozinho,
> para evitar erro 500); ele so define MIME correto, desliga a listagem de
> diretorios e cacheia os assets. A senha e ativada por (A) ou (B).

## 4. Atualizar os resultados (nas proximas corridas)

Rode `python -m bonder.cli export --out dist_web` de novo e reenvie **apenas** as
pastas `runs/`, `docs/` e o `config.json` (o `index.html`/`lib/` raramente mudam).

## Como o pesquisador usa (na area interna)

- Escolhe a corrida na barra lateral.
- **Resumo/QC**, **Volcano**, **Rede** (Cytoscape) - somente leitura.
- **Interatores (edicao)**: marca *Validado*, define *Confianca (curada)* e
  escreve *Nota*. As edicoes sao salvas **no proprio navegador** (localStorage) e
  podem ser **exportadas/importadas em JSON** e **baixadas como TSV** (interatores
  + curadoria) para anexar ao artigo/depositar.

> Observacao: por padrao a curadoria e por-navegador (client-side). Se voce quiser
> curadoria **compartilhada entre dispositivos/usuarios** (persistida no servidor),
> da para adicionar um mini-backend PHP+MySQL depois - a Hostinger compartilhada
> suporta nativamente. Peca que a gente evolui para essa versao.
