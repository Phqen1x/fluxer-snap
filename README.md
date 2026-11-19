# Fluxer snap

Unofficial snap package for [Fluxer](https://fluxer.app), an instant messaging
and VoIP desktop app. It builds the Electron app from the
[upstream source](https://github.com/fluxerapp/fluxer) at each stable release
tag, as a `core26` snap for amd64 and arm64.

## Install from the Snap Store

```sh
sudo snap install fluxer
```

Or find it in the Snap Store / App Center. Updates arrive automatically.

If your microphone or camera doesn't work, connect the
permissions below.

```sh
sudo snap connect fluxer:audio-record              # microphone
sudo snap connect fluxer:camera                    # webcam
```

## Build

```sh
snapcraft pack
```

Needs [snapcraft](https://snapcraft.io/snapcraft) 9 or newer and LXD or
Multipass. The build compiles Rust native modules and the web app, so expect
it to take a while and to need several GB of disk and memory. Run
`snapcraft clean` first if a previous build failed, since stale part state can
break the next one.

## Install a local build

```sh
sudo snap install --dangerous fluxer_*_amd64.snap
```

Snaps installed with `--dangerous` don't auto-connect any optional
permissions, so connect them yourself:

```sh
sudo snap connect fluxer:audio-record              # microphone
sudo snap connect fluxer:camera                    # webcam
```

Then run `fluxer`, or launch it from your app menu.

## How it works

- **Source:** the `fluxer-desktop-stable@<version>` tag of
  `fluxerapp/fluxer` is built following upstream's
  [`fluxer_desktop/PACKAGING.md`](https://github.com/fluxerapp/fluxer/blob/main/fluxer_desktop/PACKAGING.md).
  The Rust toolchain, pnpm and wasm-bindgen versions are read from the tagged
  source tree; Node.js 26 comes from the `node` snap.
- **Electron:** upstream's Electron build with its VA-API patch is downloaded
  from their GitHub release, and the build verifies it against the checksums
  pinned in the tagged `electron/runtime.json`.
- **No in-app updates:** the app is built with `FLUXER_OFFLINE=1`, upstream's
  switch for distribution builds. It is compiled into the bundle and turns off
  the desktop updater, the web app update check and module downloads, and stops
  the app writing its own `.desktop` file. Updates come from the Snap Store
  instead.
- **Data directory:** offline builds keep their data in
  `~/snap/fluxer/current/.config/fluxer-distro`, separate from upstream's own
  packages. For users upgrading from the old deb-based snap,
  `snap/local/migrate-config` (an app `command-chain` entry) copies
  `.config/fluxer` to `.config/fluxer-distro` once, at the first launch, so
  they stay signed in. It leaves the old directory in place.
- **Libraries:** runtime libraries the app and Electron need are listed in
  `stage-packages`; the `gnome` extension provides GTK and the GPU stack.
- **Sandbox:** Fluxer is launched with `--no-sandbox` and the setuid
  `chrome-sandbox` helper is removed, because it can't work inside a snap.
  Confinement comes from snap's own sandbox instead.
- **Desktop entry:** `snap/local/app.fluxer.FluxerDesktop.desktop` is
  installed under the desktop ID the app looks for, so `fluxer://` links work.

## Updates

### Automatic publishing

`.github/workflows/update-fluxer.yml` checks upstream's stable feed every six
hours. When `shell.latest_version` changes (and its
`fluxer-desktop-stable@<version>` tag exists) it updates `source-tag` and
`FLUXER_VERSION` in `snap/snapcraft.yaml`, builds the snap from source for
amd64 and arm64 (the latter on GitHub's arm64 runner), publishes both to the
**edge** channel and commits the change. Pull requests touching the packaging
build both architectures without publishing. You can also run it by hand from the Actions tab
(tick "force" to rebuild without a new release).

It needs a repository secret named `SNAPCRAFT_STORE_CREDENTIALS`:

```sh
snapcraft export-login --snaps fluxer --channels edge \
  --acls package_access,package_push,package_update,package_release -
```

Promote edge to `beta`/`candidate`/`stable` yourself once you've tested it.

### Manual update

Check the current stable version:

```sh
curl -fsS https://pkgs.fluxer.com/desktop/stable/linux/x64/modules.json | jq -r .shell.latest_version
```

Then set `source-tag` (`fluxer-desktop-stable@<version>`) and
`FLUXER_VERSION` in `snap/snapcraft.yaml` and rebuild, or just run
`python3 .github/scripts/update_snapcraft.py`.

## Known limitations

- The arm64 build is only built by the GitHub workflow (on an arm64 runner); I haven't run it on real arm64 hardware.
- `grade: devel`; switch to `stable` before publishing to the Snap Store.
- The permissions requested are best guesses for a chat and voice app. If
  something is blocked, `snappy-debug` shows which interface is missing.
- Unofficial and not affiliated with Fluxer Platform AB.
