#!/usr/bin/env python3
"""
提取结果质量评估工具
自动评估生成的智能体代码质量
"""

import re
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class QualityReport:
    """质量报告"""
    score: int  # 总分 (0-100)
    grade: str  # 等级 (A/B/C/D/F)
    metrics: Dict[str, any]  # 各项指标
    issues: List[str]  # 问题列表
    suggestions: List[str]  # 改进建议


class QualityChecker:
    """质量检查器"""
    
    def __init__(self):
        self.required_sections = [
            'defun',
            '目标',
            '思维模型',
        ]
        
        self.recommended_sections = [
            '人格特质',
            '核心信念',
            '语言武器库',
            '执行流程',
            '质量检验标准',
            '禁忌清单',
        ]
    
    def check_file(self, file_path: str) -> QualityReport:
        """检查文件质量"""
        try:
            content = self._read_file(file_path)
            
            # 执行各项检查
            structure_score, structure_issues = self._check_structure(content)
            syntax_score, syntax_issues = self._check_syntax(content)
            content_score, content_issues = self._check_content_quality(content)
            completeness_score, completeness_issues = self._check_completeness(content)
            
            # 计算总分
            total_score = int(
                structure_score * 0.25 +
                syntax_score * 0.25 +
                content_score * 0.30 +
                completeness_score * 0.20
            )
            
            # 确定等级
            grade = self._calculate_grade(total_score)
            
            # 收集所有问题
            all_issues = (
                structure_issues + 
                syntax_issues + 
                content_issues + 
                completeness_issues
            )
            
            # 生成改进建议
            suggestions = self._generate_suggestions(
                total_score, 
                structure_score,
                syntax_score,
                content_score,
                completeness_score
            )
            
            # 收集指标
            metrics = {
                '结构完整性': f"{structure_score}/100",
                'Lisp语法': f"{syntax_score}/100",
                '内容质量': f"{content_score}/100",
                '完整度': f"{completeness_score}/100",
                '文件大小': f"{len(content)} 字符",
                '总行数': len(content.split('\n')),
            }
            
            return QualityReport(
                score=total_score,
                grade=grade,
                metrics=metrics,
                issues=all_issues,
                suggestions=suggestions
            )
            
        except Exception as e:
            return QualityReport(
                score=0,
                grade='F',
                metrics={},
                issues=[f"文件读取失败: {str(e)}"],
                suggestions=["检查文件路径是否正确", "确保文件格式正确"]
            )
    
    def _read_file(self, file_path: str) -> str:
        """读取文件"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _check_structure(self, content: str) -> Tuple[int, List[str]]:
        """检查结构完整性"""
        score = 100
        issues = []
        
        # 检查必需部分
        for section in self.required_sections:
            if section not in content:
                score -= 30
                issues.append(f"❌ 缺少必需部分: {section}")
        
        # 检查推荐部分
        missing_recommended = 0
        for section in self.recommended_sections:
            if section not in content:
                missing_recommended += 1
        
        # 每缺少一个推荐部分扣5分
        score -= missing_recommended * 5
        
        if missing_recommended > 0:
            issues.append(f"⚠️  缺少 {missing_recommended} 个推荐部分")
        
        return max(0, score), issues
    
    def _check_syntax(self, content: str) -> Tuple[int, List[str]]:
        """检查 Lisp 语法"""
        score = 100
        issues = []
        
        # 检查括号配对
        open_count = content.count('(')
        close_count = content.count(')')
        
        if open_count != close_count:
            diff = abs(open_count - close_count)
            score -= min(50, diff * 5)
            issues.append(f"❌ 括号不配对: 左括号 {open_count} 个, 右括号 {close_count} 个")
        
        # 检查是否有基本的 defun 结构
        defun_pattern = r'\(defun\s+\S+\s+\(\)'
        if not re.search(defun_pattern, content):
            score -= 20
            issues.append("⚠️  defun 函数定义格式可能不正确")
        
        # 检查是否有中文注释
        if not re.search(r';.*[\u4e00-\u9fa5]', content):
            score -= 10
            issues.append("⚠️  缺少中文注释")
        
        return max(0, score), issues
    
    def _check_content_quality(self, content: str) -> Tuple[int, List[str]]:
        """检查内容质量"""
        score = 100
        issues = []
        
        # 检查长度
        if len(content) < 500:
            score -= 40
            issues.append("❌ 内容过短，可能提取不完整")
        elif len(content) < 1000:
            score -= 20
            issues.append("⚠️  内容较短，建议丰富细节")
        
        # 检查是否有具体内容（不是空泛的占位符）
        if '...' in content or '待补充' in content or 'TODO' in content:
            score -= 15
            issues.append("⚠️  包含占位符或待完成内容")
        
        # 检查思维模型数量
        thinking_models = re.findall(r'\([^)]+法|\([^)]+思维|\([^)]+模型', content)
        if len(thinking_models) < 2:
            score -= 20
            issues.append("⚠️  思维模型数量偏少（建议3-5个）")
        
        # 检查是否有具体步骤
        steps = re.findall(r'第[一二三四五六七八九十]+步', content)
        if len(steps) < 3:
            score -= 15
            issues.append("⚠️  执行步骤较少（建议3-7步）")
        
        # 检查是否有实例或示例
        if '示例' not in content and '例如' not in content and '案例' not in content:
            score -= 10
            issues.append("💡 建议添加示例或案例")
        
        return max(0, score), issues
    
    def _check_completeness(self, content: str) -> Tuple[int, List[str]]:
        """检查完整度"""
        score = 100
        issues = []
        
        # 检查各部分的内容是否充实
        sections_to_check = {
            '目标': 20,
            '核心信念': 30,
            '思维模型': 50,
        }
        
        for section, expected_min_length in sections_to_check.items():
            if section in content:
                # 提取该部分的内容
                pattern = f'{section}[^)]*\\)'
                matches = re.findall(pattern, content)
                if matches:
                    section_content = matches[0]
                    if len(section_content) < expected_min_length:
                        score -= 15
                        issues.append(f"⚠️  '{section}' 部分内容过于简单")
        
        # 检查是否有使用指南
        if '使用指南' not in content and 'start' not in content:
            score -= 10
            issues.append("💡 建议添加使用指南或启动函数")
        
        return max(0, score), issues
    
    def _calculate_grade(self, score: int) -> str:
        """计算等级"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _generate_suggestions(
        self, 
        total_score: int,
        structure_score: int,
        syntax_score: int,
        content_score: int,
        completeness_score: int
    ) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if total_score >= 90:
            suggestions.append("✨ 质量优秀！可以直接使用")
        elif total_score >= 80:
            suggestions.append("👍 质量良好，建议优化到90分以上")
        else:
            suggestions.append("⚠️  质量需要改进")
        
        if structure_score < 80:
            suggestions.append("📝 补充缺失的结构部分（人格特质、核心信念等）")
        
        if syntax_score < 80:
            suggestions.append("🔧 修复 Lisp 语法问题，确保括号配对")
        
        if content_score < 80:
            suggestions.append("📚 丰富内容细节，添加更多思维模型和步骤")
            suggestions.append("💡 添加具体示例和案例")
        
        if completeness_score < 80:
            suggestions.append("✏️  扩充各部分内容，避免过于简单")
        
        if total_score < 70:
            suggestions.append("🔄 建议优化输入文案后重新提取")
        
        return suggestions
    
    def print_report(self, file_path: str, report: QualityReport):
        """打印报告"""
        print("=" * 60)
        print(f"📊 质量评估报告: {Path(file_path).name}")
        print("=" * 60)
        print()
        
        # 总分和等级
        print(f"🎯 总分: {report.score}/100  等级: {report.grade}")
        print()
        
        # 详细指标
        print("📈 详细指标:")
        print("-" * 60)
        for metric, value in report.metrics.items():
            print(f"  {metric:.<30} {value}")
        print()
        
        # 问题列表
        if report.issues:
            print("⚠️  发现的问题:")
            print("-" * 60)
            for issue in report.issues:
                print(f"  {issue}")
            print()
        else:
            print("✅ 未发现明显问题")
            print()
        
        # 改进建议
        if report.suggestions:
            print("💡 改进建议:")
            print("-" * 60)
            for i, suggestion in enumerate(report.suggestions, 1):
                print(f"  {i}. {suggestion}")
            print()
        
        print("=" * 60)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='提取结果质量评估工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 检查单个文件
  python quality_checker.py output/extracted_xxx.lisp
  
  # 检查并输出 JSON 格式
  python quality_checker.py output/extracted_xxx.lisp --json
  
  # 批量检查 output 目录下的所有文件
  python quality_checker.py output/*.lisp
        """
    )
    
    parser.add_argument(
        'files',
        nargs='+',
        help='要检查的文件路径（支持多个文件）'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='以 JSON 格式输出结果'
    )
    
    parser.add_argument(
        '--min-score',
        type=int,
        default=0,
        help='最低分数阈值，低于此分数的文件会标记（默认: 0）'
    )
    
    args = parser.parse_args()
    
    checker = QualityChecker()
    results = []
    
    for file_path in args.files:
        report = checker.check_file(file_path)
        
        if args.json:
            results.append({
                'file': file_path,
                'score': report.score,
                'grade': report.grade,
                'metrics': report.metrics,
                'issues': report.issues,
                'suggestions': report.suggestions,
            })
        else:
            checker.print_report(file_path, report)
            
            if report.score < args.min_score:
                print(f"⚠️  警告: 分数 {report.score} 低于阈值 {args.min_score}")
                print()
    
    # JSON 输出
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    
    # 如果检查了多个文件，显示汇总
    if len(args.files) > 1 and not args.json:
        print("=" * 60)
        print("📊 汇总统计")
        print("=" * 60)
        
        all_reports = [checker.check_file(f) for f in args.files]
        avg_score = sum(r.score for r in all_reports) / len(all_reports)
        
        print(f"文件总数: {len(all_reports)}")
        print(f"平均分数: {avg_score:.1f}/100")
        print(f"最高分数: {max(r.score for r in all_reports)}/100")
        print(f"最低分数: {min(r.score for r in all_reports)}/100")
        print()
        
        # 等级分布
        grade_dist = {}
        for report in all_reports:
            grade_dist[report.grade] = grade_dist.get(report.grade, 0) + 1
        
        print("等级分布:")
        for grade in ['A', 'B', 'C', 'D', 'F']:
            if grade in grade_dist:
                print(f"  {grade}: {'█' * grade_dist[grade]} ({grade_dist[grade]})")
        print()


if __name__ == '__main__':
    main()

