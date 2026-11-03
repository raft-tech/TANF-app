#!/usr/bin/env bash
set -euo pipefail

# Keep the final runtime's libc/loader and existing SONAMEs. Only add the missing
# dependency closure, with package metadata so scanners can see copied libraries.
root=/runtime-additions
mkdir -p "$root/usr/bin" "$root/usr/sbin" "$root/var/lib/dpkg" "$root/usr/share/keycloak-image"
cp /runtime-status "$root/var/lib/dpkg/status"
declare -A packages=()
for binary in /usr/bin/curl /usr/bin/jq /usr/bin/grep /usr/sbin/nginx; do
    cp --parents "$binary" "$root"
    dependencies="$(ldd "$binary")"
    if [[ "$dependencies" == *'not found'* ]]; then
        echo "Unresolved dependencies for $binary: $dependencies" >&2
        exit 1
    fi
    while read -r library; do
        library="${library/#\/lib\//\/usr\/lib\/}"
        relative="${library#/usr/lib/}"
        if [[ -e "/runtime-libs/$relative" ]]; then
            continue
        fi
        case "$(basename "$library")" in
            ld-linux*|libc.so.*|libm.so.*|libdl.so.*|libpthread.so.*|librt.so.*)
                echo "Refusing to transplant glibc component: $library" >&2
                exit 1 ;;
        esac
        cp -L --parents "$library" "$root"
        package="$(dpkg-query -S "$library" | head -1)"
        packages["${package%%: /*}"]=1
    done < <(awk '/=> \// {print $3}' <<< "$dependencies")
    if [[ "$binary" != /usr/sbin/nginx ]]; then
        packages["$(basename "$binary")"]=1
    fi
done

for package in "${!packages[@]}"; do
    name="${package%%:*}"
    # An existing runtime package must not acquire a misleading duplicate record.
    awk -v name="$name" 'BEGIN {RS=""; ORS="\n\n"} $0 !~ "(^|\n)Package: " name "(\n|$)"' \
        "$root/var/lib/dpkg/status" > /status-next
    mv /status-next "$root/var/lib/dpkg/status"
    dpkg-query -s "$package" >> "$root/var/lib/dpkg/status"
    printf '\n' >> "$root/var/lib/dpkg/status"
    if [[ -d "/usr/share/doc/$name" ]]; then
        mkdir -p "$root/usr/share/doc"
        cp -a "/usr/share/doc/$name" "$root/usr/share/doc/"
    fi
done
awk 'BEGIN {RS=""; ORS="\n\n"} /(^|\n)Package: nginx-stable(\n|$)/' /nginx-status >> "$root/var/lib/dpkg/status"
grep -q '^Package: nginx-stable$' "$root/var/lib/dpkg/status"
dpkg-query -W > "$root/usr/share/keycloak-image/assembly-packages.tsv"
find "$root/usr/bin" "$root/usr/sbin" "$root/usr/lib" -type f -exec sha256sum {} + \
    | sed "s@$root/@/@g" > "$root/usr/share/keycloak-image/copied-files.sha256"
