#!/bin/bash
# 手动提取辅助脚本
# 用于快速准备手动提取的完整提示词

echo "📖 手动提取辅助工具"
echo "===================="
echo ""

# 检查输入参数
if [ -z "$1" ]; then
    echo "用法: ./prepare_manual.sh <your_content.txt>"
    echo ""
    echo "示例:"
    echo "  ./prepare_manual.sh input/example_input.txt"
    echo "  ./prepare_manual.sh input/my_article.txt"
    echo ""
    exit 1
fi

INPUT_FILE="$1"
OUTPUT_FILE="manual_prompt_ready.txt"
TEMPLATE_FILE="extraction-prompt.md"

# 检查文件是否存在
if [ ! -f "$INPUT_FILE" ]; then
    echo "❌ 错误: 输入文件不存在: $INPUT_FILE"
    exit 1
fi

if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "❌ 错误: 模板文件不存在: $TEMPLATE_FILE"
    exit 1
fi

echo "📄 输入文件: $INPUT_FILE"
echo "📝 模板文件: $TEMPLATE_FILE"
echo ""

# 读取文件内容
echo "🔄 正在处理..."

# 复制模板
cp "$TEMPLATE_FILE" "$OUTPUT_FILE"

# 读取输入内容
CONTENT=$(cat "$INPUT_FILE")

# 根据操作系统选择 sed 命令
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s|{{INPUT_CONTENT}}|${CONTENT}|" "$OUTPUT_FILE"
else
    # Linux
    sed -i "s|{{INPUT_CONTENT}}|${CONTENT}|" "$OUTPUT_FILE"
fi

echo "✅ 处理完成！"
echo ""
echo "📋 输出文件: $OUTPUT_FILE"
echo ""

# 尝试复制到剪贴板
if command -v pbcopy &> /dev/null; then
    cat "$OUTPUT_FILE" | pbcopy
    echo "✅ 内容已复制到剪贴板！(macOS)"
elif command -v xclip &> /dev/null; then
    cat "$OUTPUT_FILE" | xclip -selection clipboard
    echo "✅ 内容已复制到剪贴板！(Linux)"
elif command -v clip &> /dev/null; then
    cat "$OUTPUT_FILE" | clip
    echo "✅ 内容已复制到剪贴板！(Windows)"
else
    echo "⚠️  无法自动复制到剪贴板"
    echo "   请手动复制文件内容: $OUTPUT_FILE"
fi

echo ""
echo "📌 下一步操作:"
echo "   1. 打开 ChatGPT (https://chat.openai.com)"
echo "      或 Claude (https://claude.ai)"
echo "   2. 粘贴剪贴板内容 (Cmd+V 或 Ctrl+V)"
echo "   3. 发送并等待 AI 生成结果"
echo "   4. 复制结果并保存到 output/ 目录"
echo ""
echo "💡 提示: 推荐使用 Claude 3.5 Sonnet 获得最佳效果"
echo ""

