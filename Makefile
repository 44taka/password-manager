.PHONY: run build test lint lint-fix format fix typecheck check clean setup help bump-patch

# pyproject.tomlからバージョンを自動取得
VERSION := $(shell awk -F'"' '/^version =/ {print $$2}' pyproject.toml)

# デフォルトのターゲット
.DEFAULT_GOAL := help

# よく使うコマンド群
run: ## 開発用にアプリを起動
	uv run password-manager

run-flet: ## 開発用にFletアプリを起動
	uv run flet run src/password_manager

run-mock: ## デザインモック用のFletアプリを起動
	uv run flet run src/password_manager/presentation/design_mock.py

build: clean ## デスクトップアプリ(.app)をFletでビルド
	uv run flet build macos --yes --no-rich-output
	@APP=$$(find build/macos -name "*.app" -maxdepth 2 | head -1); \
	  echo "署名対象: $$APP"; \
	  codesign --force --deep --sign "PasswordManagerSign" "$$APP"; \
	  echo "✅ ビルドと署名が完了しました。 $$APP を開いてください。(Version: $(VERSION))"

build-flet: build ## build のエイリアス


test: ## ユニットテストの実行
	uv run pytest -v

coverage: ## テストカバレッジの測定
	uv run pytest --cov=src --cov-report=term-missing --cov-report=html --cov-branch

lint: ## Ruffでコードをチェック
	uv run ruff check src/ tests/

lint-fix: ## Ruffでコードを自動修正 (Unsafeな修正を含む)
	uv run ruff check --fix --unsafe-fixes src/ tests/

format: ## Ruffでコードを自動フォーマット
	uv run ruff format src/ tests/

fix: lint-fix format ## lint-fix + format をまとめて実行

typecheck: ## Pyrightで型チェック
	uv run pyright

check: lint typecheck ## lint + 型チェックをまとめて実行

clean: ## ビルド用の一時ファイル（キャッシュやdist/buildディレクトリ）を削除
	rm -rf build/ dist/ *.spec
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +

setup: ## 依存関係のインストール (初回用)
	uv sync

help: ## このヘルプを表示
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

bump-patch: ## パッチバージョンを1上げる (例: 0.1.0 -> 0.1.1)
	python -c "import re; f='pyproject.toml'; c=open(f).read(); c=re.sub(r'(version\s*=\s*\")(\d+)\.(\d+)\.(\d+)(\")', lambda m: f'{m.group(1)}{m.group(2)}.{m.group(3)}.{int(m.group(4))+1}{m.group(5)}', c); open(f,'w').write(c)"
	@echo "✅ パッチバージョンを更新しました。新しいバージョンを確認してください。"

sync-gemini: ## .agents/rules の内容を .gemini/styleguide.md に同期
	python3 .agents/scripts/sync_gemini_rules.py
