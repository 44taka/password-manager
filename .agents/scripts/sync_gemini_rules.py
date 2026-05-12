#!/usr/bin/env python3
import pathlib


def sync():
    root = pathlib.Path(__file__).parent.parent.parent
    rules_dir = root / ".agents" / "rules"
    gemini_styleguide = root / ".gemini" / "styleguide.md"

    if not rules_dir.exists():
        print(f"Rules directory not found: {rules_dir}")
        return

    # 既存の styleguide.md のヘッダー部分を保持するか、テンプレートから生成する
    header = """# 🎨 Password Manager Coding Style Guide for Gemini

## 🚨 CRITICAL: LANGUAGE REQUIREMENT
- **サマリー（Code Reviewセクション）を含め、ユーザーへの全ての回答は必ず「日本語」で行ってください。**
- 英語での出力は一切禁止します。

あなたは、この Python プロジェクトの熟練したシニアエンジニアとして、プルリクエストのレビューを行ってください。
以下の規約および設計原則を遵守しているか厳格にチェックし、違反がある場合は修正案を提示してください。

## プロジェクト固有の規約 (Source: .agents/rules/)
"""

    content = ""
    for rule_file in sorted(rules_dir.glob("*.md")):
        # Git コミット規約はコードレビューに関係ないのでスキップ
        if "git-commit" in rule_file.name:
            continue

        with open(rule_file, encoding="utf-8") as f:
            lines = f.readlines()

            # フロントマターの削除
            if lines and lines[0].strip() == "---":
                try:
                    end_idx = lines.index("---\n", 1)
                    lines = lines[end_idx+1:]
                except ValueError:
                    pass

            file_content = "".join(lines)

            # 開発サイクルガイドの場合、手順(コマンド等)は不要なので、設計原則に関連する部分だけを抽出
            if "implementation-cycle" in rule_file.name:
                # セクション 0 (基本原則) と セクション 2 (アーキテクチャ実装順序/責務) を抽出
                sections = file_content.split("## ")
                extracted = []
                for sec in sections:
                    if sec.startswith("0. 基本原則") or sec.startswith("2. オニオンアーキテクチャ"):
                        extracted.append("## " + sec)
                file_content = "\n".join(extracted)

            content += f"\n### {rule_file.stem.replace('-', ' ').title()}\n"
            content += file_content
            content += "\n---\n"

    footer = """
## レビュー時のトーン
- **必ず日本語（丁寧語）で指摘を行ってください。**
- 修正が必要な理由を、上記の規約や設計原則に基づいて説明してください。
- 優れたコードに対しては、積極的に褒めてください。
"""

    with open(gemini_styleguide, "w", encoding="utf-8") as f:
        f.write(header)
        f.write(content)
        f.write(footer)

    print(f"Successfully synced rules to {gemini_styleguide}")

if __name__ == "__main__":
    sync()
