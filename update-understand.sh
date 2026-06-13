#!/usr/bin/env bash
# update-understand.sh — пересобрать дашборд Understand-Anything и выложить на
#   https://docs.billing.smit34.ru/understand/
#
# Запускать из Git Bash (Windows):
#   cd /d/DevTools/Database/2026Carbon/carbon_modern/docs
#   ./update-understand.sh
#
# ─────────────────────────────────────────────────────────────────────────────
# ЧТО ИМЕННО ОБНОВЛЯЕТСЯ
#   1. Фронтенд дашборда (React/Vite) — собирается из исходников плагина
#      Understand-Anything (UA_DASH) с нашими правками (зелёная тема СмИТ,
#      логотипы, русская локаль, мобильные фиксы).
#   2. Граф знаний: knowledge-graph.json + meta.json + config.json — берётся
#      из ПОСЛЕДНЕГО анализа в  carbon_modern/.understand-anything/.
#
# ВАЖНО про граф знаний:
#   Семантику графа (описания узлов, архитектуру, тур) генерирует LLM-пайплайн
#   Understand-Anything — скилл «/understand» в Claude Code. Этот скрипт граф
#   НЕ пересчитывает, он только ПУБЛИКУЕТ то, что уже лежит в .understand-anything/.
#   Когда нужно пересчитать граф по свежему коду биллинга:
#       1) в Claude Code прогнать анализ заново (скилл /understand),
#       2) затем запустить этот скрипт — он соберёт фронт и выложит свежий граф.
#
# РЕЖИМЫ:
#   ./update-understand.sh                полный цикл: сборка фронта + граф + деплой
#   ./update-understand.sh --graph-only   только перезалить граф (быстро, без сборки)
#   ./update-understand.sh --build-only   собрать фронт + деплой, граф не перезаливать
#   ./update-understand.sh --dry-run      всё собрать локально, но НЕ заливать на сервер
#   ./update-understand.sh --help         показать справку
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

# ── Конфигурация (можно переопределить через переменные окружения) ───────────
# Исходники дашборда (pnpm-workspace плагина Understand-Anything с нашими правками).
UA_DASH="${UA_DASH:-/tmp/ua/understand-anything-plugin/packages/dashboard}"
# Корень проекта биллинга — отсюда берём свежий граф знаний.
PROJECT="${PROJECT:-/d/DevTools/Database/2026Carbon/carbon_modern}"
GRAPH_DIR="$PROJECT/.understand-anything"
# Сервер и путь публикации.
SERVER="${SERVER:-root@31.44.7.144}"
SERVER_PATH="${SERVER_PATH:-/var/www/docs.billing.smit34.ru/understand}"
LIVE_URL="https://docs.billing.smit34.ru/understand/"

# Vite-параметры статической сборки (как при первом деплое).
BASE="/understand/"
VITE_ENV=(
  VITE_DEMO_MODE=true
  VITE_GRAPH_URL=/understand/knowledge-graph.json
  VITE_META_URL=/understand/meta.json
  VITE_CONFIG_URL=/understand/config.json
)

# ── Разбор аргументов ────────────────────────────────────────────────────────
MODE="full"   # full | graph | build
DRY_RUN=0
for arg in "$@"; do
  case "$arg" in
    --graph-only) MODE="graph" ;;
    --build-only) MODE="build" ;;
    --dry-run)    DRY_RUN=1 ;;
    --help|-h)
      sed -n '2,40p' "$0"; exit 0 ;;
    *) echo "Неизвестный аргумент: $arg (см. --help)"; exit 2 ;;
  esac
done

say()  { printf '\n\033[1;32m==> %s\033[0m\n' "$*"; }
warn() { printf '\033[1;33m  ! %s\033[0m\n' "$*"; }
die()  { printf '\033[1;31mОШИБКА: %s\033[0m\n' "$*" >&2; exit 1; }

# ── Проверки окружения ───────────────────────────────────────────────────────
say "Проверка окружения"
command -v ssh >/dev/null || die "ssh не найден в PATH"
command -v scp >/dev/null || die "scp не найден в PATH"
command -v tar >/dev/null || die "tar не найден в PATH"
[ -d "$GRAPH_DIR" ] || die "Нет каталога графа: $GRAPH_DIR (проект не проанализирован?)"
for f in knowledge-graph.json meta.json config.json; do
  [ -f "$GRAPH_DIR/$f" ] || die "Нет файла графа: $GRAPH_DIR/$f"
done
if [ "$MODE" != "graph" ]; then
  [ -d "$UA_DASH" ] || die "Нет исходников дашборда: $UA_DASH
  Укажи правильный путь:  UA_DASH=/путь/к/packages/dashboard ./update-understand.sh"
  [ -x "$UA_DASH/node_modules/.bin/vite" ] || die "Не найден vite в $UA_DASH/node_modules/.bin/
  Установи зависимости (pnpm install) в корне плагина."
fi
echo "  UA_DASH     = $UA_DASH"
echo "  GRAPH_DIR   = $GRAPH_DIR"
echo "  SERVER      = $SERVER:$SERVER_PATH"
echo "  MODE        = $MODE   DRY_RUN=$DRY_RUN"

# ── Сборка фронтенда (режимы full / build) ───────────────────────────────────
DIST="$UA_DASH/dist"
if [ "$MODE" = "graph" ]; then
  warn "Режим --graph-only: фронт не пересобираю, использую существующий dist при деплое графа отдельными файлами."
else
  say "Сборка дашборда (vite build, base=$BASE)"
  # MSYS_NO_PATHCONV=1 обязателен: иначе Git Bash превращает /understand/ в путь к Program Files.
  ( cd "$UA_DASH" \
    && MSYS_NO_PATHCONV=1 env "${VITE_ENV[@]}" \
       "$UA_DASH/node_modules/.bin/vite" build --base="$BASE" )
  [ -f "$DIST/index.html" ] || die "Сборка не создала $DIST/index.html"
  # Проверка, что base прошит верно (а не в /Program Files/...).
  grep -q "$BASE" "$DIST/index.html" || die "В dist/index.html нет base=$BASE — сборка с битым путём, не деплою."
  echo "  dist готов: $DIST"
fi

# ── Внедрение свежего графа знаний в dist ────────────────────────────────────
if [ "$MODE" != "build" ]; then
  say "Копирую свежий граф знаний в сборку"
  mkdir -p "$DIST"
  for f in knowledge-graph.json meta.json config.json; do
    cp -f "$GRAPH_DIR/$f" "$DIST/$f"
    echo "  + $f ($(wc -c < "$DIST/$f") байт)"
  done
fi

# Логотипы/фавиконки кладутся в dist автоматически из public/ при сборке.
# В режиме --graph-only их не трогаем (они уже на сервере).

# ── Деплой на сервер ─────────────────────────────────────────────────────────
TARBALL="/tmp/understand-deploy.$$.tar.gz"
if [ "$MODE" = "graph" ]; then
  say "Деплой только графа (3 файла) на $SERVER"
  if [ "$DRY_RUN" = "1" ]; then warn "--dry-run: пропускаю заливку"; else
    scp "$GRAPH_DIR/knowledge-graph.json" "$GRAPH_DIR/meta.json" "$GRAPH_DIR/config.json" \
        "$SERVER:$SERVER_PATH/"
    echo "  граф залит"
  fi
else
  say "Упаковка dist → $TARBALL"
  tar -czf "$TARBALL" -C "$DIST" .
  echo "  размер: $(wc -c < "$TARBALL") байт"
  if [ "$DRY_RUN" = "1" ]; then
    warn "--dry-run: НЕ заливаю. Пакет лежит в $TARBALL"
  else
    say "Заливка и распаковка на $SERVER:$SERVER_PATH"
    scp "$TARBALL" "$SERVER:/tmp/understand-deploy.tar.gz"
    # Чистим только assets/ (старые хэшированные бандлы), затем распаковываем поверх.
    ssh "$SERVER" "set -e; \
      mkdir -p '$SERVER_PATH'; \
      rm -rf '$SERVER_PATH/assets'; \
      tar -xzf /tmp/understand-deploy.tar.gz -C '$SERVER_PATH'; \
      rm -f /tmp/understand-deploy.tar.gz; \
      echo '  распаковано в $SERVER_PATH'"
    rm -f "$TARBALL"
  fi
fi

# ── Проверка, что сайт жив ───────────────────────────────────────────────────
if [ "$DRY_RUN" != "1" ]; then
  say "Проверка live ($LIVE_URL)"
  if command -v curl >/dev/null; then
    code=$(curl -s -o /dev/null -w '%{http_code}' "$LIVE_URL" || echo "ERR")
  else
    code=$(ssh "$SERVER" "curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1/understand/ -H 'Host: docs.billing.smit34.ru'" || echo "ERR")
  fi
  echo "  HTTP $code"
  [ "$code" = "200" ] && say "ГОТОВО ✓  $LIVE_URL обновлён" || warn "Ответ не 200 — проверь вручную: $LIVE_URL"
else
  say "ГОТОВО (dry-run) — на сервер ничего не залито"
fi
