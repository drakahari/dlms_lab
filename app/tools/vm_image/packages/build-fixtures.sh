#!/bin/bash
# Reviewed developer recipe: run only in the fresh guest installer, never on host.
set -euo pipefail
export LC_ALL=C SOURCE_DATE_EPOCH=1767225600
root=/opt/learning-lab/package-fixtures
[[ ! -e "$root" && ! -L "$root" ]]
mkdir -p "$root/archives" "$root/source" "$root/notices"
cp /tmp/build-fixtures.sh "$root/source/build-fixtures.sh"
printf '%s\n' 'Original Learning Lab fixture source; MIT. See notices/LICENSE.' > "$root/source/README"
cp /tmp/learning-lab-LICENSE "$root/notices/LICENSE"
work=$(mktemp -d /tmp/ll-fixture-build.XXXXXXXX)
trap 'rm -rf -- "$work"' EXIT
for run in a b; do
 mkdir "$work/$run"
 for item in data:1.0-1 report:1.0-1 report:1.1-1; do
  name=${item%%:*}; version=${item#*:}; package=ll-discovery-$name
  dir="$work/$run/${package}_${version}_all"
  mkdir -p "$dir/DEBIAN" "$dir/usr/share/doc/$package"
  printf 'Package: %s\nVersion: %s\nArchitecture: all\nMaintainer: Learning Lab project\nSection: misc\nPriority: optional\nDescription: Small trusted offline teaching fixture\n' "$package" "$version" > "$dir/DEBIAN/control"
  cp "$root/notices/LICENSE" "$dir/usr/share/doc/$package/copyright"
  if [[ $name = data ]]; then
   mkdir -p "$dir/usr/share/ll-discovery"
   printf 'Known offline fixture data.\n' > "$dir/usr/share/ll-discovery/message.txt"
  else
   printf 'Depends: ll-discovery-data (= 1.0-1), dash, coreutils\n' >> "$dir/DEBIAN/control"
   mkdir -p "$dir/usr/bin" "$dir/etc"
   cat > "$dir/usr/bin/ll-discovery-report" <<EOF
#!/bin/sh
set -eu
printf '%s\\n' 'll-discovery-report $version'
cat /usr/share/ll-discovery/message.txt
cat /etc/ll-discovery-report.conf
EOF
   chmod 0755 "$dir/usr/bin/ll-discovery-report"
   printf 'format=short\n' > "$dir/etc/ll-discovery-report.conf"
   printf '/etc/ll-discovery-report.conf\n' > "$dir/DEBIAN/conffiles"
  fi
  # Standard package content metadata; ordinary files only and fixed root ownership.
  (cd "$dir"; find . -type f ! -path './DEBIAN/*' | LC_ALL=C sort | sed 's|^./||' | xargs -r md5sum) > "$dir/DEBIAN/md5sums"
  find "$dir" -type f ! -path '*/usr/bin/ll-discovery-report' -exec chmod 0644 '{}' +
  find "$dir" -type d -exec chmod 0755 '{}' +
  [[ -z $(find "$dir" -type l -print -quit) ]]
  [[ -z $(find "$dir" -perm /6000 -print -quit) ]]
  [[ -z $(find "$dir/DEBIAN" -type f ! -name control ! -name md5sums ! -name conffiles -print -quit) ]]
  find "$dir" -exec touch -h -d '@1767225600' '{}' +
  dpkg-deb --build --root-owner-group --uniform-compression -Zgzip -z9 --threads-max=1 "$dir" "$work/$run/${package}_${version}_all.deb"
  if [[ $run = a ]]; then cp -a "$dir" "$root/source/${package}_${version}_all"; fi
 done
done
for a in "$work/a/"*.deb; do
 name=${a##*/}; cmp "$a" "$work/b/$name"
 [[ $(stat -c %s "$a") -le 65536 ]]
 cp "$a" "$root/archives/$name"
 dpkg-deb --info "$a" > "$root/source/$name.info"
 dpkg-deb --contents "$a" > "$root/source/$name.contents"
 printf '\nDISCOVERY_DEB_BEGIN %s\n' "$name" > /dev/ttyS0
 base64 "$a" > /dev/ttyS0
 printf 'DISCOVERY_DEB_END\n' > /dev/ttyS0
done
(cd "$root"; find archives source notices -type f | LC_ALL=C sort | xargs sha256sum) > "$root/SHA256SUMS"
# There is no repository and no acquisition; only explicit local archive lessons.
printf '%s\n' 'Fixture packages are UNINSTALLED; archives/source are root-owned. Guest root can alter them.' > "$root/README"
find "$root" -type d -exec chmod 0755 '{}' +
find "$root" -type f -exec chmod 0444 '{}' +
chown -R root:root "$root"
[[ $(dpkg-query -W -f='${db:Status-Status}' ll-discovery-data 2>/dev/null || :) != installed ]]
[[ $(dpkg-query -W -f='${db:Status-Status}' ll-discovery-report 2>/dev/null || :) != installed ]]
printf 'DISCOVERY_FIXTURES_REPRODUCIBLE\n' > /dev/ttyS0
