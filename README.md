# Aholo Lux3D

**Languages:** [English](#english) · [中文](#中文) · [日本語](#日本語) · [Español](#español) · [Português](#português)

Codex plugin marketplace for [Aholo Lux3D](https://lux3d.aholo3d.com) — turn a single image or text prompt into production-ready 3D assets (geometry, PBR materials, online preview, GLB export, API / ComfyUI).

| | |
| --- | --- |
| China site | https://lux3d.aholo3d.cn |
| International site | https://lux3d.aholo3d.com |
| Marketplace | `lux3d` |
| Plugin | `aholo-lux3d` |
| Selector | `aholo-lux3d@lux3d` |
| Version | `0.1.0` |

---

## English

### What is Aholo Lux3D?

Aholo Lux3D generates accurate 3D geometry and complete PBR textures from one image or a text description. Preview models in the browser, export GLB, or integrate through API and ComfyUI for production workflows.

### Install for Codex

**Option A — one command (recommended)**

Paste into any Codex task:

```text
/goal Read https://raw.githubusercontent.com/manycore-research/Aholo-Lux3D/master/AGENTS.md to install Aholo Lux3D for Codex and set up a new task for me.
```

**Option B — CLI**

```bash
codex plugin marketplace add manycore-research/Aholo-Lux3D --ref master
codex plugin add aholo-lux3d@lux3d
```

**Option C — download the package**

1. Download `aholo-lux3d.tar.gz` from [Releases](https://github.com/manycore-research/Aholo-Lux3D/releases).
2. Ask your AI agent to install that archive into Codex (for example: “Install this Codex plugin from `aholo-lux3d.tar.gz`”).

After install, start a **new** Codex task and run `$lux3d` or `@aholo-lux3d`. Paid generation needs `LUX3D_GLOBAL_API_KEY` (international) or `LUX3D_CN_API_KEY` (China) in the environment.

This repository must stay **public** so marketplace install works for everyone.

### Layout

```text
.agents/plugins/marketplace.json   Codex marketplace catalog
plugins/codex/aholo-lux3d/         Installable plugin payload
AGENTS.md                          Canonical agent install guide
lux3d-plugin/codex/*.tar.gz        Packaged archive (portal / Release)
```

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
/goal Read https://raw.githubusercontent.com/manycore-research/Aholo-Lux3D/master/AGENTS.md to install Aholo Lux3D for Codex and set up a new task for me.
```

**方式 B — 命令行**

```bash
codex plugin marketplace add manycore-research/Aholo-Lux3D --ref master
codex plugin add aholo-lux3d@lux3d
```

**方式 C — 下载安装包**

1. 从 [Releases](https://github.com/manycore-research/Aholo-Lux3D/releases) 下载 `aholo-lux3d.tar.gz`。
2. 把压缩包交给 AI，让它帮你安装到 Codex（例如：“请用这个 `aholo-lux3d.tar.gz` 安装 Codex 插件”）。

安装完成后，请**新建** Codex 任务，输入 `$lux3d` 或 `@aholo-lux3d`。付费生成时在环境中配置 `LUX3D_CN_API_KEY`（国内）或 `LUX3D_GLOBAL_API_KEY`（国际）。

本仓库需保持 **Public**，否则他人无法通过 marketplace 安装。

---

## 日本語

### Aholo Lux3D とは？

Aholo Lux3D は、1 枚の画像またはテキストから、正確なジオメトリと完全な PBR テクスチャを持つ本番向け 3D アセットを生成します。ブラウザでプレビューし、GLB を書き出し、API / ComfyUI で連携できます。

- 中国向けサイト：https://lux3d.aholo3d.cn
- 国際サイト：https://lux3d.aholo3d.com

### Codex へのインストール

**方法 A — 1 行コマンド（推奨）**

任意の Codex タスクに貼り付け：

```text
/goal Read https://raw.githubusercontent.com/manycore-research/Aholo-Lux3D/master/AGENTS.md to install Aholo Lux3D for Codex and set up a new task for me.
```

**方法 B — CLI**

```bash
codex plugin marketplace add manycore-research/Aholo-Lux3D --ref master
codex plugin add aholo-lux3d@lux3d
```

**方法 C — パッケージをダウンロード**

1. [Releases](https://github.com/manycore-research/Aholo-Lux3D/releases) から `aholo-lux3d.tar.gz` を入手。
2. AI にそのアーカイブを渡して Codex へインストールしてもらう。

インストール後は**新しい** Codex タスクを開始し、`$lux3d` または `@aholo-lux3d` を実行してください。有料生成には `LUX3D_GLOBAL_API_KEY`（国際）または `LUX3D_CN_API_KEY`（中国）が必要です。

---

## Español

### ¿Qué es Aholo Lux3D?

Aholo Lux3D convierte una imagen o una descripción de texto en activos 3D listos para producción: geometría precisa, texturas PBR completas, vista previa en el navegador, exportación GLB e integración por API / ComfyUI.

- Sitio de China：https://lux3d.aholo3d.cn
- Sitio internacional：https://lux3d.aholo3d.com

### Instalar en Codex

**Opción A — un comando (recomendada)**

Pega esto en cualquier tarea de Codex:

```text
/goal Read https://raw.githubusercontent.com/manycore-research/Aholo-Lux3D/master/AGENTS.md to install Aholo Lux3D for Codex and set up a new task for me.
```

**Opción B — CLI**

```bash
codex plugin marketplace add manycore-research/Aholo-Lux3D --ref master
codex plugin add aholo-lux3d@lux3d
```

**Opción C — descargar el paquete**

1. Descarga `aholo-lux3d.tar.gz` desde [Releases](https://github.com/manycore-research/Aholo-Lux3D/releases).
2. Pide a tu agente de IA que instale ese archivo en Codex.

Después de instalar, inicia una **nueva** tarea de Codex y ejecuta `$lux3d` o `@aholo-lux3d`. La generación de pago requiere `LUX3D_GLOBAL_API_KEY` (internacional) o `LUX3D_CN_API_KEY` (China).

---

## Português

### O que é o Aholo Lux3D?

O Aholo Lux3D transforma uma imagem ou um texto em ativos 3D prontos para produção: geometria precisa, texturas PBR completas, pré-visualização no navegador, exportação GLB e integração via API / ComfyUI.

- Site da China：https://lux3d.aholo3d.cn
- Site internacional：https://lux3d.aholo3d.com

### Instalar no Codex

**Opção A — um comando (recomendada)**

Cole em qualquer tarefa do Codex:

```text
/goal Read https://raw.githubusercontent.com/manycore-research/Aholo-Lux3D/master/AGENTS.md to install Aholo Lux3D for Codex and set up a new task for me.
```

**Opção B — CLI**

```bash
codex plugin marketplace add manycore-research/Aholo-Lux3D --ref master
codex plugin add aholo-lux3d@lux3d
```

**Opção C — baixar o pacote**

1. Baixe `aholo-lux3d.tar.gz` em [Releases](https://github.com/manycore-research/Aholo-Lux3D/releases).
2. Peça ao agente de IA para instalar esse arquivo no Codex.

Após a instalação, inicie uma **nova** tarefa do Codex e execute `$lux3d` ou `@aholo-lux3d`. A geração paga precisa de `LUX3D_GLOBAL_API_KEY` (internacional) ou `LUX3D_CN_API_KEY` (China).
