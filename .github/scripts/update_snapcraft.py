#!/usr/bin/env python3
"""Point snap/snapcraft.yaml at the current stable Fluxer desktop release tag.

Upstream's packaging guide says to build the version in the stable feed's
`shell.latest_version` from the `fluxer-desktop-stable@<version>` tag, rather
than the newest tag, since some tags are web-app-only or held-back releases.

Writes `changed` and `version` to $GITHUB_OUTPUT. Set FORCE=true to report a
change even when the snap already matches the feed.
"""
import json
import os
import re
import subprocess
import sys
import urllib.request

FEED = "https://pkgs.fluxer.com/desktop/stable/linux/{arch}/modules.json"
ARCHES = ("x64", "arm64")
UPSTREAM = "https://github.com/fluxerapp/fluxer"
TAG_PREFIX = "fluxer-desktop-stable@"
YAML = "snap/snapcraft.yaml"


def feed_version(arch):
    with urllib.request.urlopen(FEED.format(arch=arch), timeout=30) as resp:
        return json.load(resp)["shell"]["latest_version"]


def tag_exists(tag):
    result = subprocess.run(
        ["git", "ls-remote", "--exit-code", "--tags", UPSTREAM, f"refs/tags/{tag}"],
        capture_output=True,
    )
    return result.returncode == 0


def main():
    versions = {feed_version(arch) for arch in ARCHES}
    if len(versions) != 1:
        sys.exit(f"x64 and arm64 feeds are on different versions: {sorted(versions)}")
    version = versions.pop()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        sys.exit(f"unexpected version in the stable feed: {version!r}")
    tag = f"{TAG_PREFIX}{version}"
    if not tag_exists(tag):
        sys.exit(f"{tag} is in the stable feed but not tagged in {UPSTREAM}")

    with open(YAML) as f:
        original = f.read()
    text, n_tag = re.subn(r"(source-tag: )\S+", rf"\g<1>{tag}", original)
    text, n_ver = re.subn(r'(FLUXER_VERSION: )"[^"]*"', rf'\g<1>"{version}"', text)
    if (n_tag, n_ver) != (1, 1):
        sys.exit(f"could not find source-tag and FLUXER_VERSION in {YAML}")

    changed = os.environ.get("FORCE") == "true" or text != original
    with open(YAML, "w") as f:
        f.write(text)

    print(f"fluxer {version}: {'update needed' if changed else 'snap is up to date'}")
    with open(os.environ.get("GITHUB_OUTPUT", os.devnull), "a") as out:
        out.write(f"changed={'true' if changed else 'false'}\nversion={version}\n")


main()
