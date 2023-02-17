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
        "url": "https://api.nuget.org/v3-flatcontainer/microsoft.aspnetcore.app.runtime.linux-arm/7.0.3/microsoft.aspnetcore.app.runtime.linux-arm.7.0.3.nupkg",
        "sha512": "af20c42549dcf7f25a2046aa6ef071d0231c554e0b5c5a357207fc708384d46a1d57e6f2e054a4eddeb2f04fe64d7ef3c9974fc50878d6e3ae018b0f735cd141",
        "dest": "nuget-sources",
        "dest-filename": "microsoft.aspnetcore.app.runtime.linux-arm.7.0.3.nupkg"
    },
    {
        "type": "file",
        "url": "https://api.nuget.org/v3-flatcontainer/microsoft.aspnetcore.app.runtime.linux-arm64/7.0.3/microsoft.aspnetcore.app.runtime.linux-arm64.7.0.3.nupkg",
        "sha512": "15a2fbfed3d2bb2433c560e2ddd5f292d3c35912855f912d4544f7d24be9144d0c910f65db041399c1d06aaa726616e984f0cf62223ca214587c6620645c5bca",
        "dest": "nuget-sources",
        "dest-filename": "microsoft.aspnetcore.app.runtime.linux-arm64.7.0.3.nupkg"
    },
    {
        "type": "file",
        "url": "https://api.nuget.org/v3-flatcontainer/microsoft.aspnetcore.app.runtime.linux-x64/7.0.3/microsoft.aspnetcore.app.runtime.linux-x64.7.0.3.nupkg",
        "sha512": "5d5260808836083ea348d5c99e5f447eef0de117672c3b00113874e1f3b25c7eca7ae0036a10a167f788cbf5953ddaa9f3a84f9ea9944dca079b7a44c4aa7ad6",
        "dest": "nuget-sources",
        "dest-filename": "microsoft.aspnetcore.app.runtime.linux-x64.7.0.3.nupkg"
    },
    {
        "type": "file",
        "url": "https://api.nuget.org/v3-flatcontainer/microsoft.netcore.app.runtime.linux-arm/7.0.3/microsoft.netcore.app.runtime.linux-arm.7.0.3.nupkg",
        "sha512": "33dce0732a115e8b598edc0df37643f6d88aaa9885ac58653394b42131833aea2d71c54c69a4fa6aec2ea03064ce1414eb98c4dd1a1c74a9fc5f57376c8e7796",
        "dest": "nuget-sources",
        "dest-filename": "microsoft.netcore.app.runtime.linux-arm.7.0.3.nupkg"
    },
    {
        "type": "file",
        "url": "https://api.nuget.org/v3-flatcontainer/microsoft.netcore.app.runtime.linux-arm64/7.0.3/microsoft.netcore.app.runtime.linux-arm64.7.0.3.nupkg",
        "sha512": "49f15b132aa6a48b318304450ee94afbec8580ba2b46ac2c8a6800237ca6b1b59b74e7f3fa5fc4020909d99f267863f0f8733debf1a6da3679ac8b1f42d525e0",
        "dest": "nuget-sources",
        "dest-filename": "microsoft.netcore.app.runtime.linux-arm64.7.0.3.nupkg"
    },
    {
        "type": "file",
        "url": "https://api.nuget.org/v3-flatcontainer/microsoft.netcore.app.runtime.linux-x64/7.0.3/microsoft.netcore.app.runtime.linux-x64.7.0.3.nupkg",
        "sha512": "8e82d6cc1c72b1fb098e857d66e9a0445ac99f66d9f94ecdb5c68f398bf71f95783982c7e33f8ca0869778fcba8e9f3d78dacd93003c715f11fa5f987fff10ac",
        "dest": "nuget-sources",
        "dest-filename": "microsoft.netcore.app.runtime.linux-x64.7.0.3.nupkg"
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
