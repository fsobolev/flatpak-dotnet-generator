#!/usr/bin/env python3

__license__ = 'MIT'

from pathlib import Path

import argparse
import base64
import binascii
import json
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('output', help='The output JSON sources file')
    parser.add_argument('project', help='The project file')
    parser.add_argument('--runtime', '-r', help='The target runtime to restore packages for')
    parser.add_argument('--destdir',
                        help='The directory the generated sources file will save sources to',
                        default='nuget-sources')
    args = parser.parse_args()

    sources = []

    sources += json.loads('''[{
        "type": "file",
        "url": "https://api.nuget.org/v3-flatcontainer/microsoft.aspnetcore.app.runtime.linux-arm/7.0.1/microsoft.aspnetcore.app.runtime.linux-arm.7.0.1.nupkg",
        "sha512": "699c9c3f3b529cae97adf0e147ce7f2a45980f7a9793d0e6ff8fbf068a66a06a9c8692e58e7f17f71bf55f4d2118da21840a41408ec1c9ab2661dc8d7b74bc88",
        "dest": "nuget-sources",
        "dest-filename": "microsoft.aspnetcore.app.runtime.linux-arm.7.0.1.nupkg"
    },
    {
        "type": "file",
        "url": "https://api.nuget.org/v3-flatcontainer/microsoft.aspnetcore.app.runtime.linux-arm64/7.0.1/microsoft.aspnetcore.app.runtime.linux-arm64.7.0.1.nupkg",
        "sha512": "6118682a2978748205478db312ce64593e1b171a6afe28a443d3539aeaabf6d886370ff03462b31493a206849ed6587ec044e075d2e0e5db829f55a143c09a43",
        "dest": "nuget-sources",
        "dest-filename": "microsoft.aspnetcore.app.runtime.linux-arm64.7.0.1.nupkg"
    },
    {
        "type": "file",
        "url": "https://api.nuget.org/v3-flatcontainer/microsoft.aspnetcore.app.runtime.linux-x64/7.0.1/microsoft.aspnetcore.app.runtime.linux-x64.7.0.1.nupkg",
        "sha512": "c33828b32f4b8a957a877329d38b5677fa1fe25f38192484bcafe7adfe669c8bd2f5d9cfc920fd1f1932f5d35160677243d8a6a33c98de1cca7369a1bf9b0bce",
        "dest": "nuget-sources",
        "dest-filename": "microsoft.aspnetcore.app.runtime.linux-x64.7.0.1.nupkg"
    },
    {
        "type": "file",
        "url": "https://api.nuget.org/v3-flatcontainer/microsoft.netcore.app.runtime.linux-arm/7.0.1/microsoft.netcore.app.runtime.linux-arm.7.0.1.nupkg",
        "sha512": "bb6fd7f9dff0666582cd3d122fe87e0c1082d4e62f2be6f4cc9d42b7c4d7ac54eb0ddc8400dc008bc1955d851683f07e64a9ca09aa8c810b78618bb91ca411da",
        "dest": "nuget-sources",
        "dest-filename": "microsoft.netcore.app.runtime.linux-arm.7.0.1.nupkg"
    },
    {
        "type": "file",
        "url": "https://api.nuget.org/v3-flatcontainer/microsoft.netcore.app.runtime.linux-arm64/7.0.1/microsoft.netcore.app.runtime.linux-arm64.7.0.1.nupkg",
        "sha512": "efb6bcef77e3f26a8b3c9152caa60c47d2b514aa4feb57719f9cd865e7bef6da9d76b5b101e48795eec3c8cb27864e86e4afcab17e8dc249caf49218d14efeb5",
        "dest": "nuget-sources",
        "dest-filename": "microsoft.netcore.app.runtime.linux-arm64.7.0.1.nupkg"
    },
    {
        "type": "file",
        "url": "https://api.nuget.org/v3-flatcontainer/microsoft.netcore.app.runtime.linux-x64/7.0.1/microsoft.netcore.app.runtime.linux-x64.7.0.1.nupkg",
        "sha512": "3af5711902471ccd0f663419a4255c93bac3cd84243fb9fe6a3d73dccdec4d10cd454277c83ce1a8f25b02924cadebee7e57e866086082184961c3697351b1b7",
        "dest": "nuget-sources",
        "dest-filename": "microsoft.netcore.app.runtime.linux-x64.7.0.1.nupkg"
    }]''')

    with tempfile.TemporaryDirectory(dir=Path()) as tmp:
        runtime_args = []
        if args.runtime:
            runtime_args.extend(('-r', args.runtime))

        subprocess.run([
            'flatpak', 'run',
            '--env=DOTNET_CLI_TELEMETRY_OPTOUT=true',
            '--env=DOTNET_SKIP_FIRST_TIME_EXPERIENCE=true',
            '--command=sh', '--runtime=org.freedesktop.Sdk//22.08', '--share=network',
            '--filesystem=host', 'org.freedesktop.Sdk.Extension.dotnet7//22.08', '-c',
            'PATH="${PATH}:/usr/lib/sdk/dotnet7/bin" LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/lib/sdk/dotnet7/lib" exec dotnet restore "$@"',
            '--', '--packages', tmp, args.project] + runtime_args)

        for path in Path(tmp).glob('**/*.nupkg.sha512'):
            name = path.parent.parent.name
            version = path.parent.name
            filename = '{}.{}.nupkg'.format(name, version)
            url = 'https://api.nuget.org/v3-flatcontainer/{}/{}/{}'.format(name, version,
                                                                           filename)

            with path.open() as fp:
                sha512 = binascii.hexlify(base64.b64decode(fp.read())).decode('ascii')

            sources.append({
                'type': 'file',
                'url': url,
                'sha512': sha512,
                'dest': args.destdir,
                'dest-filename': filename,
            })

    with open(args.output, 'w') as fp:
        json.dump(
            sorted(sources, key=lambda n: n.get("dest-filename")),
            fp,
            indent=4
        )


if __name__ == '__main__':
    main()
