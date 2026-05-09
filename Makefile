.PHONY: run build test lint format typecheck check clean setup help bump-patch

# pyproject.tomlからバージョンを自動取得
VERSION := $(shell awk -F'"' '/^version =/ {print $$2}' pyproject.toml)

# デフォルトのターゲット
.DEFAULT_GOAL := help

# よく使うコマンド群
run: ## 開発用にアプリを起動
	uv run password-manager

build: clean ## デスクトップアプリ(.app)としてPyInstallerでビルド
	uv run pyinstaller --windowed --name "Password Manager" --icon=resources/AppIcon.icns --collect-submodules keyring src/password_manager/app.py
	plutil -replace CFBundleShortVersionString -string "$(VERSION)" "dist/Password Manager.app/Contents/Info.plist"
	plutil -replace CFBundleVersion -string "$(VERSION)" "dist/Password Manager.app/Contents/Info.plist"
	codesign --force --deep --sign - "dist/Password Manager.app"
	@echo "✅ ビルドと署名が完了しました。 'dist/Password Manager.app' を開いてください。(Version: $(VERSION))"

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

bump-patch: ## パッチバージョンを1上げる (例: 0.1.0 -> 0.1.1)
	python -c "import re; f='pyproject.toml'; c=open(f).read(); c=re.sub(r'(version\s*=\s*\")(\d+)\.(\d+)\.(\d+)(\")', lambda m: f'{m.group(1)}{m.group(2)}.{m.group(3)}.{int(m.group(4))+1}{m.group(5)}', c); open(f,'w').write(c)"
	@echo "✅ パッチバージョンを更新しました。新しいバージョンを確認してください。"
