# 文案结构化提炼工具

从文案中自动提取思维模型、方法论和语言风格，生成 Lisp 格式的智能体函数代码。

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install openai anthropic
```

### 2. 设置 API Key

```bash
export DEEPSEEK_API_KEY="your-key"     # 默认（性价比高）
export ANTHROPIC_API_KEY="your-key"   # 或 Claude（质量最好）
export OPENAI_API_KEY="your-key"      # 或 GPT-4
```

### 3. 提取智能体

```bash
# 基本用法
python extractor.py -i input/your_file.txt

# 指定提供商
python extractor.py -i input/your_file.txt --provider anthropic
```

### 4. 检查质量

```bash
python quality_checker.py output/extracted_*.lisp
```

**质量标准：**
- A (90-100分): ✨ 优秀，可直接使用
- B (80-89分): 👍 良好，建议优化
- C (70-79分): ⚠️ 及格，需要改进

## 📁 项目结构

```
structured-insights/
├── extractor.py              # 主程序：自动提取工具
├── quality_checker.py        # 质量评估工具
├── extraction-prompt.md      # 提示词模板
├── config.json              # 配置文件
│
├── input/                   # 放入您的文案文件
│   └── example_input.txt    # 示例
│
├── output/                  # 生成的智能体代码
│   └── extracted_*.lisp
│
└── insight-generator.lisp   # 完整示例
```

## 🎯 使用提取结果

生成的 `.lisp` 文件主要用途：

### 1. 作为 AI 提示词（最主要）

```bash
# 复制文件内容
cat output/extracted_xxx.lisp | pbcopy

# 发送给 ChatGPT/Claude：
"请阅读以下智能体定义，然后按这个思维方式分析：[你的问题]
[粘贴 .lisp 内容]"
```

### 2. 建立知识库

```bash
# 按主题分类
mkdir -p knowledge/{thinking,workflow,communication}
mv output/first_principles.lisp knowledge/thinking/
```

### 3. 团队共享

```bash
# 版本管理
git add output/team_workflow.lisp
git commit -m "Add team workflow agent"
```

## 📝 输入文案建议

为获得90分以上的高质量结果：

✅ **长度**：500-5000字  
✅ **结构**：包含方法论、步骤、案例  
✅ **具体**：有明确的思维模型和语言风格  
✅ **完整**：核心理念、执行流程、质量标准  

## 🔧 高级功能

### 手动使用（无需 Python）

```bash
# 1. 准备提示词
./prepare_manual.sh input/your_file.txt

# 2. 复制到剪贴板，粘贴给 ChatGPT/Claude

# 3. 保存AI的回复为 .lisp 文件
```

### 一键提取+检查

```bash
./extract_with_check.sh input/your_file.txt
```

### 批量质量检查

```bash
python quality_checker.py output/*.lisp
```

## ⚙️ 配置

编辑 `config.json`：

```json
{
  "llm": {
    "provider": "deepseek",           // 默认提供商
    "model": "deepseek-chat",         // 模型
    "temperature": 0.7,               // 创造性 (0-1)
    "max_tokens": 4000                // 最大输出长度
  }
}
```

## 🎨 示例

### 输入示例

`input/example_input.txt`:
```
第一性原理思维框架

【核心理念】
从根本出发，不依赖类比和经验...

【思维模型】
1. 拆解假设
2. 归纳本质
3. 重新构建
...
```

### 输出示例

`output/extracted_xxx.lisp`:
```lisp
(defun 第一性原理思维 ()
  "从基本真理出发的思维框架"
  
  (目标 . 不依赖类比和经验，从最基本的真理层层推导)
  
  (思维模型
   (拆解假设
    (识别假设 . 区分理所当然的假设和验证的事实))
   (归纳本质
    (寻找真理 . 找出不可再分的核心真理))
   (重新构建
    (摆脱框架 . 不受旧有思维限制)))
  ...)
```

## 💡 工作流建议

```
1. 准备文案 → input/your_topic.txt
2. 提取智能体 → python extractor.py -i input/your_topic.txt
3. 检查质量 → python quality_checker.py output/extracted_*.lisp
4. 如果 < 90分 → 优化输入文案，重新提取
5. 达到90分 → 复制使用或保存到知识库
```

## 📊 质量评估维度

| 维度 | 权重 | 检查内容 |
|-----|------|---------|
| 结构完整性 | 25% | 必需部分是否齐全 |
| Lisp 语法 | 25% | 括号配对、格式正确 |
| 内容质量 | 30% | 内容充实、有示例 |
| 完整度 | 20% | 各部分是否详细 |

## 🆘 常见问题

**Q: 如何提高质量到90分？**  
A: 
1. 输入文案增加具体案例和示例
2. 详细描述思维模型和执行步骤
3. 使用 Claude 3.5（`--provider anthropic`）
4. 确保文案结构完整（理念+模型+流程+标准）

**Q: 生成的代码可以运行吗？**  
A: 不能。这是**声明式代码**，用于描述思维模式，主要作为 AI 提示词使用。

**Q: 支持哪些 LLM？**  
A: OpenAI、Anthropic Claude、DeepSeek。推荐 Claude 3.5（质量最高）或 DeepSeek（性价比最高）。

**Q: API 费用大概多少？**  
A: 
- DeepSeek: ¥0.01-0.05/次
- Claude 3.5: ¥0.2-0.6/次  
- GPT-4: $0.05-0.20/次

## 🔗 核心文件

- **extractor.py** - 主程序（400行）
- **quality_checker.py** - 质量检查器（350行）
- **extraction-prompt.md** - 提取提示词模板（270行）
- **config.json** - 配置文件
- **insight-generator.lisp** - 完整示例

## 📦 工具脚本

- `check_env.py` - 环境检测
- `prepare_manual.sh` - 手动提取辅助
- `extract_with_check.sh` - 一键提取+检查

## 🎓 最佳实践

1. **输入文案要充实** - 至少500字，包含具体案例
2. **目标90分以上** - 低于90分建议优化后重提取
3. **使用 Claude** - 质量明显优于其他模型
4. **版本管理** - 使用 Git 管理智能体演化
5. **定期审查** - 每月检查智能体库质量

## 📄 许可

仅供学习和研究使用。

---

**开始构建您的智能体知识库！** 🚀
