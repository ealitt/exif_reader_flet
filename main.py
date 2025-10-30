import flet as ft
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import piexif
import base64
import io
import os


class ExifReaderApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "EXIF Metadata Reader"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 20

        # Image display
        self.image_display = ft.Image(
            width=500,
            height=500,
            fit=ft.ImageFit.CONTAIN,
            visible=False
        )

        # Metadata display
        self.metadata_column = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=5
        )

        # Placeholder area when no image is loaded
        self.placeholder_area = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.IMAGE_OUTLINED, size=100, color=ft.Colors.GREY_400),
                    ft.Text(
                        "No image loaded",
                        size=20,
                        color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        "Click the button below to select an image",
                        size=14,
                        color=ft.Colors.GREY_500,
                        text_align=ft.TextAlign.CENTER
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=15
            ),
            width=500,
            height=500,
            border=ft.border.all(2, ft.Colors.GREY_300),
            border_radius=10,
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.GREY_50,
        )

        # File picker button
        self.pick_file_button = ft.ElevatedButton(
            text="Choose Image File",
            icon=ft.Icons.FOLDER_OPEN,
            on_click=lambda _: self.file_picker.pick_files(
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["jpg", "jpeg", "png", "tiff", "tif", "bmp", "gif", "webp"]
            ),
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_700,
            )
        )

        # File picker
        self.file_picker = ft.FilePicker(on_result=self.on_file_picked)
        self.page.overlay.append(self.file_picker)
        self.page.update()  # Important: update page after adding to overlay

        # Current file info
        self.file_info_text = ft.Text(
            "",
            size=12,
            color=ft.Colors.GREY_700,
            weight=ft.FontWeight.BOLD,
            visible=False
        )

        self.setup_ui()

    def setup_ui(self):
        # Left side - Image display area
        left_side = ft.Container(
            content=ft.Column(
                [
                    ft.Stack(
                        [
                            self.placeholder_area,
                            self.image_display,
                        ]
                    ),
                    ft.Container(height=10),
                    self.pick_file_button,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=500,
        )

        # Right side - Metadata display
        right_side = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Image Metadata",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_900
                    ),
                    self.file_info_text,
                    ft.Divider(height=20, color=ft.Colors.BLUE_200),
                    self.metadata_column,
                ],
                spacing=10,
                expand=True
            ),
            expand=True,
            padding=20,
            bgcolor=ft.Colors.GREY_100,
            border_radius=10,
        )

        # Main layout
        main_row = ft.Row(
            [
                left_side,
                ft.VerticalDivider(width=20),
                right_side,
            ],
            expand=True,
            spacing=20,
        )

        self.page.add(main_row)

    def on_file_picked(self, e: ft.FilePickerResultEvent):
        if e.files:
            file_path = e.files[0].path
            self.load_image(file_path)

    def load_image(self, file_path: str):
        try:
            # Read the image
            with open(file_path, 'rb') as f:
                img_bytes = f.read()

            # Display the image
            img = Image.open(io.BytesIO(img_bytes))

            # Convert image to base64 for display
            buffered = io.BytesIO()
            # Convert to RGB if necessary for display
            if img.mode in ('RGBA', 'LA', 'P'):
                display_img = img.convert('RGB')
            elif img.mode == 'I;16':
                # Handle 16-bit images
                display_img = img.point(lambda i: i * (1 / 256)).convert('RGB')
            else:
                display_img = img

            display_img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            self.image_display.src_base64 = img_str
            self.image_display.visible = True
            self.placeholder_area.visible = False

            # Update file info
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            file_size_kb = file_size / 1024
            self.file_info_text.value = f"File: {file_name} | Size: {file_size_kb:.2f} KB | Format: {img.format} | Mode: {img.mode} | Dimensions: {img.width}x{img.height}"
            self.file_info_text.visible = True

            # Extract and display metadata
            self.extract_metadata(img, file_path)

            self.page.update()

        except Exception as e:
            self.show_error(f"Error loading image: {str(e)}")

    def extract_metadata(self, img: Image.Image, file_path: str):
        self.metadata_column.controls.clear()
        metadata = {}

        try:
            # Try to get EXIF data using PIL
            exif_data = img._getexif()

            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)

                    # Handle GPS data specially
                    if tag == "GPSInfo":
                        gps_data = {}
                        for gps_tag_id, gps_value in value.items():
                            gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                            gps_data[gps_tag] = gps_value
                        metadata[tag] = gps_data
                    else:
                        metadata[tag] = value
        except (AttributeError, KeyError):
            pass

        # Try piexif for additional EXIF data (especially for TIFF)
        try:
            exif_dict = piexif.load(file_path)

            for ifd_name in exif_dict:
                if ifd_name == "thumbnail":
                    continue

                ifd = exif_dict[ifd_name]
                if not ifd:
                    continue

                for tag_id, value in ifd.items():
                    tag_name = piexif.TAGS[ifd_name].get(tag_id, {}).get("name", f"Tag_{tag_id}")

                    # Skip if already added from PIL
                    if tag_name not in metadata:
                        metadata[tag_name] = value
        except Exception:
            pass

        # Add PIL info metadata
        if hasattr(img, 'info') and img.info:
            for key, value in img.info.items():
                if key not in metadata and key != 'exif':
                    metadata[key] = value

        # Display metadata
        if metadata:
            self.display_metadata(metadata)
        else:
            self.metadata_column.controls.append(
                ft.Text(
                    "No metadata found in this image.",
                    size=14,
                    color=ft.Colors.GREY_600,
                    italic=True
                )
            )

        self.page.update()

    def display_metadata(self, metadata: dict):
        for key, value in sorted(metadata.items()):
            # Skip empty or meaningless values
            if value is None or value == "" or value == b"":
                continue

            # Format the value
            formatted_value = self.format_metadata_value(value)

            # Skip if still empty after formatting
            if not formatted_value or formatted_value == "None":
                continue

            # Create metadata entry
            entry = ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            str(key),
                            size=13,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_800
                        ),
                        ft.Text(
                            formatted_value,
                            size=12,
                            color=ft.Colors.GREY_900,
                            selectable=True
                        ),
                    ],
                    spacing=3
                ),
                padding=10,
                bgcolor=ft.Colors.WHITE,
                border_radius=5,
                border=ft.border.all(1, ft.Colors.GREY_300)
            )

            self.metadata_column.controls.append(entry)

    def format_metadata_value(self, value):
        """Format metadata value for display"""
        # Handle bytes
        if isinstance(value, bytes):
            try:
                # Try to decode as UTF-8
                decoded = value.decode('utf-8', errors='ignore').strip()
                if decoded and decoded.isprintable():
                    return decoded
                # If not printable, show hex for short values
                if len(value) <= 32:
                    return f"0x{value.hex()}"
                return f"<binary data, {len(value)} bytes>"
            except Exception:
                return f"<binary data, {len(value)} bytes>"

        # Handle tuples (common in EXIF, e.g., rational numbers)
        elif isinstance(value, tuple):
            if len(value) == 2 and isinstance(value[0], int) and isinstance(value[1], int):
                # Rational number
                if value[1] != 0:
                    return f"{value[0]}/{value[1]} ({value[0]/value[1]:.4f})"
                return f"{value[0]}/{value[1]}"
            return str(value)

        # Handle dictionaries (like GPS data)
        elif isinstance(value, dict):
            formatted_items = []
            for k, v in value.items():
                formatted_v = self.format_metadata_value(v)
                formatted_items.append(f"  {k}: {formatted_v}")
            return "\n".join(formatted_items)

        # Handle lists
        elif isinstance(value, list):
            if len(value) == 0:
                return None
            if len(value) <= 5:
                return ", ".join(str(v) for v in value)
            return f"[{len(value)} items]"

        # Handle regular values
        else:
            str_value = str(value)
            # Truncate very long values
            if len(str_value) > 200:
                return str_value[:200] + "..."
            return str_value

    def show_error(self, message: str):
        dialog = ft.AlertDialog(
            title=ft.Text("Error"),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=lambda _: self.page.close(dialog))
            ]
        )
        self.page.open(dialog)


def main(page: ft.Page):
    ExifReaderApp(page)


if __name__ == "__main__":
    ft.app(target=main)