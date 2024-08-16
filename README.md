# Introduction

This is a solution to translate SRPG Studio games. The process involves detecting specific values in the game files, extracting text for translation, and then writing the translated text back into the game.

## Setup

Before using the scripts, make sure to install the required dependency:

```bash
pip install frida
pip install polib
pip install pycryptodome
```

## Usage

Follow these steps to translate the game:

### 1. Get RVA Value

Run the `detect.py` script to get the RVA value, which is essential for the following steps.

```bash
python translate_tools.py patch detect game_directory project_file_path
```

- `game_directory`: The directory where the SRPG Studio game is located.
- `project_file_path`: The path to the project file within the game directory.

### 2. Extract Text from `data.dts`

Next, run the `fetch.py` script to extract all the text from the `data.dts` file in the game directory. This step generates a `translation.pot` file containing all the text.

```bash
python translate_tools.py fetch game_directory -r rva
```

- `rva`: The RVA value obtained from the previous step.

### 3. Write Translation Data Back to `data.dts`

Finally, use the `patch.py` script to write the translated text back into the `data.dts` file.

```bash
python translate_tools.py patch game_directory mo_file_path
```

### Example

Here’s a brief example of the full process:

```bash
python translate_tools.py detect ./game ./game/project.srpgs
python translate_tools.py fetch ./game -r 0x123456
python translate_tools.py patch ./game ./translation.mo
```

## Notes

- Ensure that all dependencies are installed before running the scripts.
- This solution is designed specifically for SRPG Studio games and may not work with other types of games.
- If you encounter any issues, please refer to the log output for debugging information.