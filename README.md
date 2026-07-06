# IP Location

<p align="center">
  <strong>Language:</strong>
  <a href="README.md">English</a>
  |
  <a href="README.ru.md">Русский</a>
</p>

Desktop application for looking up an IP address location with a PySide6 interface styled with the Catppuccin Mocha palette.

The app detects the current public IP on startup, sends it to `ipgeolocationio`, and displays location, timezone, ISP, organization, coordinates, and a country flag when available.

## Requirements

- Python 3.10 or newer
- Internet access
- An `ipgeolocationio` API key
- System support for Qt/PySide6 desktop windows

Python dependencies:

```bash
pip install PySide6 ipgeolocation
```

If your system has multiple Python versions, use the matching launcher:

```bash
python -m pip install PySide6 ipgeolocation
```

On Linux, make sure a desktop session and Qt platform dependencies are available. On minimal server images, PySide6 may need additional system packages for X11 or Wayland.

## Configuration

Create a local `.env` file from the example:

Windows PowerShell:

```powershell
Copy-Item example.env .env
```

macOS / Linux:

```bash
cp example.env .env
```

Then open `.env` and set your API key:

```env
IPGEOLOCATION_API_KEY=your_api_key_here
CURRENT_IP_ENDPOINT=https://api.ipify.org
FLAG_IMAGE_ENDPOINT_TEMPLATE=https://flagcdn.com/w80/{country_code}.png
```

Variables:

- `IPGEOLOCATION_API_KEY`: required API key for `ipgeolocationio`.
- `CURRENT_IP_ENDPOINT`: endpoint used to detect the current public IP.
- `FLAG_IMAGE_ENDPOINT_TEMPLATE`: PNG flag URL template. `{country_code}` is replaced with the lower-case ISO country code.

Keep `.env` private. It contains your API key and should not be committed.

## Run

From the project directory:

```bash
python main.py
```

Windows PowerShell:

```powershell
python .\main.py
```

macOS / Linux:

```bash
python3 main.py
```

## Cross-Platform Notes

Windows:

- If `python` opens Microsoft Store or fails to run, install Python from python.org and enable "Add Python to PATH".
- PySide6 uses native Qt windows, so no extra browser or web server is required.

macOS:

- If using Homebrew Python, install dependencies with `python3 -m pip install PySide6 ipgeolocation`.
- On Apple Silicon, use packages installed for the same architecture as your Python interpreter.

Linux:

- Run from a graphical desktop session.
- For Wayland/X11 issues, install the Qt platform packages provided by your distribution.
- If the app cannot start because the `xcb` plugin is missing, install the common XCB runtime libraries for your distro.

## Project Files

- `main.py`: application logic, API calls, PySide6 widgets, and `.env` loading.
- `style.qss`: Qt stylesheet with Catppuccin Mocha color placeholders.
- `example.env`: configuration template.
- `.env`: local private configuration.

## Troubleshooting

`Set IPGEOLOCATION_API_KEY in .env.`

The `.env` file is missing or `IPGEOLOCATION_API_KEY` is empty.

`Set CURRENT_IP_ENDPOINT in .env.`

The endpoint for current public IP detection is missing.

Flag does not appear:

- Check internet access to the domain in `FLAG_IMAGE_ENDPOINT_TEMPLATE`.
- Make sure the geolocation API response includes a two-letter country code.

Location is inaccurate:

IP geolocation is approximate and depends on provider registry data. VPNs, proxies, mobile networks, and corporate networks can affect the result.
