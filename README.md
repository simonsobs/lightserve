Lightserve
==========

A lightcurve server, backed by lightcurvedb.

Install with:

```
uv pip install -e ".[dev,ephemeral]"
```

Run an ephemeral server with

```
lightserve-ephemeral
```

Check out the docs at

```
localhost:8000/docs
```

## Tag and push a stable release

The [build-and-push workflow](./.github/workflows/build-and-push.yml) builds and pushes the `latest` image on every push to `main`. Stable releases use version tags in the form `vMAJOR.MINOR.PATCH`, such as `v0.1.0`.

First, make sure you are tagging the commit you want to release. Then create and push the tag:

```bash
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

Pushing the tag triggers GitHub Actions to build and push a multi-platform image to GHCR. For the upstream repository, the image is published as:

```text
ghcr.io/simonsobs/lightserve:v0.1.0
```

Check the repository's **Actions** tab to confirm that the build succeeded.