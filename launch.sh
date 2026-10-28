#!/usr/bin/env bash
set -euo pipefail
planner_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
planner_version="$(tr -d '\r\n' < "$planner_dir/VERSION")"
planner_python="${LIQUID_CALENDAR_PYTHON:-}"
if [[ -z "$planner_python" ]]; then
    if [[ -x "$planner_dir/.venvs/$planner_version/bin/python" && -f "$planner_dir/.venvs/$planner_version/.ready" ]]; then
        planner_python="$planner_dir/.venvs/$planner_version/bin/python"
    elif [[ -x "$planner_dir/.venv/bin/python" ]]; then
        planner_python="$planner_dir/.venv/bin/python"
    else
        planner_python="python3"
    fi
fi
unset QT_PLUGIN_PATH QML_IMPORT_PATH QML2_IMPORT_PATH QT_QPA_PLATFORM_PLUGIN_PATH
export QT_QUICK_CONTROLS_STYLE=Basic
exec "$planner_python" "$planner_dir/app.py" "$@"
