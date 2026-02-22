# tools/

Place third-party executables here.

## texconv.exe
Required for PNG → BC7_UNORM DDS conversion.

Download from: https://github.com/microsoft/DirectXTex/releases
Pick the latest `texconv.exe` from the release assets and drop it here.

The logo patcher will look for it at `tools/texconv.exe` relative to the
repo root, or you can pass `--texconv <path>` on the command line.
