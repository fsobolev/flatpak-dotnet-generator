#!/usr/bin/env python3

__license__ = 'MIT'

from pathlib import Path

import argparse
import base64
import binascii
import json
import subprocess
import tempfile
import urllib.request


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('output', help='The output JSON sources file')
    parser.add_argument('project', help='The project file')
    parser.add_argument('--runtime', '-r', help='The target runtime to restore packages for')
    parser.add_argument('--destdir',
                        help='The directory the generated sources file will save sources to',
                        default='nuget-sources')
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(dir=Path()) as tmp:
        sources = get_runtime_sources(args.destdir)

        runtime_args = []
        if args.runtime:
            runtime_args.extend(('-r', args.runtime))

        print('Restoring the project...')
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

def get_runtime_sources(destdir):
    result = []
    for core in ('aspnetcore', 'netcore'):
        for arch in ('arm', 'arm64', 'x64'):
            print(f'Getting data for microsoft.{core}.app.runtime.linux-{arch}...')
            with urllib.request.urlopen(f'https://api.nuget.org/v3/registration5-semver1/microsoft.{core}.app.runtime.linux-{arch}/index.json') as reg_data:
                catalog_url = json.load(reg_data)['items'][-1]['items'][-1]['catalogEntry']['@id']
            with urllib.request.urlopen(catalog_url) as catalog_data:
                data = json.load(catalog_data)
                version = data['version']
                sha512 = binascii.hexlify(base64.b64decode(data['packageHash'])).decode('ascii')
            result.append({
                'type': 'file',
                'url': f'https://api.nuget.org/v3-flatcontainer/microsoft.{core}.app.runtime.linux-{arch}/{version}/microsoft.{core}.app.runtime.linux-{arch}.{version}.nupkg',
                'sha512': sha512,
                'dest': destdir,
                'dest-filename': f'microsoft.{core}.app.runtime.linux-{arch}.{version}.nupkg',
            })
    return result

if __name__ == '__main__':
    main()
