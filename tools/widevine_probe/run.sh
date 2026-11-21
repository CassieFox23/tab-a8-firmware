#!/usr/bin/env bash
# Usage: run.sh <adb-serial>
set -euo pipefail
serial="${1:?usage: run.sh <adb-serial>}"
here="$(cd "$(dirname "$0")" && pwd)"
sdk="${ANDROID_SDK:-$HOME/Android/sdk}"
jar="$sdk/platforms/android-36/android.jar"
d8="$sdk/build-tools/36.0.0/d8"
build="$(mktemp -d)"
trap 'rm -rf "$build"' EXIT
javac -Xlint:-options -source 11 -target 11 -cp "$jar" -d "$build" "$here/WidevineProbe.java"
"$d8" --min-api 28 --lib "$jar" --output "$build" "$build/WidevineProbe.class"
adb -s "$serial" push "$build/classes.dex" /data/local/tmp/wvprobe.dex >/dev/null
rc=0
adb -s "$serial" shell 'CLASSPATH=/data/local/tmp/wvprobe.dex app_process / WidevineProbe; echo "probe_exit=$?"' || rc=$?
adb -s "$serial" shell rm -f /data/local/tmp/wvprobe.dex
exit "$rc"
