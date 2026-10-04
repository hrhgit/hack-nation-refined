# Python 后端迁移到 TypeScript：范围和核对结果

迁移已完成。网页服务、原文处理、规则提取、模型调用、地址判断、结果导出和变更追踪都由 TypeScript 实现，编译后直接在 Node.js 上运行。原有网页、输入和输出格式、已完成分包、规则编号以及本地缓存继续沿用。

Python 实现保留作测试参考和离线研究使用；新后端运行时不启动 Python，也不调用旧 Python 服务。

## 先确定参考版本，再迁移

用户要求等并行修改完成后再确定参考版本。收到“已完成”后，固定当时的 Python 代码和数据，在实现 TypeScript 后端之前通过了 403 项测试。

固定版本记录在本地忽略目录 `tests/.migration/`：

- `source-manifest.json` 保存 77 份代码和关键数据文件的 SHA-256（文件内容指纹）。清单自身的指纹为 `9e289cf5899c9102b33970da2664a0dcbb0d7ab8b2523b56b0affe5434c79a93`。
- `baseline-root/` 保存参考副本。迁移后逐字节核对了 804 份原有项目文件及 65 份题目随包文件，共 869 份，内容均未改变；Python、原始提示词、规则数据和已有回答都在这次核对范围内。
- 测试使用临时目录及本地 HTTP 服务，生成结果不会覆盖已有正式输出。

## 最终验证

执行 `npm run verify` 全部通过。实际验证环境为 Node.js 26.10.0、TypeScript 7.0.2、Python 3.14.7。

| 检查 | 结果 | 说明 |
|---|---|---|
| 迁移前 Python 完整测试 | 403 项通过 | TypeScript 实现开始前完成 |
| 最终 Python 完整测试 | 424 项通过 | 含迁移中新增的边界和网络检查 |
| 同一组测试检查 TypeScript | 243 项通过 | 用相同输入逐项核对 Python 与 TypeScript 返回的内容 |
| TypeScript 原生完整流程 | 12 项通过 | 实际运行命令、HTTP 请求、文件生成、续跑和并行处理 |
| TypeScript 严格编译 | 通过 | `tsconfig.json` 启用 `strict` |

424 项 Python 测试包含上述 243 项共用测试，不应把两组数字相加当作独立测试总数。测试无跳过或失败。

共用测试的 `cases.py` 同时给两个版本提供输入；Python 参考实现通过仅供测试的 `oracle.py` 返回结果，TypeScript 使用自己的测试入口。测试入口不会进入产品运行流程。

| 范围 | 已核对的内容 |
|---|---|
| 原文与分包 | 97 份文档、108 个分包；清洗、选段、标题、Unicode 位置、文本及指纹 |
| 回答导入 | JSON 提取、嵌套和残缺回答、收据、字段校验、日期和数字、逐字及近似引文、重复记录、章节合并、冲突、编号保留 |
| 适用条件 | 日期和户数边界、入住证、滚动年限、房东例外、需备案的豁免、替代住宅、缺失及矛盾事实、政府所有住房 |
| 地址与判断 | 全部 500 个实际地址，在 2026-10-01、2027-07-01、2024-02-29 三个日期的全部结论、解释和判断记录；现有 97 条规则 |
| 规则关系与变更 | 取代方向、依赖及循环检查、州和市的复核标记、规则导出、五道实际变更题及日期覆盖 |
| 模型处理流程 | 普通提取、工具调用、卡片和自检、修正回答、完整响应保存、失败后保留进度、完成后跳过、全部选中分包先检查再请求 |
| HTTP 与缓存 | 用实际本地请求检查请求体、身份信息、错误和重定向处理；Census 单地址及批量请求、缓存键、离线重放、无缓存报错 |
| 网页服务 | 六个 API 路由的字段及错误、原有静态文件内容、路径检查、单次查询补充事实不写回文件 |
| 命令与产物 | prepare、bundle、add-doc、ingest、status、api、resolve、build、lookup、changes、review；报告文本及全部提交文件可重复生成 |

对比保留数组顺序、错误内容、解释、来源、被省略的原因及其他稳定字段。仅对实际耗时、随机临时目录或调用文件名、调用时间等每次运行必然变化的内容做统一处理；没有忽略规则结论或稳定业务字段。

原生测试在没有 Python 命令的环境中运行后端命令，验证准备、分包、导入、状态查询及结果生成。模型与 Census 请求使用本地模拟服务，验证了真正的 HTTP 收发；本次没有发送付费模型请求或进行外部部署。

## 当前入口

在 `navigator/` 下运行：

```bash
npm ci
npm run build
npm start
```

网页默认地址为 `http://127.0.0.1:8000`。运行后端需要 Node.js 22 或更新版本；运行时仅使用 Node.js 自带功能。

| 原 Python 入口 | 当前 TypeScript 入口 |
|---|---|
| `python3 run.py prepare` | `npm run nav -- prepare` |
| `python3 run.py bundle` | `npm run nav -- bundle` |
| `python3 run.py ingest` | `npm run nav -- ingest` |
| `python3 run.py status` | `npm run nav -- status` |
| `python3 run.py add-doc ...` | `npm run nav -- add-doc ...` |
| `python3 run.py api ...` | `npm run nav -- api ...` |
| `python3 -m lookup ...` | `npm run lookup -- ...` |
| `python3 -m changes ...` | `npm run changes -- ...` |
| `python3 web/server.py` | `npm start` |

例如：

```bash
npm run nav -- api --dry-run
npm run lookup -- lookup --address-id A0001 --as-of 2026-10-01
npm run lookup -- build --offline
npm run changes --
```

默认数据目录、`.env` 配置、`work/` 和 `outputs/` 沿用原项目。没有新增应用层请求超时、回答截断、自动 HTTP 重试或固定修正次数；原有分包行为保留。

有意调整的内容是启动命令和代码路径。生成的操作说明使用 TypeScript 专用 `prompts/delivery.typescript.md`；原始 Python 说明保留给参考实现。生成记录里的代码指纹现在包含 TypeScript 源码、编译配置和依赖锁文件。新增工作目录选项供独立测试使用，不改变默认目录。

## 重跑检查与文件位置

```bash
# 完整核对，另需 Python 3
npm run verify

# 仅运行原生完整流程，不需要 Python
npm test

# 已编译后，单独对比两个版本
npm run test:parity
```

- 新后端：`src/nav/`、`src/lookup/`、`src/changes/`、`src/web/`。
- 共用测试：`tests/migration/`、`tests/test_migration_contract.py`、`tests/test_migration_http.py`、`tests/test_migration_network.py`。
- 原生测试：`tests/typescript/backend.test.mjs`。
- 迁移前及最终原始运行日志：`tests/.migration/python-final-baseline.log`、`tests/.migration/final-verification.log`，仅保存在本地。

代码、测试、输入配置和本报告可以纳入 Git；参考副本、原始运行日志、编译产物和模型调用记录保持本地忽略。

这些结果证明已测试的旧后端行为得到保留，也覆盖了全部当前文档、分包和地址；它们不等同于每行代码都有测试，也不证明模型提取的法律事实本身全部正确。
