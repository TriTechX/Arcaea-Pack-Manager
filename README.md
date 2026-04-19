# Arcaea-Pack-Manager
A GUI utility for extracting/repacking .pack files in NX Arcaea's RomFS. Useful for creating RomFS mods for Arcaea for NX.

## How to use
- Download `packman.py`
- Install Python 3.8+
- Run the file by double clicking, or running `python packman.py` in the terminal in the directory where the pack manager is stored
- Note: all dependencies for this project are built into Python 3.8+, no external dependency installs are required

## How do I get RomFS?
- Install Ryujinx from https://ryujinx.app/
- Provide Ryujinx with keys and firmware extracted from your console
  - I will not be providing a guide on how to obtian these keys and firmware, please refer to external guides on how to use lockpick_rcm
  - Do NOT download these files online, there is no guarantee that they are safe, and this is illegal, as these files are copyright protected content
- Extract the Arcaea base game and update NSPs from your console
  - I recommend using https://github.com/DarkMatterCore/nxdumptool to dump the NSPs from your console to your PC
- Install the title and update NSPs in Ryujinx
- Right click on the title, 'Extract Data' -> 'RomFS'
- Select a dedicated RomFS extraction directory, and the RomFS files will be extracted there

## How do I make a mod?
- For making mods, I recommend modifying existing files within arc_x.pack files, adding custom charts/characters etc. instead of replacing pre-existing ones is significantly more convoluted

- First, extract the pack you wish to modify
  - To keep your mod small, you should modify the smallest arc_x.pack files
  - I choose to modify arc_1.pack, as this is the smallest pack (around 39 MB) that contains charts and characters, unless you really enjoy all of the Groove Coaster charts/content (which this pack contains), I suggest modifying this one
- Then, modify the content of the extracted pack
  - Charts are found in 'songs', characters are found in 'char', misc sound effects are in 'audio', misc textures are in 'img', sky note textures and models are found in 'models'
- You can modify bpm/chart constants in the 'songlist' file in 'songs', and the 'songs.json' file in 'switch-local-29-06-20', except I've had difficulty when trying to get songs.json changes to show in game, my theory is that every instance of songlist and songs.json must be modified in every .pack to make changes, but this is not worth it because the mod size would then exceed 800 MB, I will gladly be proven wrong
- Once done, repack the directory you were working on, and set the names of the .pack and .json files to match the name of the .pack file you extracted, in this example we extracted arc_4.pack, so we will set the pack name to arc_4.pack, and the json name to arc_4.json
- To create a mod, put these new, packed files (new arc_4.pack and arc_4.json) in a folder called 'romfs', and put that folder in another folder called the name of your mod
- To run the mod on Ryujinx, add the mod through right click -> 'Manage Mods' -> 'Add' and select the folder called the name of your mod
- To run the mod on a modified Nintendo Switch (running Atmosphere), put the 'romfs' folder in sdcard/atmosphere/contents/0100E680149DC000/, so it becomes sdcard/atmosphere/contents/0100E680149DC000/romfs/, where romfs contains your mod data (arc_x.pack, arc_x.json)
