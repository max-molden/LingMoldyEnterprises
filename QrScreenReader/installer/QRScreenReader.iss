#define MyAppName "QR Screen Reader"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "Ling Moldy Enterprises"
#define MyAppExeName "QRScreenReader.exe"

[Setup]
AppId={{B1C1A4E3-882D-4A0D-8FA7-3A934EEA0A49}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\\QRScreenReader
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=.
OutputBaseFilename=QRScreenReaderInstaller
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ChangesAssociations=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Additional icons:";

[Files]
Source: "..\\dist\\QRScreenReader\\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{autoprograms}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"
Name: "{autoprograms}\\{#MyAppName} (Snip Mode)"; Filename: "{app}\\{#MyAppExeName}"; Parameters: "--mode snip"
Name: "{autodesktop}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
