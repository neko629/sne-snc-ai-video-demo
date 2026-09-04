# ComfyUI 任务接口

真实项目通过 ComfyUI / Wan2.2 生成动作片段。展示版提取以下通用工程模式：

1. 接收调用方的 API 节点图，利用绑定表明确可替换的输入。
2. 校验绑定，深拷贝模板后写入图片、文本或其他参数。
3. 向 `/prompt` 提交请求，保留任务 ID。
4. 轮询 `/history/{id}`，区分成功、失败与超时。
5. 返回输出元数据，后续由调用方检查和管理实际文件。

默认命令只生成计划，不发送请求：

```sh
python skills/comfyui-job-demo/scripts/client.py --workflow skills/comfyui-job-demo/assets/workflow.mock.json --bindings skills/comfyui-job-demo/assets/bindings.demo.json --values skills/comfyui-job-demo/assets/values.demo.json
```

模拟节点仅用于演示参数替换。CLI 会阻止把这些节点提交到真实服务。调用真实服务时需自行提供可执行的工作流、配置模型与输入文件，并显式指定 `--submit`。

示例没有包含生产节点图、参数组合、动作提示词、资产路由或多阶段生成策略。模拟服务也不验证完整 ComfyUI 行为。接口源码的价值在于可读的参数边界、状态处理和可重复的失败验证。
