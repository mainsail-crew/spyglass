#!/usr/bin/env bash
set -euo pipefail

# Usage: ./build_deb.sh <version>
BINNAME="spyglass"
PKGNAME="mainsail-${BINNAME}"

DEPENDS=(python3-libcamera python3-kms++ python3-picamera2 python3-av)

TMP_VENV="/opt/${BINNAME}/venv"
STAGING_DIR="$(mktemp -d /tmp/${BINNAME}-pkg.XXXXXX)"
VENV_DIR="${STAGING_DIR}/opt/${BINNAME}/venv"
BIN_DIR="${STAGING_DIR}/usr/bin"

echo "Creating virtualenv in ${TMP_VENV}"
python3 -m venv --system-site-packages "${TMP_VENV}"

"${TMP_VENV}/bin/pip" install --upgrade pip setuptools wheel
"${TMP_VENV}/bin/pip" config list

WHEEL=$(ls -t *.whl | head -n 1)
VERSION="$(echo "$WHEEL" | awk -F'-' '{print $2}').${1}"
echo "Installing whl into venv"
"${TMP_VENV}/bin/pip" install --no-cache-dir --extra-index-url https://www.piwheels.org/simple "${WHEEL}"

echo "Cleaning up virtualenv to reduce size"
"${TMP_VENV}/bin/pip" cache purge
find "${TMP_VENV}" -name '__pycache__' -type d -print0 | xargs -0 -r rm -rf
find "${TMP_VENV}" -name '*.pyc' -print0 | xargs -0 -r rm -f
rm -rf "${TMP_VENV}/.cache" "${TMP_VENV}/pip-selfcheck.json" "${TMP_VENV}/share"

echo "Removing pip/wheel from staged venv to reduce size"
PYVER="$(${TMP_VENV}/bin/python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
STAGED_SITEPKG="${TMP_VENV}/lib/python${PYVER}/site-packages"
rm -f "${TMP_VENV}/bin/pip" "${TMP_VENV}/bin/pip3" "${TMP_VENV}/bin/pip${PYVER}"
rm -rf "${STAGED_SITEPKG}/pip" "${STAGED_SITEPKG}"/pip-*
rm -rf "${STAGED_SITEPKG}/wheel" "${STAGED_SITEPKG}"/wheel-*
rm -rf "${STAGED_SITEPKG}/setuptools" "${STAGED_SITEPKG}"/setuptools-*

echo "Preparing staging layout at ${STAGING_DIR}"
mkdir -p "${VENV_DIR}" "${BIN_DIR}"

echo "Copying virtualenv to staging"
cp -a "${TMP_VENV}/." "${VENV_DIR}/"

# Fix permissions in the staged venv so non-root users can run it:
# - directories: 0755 (owner rwx, group/other rx)
# - files: 0644 (owner rw, group/other r)
# - venv/bin/* executables: 0755
echo "Adjusting permissions in staged venv so non-root users can execute it"
# give directories execute bit so they are traversable
find "${VENV_DIR}" -type d -exec chmod 0755 {} +
# make regular files readable
find "${VENV_DIR}" -type f -exec chmod 0644 {} +
# make sure scripts and binaries in bin are executable
if [ -d "${VENV_DIR}/bin" ]; then
  find "${VENV_DIR}/bin" -type f -exec chmod 0755 {} +
fi
# ensure any existing shebang scripts under bin are executable (some tools create them)
if [ -d "${VENV_DIR}/bin" ]; then
  chmod -R a+rx "${VENV_DIR}/bin"
fi

echo "Writing wrapper to ${BIN_DIR}/${BINNAME}"
cat > "${BIN_DIR}/${BINNAME}" <<'EOF'
#!/usr/bin/env bash

APP_BIN="/opt/spyglass/venv/bin/spyglass"

exec "${APP_BIN}" "$@"
EOF
chmod 0755 "${BIN_DIR}/${BINNAME}"

FPM_DEPENDS=()
for dep in "${DEPENDS[@]}"; do
  FPM_DEPENDS+=(--depends "${dep}")
done

echo "Building .deb with fpm (declaring system package dependencies: ${DEPENDS[*]:-none})"
# Ensure fpm is installed: sudo gem install --no-document fpm
fpm -s dir -t deb \
  -n "${PKGNAME}" -v "${VERSION}" \
  --description "Spyglass packaged with a bundled virtualenv and pip-installed app" \
  --maintainer "Patrick Gehrsitz <github@mryel.de>" \
  --url "https://github.com/mainsail-crew/spyglass" \
  --license "GPLv3" \
  "${FPM_DEPENDS[@]}" \
  -C "${STAGING_DIR}" .

echo "Cleaning up"
rm -rf "${TMP_VENV}" "${STAGING_DIR}"
echo "Done. .deb is in the current directory."
