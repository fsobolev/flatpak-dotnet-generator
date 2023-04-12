# Flatpak .NET Generator

Tool to automatically generate a `flatpak-builder` sources file from a .NET Core .csproj file.

This is a modified version of a script from [Flatpak Builder Tools](https://github.com/flatpak/flatpak-builder-tools/tree/master/dotnet).

List of changes:
* Added packages that are required to build self-contained apps (latest stable version is retrieved automatically)
* `org.freedesktop.Sdk` version changed to 22.08
* `dotnet` version changed to 7

For instructions on how to build dotnet apps using flatpak, see [Dotnet SDK Extension README](https://github.com/flathub/org.freedesktop.Sdk.Extension.dotnet7#readme).
