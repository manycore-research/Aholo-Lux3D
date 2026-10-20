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

One common Aholo Lux3D suite for local installation in Codex, WorkBuddy, and other compatible hosts. A single `aholo-lux3d` Skill entry supports OpenAPI and MCP workflows. Generate 3D assets from images or text, process existing models, and deliver verified files with an offline preview.

**[国内官网 / China](https://lux3d.aholo3d.cn) · [International website / 国际官网](https://lux3d.aholo.ai)**

## Websites and API access / 网站与 API 入口

| Entry / 用途 | China / 国内 | International / 国际 |
| --- | --- | --- |
| Website / 官网 | [lux3d.aholo3d.cn](https://lux3d.aholo3d.cn) | [lux3d.aholo.ai](https://lux3d.aholo.ai) |
| API Key / 申请密钥 | [国内 API Key](https://labs.aholo3d.cn/api-keys?from=lux3d) | [International API Key](https://labs.aholo.ai/api-keys?from=lux3d) |
| Plans and credits / 套餐与积分 | [国内定价](https://lux3d.aholo3d.cn/lux3d/home?view=pricing&lang=zh_CN) | [International pricing](https://lux3d.aholo.ai/lux3d/home?view=pricing&lang=en_US) |
| API reference / 接口文档 | [国内接口文档](https://labs.aholo3d.cn/api-docs/api-reference) | [International API reference](https://labs.aholo.ai/api-docs/en/api-reference) |

Choose the website and API Key for the service region you intend to use. China and international API Keys are not interchangeable. No key is required to install this Common suite; follow the local installation instructions below.

请按计划使用的服务区域选择官网和 API Key，国内与国际区的密钥不通用。安装本仓库的 Common 套件无需 API Key，具体步骤见下方各语言的本地安装说明。

## Package / 套件信息

| | |
| --- | --- |
| Local Skill name | `aholo-lux3d` |
| Version | `1.2.0` |
| License | [MIT](LICENSE) |
| Execution modes | OpenAPI / MCP; China (`cn`) / international (`international`) |
| Maintained Skill source | [`plugins/common/aholo-lux3d/`](plugins/common/aholo-lux3d/) |
| Upstream suite snapshot (reference only) | [`lux3d-plugin-1.2.0-common-suite.zip`](lux3d-plugin/common/lux3d-plugin-1.2.0-common-suite.zip) |

## 1.2.0 common suite

Version `1.2.0` provides one complete `aholo-lux3d` Skill with OpenAPI and MCP
workflows. Choose the execution mode and service region before account, quote or
create calls. Both workflows retain plan review, pricing, authorization, REPORT
and delivery requirements; recorded tasks resume through their original route.

The suite supports image/text generation, material processing, mesh retopology,
model articulation, character auto-rigging and animation retargeting. Each paid
stage uses its matching quote and task authorization. Retargeting preserves
per-action partial results. International OpenAPI requests use
`https://api.aholo.ai/global`; see the
[official API reference](https://labs.aholo.ai/api-docs/en/llms.txt).

`plugins/common/aholo-lux3d/` is the maintained installation source. The original
`1.2.0` suite ZIP and its sidecars provide upstream provenance; source integrity
is recorded independently, including this repository's invite-code integration.

`1.2.0` 套件以一个 `aholo-lux3d` 入口提供 OpenAPI、MCP 两种方式，支持国内与国际区。
能力包括图文生成、材质处理、重拓扑、模型关节化、人物自动绑骨和动作迁移，
并统一使用计划、报价、授权、REPORT、任务恢复和交付流程。
实际安装来源是 `plugins/common/aholo-lux3d/`；原始 `1.2.0` ZIP 及其校验记录用于上游追溯，
当前源码独立记录完整性，并包含本仓库的邀请码集成。

REPORT sends the complete versioned plan, task-related original inputs and attachment
references, actual calls and result evidence to Lux3D for collaborative evaluation.
It lets the local agent and remote evaluator assess the plan and its execution together;
short summaries or plan links alone do not replace the available task context.
REPORT is automatic, including on first use; optional experience FEEDBACK has its
own exact-text consent. A valid successful REPORT receipt means remote evaluation passed; it does not replace user acceptance or authorize new spending.

REPORT 会将完整版本化计划、任务相关原始输入与附件引用、实际调用和结果证据提交到 Lux3D，
供本地 Agent 与远端协同评估方案及执行是否符合预期，不默认缩减为摘要。
REPORT 自动收尾，FEEDBACK 单独征求同意；REPORT 的有效成功回执表示远端评估通过，但不替代用户最终验收或费用授权。

## English

[International website](https://lux3d.aholo.ai) · [China website](https://lux3d.aholo3d.cn). Use the corresponding [international API Key](https://labs.aholo.ai/api-keys?from=lux3d) or [China API Key](https://labs.aholo3d.cn/api-keys?from=lux3d) for generation; the two regions' keys are not interchangeable.

### Install in a compatible host

Ask your agent to install the common Skill:

```text
Read https://raw.githubusercontent.com/manycore-research/Aholo-Lux3D/master/AGENTS.md and install Aholo Lux3D as a local Skill in the current host.
```

The agent checks the host's supported local Skill directory and existing Aholo Lux3D installations, downloads the repository, verifies the maintained source, and installs the complete `aholo-lux3d` directory. The installation helper needs Python 3.10 or newer and file access. Execution requirements depend on the selected mode below. Codex, WorkBuddy, and other compatible hosts use the same files; each host's installation directory and reload procedure may differ.

For a manual installation from a downloaded checkout, first identify the host's actual **parent directory for local Skills**, then run from the repository root:

```text
python -B scripts/sync_release.py --check
python -B scripts/install_skill.py --skills-dir "<host-local-skills-directory>"
```

The installer creates `<host-local-skills-directory>/aholo-lux3d/`. An identical existing Skill remains unchanged. A different existing directory is rejected; it is never overwritten. Use the host's supported replacement controls when changing an existing installation. Keep only one Aholo Lux3D installation in each host.

If your installation request includes a website-provided invite code, append `Invite Code: <your-actual-invite-code>` (or `邀请码：<实际邀请码>`), replacing the placeholder with the actual code. The agent forwards it to the installer; if there is no code, leave the suffix out. For manual installation, add `--invite-code="<your-actual-invite-code>"` to the installation command, quoting the value as one literal shell argument.

The installer trims the code, checks that it has 1–255 characters with no C0/C1 controls, and atomically saves `{"inviteCode":"<trimmed-code>"}` to `<host-local-skills-directory>/.aholo-lux3d-installation.json` after installation succeeds. This also works for an identical existing Skill. An explicit new code updates that file; omitting the flag preserves it. The file stays outside the verified Skill package, and failed verification or an installation conflict does not change it. The code is not printed in installer output.

The OpenAPI runtime includes the code as `context.inviteCode` in later quote/review/report/feedback collection. It is collection metadata only; it does not bind an invitation relationship or grant rewards. The local installer does not contact Lux3D or configure MCP credentials.

For MCP, the host follows the selected workflow to read and forward the saved code in the live tool schema's supported context; this is a host instruction, not automatic injection by the OpenAPI runtime. Explicit context takes precedence over saved task attribution, then installation configuration; frozen retries retain their original request.

Reload Skills or start a new task as required by the host, then verify that `aholo-lux3d` is available. In a new Codex task, invoke `$aholo-lux3d`. In WorkBuddy and other hosts, use their native Skill entrypoint. Install the entire directory, including runtime, contracts, and viewer assets; copying `SKILL.md` alone is insufficient.

No API key is needed to install. For OpenAPI generation, configure `LUX3D_CN_API_KEY` (China) or `LUX3D_GLOBAL_API_KEY` (international) according to the Skill's credential instructions. For MCP, use the selected region's host-supported connection and secure credential configuration. Never put keys in chat or committed files.

### Choose mode and region before execution

Reuse explicit mode, region and account choices. Establish **China / international** before account, quote or create calls. If mode is unspecified, inspect readiness and use the unambiguous configured route under [connection onboarding](plugins/common/aholo-lux3d/references/connection-onboarding.md); ask only about unresolved account or setup choices. Never infer region from language or failure.

| Mode | Workflow and prerequisites |
| --- | --- |
| OpenAPI | [`references/openapi-workflow.md`](plugins/common/aholo-lux3d/references/openapi-workflow.md), then the bundled Python runtime, contracts and offline viewer; requires local processes, files, HTTPS and secure credential injection. |
| MCP | [`references/mcp/workflow.md`](plugins/common/aholo-lux3d/references/mcp/workflow.md) and [connection setup](plugins/common/aholo-lux3d/references/mcp/README.md); requires a remote MCP client, live tool discovery and secure credentials. Loading this Skill does not register or authenticate MCP. Bind this task to the selected region's verified server. |

MCP execution does not require initializing the OpenAPI Python runtime. Both routes retain planning, pricing, authorization, REPORT and delivery rules. Switching mode, region or account starts a new execution context with fresh account and pricing checks. Resume recorded tasks and reports on their original route; resolve an uncertain create result before creating again, without automatically retrying through another mode or region.

### Host identity

The suite detects the actual host automatically: Codex `1`, Claude Code `2`,
DeepSeek `3`, WorkBuddy `4`, and other hosts `100`. Users select the execution
mode and service region; host identity comes from the current session.

The public `AGENTS.md` URL is the installation entrypoint. Install the complete
suite into the host's supported local Skill directory. In a new Codex task, use
`$aholo-lux3d`; other hosts use their native Skill entrypoint.

### Repository layers and maintenance

```text
plugins/common/aholo-lux3d/              Maintained Skill and installation input
  SKILL.md                             One entry: choose mode and region
  references/openapi-workflow.md        OpenAPI workflow and existing runtime
  references/mcp/                      MCP workflow and connection description
lux3d-plugin/common/
  lux3d-plugin-1.2.0-common-suite.zip    Original upstream reference snapshot
  *.sha256                             Original archive checksums
  *.release.json                       Original release records
release-manifest.json                  Source integrity and archive metadata
scripts/sync_release.py                Record and verify current Skill source
scripts/install_skill.py               Copy verified source to the host's Skill directory
AGENTS.md                              Agent installation and maintenance instructions
```

Maintain `plugins/common/aholo-lux3d/` as one complete suite. After source changes,
refresh its integrity record, then verify and test from the repository root with
Python 3.10 or newer:

```text
python -B scripts/sync_release.py
python -B scripts/sync_release.py --check
python -B -m unittest discover -s tests -v
```

The default command refreshes source metadata; `--check` validates without writing.
The installer copies the verified source and checks the staged copy. It rejects a
different existing installation. The upstream `1.2.0` ZIP and its sidecars remain
reference artifacts, independent of source validation and installation.

The scripts use the Python standard library. Runtime tests also need `requests`
from `plugins/common/aholo-lux3d/core/runtime/requirements.txt`. Record checks for
the actual source revision; real host loading, MCP authentication and paid
generation require their own validation. Remote installation receives repository
changes after publication.

## 中文

[国内官网](https://lux3d.aholo3d.cn) · [国际官网](https://lux3d.aholo.ai)。生成前按所选区域申请[国内 API Key](https://labs.aholo3d.cn/api-keys?from=lux3d)或[国际 API Key](https://labs.aholo.ai/api-keys?from=lux3d)，两区密钥不通用。

### 安装到支持本地 Skill 的宿主

将下面的指令发送给当前宿主的 agent：

```text
读取 https://raw.githubusercontent.com/manycore-research/Aholo-Lux3D/master/AGENTS.md，并将 Aholo Lux3D 作为本地 Skill 安装到当前宿主。
```

Agent 会确认宿主支持的本地 Skill 目录、检查已有的 Aholo Lux3D 安装、下载仓库并验证当前源码，再安装完整的 `aholo-lux3d` 目录。安装脚本需要 Python 3.10 及以上和文件访问能力；运行所需能力按下方选定模式检查。Codex、WorkBuddy 及其他兼容宿主共用同一份内容，各自的安装目录和重新加载方式可以不同。

手动安装时，先下载仓库并确认宿主实际支持的**本地 Skill 父目录**，然后在仓库根目录执行：

```text
python -B scripts/sync_release.py --check
python -B scripts/install_skill.py --skills-dir "<宿主的本地Skill目录>"
```

安装结果位于 `<宿主的本地Skill目录>/aholo-lux3d/`。目标内容完全相同时不重复写入；目标已存在且内容不同时拒绝覆盖。替换已有安装时使用宿主支持的方式，同一宿主只保留一份 Aholo Lux3D。

若官网安装请求带有邀请码，在请求后保留 `Invite Code: <实际邀请码>` 或 `邀请码：<实际邀请码>`，将占位文字替换为实际值。Agent 会将它传给安装器；没有邀请码时省略，不需要询问或编造。手动安装时，在安装命令后添加 `--invite-code="<实际邀请码>"`，按当前 shell 的规则将值作为一个字面量参数传入。

安装器去除首尾空白，校验剩余长度为 1–255 个字符且原值不含 C0/C1 控制字符；安装成功或确认同包已安装后，将 `{"inviteCode":"<去除首尾空白的邀请码>"}` 原子保存到 `<宿主的本地Skill目录>/.aholo-lux3d-installation.json`。显式传入新码可更新该文件，不传码则保留已有配置。配置位于 Skill 目录外，不影响源码校验；源码校验失败或安装冲突不会修改配置，命令输出不回显邀请码。

OpenAPI 运行时的后续 quote/review/report/feedback 采集会携带 `context.inviteCode`。当前仅记录采集元数据，不建立邀请关系、不校验奖励资格或发放奖励；本地安装器不会调用 Lux3D 接口，也不会配置 MCP 凭据。

MCP 路线由宿主按所选工作流读取并转发保存的邀请码，使用实时工具 schema 支持的 context；这是宿主执行指引，不是 OpenAPI 运行时自动注入。显式 context 优先于已保存任务归因，再读取安装配置；冻结重试保留原请求。

按宿主要求重新加载 Skill 或新建任务，确认能发现 `aholo-lux3d`。Codex 在新任务中使用 `$aholo-lux3d`；WorkBuddy 及其他宿主使用各自的原生 Skill 入口。必须安装完整目录，包括运行时、契约和离线查看器，不能只复制 `SKILL.md`。

安装阶段不需要 API Key。后续使用 OpenAPI 时，按 Skill 的凭据说明配置 `LUX3D_CN_API_KEY`（国内）或 `LUX3D_GLOBAL_API_KEY`（国际）；使用 MCP 时，通过宿主支持的方式配置选定区域的连接与凭据。不要将密钥放入聊天或提交到仓库。

### 执行前选择模式和区域

复用已明确的模式、区域和账户。国内 / 国际区未明确时先询问；模式未指定时先检查连接，复用该区域无歧义的可用路线，不强制用户理解 OpenAPI / MCP。缺少连接时先准备可自动完成的配置，只请用户补充私密凭据或完成必要重载。不能凭语言或失败请求推断区域；详见[连接引导](plugins/common/aholo-lux3d/references/connection-onboarding.md)。

| 模式 | 执行流程与条件 |
| --- | --- |
| OpenAPI | 从 [`references/openapi-workflow.md`](plugins/common/aholo-lux3d/references/openapi-workflow.md) 进入现有 Python 运行时、契约和离线查看器流程；需要本地进程、文件、HTTPS 和安全凭据注入。 |
| MCP | 使用 [`references/mcp/workflow.md`](plugins/common/aholo-lux3d/references/mcp/workflow.md) 和[连接说明](plugins/common/aholo-lux3d/references/mcp/README.md)；需要远程 MCP 客户端、实时工具发现和安全凭据配置。加载 Skill 不会自动注册或认证 MCP，本次任务只调用所选区域的已验证服务。 |

仅使用 MCP 时，无需初始化 OpenAPI 的 Python 运行时。两种路线都保留计划、报价、授权、REPORT 和交付要求。切换模式、区域或账号时建立新执行上下文，重新确认账号与报价；已有任务和报告沿原路线恢复。create 结果不确定时先核实，不得自动换模式或换区域重复创建。

### 宿主识别

套件自动识别实际宿主：Codex 为 `1`、Claude Code 为 `2`、DeepSeek 为 `3`、
WorkBuddy 为 `4`，其他为 `100`。用户明确服务区域，执行方式按连接引导解析，宿主身份由当前会话确定。

公开的 `AGENTS.md` 地址是 agent 安装入口，将完整套件安装到宿主支持的本地 Skill 目录。
Codex 在新任务中使用 `$aholo-lux3d`，其他宿主使用各自的原生 Skill 入口。

### 仓库分层与维护

- `plugins/common/aholo-lux3d/`：完整的 `1.2.0` 套件，一个 Skill 入口，包含 OpenAPI 运行时和 MCP 资源，也是各宿主的实际安装来源。
- `lux3d-plugin/common/`：原始 `1.2.0` 套件 ZIP、`.sha256` 和 `.release.json`，用于追溯上游产物。
- `release-manifest.json`：记录版本、双模式要求、当前源码完整性和上游产物信息。
- `scripts/sync_release.py`：更新源码记录或进行只读校验。
- `scripts/install_skill.py`：将校验后的完整源码安装到宿主支持的本地目录。

维护 `plugins/common/aholo-lux3d/` 后，使用 Python 3.10 及以上在仓库根目录更新记录并检查：

```text
python -B scripts/sync_release.py
python -B scripts/sync_release.py --check
python -B -m unittest discover -s tests -v
```

不带参数时更新源码完整性记录，`--check` 只验证不写入。安装器校验源码和暂存副本，
并拒绝覆盖内容不同的已有安装。原始 `1.2.0` ZIP 及其校验记录独立留存，安装与源码校验
直接使用维护目录。脚本仅使用 Python 标准库；运行时测试另需安装
`core/runtime/requirements.txt` 中的依赖。

验收结果对应实际源码修订。真实宿主加载、MCP 鉴权和付费生成需分别验证；
远程安装在仓库变更发布后获取新内容。

## 日本語

[国際サイト](https://lux3d.aholo.ai) · [中国サイト](https://lux3d.aholo3d.cn)。生成時には選択した地域の [国際 API キー](https://labs.aholo.ai/api-keys?from=lux3d) または [中国 API キー](https://labs.aholo3d.cn/api-keys?from=lux3d) を使用してください。両地域のキーは相互に利用できません。

### 共通のローカル Skill をインストール

Aholo Lux3D は画像やテキストから 3D アセットを生成し、モデル処理とオフラインプレビューに対応します。Codex、WorkBuddy、その他の対応ホストは同じ `aholo-lux3d` Skill を使用します。

現在のホストの agent に次の指示を送信してください：

```text
Read https://raw.githubusercontent.com/manycore-research/Aholo-Lux3D/master/AGENTS.md and install Aholo Lux3D as a local Skill in the current host.
```

ホストにはローカル Skill への対応が必要で、インストール用スクリプトには Python 3.10 以上とファイル操作が必要です。手動の場合はリポジトリを取得し、ホストで実際に使われる Skill の親ディレクトリを確認して、ルートで実行します：

```text
python -B scripts/sync_release.py --check
python -B scripts/install_skill.py --skills-dir "<host-local-skills-directory>"
```

完全な `aholo-lux3d/` ディレクトリがインストールされます。同一内容の再インストールは変更なしで完了し、異なる既存内容は上書きしません。既存のインストールを置き換える場合はホストの正式な方法を使い、同じホストに一つだけインストールしてください。

招待コードがある場合だけ、インストール依頼の末尾に `Invite Code: <実際のコード>` を追加してください。agent は `--invite-code` で渡し、Skill の親ディレクトリの `.aholo-lux3d-installation.json` に保存します。コードを省略すると既存設定を保持します。後の OpenAPI 収集に `context.inviteCode` として含まれますが、招待関係の登録や報酬付与は行いません。

ホストの手順で再読み込みし、Codex では新しいタスクで `$aholo-lux3d` を使います。他のホストでは各自の Skill 入口を使用します。実際のホストは自動識別されるため、インストール時に `source` を選ぶ必要はありません。インストール時に API キーは不要です。OpenAPI の利用時には Skill の手順に従って `LUX3D_CN_API_KEY`（中国）または `LUX3D_GLOBAL_API_KEY`（海外）を設定します。MCP では選択した地域の接続とホストの安全な認証設定を使用します。

同じ入口で OpenAPI / MCP と中国 / 海外を選びます。既に確定した選択を引き継ぎ、不明なら account、quote、create の前に確認します。MCP の説明は `references/mcp/` に含まれますが、Skill のインストールだけで MCP の登録や認証は行われません。MCP の実行に OpenAPI 用 Python ランタイムの初期化は不要です。モード・地域・アカウントを変更したら新しい実行コンテキストでアカウントと料金を再確認し、既存タスクは元の経路で再開します。create の結果が不明な場合、経路を切り替えて重複作成せず、先に結果を確認します。両モードで計画、承認、REPORT、納品の要件を維持します。

このリポジトリは単一入口の Common suite `1.2.0` を配布します。`AGENTS.md` に従って完全なソースディレクトリをインストールし、Codex では `$aholo-lux3d` を使用してください。構成と保守コマンドは英語セクションを参照してください。実際のホストでの読み込み、MCP 認証、有料生成はそれぞれ検証が必要です。

## Español

[Sitio internacional](https://lux3d.aholo.ai) · [Sitio de China](https://lux3d.aholo3d.cn). Para generar, solicita la [clave de API internacional](https://labs.aholo.ai/api-keys?from=lux3d) o la [clave de API de China](https://labs.aholo3d.cn/api-keys?from=lux3d) correspondiente a la región elegida. Las claves no son intercambiables entre regiones.

### Instalar la Skill local común

Aholo Lux3D genera activos 3D a partir de imágenes o texto, procesa modelos y ofrece una vista previa sin conexión. Codex, WorkBuddy y otros entornos compatibles usan la misma Skill `aholo-lux3d`.

Envía esta instrucción al agente del entorno actual:

```text
Read https://raw.githubusercontent.com/manycore-research/Aholo-Lux3D/master/AGENTS.md and install Aholo Lux3D as a local Skill in the current host.
```

El entorno debe admitir Skills locales; el instalador necesita Python 3.10 o posterior y acceso a archivos. Para instalar manualmente, descarga el repositorio, identifica el directorio padre de Skills que admite el entorno y ejecuta desde la raíz:

```text
python -B scripts/sync_release.py --check
python -B scripts/install_skill.py --skills-dir "<host-local-skills-directory>"
```

Se instala el directorio completo `aholo-lux3d/`. Una instalación idéntica no se modifica; una instalación diferente nunca se sobrescribe. Para reemplazar una instalación existente, utiliza el mecanismo admitido por el entorno. Mantén una sola instalación de Aholo Lux3D por entorno.

Si tienes un código de invitación, añade `Invite Code: <código real>` a la solicitud de instalación. El agente lo pasa con `--invite-code` y lo guarda en `.aholo-lux3d-installation.json`, en el directorio padre de la Skill. Omitir el código conserva la configuración existente. Las recopilaciones posteriores de OpenAPI incluyen `context.inviteCode`; esto no vincula una invitación ni concede recompensas.

Recarga las Skills según el entorno; en Codex, inicia una nueva tarea y usa `$aholo-lux3d`. En otros entornos, usa su entrada nativa de Skills. La identidad del entorno se detecta automáticamente: no selecciones un `source` al instalar. La instalación no requiere clave API. Para OpenAPI, configura `LUX3D_CN_API_KEY` (China) o `LUX3D_GLOBAL_API_KEY` (internacional) siguiendo las instrucciones de la Skill. Para MCP, usa la conexión de la región elegida y la configuración segura de credenciales del entorno.

La misma entrada permite elegir OpenAPI / MCP y China / internacional. El agente conserva las opciones confirmadas, pregunta por la región si falta y resuelve el transporte mediante la guía de conexión antes de account, quote o create. Las instrucciones MCP están en `references/mcp/`; instalar la Skill no registra ni autentica un servidor MCP. Ejecutar MCP no requiere inicializar el runtime Python de OpenAPI. Cambiar de modo, región o cuenta crea un nuevo contexto con nuevas comprobaciones de cuenta y precio. Reanuda tareas por su ruta original y comprueba un resultado create incierto antes de crear de nuevo; no cambies de ruta para repetirlo automáticamente. Ambos modos conservan planificación, autorización, REPORT y entrega.

Este repositorio distribuye Common suite `1.2.0` con una sola entrada. Instala el directorio fuente completo siguiendo `AGENTS.md`; en Codex, usa `$aholo-lux3d`. Consulta la estructura y los comandos de mantenimiento en inglés. La carga en cada entorno, la autenticación MCP y la generación de pago requieren verificaciones propias.

## Português

[Site internacional](https://lux3d.aholo.ai) · [Site da China](https://lux3d.aholo3d.cn). Para gerar, obtenha a [chave API internacional](https://labs.aholo.ai/api-keys?from=lux3d) ou a [chave API da China](https://labs.aholo3d.cn/api-keys?from=lux3d) da região escolhida. As chaves não são intercambiáveis entre regiões.

### Instalar a Skill local comum

O Aholo Lux3D gera ativos 3D a partir de imagens ou texto, processa modelos e oferece pré-visualização offline. Codex, WorkBuddy e outros ambientes compatíveis usam a mesma Skill `aholo-lux3d`.

Envie esta instrução ao agente do ambiente atual:

```text
Read https://raw.githubusercontent.com/manycore-research/Aholo-Lux3D/master/AGENTS.md and install Aholo Lux3D as a local Skill in the current host.
```

O ambiente precisa oferecer Skills locais; o instalador requer Python 3.10 ou superior e acesso a arquivos. Para instalar manualmente, baixe o repositório, identifique o diretório pai de Skills aceito pelo ambiente e execute na raiz:

```text
python -B scripts/sync_release.py --check
python -B scripts/install_skill.py --skills-dir "<host-local-skills-directory>"
```

O diretório completo `aholo-lux3d/` será instalado. Uma instalação idêntica não é alterada; uma instalação diferente nunca é sobrescrita. Para substituir uma instalação existente, use o mecanismo suportado pelo ambiente. Mantenha apenas uma instalação do Aholo Lux3D por ambiente.

Se tiver um código de convite, acrescente `Invite Code: <código real>` à solicitação de instalação. O agente o passa com `--invite-code` e o salva em `.aholo-lux3d-installation.json`, no diretório pai da Skill. Omitir o código preserva a configuração existente. As coletas posteriores do OpenAPI incluem `context.inviteCode`; isso não vincula um convite nem concede recompensas.

Recarregue as Skills conforme o ambiente; no Codex, inicie uma nova tarefa e use `$aholo-lux3d`. Em outros ambientes, use a entrada nativa de Skills. O ambiente real é detectado automaticamente: não escolha um `source` na instalação. Nenhuma chave API é necessária para instalar. Para OpenAPI, configure `LUX3D_CN_API_KEY` (China) ou `LUX3D_GLOBAL_API_KEY` (internacional), conforme as instruções da Skill. Para MCP, use a conexão da região escolhida e a configuração segura de credenciais do ambiente.

A mesma entrada permite escolher OpenAPI / MCP e China / internacional. O agente mantém escolhas confirmadas, pergunta pela região se faltar e resolve o transporte pelo guia de conexão antes de account, quote ou create. As instruções MCP ficam em `references/mcp/`; instalar a Skill não registra nem autentica um servidor MCP. Executar MCP não exige inicializar o runtime Python de OpenAPI. Mudar de modo, região ou conta inicia um novo contexto com novas verificações de conta e preço. Retome tarefas pela rota original e confira um resultado create incerto antes de criar novamente; não troque de rota para repeti-lo automaticamente. Ambos os modos mantêm planejamento, autorização, REPORT e entrega.

Este repositório distribui Common suite `1.2.0` com uma única entrada. Instale o diretório-fonte completo seguindo `AGENTS.md`; no Codex, use `$aholo-lux3d`. Consulte a estrutura e os comandos de manutenção na seção em inglês. O carregamento em cada ambiente, a autenticação MCP e a geração paga exigem verificações próprias.

## License / 许可证

[MIT License](LICENSE) — Copyright (c) 2026 Manycore Research.

The installed Common suite includes its own [LICENSE.txt](plugins/common/aholo-lux3d/LICENSE.txt).
Bundled third-party components retain their original licenses and attribution;
see [third-party notices](plugins/common/aholo-lux3d/core/viewer/THIRD_PARTY_NOTICES.txt).

Exception: [`fbx_readback.py`](plugins/common/aholo-lux3d/core/runtime/fbx_readback.py) uses Blender's
Python API and is licensed under [GPL-2.0-or-later](plugins/common/aholo-lux3d/LICENSES/GPL-2.0-or-later.txt).
It runs only in a separate Blender process and communicates with the rest of the suite through a JSON file;
all other files remain under the MIT License. Blender itself is not bundled.

本项目采用 MIT 许可证，实际安装的 Common 套件包含同一份许可文本。
第三方组件继续遵循各自的许可证与署名要求，详见上述第三方声明。

例外：`fbx_readback.py` 调用了 Blender Python API，按 [GPL-2.0-or-later](plugins/common/aholo-lux3d/LICENSES/GPL-2.0-or-later.txt) 授权；
它只在独立的 Blender 进程中运行，与套件其余部分仅通过 JSON 文件交换数据，其余文件仍采用 MIT 许可证。本项目不捆绑 Blender。

## Release and contribution guidance / 发布与贡献说明

See [security reporting](SECURITY.md), [contribution checks](CONTRIBUTING.md), and the [changelog](CHANGELOG.md).

The MIT license covers this repository's own code and documentation. It does not grant hosted-service access, third-party commercial software licenses, or rights to arbitrary user inputs and generated assets. Logos and other visual assets require applicable redistribution rights. References to Maya or other DCC tools describe format compatibility and do not include those tools or their licenses.

Python runtime dependencies are declared in `plugins/common/aholo-lux3d/core/runtime/requirements.txt`; this version range is not a lockfile or a complete SBOM. Record the resolved dependency versions and their licenses for each release environment. Preserve the bundled viewer's third-party notices.

发布前需分别审核完整 Git 历史、原始参考 ZIP、素材授权及实际解析的依赖版本。仅清理当前源码不能消除历史或压缩包中的信息；MIT 许可不授予在线服务访问权、第三方商业软件许可或任意输入与生成素材的使用权。
