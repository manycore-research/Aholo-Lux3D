<p align="center">
  <img src="assets/aholo-lux3d-logo.png" alt="Aholo Lux3D" width="420" />
</p>

# Aholo Lux3D

<p align="center">
  <strong>Languages:</strong>
  <a href="#english">English</a> ·
  <a href="#中文">中文</a> ·
  <a href="#日本語">日本語</a> ·
  <a href="#español">Español</a> ·
  <a href="#português">Português</a>
</p>

Codex plugin marketplace for [Aholo Lux3D](https://lux3d.aholo3d.com) — turn a single image or text prompt into production-ready 3D assets (geometry, PBR materials, online preview, GLB export, API / ComfyUI).

| | |
| --- | --- |
| Website | https://lux3d.aholo3d.com |
| Marketplace | `lux3d` |
| Plugin | `aholo-lux3d` |
| Selector | `aholo-lux3d@lux3d` |
| Version | `0.1.0` |

---

## English

### What is Aholo Lux3D?

Aholo Lux3D generates accurate 3D geometry and complete PBR textures from one image or a text description. Preview models in the browser, export GLB, or integrate through API and ComfyUI for production workflows.

Website: https://lux3d.aholo3d.com

### Install for Codex

**Option A — one command (recommended)**

Paste into any Codex task:

```text
/goal Read https://raw.githubusercontent.com/manycore-research/Aholo-Lux3D/master/AGENTS.md and install Aholo Lux3D for Codex.
```

**Option B — CLI**

```bash
codex plugin marketplace add manycore-research/Aholo-Lux3D --ref master
codex plugin add aholo-lux3d@lux3d
```

**Option C — download the package**

1. Download `aholo-lux3d.tar.gz` from [Releases](https://github.com/manycore-research/Aholo-Lux3D/releases).
2. Ask your AI agent to install that archive into Codex (for example: “Install this Codex plugin from `aholo-lux3d.tar.gz`”).

After install, start a **new** Codex task and run `$lux3d` or `@aholo-lux3d`. Plugin capabilities load when a task starts, so an existing task will not see it. Paid generation needs `LUX3D_CN_API_KEY` (China) or `LUX3D_GLOBAL_API_KEY` (international) in the environment.

### Check before you install

Find out whether Aholo Lux3D is already installed, from the Codex plugin directory or from this repository:

```bash
codex plugin list
```

Codex does **not** merge two skills that share a name. If this plugin ends up installed twice, `$lux3d` appears twice in the skill selector and the agent picks between them arbitrarily — a worse experience than a single install. If Aholo Lux3D is already present, keep that copy instead of adding a second one, or remove the old one first:

```bash
codex plugin remove aholo-lux3d@lux3d
```

Requires Codex CLI `0.121.0` or newer, which is when `codex plugin marketplace` was introduced. Older clients cannot install through the marketplace and should use Option C. Older clients are also a common reason a plugin appears to be “missing” from search.

### Layout

```text
.agents/plugins/marketplace.json   Codex marketplace catalog
plugins/codex/aholo-lux3d/         Installable plugin payload
AGENTS.md                          Canonical agent install guide
lux3d-plugin/codex/*.tar.gz        Packaged archive (portal / Release)
```

Releasing a new build: replace `plugins/codex/aholo-lux3d/` and bump `version` in `.codex-plugin/plugin.json`. Codex keys its install cache on `marketplace / plugin / version`, so an unchanged version number never triggers a reinstall.

---

## 中文

### Aholo Lux3D 是什么？

Aholo Lux3D 可将单张图片或文字描述转为可用于生产的 3D 资产：准确几何、完整 PBR 材质、在线预览、GLB 导出，并支持 API / ComfyUI 接入。

- 中国站：https://lux3d.aholo3d.cn
- 国际站：https://lux3d.aholo3d.com

### 安装到 Codex

**方式 A — 一条指令（推荐）**

在任意 Codex 任务中粘贴：

```text
/goal Read https://raw.githubusercontent.com/manycore-research/Aholo-Lux3D/master/AGENTS.md and install Aholo Lux3D for Codex.
```

**方式 B — 命令行**

```bash
codex plugin marketplace add manycore-research/Aholo-Lux3D --ref master
codex plugin add aholo-lux3d@lux3d
```

**方式 C — 下载安装包**

1. 从 [Releases](https://github.com/manycore-research/Aholo-Lux3D/releases) 下载 `aholo-lux3d.tar.gz`。
2. 把压缩包交给 AI，让它帮你安装到 Codex（例如：“请用这个 `aholo-lux3d.tar.gz` 安装 Codex 插件”）。

安装完成后，请**新建** Codex 任务，输入 `$lux3d` 或 `@aholo-lux3d`。插件能力在任务启动时才加载，已经在跑的任务看不到它。付费生成时在环境中配置 `LUX3D_CN_API_KEY`（国内）或 `LUX3D_GLOBAL_API_KEY`（国际）。

### 安装前先确认

先在 Codex 插件目录或本仓库确认 Aholo Lux3D 是否已经装过：

```bash
codex plugin list
```

Codex **不会合并**同名 Skill。如果这个插件被装了两份，`$lux3d` 会在技能选择器里出现两次，由 agent 随意挑一个，体验反而比只装一份更差。如果已经装了 Aholo Lux3D，请沿用已有那份，不要再装第二份；或者先卸载旧的：

```bash
codex plugin remove aholo-lux3d@lux3d
```

需要 Codex CLI `0.121.0` 及以上——`codex plugin marketplace` 从该版本开始提供。更低版本的客户端无法通过 marketplace 安装，请改用方式 C。客户端版本过旧，也是插件在搜索里“找不到”的常见原因。

---

## 日本語

### Aholo Lux3D とは？

Aholo Lux3D は、1 枚の画像またはテキストから、正確なジオメトリと完全な PBR テクスチャを持つ本番向け 3D アセットを生成します。ブラウザでプレビューし、GLB を書き出し、API / ComfyUI で連携できます。

ウェブサイト：https://lux3d.aholo3d.com

### Codex へのインストール

**方法 A — 1 行コマンド（推奨）**

任意の Codex タスクに貼り付け：

```text
/goal Read https://raw.githubusercontent.com/manycore-research/Aholo-Lux3D/master/AGENTS.md and install Aholo Lux3D for Codex.
```

**方法 B — CLI**

```bash
codex plugin marketplace add manycore-research/Aholo-Lux3D --ref master
codex plugin add aholo-lux3d@lux3d
```

**方法 C — パッケージをダウンロード**

1. [Releases](https://github.com/manycore-research/Aholo-Lux3D/releases) から `aholo-lux3d.tar.gz` を入手。
2. AI にそのアーカイブを渡して Codex へインストールしてもらう。

インストール後は**新しい** Codex タスクを開始し、`$lux3d` または `@aholo-lux3d` を実行してください。プラグインの機能はタスク開始時に読み込まれるため、実行中のタスクからは見えません。有料生成には `LUX3D_CN_API_KEY`（中国）または `LUX3D_GLOBAL_API_KEY`（海外）が必要です。

### インストール前の確認

Codex のプラグインディレクトリ、または本リポジトリで、Aholo Lux3D がすでに入っているか確認してください：

```bash
codex plugin list
```

Codex は同名のスキルを**統合しません**。このプラグインが二重に入ると、`$lux3d` がスキルセレクタに 2 つ現れ、agent がどちらかを任意に選びます。1 回だけ入れるより体験が悪くなります。すでに Aholo Lux3D がある場合は、それをそのまま使い、二つ目を追加しないでください。旧い方を先に削除する場合：

```bash
codex plugin remove aholo-lux3d@lux3d
```

Codex CLI `0.121.0` 以上が必要です（`codex plugin marketplace` はこのバージョンで導入されました）。それより古いクライアントは marketplace 経由でインストールできないため、方法 C をご利用ください。クライアントが古いことも、検索で「見つからない」よくある原因です。

---

## Español

### ¿Qué es Aholo Lux3D?

Aholo Lux3D convierte una imagen o una descripción de texto en activos 3D listos para producción: geometría precisa, texturas PBR completas, vista previa en el navegador, exportación GLB e integración por API / ComfyUI.

Sitio web: https://lux3d.aholo3d.com

### Instalar en Codex

**Opción A — un comando (recomendada)**

Pega esto en cualquier tarea de Codex:

```text
/goal Read https://raw.githubusercontent.com/manycore-research/Aholo-Lux3D/master/AGENTS.md and install Aholo Lux3D for Codex.
```

**Opción B — CLI**

```bash
codex plugin marketplace add manycore-research/Aholo-Lux3D --ref master
codex plugin add aholo-lux3d@lux3d
```

**Opción C — descargar el paquete**

1. Descarga `aholo-lux3d.tar.gz` desde [Releases](https://github.com/manycore-research/Aholo-Lux3D/releases).
2. Pide a tu agente de IA que instale ese archivo en Codex.

Después de instalar, inicia una **nueva** tarea de Codex y ejecuta `$lux3d` o `@aholo-lux3d`. Las capacidades del plugin se cargan al iniciar la tarea, así que una tarea en curso no lo verá. La generación de pago requiere `LUX3D_CN_API_KEY` (China) o `LUX3D_GLOBAL_API_KEY` (internacional).

### Comprueba antes de instalar

Averigua si Aholo Lux3D ya está instalado, desde el directorio de plugins de Codex o desde este repositorio:

```bash
codex plugin list
```

Codex **no** fusiona dos skills con el mismo nombre. Si este plugin acaba instalado dos veces, `$lux3d` aparecerá dos veces en el selector y el agente elegirá entre ellas de forma arbitraria: peor experiencia que una sola instalación. Si Aholo Lux3D ya está presente, quédate con esa copia en lugar de añadir una segunda, o elimina antes la antigua:

```bash
codex plugin remove aholo-lux3d@lux3d
```

Requiere Codex CLI `0.121.0` o superior, que es cuando se introdujo `codex plugin marketplace`. Los clientes más antiguos no pueden instalar desde el marketplace y deberían usar la Opción C. Un cliente antiguo también es una causa habitual de que un plugin parezca “no aparecer” en la búsqueda.

---

## Português

### O que é o Aholo Lux3D?

O Aholo Lux3D transforma uma imagem ou um texto em ativos 3D prontos para produção: geometria precisa, texturas PBR completas, pré-visualização no navegador, exportação GLB e integração via API / ComfyUI.

Site: https://lux3d.aholo3d.com

### Instalar no Codex

**Opção A — um comando (recomendada)**

Cole em qualquer tarefa do Codex:

```text
/goal Read https://raw.githubusercontent.com/manycore-research/Aholo-Lux3D/master/AGENTS.md and install Aholo Lux3D for Codex.
```

**Opção B — CLI**

```bash
codex plugin marketplace add manycore-research/Aholo-Lux3D --ref master
codex plugin add aholo-lux3d@lux3d
```

**Opção C — baixar o pacote**

1. Baixe `aholo-lux3d.tar.gz` em [Releases](https://github.com/manycore-research/Aholo-Lux3D/releases).
2. Peça ao agente de IA para instalar esse arquivo no Codex.

Após a instalação, inicie uma **nova** tarefa do Codex e execute `$lux3d` ou `@aholo-lux3d`. As capacidades do plugin são carregadas no início da tarefa, portanto uma tarefa em andamento não o verá. A geração paga precisa de `LUX3D_CN_API_KEY` (China) ou `LUX3D_GLOBAL_API_KEY` (internacional).

### Verifique antes de instalar

Descubra se o Aholo Lux3D já está instalado, no diretório de plugins do Codex ou neste repositório:

```bash
codex plugin list
```

O Codex **não** mescla duas skills com o mesmo nome. Se este plugin for instalado duas vezes, `$lux3d` aparecerá duas vezes no seletor e o agente escolherá entre elas de forma arbitrária — pior do que uma única instalação. Se o Aholo Lux3D já estiver presente, fique com essa cópia em vez de adicionar uma segunda, ou remova antes a antiga:

```bash
codex plugin remove aholo-lux3d@lux3d
```

Requer Codex CLI `0.121.0` ou superior, quando `codex plugin marketplace` foi introduzido. Clientes mais antigos não conseguem instalar pelo marketplace e devem usar a Opção C. Um cliente antigo também é uma causa comum de o plugin parecer “não aparecer” na busca.
