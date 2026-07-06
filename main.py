import os
import sys
from dataclasses import dataclass
from ipaddress import ip_address as validate_ip_address
from urllib.request import urlopen

from ipgeolocation import (
    IpGeolocationClient,
    IpGeolocationClientConfig,
    LookupIpGeolocationRequest,
)
from PySide6.QtCore import QObject, QRunnable, QSize, Qt, QThreadPool, Signal, Slot
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


ENV_FILE = ".env"
STYLE_FILE = "style.qss"
API_KEY_ENV_NAME = "IPGEOLOCATION_API_KEY"
CURRENT_IP_ENDPOINT_ENV_NAME = "CURRENT_IP_ENDPOINT"
FLAG_IMAGE_ENDPOINT_TEMPLATE_ENV_NAME = "FLAG_IMAGE_ENDPOINT_TEMPLATE"


class Mocha:
    rosewater = "#f5e0dc"
    flamingo = "#f2cdcd"
    pink = "#f5c2e7"
    mauve = "#cba6f7"
    red = "#f38ba8"
    peach = "#fab387"
    yellow = "#f9e2af"
    green = "#a6e3a1"
    teal = "#94e2d5"
    sky = "#89dceb"
    sapphire = "#74c7ec"
    blue = "#89b4fa"
    lavender = "#b4befe"
    text = "#cdd6f4"
    subtext1 = "#bac2de"
    subtext0 = "#a6adc8"
    overlay1 = "#7f849c"
    surface2 = "#585b70"
    surface1 = "#45475a"
    surface0 = "#313244"
    base = "#1e1e2e"
    mantle = "#181825"
    crust = "#11111b"


@dataclass
class LocationResult:
    ip: str
    country: str
    country_code: str
    flag_image: bytes | None
    region: str
    city: str
    latitude: str
    longitude: str
    timezone: str
    isp: str
    organization: str


class LookupSignals(QObject):
    finished = Signal(object)
    failed = Signal(str)


class LookupWorker(QRunnable):
    def __init__(self, ip_address: str | None = None):
        super().__init__()
        self.ip_address = ip_address
        self.signals = LookupSignals()

    @Slot()
    def run(self):
        try:
            api_key = get_api_key()
            target_ip = self.ip_address or resolve_current_public_ip()
            config = IpGeolocationClientConfig(api_key=api_key)
            with IpGeolocationClient(config) as client:
                response = client.lookup_ip_geolocation(
                    LookupIpGeolocationRequest(ip=target_ip)
                )
            result = parse_response(response.data)
            result.flag_image = fetch_flag_image(result.country_code)
            self.signals.finished.emit(result)
        except Exception as exc:
            self.signals.failed.emit(str(exc))


def load_env_file(path: str = ENV_FILE):
    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            name = name.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(name, value)


def app_path(filename: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


def get_api_key() -> str:
    api_key = os.getenv(API_KEY_ENV_NAME, "").strip()
    if not api_key:
        raise RuntimeError(f"Set {API_KEY_ENV_NAME} in {ENV_FILE}.")
    return api_key


def get_current_ip_endpoint() -> str:
    endpoint = os.getenv(CURRENT_IP_ENDPOINT_ENV_NAME, "").strip()
    if not endpoint:
        raise RuntimeError(f"Set {CURRENT_IP_ENDPOINT_ENV_NAME} in {ENV_FILE}.")
    return endpoint


def get_flag_image_endpoint_template() -> str:
    return os.getenv(FLAG_IMAGE_ENDPOINT_TEMPLATE_ENV_NAME, "").strip()


def resolve_current_public_ip() -> str:
    with urlopen(get_current_ip_endpoint(), timeout=8) as response:
        current_ip = response.read().decode("utf-8").strip()
    validate_ip_address(current_ip)
    return current_ip


def nested_value(source, path, default="Not available"):
    value = source
    for name in path:
        if value is None:
            return default
        value = getattr(value, name, None)
    if value in (None, ""):
        return default
    return str(value)


def first_nested_value(source, paths, default="Not available"):
    for path in paths:
        value = nested_value(source, path, default="")
        if value:
            return value
    return default


def is_country_code(country_code: str) -> bool:
    code = country_code.strip().upper()
    return len(code) == 2 and code.isalpha()


def fetch_flag_image(country_code: str) -> bytes | None:
    if not is_country_code(country_code):
        return None

    endpoint_template = get_flag_image_endpoint_template()
    if not endpoint_template:
        return None

    flag_url = endpoint_template.format(country_code=country_code.lower())
    try:
        with urlopen(flag_url, timeout=8) as response:
            return response.read()
    except Exception:
        return None


def format_country(country: str) -> str:
    if country == "Not available":
        return "Not available"
    return country


def parse_response(data) -> LocationResult:
    country_code = first_nested_value(
        data,
        [
            ["location", "country_code2"],
            ["location", "country_code"],
            ["location", "country_iso_code"],
            ["location", "country_iso_code2"],
        ],
    )
    return LocationResult(
        ip=nested_value(data, ["ip"]),
        country=nested_value(data, ["location", "country_name"]),
        country_code=country_code,
        flag_image=None,
        region=nested_value(data, ["location", "state_prov"]),
        city=nested_value(data, ["location", "city"]),
        latitude=nested_value(data, ["location", "latitude"]),
        longitude=nested_value(data, ["location", "longitude"]),
        timezone=nested_value(data, ["time_zone", "name"]),
        isp=nested_value(data, ["isp"]),
        organization=nested_value(data, ["organization"]),
    )


def format_coordinates(latitude: str, longitude: str) -> str:
    if latitude == "Not available" or longitude == "Not available":
        return "Not available"
    return f"{latitude}, {longitude}"


def load_stylesheet(path: str = STYLE_FILE) -> str:
    with open(app_path(path), "r", encoding="utf-8") as style_file:
        stylesheet = style_file.read()
    colors = {
        name: value
        for name, value in vars(Mocha).items()
        if not name.startswith("_") and isinstance(value, str)
    }
    for name, value in colors.items():
        stylesheet = stylesheet.replace(f"{{{name}}}", value)
    return stylesheet


class InfoCard(QFrame):
    def __init__(self, title: str, accent: str):
        super().__init__()
        self.setObjectName("InfoCard")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        accent_line = QFrame()
        accent_line.setObjectName("AccentLine")
        accent_line.setStyleSheet(f"background-color: {accent};")
        accent_line.setFixedWidth(4)

        self.title_label = QLabel(title.upper())
        self.title_label.setObjectName("CardTitle")

        self.value_label = QLabel("Not available")
        self.value_label.setObjectName("CardValue")
        self.value_label.setWordWrap(True)

        self.icon_label = QLabel()
        self.icon_label.setObjectName("FlagImage")
        self.icon_label.setFixedSize(QSize(34, 24))
        self.icon_label.setScaledContents(False)
        self.icon_label.hide()

        value_row = QHBoxLayout()
        value_row.setContentsMargins(0, 0, 0, 0)
        value_row.setSpacing(10)
        value_row.addWidget(self.icon_label, 0, Qt.AlignmentFlag.AlignTop)
        value_row.addWidget(self.value_label, 1)

        content = QVBoxLayout()
        content.setContentsMargins(14, 13, 14, 13)
        content.setSpacing(5)
        content.addWidget(self.title_label)
        content.addLayout(value_row)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(accent_line)
        layout.addLayout(content)

    def set_value(self, value: str):
        self.value_label.setText(value or "Not available")

    def set_icon_image(self, image_data: bytes | None):
        if not image_data:
            self.icon_label.clear()
            self.icon_label.hide()
            return

        pixmap = QPixmap()
        if not pixmap.loadFromData(image_data):
            self.icon_label.clear()
            self.icon_label.hide()
            return

        self.icon_label.setPixmap(
            pixmap.scaled(
                self.icon_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        self.icon_label.show()


class IpLocationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.thread_pool = QThreadPool.globalInstance()
        self.cards = {}

        self.setWindowTitle("IP Location")
        self.setMinimumSize(520, 840)
        self.resize(980, 860)

        self.setCentralWidget(self.build_ui())
        self.apply_styles()
        self.lookup_current_ip()

    def build_ui(self):
        root = QWidget()
        root.setObjectName("Root")

        page = QVBoxLayout(root)
        page.setContentsMargins(34, 30, 34, 30)
        page.setSpacing(22)

        top_row = QHBoxLayout()
        top_row.setSpacing(16)

        title_block = QVBoxLayout()
        title_block.setSpacing(6)

        eyebrow = QLabel("IP GEOLOCATION")
        eyebrow.setObjectName("Eyebrow")

        title = QLabel("Location Lookup")
        title.setObjectName("Title")

        subtitle = QLabel("Enter an IP address and inspect its approximate geographic and network profile.")
        subtitle.setObjectName("Subtitle")
        subtitle.setWordWrap(True)

        title_block.addWidget(eyebrow)
        title_block.addWidget(title)
        title_block.addWidget(subtitle)

        self.status_badge = QLabel("Ready")
        self.status_badge.setObjectName("StatusBadge")
        self.status_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        top_row.addLayout(title_block, 1)
        top_row.addWidget(self.status_badge, 0, Qt.AlignmentFlag.AlignTop)

        search_panel = QFrame()
        search_panel.setObjectName("SearchPanel")

        search_layout = QHBoxLayout(search_panel)
        search_layout.setContentsMargins(16, 16, 16, 16)
        search_layout.setSpacing(12)

        input_wrap = QVBoxLayout()
        input_wrap.setSpacing(7)

        input_label = QLabel("IP address")
        input_label.setObjectName("InputLabel")

        self.ip_input = QLineEdit()
        self.ip_input.setObjectName("IpInput")
        self.ip_input.setPlaceholderText("Current public IP is detected automatically")
        self.ip_input.returnPressed.connect(self.submit_lookup)

        input_wrap.addWidget(input_label)
        input_wrap.addWidget(self.ip_input)

        self.lookup_button = QPushButton("Search")
        self.lookup_button.setObjectName("PrimaryButton")
        self.lookup_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lookup_button.clicked.connect(self.submit_lookup)

        search_layout.addLayout(input_wrap, 1)
        search_layout.addWidget(self.lookup_button, 0, Qt.AlignmentFlag.AlignBottom)

        hero = QFrame()
        hero.setObjectName("HeroResult")

        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(22, 20, 22, 20)
        hero_layout.setSpacing(8)

        hero_caption = QLabel("CURRENT RESULT")
        hero_caption.setObjectName("HeroCaption")

        self.ip_result = QLabel("Waiting for lookup")
        self.ip_result.setObjectName("IpResult")
        self.ip_result.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self.location_summary = QLabel("Search an address to see its approximate location.")
        self.location_summary.setObjectName("LocationSummary")
        self.location_summary.setWordWrap(True)

        hero_layout.addWidget(hero_caption)
        hero_layout.addWidget(self.ip_result)
        hero_layout.addWidget(self.location_summary)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)

        card_specs = [
            ("country", "Country", Mocha.green),
            ("city", "City", Mocha.sky),
            ("region", "Region", Mocha.lavender),
            ("timezone", "Timezone", Mocha.yellow),
            ("coordinates", "Coordinates", Mocha.peach),
            ("isp", "ISP", Mocha.mauve),
            ("organization", "Organization", Mocha.teal),
        ]

        for index, (key, title, accent) in enumerate(card_specs):
            card = InfoCard(title, accent)
            self.cards[key] = card
            row = index // 2
            col = index % 2
            if key == "organization":
                grid.addWidget(card, row, 0, 1, 2)
            else:
                grid.addWidget(card, row, col)

        footer = QLabel(
            "Location data is approximate and depends on the provider's IP registry records."
        )
        footer.setObjectName("Footer")

        page.addLayout(top_row)
        page.addWidget(search_panel)
        page.addWidget(hero)
        page.addLayout(grid)
        page.addItem(QSpacerItem(1, 1, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        page.addWidget(footer)

        return root

    def submit_lookup(self):
        ip_address = self.ip_input.text().strip()
        if ip_address:
            self.lookup_ip(ip_address)
        else:
            self.lookup_current_ip()

    def lookup_current_ip(self):
        self.set_loading(True)
        self.ip_input.clear()
        self.ip_result.setText("Detecting...")
        self.location_summary.setText("Detecting your current public IP address...")

        worker = LookupWorker()
        worker.signals.finished.connect(self.show_result)
        worker.signals.failed.connect(self.show_error)
        self.thread_pool.start(worker)

    def lookup_ip(self, ip_address: str):
        if not ip_address:
            self.show_error("Enter an IP address before searching.")
            return
        try:
            validate_ip_address(ip_address)
        except ValueError:
            self.show_error("Enter a valid IPv4 or IPv6 address.")
            return

        self.set_loading(True)
        self.ip_result.setText(ip_address)
        self.location_summary.setText("Looking up location and network details...")

        worker = LookupWorker(ip_address)
        worker.signals.finished.connect(self.show_result)
        worker.signals.failed.connect(self.show_error)
        self.thread_pool.start(worker)

    def set_loading(self, is_loading: bool):
        self.lookup_button.setDisabled(is_loading)
        self.ip_input.setDisabled(is_loading)
        if is_loading:
            self.lookup_button.setText("Searching...")
            self.status_badge.setText("Loading")
            self.status_badge.setProperty("state", "loading")
        else:
            self.lookup_button.setText("Search")
            self.status_badge.setProperty("state", "ready")
        self.status_badge.style().unpolish(self.status_badge)
        self.status_badge.style().polish(self.status_badge)

    @Slot(object)
    def show_result(self, result: LocationResult):
        self.set_loading(False)
        self.status_badge.setText("Located")

        self.ip_input.setText(result.ip)
        self.ip_result.setText(result.ip)
        summary_parts = [part for part in [result.city, result.region, result.country] if part != "Not available"]
        self.location_summary.setText(" / ".join(summary_parts) or "No location details returned.")

        self.cards["country"].set_value(format_country(result.country))
        self.cards["country"].set_icon_image(result.flag_image)
        self.cards["city"].set_value(result.city)
        self.cards["region"].set_value(result.region)
        self.cards["timezone"].set_value(result.timezone)
        self.cards["coordinates"].set_value(format_coordinates(result.latitude, result.longitude))
        self.cards["isp"].set_value(result.isp)
        self.cards["organization"].set_value(result.organization)

    @Slot(str)
    def show_error(self, message: str):
        self.set_loading(False)
        self.status_badge.setText("Error")
        self.status_badge.setProperty("state", "error")
        self.status_badge.style().unpolish(self.status_badge)
        self.status_badge.style().polish(self.status_badge)
        self.location_summary.setText(message or "Lookup failed.")

    def apply_styles(self):
        QApplication.instance().setStyleSheet(load_stylesheet())


def main():
    load_env_file()

    app = QApplication(sys.argv)
    app.setApplicationName("IP Location")
    app.setFont(QFont("Segoe UI", 10))

    window = IpLocationWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
