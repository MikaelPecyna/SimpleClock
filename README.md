# Clock

A simple fullscreen digital clock application built with GTK 4.

## Features

- Large, fullscreen time display (HH:MM:SS)
- Adjustable background opacity (0-100%)
- Customizable background and text colors
- Configurable padding around the text
- Settings are automatically saved
- Responsive design that adapts to window size

## Requirements

- Python 3.6+
- GTK 4
- PyGObject

### Install Dependencies

**Fedora/RHEL:**

```bash
sudo dnf install python3-gobject gtk4-devel
```

**Debian/Ubuntu:**

```bash
sudo apt install python3-gi gir1.2-gtk-4.0 libgtk-4-dev
```

**Arch:**

```bash
sudo pacman -S gtk4 python-gobject
```

## Usage

```bash
python3 main.py
```

## Configuration

Settings are stored in `~/.config/clockgtk/config.json`

Example configuration:

```json
{
  "bg_alpha": 0.7,
  "bg_color": "#363a4f",
  "text_color": "#cad3f5",
  "padding": 0,
  "time_format": "%H:%M:%S"
}
```

- `bg_alpha`: Background opacity (0.0 = transparent, 1.0 = opaque)
- `bg_color`: Background color in hex format
- `text_color`: Text color in hex format
- `padding`: Padding around the text in pixels
- `time_format`: Format string for the time display (see strftime documentation)

Common time format examples:

- `%H:%M:%S` - 24-hour format (HH:MM:SS)
- `%I:%M:%S %p` - 12-hour format with AM/PM
- `%H:%M:%S:%ms` - With milliseconds separated by colon
- `%A %H:%M:%S` - Day name + time

## Menu Options

Access the menu (hamburger icon) to adjust:

- **Transparency**: Change background opacity
- **Background Color**: Pick a custom background color
- **Text Color**: Pick a custom text color
- **Padding**: Adjust space around the time display
- **Time Format**: Change the time display format (HH:MM:SS, 12h format, with microseconds, etc.)
- **Reset**: Restore default settings

## Personal Project

I created this application for my personal use as a simple, customizable desktop clock that displays the time as large as possible while fitting nicely on the screen.
