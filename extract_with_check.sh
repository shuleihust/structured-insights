#!/bin/bash
# 完整的提取工作流：提取 + 质量检查
# 用法: ./extract_with_check.sh input/your_file.txt

set -e  # 遇到错误立即退出

echo "🚀 智能体提取工作流"
echo "===================="
echo ""

# 检查参数
if [ -z "$1" ]; then
    echo "用法: ./extract_with_check.sh <input_file>"
    echo ""
    echo "示例:"
    echo "  ./extract_with_check.sh input/example_input.txt"
    echo "  ./extract_with_check.sh input/my_article.txt"
    echo ""
    exit 1
fi

INPUT_FILE="$1"

# 检查文件是否存在
if [ ! -f "$INPUT_FILE" ]; then
    echo "❌ 错误: 输入文件不存在: $INPUT_FILE"
    exit 1
fi

echo "📄 输入文件: $INPUT_FILE"
echo ""

# 步骤1：执行提取
echo "🔄 步骤 1/2: 提取智能体..."
echo "------------------------------------------------------------"
python extractor.py -i "$INPUT_FILE"

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 提取失败！请检查错误信息"
    exit 1
fi

echo ""
echo "✅ 提取完成！"
echo ""

# 步骤2：找到最新生成的文件
LATEST_FILE=$(ls -t output/extracted_*.lisp 2>/dev/null | head -1)

if [ -z "$LATEST_FILE" ]; then
    echo "❌ 错误: 找不到生成的文件"
    exit 1
fi

echo "📊 步骤 2/2: 质量评估..."
echo "------------------------------------------------------------"
python quality_checker.py "$LATEST_FILE"

# 提取分数（使用 JSON 输出）
SCORE=$(python quality_checker.py "$LATEST_FILE" --json 2>/dev/null | grep -o '"score": [0-9]*' | grep -o '[0-9]*' | head -1)

echo ""
echo "============================================================"
echo "📋 工作流完成总结"
echo "============================================================"
echo ""
echo "📄 生成文件: $LATEST_FILE"
echo "🎯 质量评分: $SCORE/100"
echo ""

# 根据分数给出建议
if [ "$SCORE" -ge 90 ]; then
    echo "✨ 质量优秀！可以直接使用"
    echo ""
    echo "💡 下一步建议:"
    echo "   1. 查看生成的文件: cat $LATEST_FILE"
    echo "   2. 复制到剪贴板发送给 AI"
    echo "   3. 或保存到您的知识库"
elif [ "$SCORE" -ge 80 ]; then
    echo "👍 质量良好，但建议优化到90分以上"
    echo ""
    echo "💡 改进建议:"
    echo "   1. 查看评估报告中的具体问题"
    echo "   2. 优化输入文案（补充细节、添加示例）"
    echo "   3. 重新提取: python extractor.py -i $INPUT_FILE"
    echo "   4. 目标：达到90分优秀标准"
elif [ "$SCORE" -ge 70 ]; then
    echo "⚠️  质量及格，需要改进"
    echo ""
    echo "💡 下一步建议:"
    echo "   1. 优化输入文案（补充细节、添加示例）"
    echo "   2. 重新提取: python extractor.py -i $INPUT_FILE"
    echo "   3. 或手动编辑改进: $LATEST_FILE"
else
    echo "❌ 质量较低，建议重新提取"
    echo ""
    echo "💡 改进建议:"
    echo "   1. 检查输入文案是否完整"
    echo "   2. 增加内容长度和具体细节"
    echo "   3. 添加具体案例和示例"
    echo "   4. 使用 Claude 3.5 获得更好效果"
    echo "   5. 重新提取后再检查质量"
fi

echo ""
echo "============================================================"
echo ""

