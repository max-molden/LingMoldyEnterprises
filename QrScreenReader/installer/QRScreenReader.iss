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
PrivilegesRequired=admin
InfoBeforeFile=UAC_INFO.txt

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Additional icons:";
Name: "globalhotkey"; Description: "Enable always-on native global hotkey launcher (Win+Shift+Q)"; GroupDescription: "Global Hotkey:";

[Files]
Source: "..\\dist\\QRScreenReader\\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion
Source: "..\\dist\\QRScreenReader\\QRHotkeyHelper.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"
Name: "{autoprograms}\\{#MyAppName} (Snip Mode)"; Filename: "{app}\\{#MyAppExeName}"; Parameters: "--mode snip"
Name: "{autodesktop}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userstartup}\\{#MyAppName} Hotkey Launcher"; Filename: "{app}\\QRHotkeyHelper.exe"; Tasks: globalhotkey

[Run]
Filename: "{app}\\QRHotkeyHelper.exe"; Description: "Start native global hotkey launcher in background"; Flags: nowait postinstall skipifsilent; Tasks: globalhotkey
Filename: "{app}\\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
