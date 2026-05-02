.PHONY: run build test lint format typecheck check clean setup help

# デフォルトのターゲット
.DEFAULT_GOAL := help

# よく使うコマンド群
run: ## 開発用にアプリを起動
	uv run password-manager

build: clean ## デスクトップアプリ(.app)としてPyInstallerでビルド
	uv run pyinstaller --windowed --name "Password Manager" --icon=resources/AppIcon.icns src/password_manager/app.py
	@echo "✅ ビルドが完了しました。 'dist/Password Manager.app' を開いてください。"

test: ## ユニットテストの実行
	uv run pytest -v

lint: ## Ruffでコードをチェック
	uv run ruff check src/ tests/

format: ## Ruffでコードを自動フォーマット
	uv run ruff format src/ tests/

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
