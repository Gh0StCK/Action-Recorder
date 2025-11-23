ActionRecorder (Fork)

ActionRecorder is a Blender add-on that allows you to record, edit, and replay sequences of operators as reusable actions (macros).
It speeds up repetitive workflows by turning long chains of clicks into one-click tools.

This repository is an unofficial fork of the original add-on by InamuraJIN and RivinHD.
All credits for the concept, design, and core implementation belong to them.
This fork introduces small functional tweaks, minor fixes, and maintains full compatibility with the original codebase.

✨ Key Features
📌 Record Actions (Macros)

Capture sequences of Blender operators including all parameters, and save them as named reusable actions.

🧩 Local & Global Libraries

Local actions — stored inside the current .blend file.

Global actions — accessible from any project.

🗂️ Categories & Organization

Group actions into categories

Reorder actions

Move actions between categories

Quickly switch between different setups

🎯 Playback & Execution Options

Run an entire action with one click

Execute individual steps inside an action

Control property replay logic and value restoration behavior

⌨️ Keymap & Menu Integration

Assign shortcuts to your favorite actions

Access actions from 3D View menus and pie menus

Optional: add “Copy to ActionRecorder” to the right-click context menu

📤📥 Import / Export

Export global actions to a file

Import actions on another machine or share with your team

🧱 Advanced Property Support

Handles complex Blender properties correctly:

vectors

matrices

colors

and other non-trivial types

🧩 Blender Compatibility

The original add-on targets Blender 3.3.x (as indicated in bl_info).
This fork keeps the same architecture with only minor adjustments and functional polishing.

🔧 About This Fork

This fork:

preserves the original structure and logic of ActionRecorder

applies small functional changes and minor improvements

stays close to upstream to simplify future merging or comparison

introduces no major redesigns or architecture changes

For specifics, see the commit history.

🙌 Credits

Original Authors:

InamuraJIN

RivinHD

Fork Maintainer:

gh0stck
