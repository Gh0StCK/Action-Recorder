ActionRecorder (fork)

ActionRecorder is a Blender add-on that lets you record, edit and replay sequences of operators as reusable actions (macros).
It is designed to speed up repetitive workflows by turning complex click-sequences into one-click tools.

This repository is an unofficial fork of the original add-on by InamuraJIN and RivinHD.
All credits for the original idea, design and implementation belong to them.
This fork only contains small functional tweaks and minor fixes on top of their work.

Key features

📌 Record actions (macros)
Capture sequences of Blender operators with their settings and store them as named actions.

🧩 Local & Global libraries

Local actions stored inside the current .blend file.

Global actions available across all projects.

🗂️ Categories and flexible organization
Group actions into categories, reorder them, move actions between categories and switch quickly between setups.

🎯 Playback and execution options

Run a full action with one click.

Execute individual macros inside an action.

Control how properties are replayed and how values are restored.

⌨️ Keymap integration & menus

Add shortcuts for your favorite actions.

Access actions from 3D View menus and pie menus.

Optional “Copy to ActionRecorder” entry in the right-click context menu for quickly capturing settings.

📤📥 Import / export

Export global actions to a file.

Import actions on another machine or share them with the team.

🧱 Support for complex properties
Proper handling of vectors, matrices, colors and other non-trivial Blender properties when recording and replaying macros.

Blender compatibility

The original add-on targets Blender 3.3.x (as specified in bl_info).
This fork keeps the same codebase with only minimal adjustments to the functionality and behavior.

About this fork

This repository:

keeps the original structure and logic of ActionRecorder;

applies only small functional changes and minor improvements (bugfixes / behavior tweaks);

aims to stay as close as possible to upstream, so that updating or comparing with the original project remains straightforward.

For detailed differences, please refer to the commit history of this repository.

Credits

Original add-on authors: InamuraJIN, RivinHD

Fork maintainer: gh0stck
