#!/usr/bin/env python3

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, Gio
from datetime import datetime
import json
import os


class ClockApp(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("Clock")
        self.set_default_size(800, 400)

        self.bg_alpha = 0.7
        self.bg_color = "#1a1a1a"
        self.text_color = "#ffffff"
        self.padding = 20
        self.time_format = "%H:%M:%S"

        self.load_settings()

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        header_bar = self._create_header_bar()
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_hexpand(True)
        self.drawing_area.set_vexpand(True)
        self.drawing_area.set_draw_func(self._draw_time)

        main_box.append(header_bar)
        main_box.append(self.drawing_area)
        self.set_child(main_box)

        GLib.timeout_add(100, self._update_clock)
        self.apply_colors()

    def _create_header_bar(self) -> Gtk.HeaderBar:
        header_bar = Gtk.HeaderBar()
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")

        menu_model = Gio.Menu.new()

        transparency_section = Gio.Menu.new()
        transparency_section.append("Transparency", "app.transparency")
        menu_model.append_section(None, transparency_section)

        colors_section = Gio.Menu.new()
        colors_section.append("Background Color", "app.bg_color")
        colors_section.append("Text Color", "app.text_color")
        colors_section.append("Padding", "app.padding")
        colors_section.append("Time Format", "app.time_format")
        menu_model.append_section(None, colors_section)

        reset_section = Gio.Menu.new()
        reset_section.append("Reset", "app.reset")
        menu_model.append_section(None, reset_section)

        menu_button.set_menu_model(menu_model)
        header_bar.pack_end(menu_button)

        return header_bar

    def load_settings(self):
        config_file = os.path.expanduser("~/.config/clockgtk/config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, "r") as f:
                    config = json.load(f)
                    self.bg_alpha = config.get("bg_alpha", self.bg_alpha)
                    self.bg_color = config.get("bg_color", self.bg_color)
                    self.text_color = config.get("text_color", self.text_color)
                    self.padding = config.get("padding", self.padding)
                    self.time_format = config.get("time_format", self.time_format)
            except Exception:
                pass

    def save_settings(self):
        config_file = os.path.expanduser("~/.config/clockgtk/config.json")
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        try:
            with open(config_file, "w") as f:
                json.dump(
                    {
                        "bg_alpha": self.bg_alpha,
                        "bg_color": self.bg_color,
                        "text_color": self.text_color,
                        "padding": self.padding,
                        "time_format": self.time_format,
                    },
                    f,
                    indent=2,
                )
        except Exception:
            pass

    def apply_colors(self):
        css_provider = Gtk.CssProvider()
        css_code = """
        window {
            background-color: transparent;
        }
        headerbar {
            background-color: transparent;
        }
        """
        css_provider.load_from_data(css_code.encode())

        context = self.get_style_context()
        context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.drawing_area.queue_draw()

    def _update_clock(self) -> bool:
        self.drawing_area.queue_draw()
        return True

    def _draw_time(self, drawing_area, cr, width: float, height: float):
        now = datetime.now()
        try:
            time_str = now.strftime(self.time_format)
            if "%f" in self.time_format or "%ms" in self.time_format:
                milliseconds = now.microsecond // 1000
                time_str = time_str.replace(now.strftime("%f"), f"{milliseconds:03d}")
                time_str = time_str.replace("%ms", f"{milliseconds:03d}")
        except ValueError:
            time_str = now.strftime("%H:%M:%S")

        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip("#")
            return tuple(int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4))

        bg_r, bg_g, bg_b = hex_to_rgb(self.bg_color)
        text_r, text_g, text_b = hex_to_rgb(self.text_color)

        cr.set_source_rgba(bg_r, bg_g, bg_b, self.bg_alpha)
        cr.paint()

        available_width = width - (2 * self.padding)
        available_height = height - (2 * self.padding)

        test_datetime = datetime(2023, 12, 25, 23, 59, 59, 999000)
        try:
            test_str = test_datetime.strftime(self.time_format)
            if "%f" in self.time_format:
                test_str = test_str.replace("999000", "999")
            if "%ms" in self.time_format:
                test_str = test_str.replace("%ms", "999")
        except ValueError:
            test_str = "88:88:88"

        font_size = int(min(available_width, available_height) * 0.8)

        while font_size > 10:
            cr.set_font_size(font_size)
            extents = cr.text_extents(test_str)

            if (
                extents.width <= available_width * 0.95
                and extents.height <= available_height * 0.95
            ):
                break

            font_size -= 10

        extents = cr.text_extents(test_str)
        x = self.padding + (available_width - extents.width) / 2
        y = self.padding + (available_height + extents.height) / 2

        cr.set_source_rgb(text_r, text_g, text_b)
        cr.move_to(x, y)
        cr.show_text(time_str)

    def show_transparency_dialog(self):
        dialog = Gtk.Dialog()
        dialog.set_transient_for(self)
        dialog.set_title("Transparency")
        dialog.set_default_size(400, 150)
        dialog.set_modal(True)

        content_area = dialog.get_content_area()
        content_area.set_spacing(10)
        content_area.set_margin_top(10)
        content_area.set_margin_bottom(10)
        content_area.set_margin_start(10)
        content_area.set_margin_end(10)

        label = Gtk.Label(label="Background opacity (0% = transparent, 100% = opaque):")

        scale = Gtk.Scale()
        scale.set_range(0, 100)
        scale.set_value(self.bg_alpha * 100)
        scale.set_draw_value(True)
        scale.set_hexpand(True)

        content_area.append(label)
        content_area.append(scale)

        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("OK", Gtk.ResponseType.OK)
        dialog.connect("response", self._on_transparency_response, scale)
        dialog.present()

    def _on_transparency_response(self, dialog, response_id, scale):
        if response_id == Gtk.ResponseType.OK:
            self.bg_alpha = scale.get_value() / 100.0
            self.apply_colors()
            self.save_settings()
        dialog.close()

    def show_color_chooser(self, color_type: str):
        dialog = Gtk.ColorChooserDialog()
        dialog.set_transient_for(self)
        dialog.set_modal(True)

        if color_type == "bg":
            dialog.set_title("Choose background color")
            current_color = self.bg_color
        else:
            dialog.set_title("Choose text color")
            current_color = self.text_color

        hex_color = current_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        rgba = Gdk.RGBA()
        rgba.red = r / 255.0
        rgba.green = g / 255.0
        rgba.blue = b / 255.0
        rgba.alpha = 1.0

        dialog.set_rgba(rgba)
        dialog.connect("response", self._on_color_response, color_type)
        dialog.present()

    def _on_color_response(self, dialog, response_id, color_type):
        if response_id == Gtk.ResponseType.OK:
            rgba = dialog.get_rgba()
            hex_color = "#{:02x}{:02x}{:02x}".format(
                int(rgba.red * 255), int(rgba.green * 255), int(rgba.blue * 255)
            )

            if color_type == "bg":
                self.bg_color = hex_color
            else:
                self.text_color = hex_color

            self.apply_colors()
            self.save_settings()

        dialog.close()

    def show_padding_dialog(self):
        dialog = Gtk.Dialog()
        dialog.set_transient_for(self)
        dialog.set_title("Padding")
        dialog.set_default_size(400, 150)
        dialog.set_modal(True)

        content_area = dialog.get_content_area()
        content_area.set_spacing(10)
        content_area.set_margin_top(10)
        content_area.set_margin_bottom(10)
        content_area.set_margin_start(10)
        content_area.set_margin_end(10)

        label = Gtk.Label(label="Padding around text (pixels):")

        scale = Gtk.Scale()
        scale.set_range(0, 100)
        scale.set_value(self.padding)
        scale.set_draw_value(True)
        scale.set_hexpand(True)

        content_area.append(label)
        content_area.append(scale)

        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("OK", Gtk.ResponseType.OK)
        dialog.connect("response", self._on_padding_response, scale)
        dialog.present()

    def _on_padding_response(self, dialog, response_id, scale):
        if response_id == Gtk.ResponseType.OK:
            self.padding = int(scale.get_value())
            self.apply_colors()
            self.save_settings()
        dialog.close()

    def show_time_format_dialog(self):
        dialog = Gtk.Dialog()
        dialog.set_transient_for(self)
        dialog.set_title("Time Format")
        dialog.set_default_size(500, 200)
        dialog.set_modal(True)

        content_area = dialog.get_content_area()
        content_area.set_spacing(10)
        content_area.set_margin_top(10)
        content_area.set_margin_bottom(10)
        content_area.set_margin_start(10)
        content_area.set_margin_end(10)

        label = Gtk.Label(label="Format string (e.g., %H:%M:%S, %I:%M:%S %p):")
        label.set_wrap(True)

        entry = Gtk.Entry()
        entry.set_text(self.time_format)
        entry.set_hexpand(True)

        examples = Gtk.Label(
            label="Examples: %H:%M:%S, %H:%M:%S:%ms (with milliseconds), %I:%M:%S %p (12h format)"
        )
        examples.set_wrap(True)
        examples.set_margin_top(5)

        content_area.append(label)
        content_area.append(entry)
        content_area.append(examples)

        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("OK", Gtk.ResponseType.OK)

        dialog.connect("response", self._on_time_format_response, entry)
        dialog.present()

    def _on_time_format_response(self, dialog, response_id, entry):
        if response_id == Gtk.ResponseType.OK:
            new_format = entry.get_text().strip()
            if new_format:
                try:
                    datetime.now().strftime(new_format)
                    self.time_format = new_format
                    self.apply_colors()
                    self.save_settings()
                except ValueError:
                    error_dialog = Gtk.MessageDialog()
                    error_dialog.set_transient_for(self)
                    error_dialog.set_message_type(Gtk.MessageType.ERROR)
                    error_dialog.set_text("Invalid format")
                    error_dialog.format_secondary_text(
                        "Please check your format string"
                    )
                    error_dialog.add_button("OK", Gtk.ResponseType.OK)
                    error_dialog.connect("response", lambda d, r: d.close())
                    error_dialog.present()
        dialog.close()


class ClockApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.clock")
        self.connect("activate", self._on_activate)
        self._setup_actions()

    def _setup_actions(self):
        actions = {
            "transparency": self._on_transparency_action,
            "bg_color": self._on_bg_color_action,
            "text_color": self._on_text_color_action,
            "padding": self._on_padding_action,
            "time_format": self._on_time_format_action,
            "reset": self._on_reset_action,
        }

        for action_name, callback in actions.items():
            action = Gio.SimpleAction.new(action_name, None)
            action.connect("activate", callback)
            self.add_action(action)

    def _on_activate(self, app):
        self.window = ClockApp(app)
        self.window.present()

    def _on_transparency_action(self, action, param):
        self.window.show_transparency_dialog()

    def _on_bg_color_action(self, action, param):
        self.window.show_color_chooser("bg")

    def _on_text_color_action(self, action, param):
        self.window.show_color_chooser("text")

    def _on_padding_action(self, action, param):
        self.window.show_padding_dialog()

    def _on_time_format_action(self, action, param):
        self.window.show_time_format_dialog()

    def _on_reset_action(self, action, param):
        self.window.bg_alpha = 0.7
        self.window.bg_color = "#1a1a1a"
        self.window.text_color = "#ffffff"
        self.window.padding = 20
        self.window.time_format = "%H:%M:%S"
        self.window.apply_colors()
        self.window.save_settings()


if __name__ == "__main__":
    app = ClockApplication()
    app.run(None)
