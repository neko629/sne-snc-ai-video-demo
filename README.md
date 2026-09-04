# SNE / SNC — AI Video Demo

从真实语言学习视频项目提取的 **Skills + Python 源码 Demo**，展示 ComfyUI 任务接口、字幕时间处理和三语文本校验。

本仓库采用精简的独立实现与合成测试输入。完整的生成配方、生产编排和频道素材库不随 Demo 分发。

## 快速开始

需要 Python 3.10+，无需安装第三方包、提供密钥或启动 GPU 服务：

```sh
python demo/run_demo.py
```

Demo 会启动临时的本机回环模拟服务，验证任务提交、等待、失败和超时，再运行字幕与文本结构检查。输出为 `demo/output/report.json`、`job_lifecycle.json` 和 `shifted.srt`。模拟服务不会执行模型推理或生成视频。

## Skills 与源码

| Skill | 可读说明 | 可执行源码 |
|---|---|---|
| ComfyUI 任务适配 | [SKILL.md](skills/comfyui-job-demo/SKILL.md) | [client.py](skills/comfyui-job-demo/scripts/client.py) |
| 字幕时间处理 | [SKILL.md](skills/subtitle-timing-demo/SKILL.md) | [timing.py](skills/subtitle-timing-demo/scripts/timing.py) |
| 三语文本结构检查 | [SKILL.md](skills/trilingual-structure-demo/SKILL.md) | [check_structure.py](skills/trilingual-structure-demo/scripts/check_structure.py) |

每个 Skill 均包含触发范围、输入输出、执行要求和随附资源，可独立阅读与调用脚本。它们是生产技能的裁剪适配版，不是内部指令的原样副本。[Skills 说明](docs/skills.md)

## ComfyUI 如何参与生成

实际项目使用 ComfyUI / Wan2.2 生成角色动作片段，Python 负责配置工作流、提交任务、跟踪状态与处理结果。Demo 展示这层通用接口，通过绑定表替换调用方提供的节点输入。

随附的 `workflow.mock.json` 只有模拟节点，**不能用于真实图生视频**。真实运行需要调用方提供自己的 API 工作流和模型环境。[接口说明](docs/comfyui.md)

## 成片效果

| SNE · 英语学习 | SNC · 中文学习 |
|---|---|
| ![SNE](cases/sne/cover.png) | ![SNC](cases/snc/cover.png) |
| [一分钟成片预览](cases/sne/preview.mp4) | [一分钟成片预览](cases/snc/preview.mp4) |

以上是历史成片展示，不是运行本 Demo 新生成的内容。

## 目录

```text
skills/       三个适配版 Skill、源码、接口说明与合成样例
demo/         模拟服务、演示入口与验证结果
cases/        完成态封面与成片片段
docs/         架构、接口、展示范围与验证说明
```

[架构](docs/architecture.md) · [展示范围](docs/scope.md) · [验证](docs/validation.md)

代码围绕真实项目中的接口模式重新整理，保留可运行的通用逻辑；不包含完整生产系统。仓库未附开源许可，代码与素材的进一步使用需另行确认。
