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

One common [Aholo Lux3D](https://lux3d.aholo3d.com) Skill for local installation in Codex, WorkBuddy, and other compatible hosts. Generate 3D assets from images or text, process existing models, and deliver verified files with an offline preview.

| | |
| --- | --- |
| International website | https://lux3d.aholo3d.com |
| China website | https://lux3d.aholo3d.cn |
| Local Skill name | `aholo-lux3d` |
| Version | `1.1.0` |
| Maintained Skill source | [`plugins/common/aholo-lux3d/`](plugins/common/aholo-lux3d/) |
| Historical archive (record only) | [`lux3d-plugin-1.1.0-common-skill.zip`](lux3d-plugin/common/lux3d-plugin-1.1.0-common-skill.zip) |

## 1.1.0 source maintenance (2026-10-10)

The maintained source and actual installation input are in
`plugins/common/aholo-lux3d/`. Source validation uses its own integrity record.
The ZIP and sidecars in `lux3d-plugin/common/` remain unchanged historical records;
they are not rebuilt for source updates and are not used to gate installation.
Version stays `1.1.0`. Changes are limited to this GitHub repository; no GitLab
synchronization, host installation, Git push or publication is implied.

## English

### Install in a compatible host

Ask your agent to install the common Skill:

```text
Read https://raw.githubusercontent.com/manycore-research/Aholo-Lux3D/master/AGENTS.md and install Aholo Lux3D as a local Skill in the current host.
```

The agent checks the host's supported local Skill directory and existing Aholo Lux3D installations, downloads the repository, verifies the maintained source, and installs the complete `aholo-lux3d` directory. The host needs local Skill support, Python 3.10 or newer, file access, HTTPS access, and secure credential injection. Codex, WorkBuddy, and other compatible hosts use the same files; each host's installation directory and reload procedure may differ.

For a manual installation from a downloaded checkout, first identify the host's actual **parent directory for local Skills**, then run from the repository root:

```text
python -B scripts/sync_release.py --check
python -B scripts/install_skill.py --skills-dir "<host-local-skills-directory>"
```

The installer creates `<host-local-skills-directory>/aholo-lux3d/`. An identical existing Skill remains unchanged. A different existing directory is rejected; it is never overwritten. Before switching from an old Skill or plugin, remove the old installation through the host's supported mechanism. Keep only one Aholo Lux3D installation in each host.

If your installation request includes a website-provided invite code, append `Invite Code: <your-actual-invite-code>` (or `邀请码：<实际邀请码>`), replacing the placeholder with the actual code. The agent forwards it to the installer; if there is no code, leave the suffix out. For manual installation, add `--invite-code="<your-actual-invite-code>"` to the installation command, quoting the value as one literal shell argument.

The installer trims the code, checks that it has 1–255 characters with no C0/C1 controls, and atomically saves `{"inviteCode":"<trimmed-code>"}` to `<host-local-skills-directory>/.aholo-lux3d-installation.json` after installation succeeds. This also works for an identical existing Skill. An explicit new code updates that file; omitting the flag preserves it. The file stays outside the verified Skill package, and failed verification or an installation conflict does not change it. The code is not printed in installer output.

Later quote/review/report/feedback collection includes the code as `context.inviteCode`. It is collection metadata only; it does not bind an invitation relationship or grant rewards. The local installer does not contact Lux3D.

Reload Skills or start a new task as required by the host, then verify that `aholo-lux3d` is available. In a new Codex task, invoke `$aholo-lux3d`. In WorkBuddy and other hosts, use their native Skill entrypoint. Install the entire directory, including runtime, contracts, and viewer assets; copying `SKILL.md` alone is insufficient.

No API key is needed to install. Paid generation later requires `LUX3D_CN_API_KEY` (China) or `LUX3D_GLOBAL_API_KEY` (international), configured according to the Skill's credential instructions. Never put keys in chat or committed files.

### Host identity and migration

The common runtime detects the actual host automatically: Codex `1`, Claude Code `2`, DeepSeek `3`, WorkBuddy `4`, and other hosts `100`. These are runtime identity values, not installation profiles to select manually.

This repository now distributes only the common local Skill. It no longer provides the Codex Git marketplace or a separate Codex plugin package. Previous commands using `codex plugin marketplace add` and `codex plugin add aholo-lux3d@lux3d` no longer apply to this repository. An existing installation from another plugin marketplace is managed through that marketplace separately.

The public `AGENTS.md` URL remains the installation entrypoint. A webpage can keep that URL, but its copy should describe local Skill installation and use `$aholo-lux3d` for Codex; the old `$lux3d` and plugin-selector instructions describe the previous distribution. Repository changes take effect for remote installs only after publication.

### Repository layers and maintenance

```text
plugins/common/aholo-lux3d/              Maintained Skill and installation input
  SKILL.md                             Skill entrypoint: aholo-lux3d
lux3d-plugin/common/
  lux3d-plugin-1.1.0-common-skill.zip    Historical artifact only; keep unchanged
  *.sha256                             Historical archive checksum
  *.release.json                       Historical release record
release-manifest.json                  Source integrity and historical artifact metadata
scripts/sync_release.py                Record and verify current Skill source
scripts/install_skill.py               Copy verified source to the host's Skill directory
AGENTS.md                              Agent installation and maintenance instructions
```

Edit `plugins/common/aholo-lux3d/` and refresh its source integrity record. Keep the
historical ZIP, checksum and release record untouched; current source may differ from
that ZIP. Installation does not require the ZIP and never extracts it over source.
Do not use the previous `--common-archive` import workflow for source maintenance.
This GitHub-only change does not modify the separate GitLab repository.

Use Python 3.10 or newer from the repository root:

```text
python -B scripts/sync_release.py
python -B scripts/sync_release.py --check
python -B -m unittest discover -s tests -v
```

The default command refreshes the source integrity record; `--check` validates without
writing. Neither command rebuilds or imports ZIPs. Installation verifies the maintained
source and the staged copy, and rejects different existing installations. These scripts
use the standard library; runtime tests also require `requests` from
`plugins/common/aholo-lux3d/core/runtime/requirements.txt`.

Record validation for the actual source revision. Historical tests of an older `1.1.0`
archive do not validate later source edits with the same version. Offline checks do not
establish public publication, real host upgrade, WorkBuddy loading or live paid generation.

## 中文

### 安装到支持本地 Skill 的宿主

将下面的指令发送给当前宿主的 agent：

```text
读取 https://raw.githubusercontent.com/manycore-research/Aholo-Lux3D/master/AGENTS.md，并将 Aholo Lux3D 作为本地 Skill 安装到当前宿主。
```

Agent 会确认宿主支持的本地 Skill 目录、检查已有的 Aholo Lux3D 安装、下载仓库并验证当前源码，再安装完整的 `aholo-lux3d` 目录。宿主需要支持本地 Skill、Python 3.10 及以上、文件访问、HTTPS 和安全凭据注入。Codex、WorkBuddy 及其他兼容宿主共用同一份内容，各自的安装目录和重新加载方式可以不同。

手动安装时，先下载仓库并确认宿主实际支持的**本地 Skill 父目录**，然后在仓库根目录执行：

```text
python -B scripts/sync_release.py --check
python -B scripts/install_skill.py --skills-dir "<宿主的本地Skill目录>"
```

安装结果位于 `<宿主的本地Skill目录>/aholo-lux3d/`。目标内容完全相同时不重复写入；目标已存在且内容不同时拒绝覆盖。迁移已有版本或 Codex 插件前，应通过宿主支持的方式移除旧安装，同一宿主只保留一份 Aholo Lux3D。

若官网安装请求带有邀请码，在请求后保留 `Invite Code: <实际邀请码>` 或 `邀请码：<实际邀请码>`，将占位文字替换为实际值。Agent 会将它传给安装器；没有邀请码时省略，不需要询问或编造。手动安装时，在安装命令后添加 `--invite-code="<实际邀请码>"`，按当前 shell 的规则将值作为一个字面量参数传入。

安装器去除首尾空白，校验剩余长度为 1–255 个字符且原值不含 C0/C1 控制字符；安装成功或确认同包已安装后，将 `{"inviteCode":"<去除首尾空白的邀请码>"}` 原子保存到 `<宿主的本地Skill目录>/.aholo-lux3d-installation.json`。显式传入新码可更新该文件，不传码则保留已有配置。配置位于 Skill 目录外，不影响源码校验；源码校验失败或安装冲突不会修改配置，命令输出不回显邀请码。

后续 quote/review/report/feedback 采集会携带 `context.inviteCode`。当前仅记录采集元数据，不建立邀请关系、不校验奖励资格或发放奖励；本地安装器不会调用 Lux3D 接口。

按宿主要求重新加载 Skill 或新建任务，确认能发现 `aholo-lux3d`。Codex 在新任务中使用 `$aholo-lux3d`；WorkBuddy 及其他宿主使用各自的原生 Skill 入口。必须安装完整目录，包括运行时、契约和离线查看器，不能只复制 `SKILL.md`。

安装阶段不需要 API Key。后续付费生成时，按 Skill 的凭据说明配置 `LUX3D_CN_API_KEY`（国内）或 `LUX3D_GLOBAL_API_KEY`（国际），不要将密钥放入聊天或提交到仓库。

### 宿主识别与旧版本迁移

公共运行时自动识别实际宿主：Codex 为 `1`、Claude Code 为 `2`、DeepSeek 为 `3`、WorkBuddy 为 `4`，其他为 `100`。这些是运行时身份值，安装时无需手工选择 `source` 或宿主配置包。

本仓库现在只分发公共本地 Skill，不再提供 Codex Git marketplace 或单独的 Codex 插件包。旧的 `codex plugin marketplace add` 和 `codex plugin add aholo-lux3d@lux3d` 安装方式不再适用于本仓库。来自其他插件市场的已有安装仍由对应市场独立管理。

公开的 `AGENTS.md` 地址继续作为 agent 安装入口。网站可以保留该地址，但说明应改为本地 Skill 安装，Codex 的调用名改为 `$aholo-lux3d`；原来的 `$lux3d` 和插件选择器说明属于旧分发方式。远程安装只有在仓库修改发布后才会使用新内容。

### 仓库分层与维护

- `plugins/common/aholo-lux3d/`：维护中的完整 Skill，也是所有兼容宿主的实际安装来源。
- `lux3d-plugin/common/`：历史 ZIP、原 `.sha256` 和 `.release.json`，仅作记录，源码更新时不修改。
- `release-manifest.json`：分别记录当前源码的完整性信息和历史归档信息。
- `scripts/sync_release.py`：更新源码记录或进行只读校验，不导入、不重打 ZIP。
- `scripts/install_skill.py`：将校验后的完整源码安装到宿主支持的本地目录。

保持版本 `1.1.0`，仅修改 GitHub 的 `plugins/` 主源，不修改 GitLab。当前源码无需与
历史 ZIP 内容一致，安装也不依赖该 ZIP；禁止为了同步而用旧 ZIP 覆盖源码。维护时使用
Python 3.10 及以上，在仓库根目录执行：

```text
python -B scripts/sync_release.py
python -B scripts/sync_release.py --check
python -B -m unittest discover -s tests -v
```

不带参数时更新源码完整性记录，`--check` 只验证不写入；不要再使用旧的
`--common-archive` 导入流程。安装器仍校验源码及暂存副本，并拒绝覆盖内容不同的已有
安装。脚本只使用标准库，运行时测试另需安装 `core/runtime/requirements.txt` 中的依赖。

验收结果对应实际源码修订。同为 `1.1.0` 的旧归档测试不能替代新源码验证；离线测试
不代表已推送 GitHub、已更新用户安装、已通过真实 WorkBuddy 加载或付费生成验收。

## 日本語

### 共通のローカル Skill をインストール

Aholo Lux3D は画像やテキストから 3D アセットを生成し、モデル処理とオフラインプレビューに対応します。Codex、WorkBuddy、その他の対応ホストは同じ `aholo-lux3d` Skill を使用します。

現在のホストの agent に次の指示を送信してください：

```text
Read https://raw.githubusercontent.com/manycore-research/Aholo-Lux3D/master/AGENTS.md and install Aholo Lux3D as a local Skill in the current host.
```

ホストにはローカル Skill、Python 3.10 以上、ファイル操作、HTTPS、安全な認証情報の受け渡しへの対応が必要です。手動の場合はリポジトリを取得し、ホストで実際に使われる Skill の親ディレクトリを確認して、ルートで実行します：

```text
python -B scripts/sync_release.py --check
python -B scripts/install_skill.py --skills-dir "<host-local-skills-directory>"
```

完全な `aholo-lux3d/` ディレクトリがインストールされます。同一内容の再インストールは変更なしで完了し、異なる既存内容は上書きしません。旧 Skill やプラグインから移行する場合はホストの正式な方法で旧版を削除し、同じホストに二重に入れないでください。

招待コードがある場合だけ、インストール依頼の末尾に `Invite Code: <実際のコード>` を追加してください。agent は `--invite-code` で渡し、Skill の親ディレクトリの `.aholo-lux3d-installation.json` に保存します。コードを省略すると既存設定を保持します。後の収集に `context.inviteCode` として含まれますが、招待関係の登録や報酬付与は行いません。

ホストの手順で再読み込みし、Codex では新しいタスクで `$aholo-lux3d` を使います。他のホストでは各自の Skill 入口を使用します。実際のホストは自動識別されるため、インストール時に `source` を選ぶ必要はありません。インストール時に API キーは不要です。有料生成には Skill の手順に従って `LUX3D_CN_API_KEY`（中国）または `LUX3D_GLOBAL_API_KEY`（海外）を設定します。

このリポジトリは共通 Skill のみを配布し、Codex Git marketplace と専用プラグイン配布は終了します。旧 marketplace コマンドと `$lux3d` の案内は新しい方式には適用されません。公開 `AGENTS.md` URL は維持されます。構成と同期コマンドは英語セクションを参照してください。`1.1.0` はローカルのリリース候補であり、オフライン検証だけでは公開済み、全ホストでの読み込み成功、有料生成の実動作確認を意味しません。

## Español

### Instalar la Skill local común

Aholo Lux3D genera activos 3D a partir de imágenes o texto, procesa modelos y ofrece una vista previa sin conexión. Codex, WorkBuddy y otros entornos compatibles usan la misma Skill `aholo-lux3d`.

Envía esta instrucción al agente del entorno actual:

```text
Read https://raw.githubusercontent.com/manycore-research/Aholo-Lux3D/master/AGENTS.md and install Aholo Lux3D as a local Skill in the current host.
```

El entorno debe admitir Skills locales, Python 3.10 o posterior, archivos, HTTPS e inyección segura de credenciales. Para instalar manualmente, descarga el repositorio, identifica el directorio padre de Skills que admite el entorno y ejecuta desde la raíz:

```text
python -B scripts/sync_release.py --check
python -B scripts/install_skill.py --skills-dir "<host-local-skills-directory>"
```

Se instala el directorio completo `aholo-lux3d/`. Una instalación idéntica no se modifica; una instalación diferente nunca se sobrescribe. Antes de migrar desde una Skill o plugin anterior, retíralo mediante el mecanismo admitido por el entorno. Mantén una sola instalación de Aholo Lux3D por entorno.

Si tienes un código de invitación, añade `Invite Code: <código real>` a la solicitud de instalación. El agente lo pasa con `--invite-code` y lo guarda en `.aholo-lux3d-installation.json`, en el directorio padre de la Skill. Omitir el código conserva la configuración existente. Las recopilaciones posteriores incluyen `context.inviteCode`; esto no vincula una invitación ni concede recompensas.

Recarga las Skills según el entorno; en Codex, inicia una nueva tarea y usa `$aholo-lux3d`. En otros entornos, usa su entrada nativa de Skills. La identidad del entorno se detecta automáticamente: no selecciones un `source` al instalar. La instalación no requiere clave API. Para generar con pago, configura `LUX3D_CN_API_KEY` (China) o `LUX3D_GLOBAL_API_KEY` (internacional) siguiendo las instrucciones de la Skill.

Este repositorio distribuye únicamente la Skill común; ya no ofrece un marketplace Git ni un paquete específico de Codex. Los comandos anteriores de marketplace y la invocación `$lux3d` no corresponden a esta distribución. La URL pública de `AGENTS.md` se conserva. Consulta la estructura y sincronización en inglés. `1.1.0` es un candidato local: las comprobaciones sin conexión no prueban publicación, carga en todos los entornos ni generación de pago real.

## Português

### Instalar a Skill local comum

O Aholo Lux3D gera ativos 3D a partir de imagens ou texto, processa modelos e oferece pré-visualização offline. Codex, WorkBuddy e outros ambientes compatíveis usam a mesma Skill `aholo-lux3d`.

Envie esta instrução ao agente do ambiente atual:

```text
Read https://raw.githubusercontent.com/manycore-research/Aholo-Lux3D/master/AGENTS.md and install Aholo Lux3D as a local Skill in the current host.
```

O ambiente precisa oferecer Skills locais, Python 3.10 ou superior, arquivos, HTTPS e injeção segura de credenciais. Para instalar manualmente, baixe o repositório, identifique o diretório pai de Skills aceito pelo ambiente e execute na raiz:

```text
python -B scripts/sync_release.py --check
python -B scripts/install_skill.py --skills-dir "<host-local-skills-directory>"
```

O diretório completo `aholo-lux3d/` será instalado. Uma instalação idêntica não é alterada; uma instalação diferente nunca é sobrescrita. Antes de migrar de uma Skill ou plugin anterior, remova a instalação antiga pelo mecanismo suportado pelo ambiente. Mantenha apenas uma instalação do Aholo Lux3D por ambiente.

Se tiver um código de convite, acrescente `Invite Code: <código real>` à solicitação de instalação. O agente o passa com `--invite-code` e o salva em `.aholo-lux3d-installation.json`, no diretório pai da Skill. Omitir o código preserva a configuração existente. As coletas posteriores incluem `context.inviteCode`; isso não vincula um convite nem concede recompensas.

Recarregue as Skills conforme o ambiente; no Codex, inicie uma nova tarefa e use `$aholo-lux3d`. Em outros ambientes, use a entrada nativa de Skills. O ambiente real é detectado automaticamente: não escolha um `source` na instalação. Nenhuma chave API é necessária para instalar. A geração paga exige `LUX3D_CN_API_KEY` (China) ou `LUX3D_GLOBAL_API_KEY` (internacional), conforme as instruções da Skill.

Este repositório distribui somente a Skill comum; deixou de oferecer um marketplace Git ou pacote exclusivo para Codex. Os comandos antigos de marketplace e a chamada `$lux3d` não se aplicam a esta distribuição. A URL pública de `AGENTS.md` permanece. Consulte a estrutura e sincronização na seção em inglês. `1.1.0` é um candidato local: verificações offline não comprovam publicação, carregamento em todos os ambientes nem geração paga real.
