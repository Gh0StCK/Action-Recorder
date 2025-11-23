# ActionRecorder (Fork)

**ActionRecorder** is a Blender add-on that allows you to **record**, **edit**, and **replay** sequences of operators as reusable **actions (macros)**.  
It helps automate repetitive workflows by turning complex multi-click operations into **single-button actions**.

This repository is an **unofficial fork** of the original add-on by **InamuraJIN** and **RivinHD**.  
All credits for the concept, design, and core implementation belong to them.  
This fork includes **small functional tweaks**, **minor improvements**, and several **behavior fixes**, while maintaining full compatibility with the original project.

---

## ✨ Key Features

### 📌 Record Actions (Macros)
Capture sequences of Blender operators (including settings) and save them as named actions.

### 🧩 Local & Global Libraries
- **Local actions** — stored inside the `.blend` file  
- **Global actions** — shared across all Blender projects  

### 🗂️ Categories & Organization
- Group actions into categories  
- Reorder actions  
- Move actions between categories  
- Quickly switch setups  

### 🎯 Playback & Execution Options
- Run the entire action with a single click  
- Execute individual steps  
- Control property replay mode  
- Configure how values reset or persist  

### ⌨️ Keymap & Menu Integration
- Add hotkeys for actions  
- Access actions from 3D View menus and pie menus  
- Optional: “Copy to ActionRecorder” in the right-click context menu  

### 📤📥 Import / Export
- Export global actions to a file  
- Import actions between machines or share with teammates  

### 🧱 Advanced Property Support
Correct handling of complex Blender datatypes:
- vectors  
- matrices  
- colors  
- nested properties  

---

## 🧩 Blender Compatibility

The original add-on targets **Blender 3.3.x** according to `bl_info`.  
This fork remains aligned with the original design, with only minimal modifications.

---

## 🔧 About This Fork

This repository:

- preserves the original architecture and logic of **ActionRecorder**  
- applies **minor functional enhancements**  
- includes **small bugfixes** and **quality-of-life adjustments**  
- stays close to upstream for easy diffing and future merging  

See the commit history for detailed changes.

---

## 🙌 Credits

**Original Authors:**  
- **InamuraJIN**  
- **RivinHD**

**Fork Maintainer:**  
- **gh0stck**

---
