import re
import tkinter as tk
from tkinter import filedialog, messagebox

# Regex patterns for GGA and RMC sentences
GGA_REGEX = re.compile(r"\$GPGGA,(\d{2})(\d{2})(\d{2}\.\d+),(\d{2})(\d+\.\d+),([NS]),(\d{3})(\d+\.\d+),([EW]),.*?,([\d.]+),M")
RMC_REGEX = re.compile(r"\$GPRMC,(\d{2})(\d{2})(\d{2}\.\d+),A,(\d{2})(\d+\.\d+),([NS]),(\d{3})(\d+\.\d+),([EW]),([\d.]+),([\d.]+),(\d{6}),.*?")


def format_datetime(utc_hours, utc_minutes, utc_seconds, date):
    """Format datetime as YY-MM-DD_HH:MM:SSZ, return None if date is '000000'."""
    if date == "000000":
        return None  # Return None so we can filter out invalid rows

    day = date[:2]
    month = date[2:4]
    year = "20" + date[4:]  # Convert YY to YYYY
    formatted_date = f"{year}-{month}-{day}"

    formatted_time = f"{utc_hours}:{utc_minutes}:{int(float(utc_seconds))}Z"
    return f"{formatted_date}_{formatted_time}"


def convert_gps_to_custom_format(input_file, output_annotations):
    """Parses GPS log file, converts Lat/Long to decimal degrees, and saves in custom format."""
    data = []

    try:
        with open(input_file, "r") as file:
            for line in file:
                gga_match = GGA_REGEX.match(line)
                rmc_match = RMC_REGEX.match(line)

                if rmc_match:
                    h, m, s, lat_deg, lat_min, lat_dir, lon_deg, lon_min, lon_dir, speed, course, date = rmc_match.groups()
                    altitude = None  # Altitude comes from GGA

                    # Format date & time
                    formatted_datetime = format_datetime(h, m, s, date)

                    # Skip this row if the date is invalid (i.e., '000000')
                    if formatted_datetime is None:
                        continue

                    # Convert Lat/Lon to decimal degrees
                    latitude = float(lat_deg) + float(lat_min) / 60
                    if lat_dir == "S":
                        latitude = -latitude

                    longitude = float(lon_deg) + float(lon_min) / 60
                    if lon_dir == "W":
                        longitude = -longitude

                    # Store valid data
                    data.append((formatted_datetime, latitude, longitude, altitude, speed, course))

        # Write data to file
        with open(output_annotations, "w") as f:
            f.write("Annotation Container File, Version, 1.0, ROVER (64-Bit) Version: 4.24.3.500.2\n")

            for entry in data:
                formatted_datetime, lat, lon, altitude, speed, course = entry
                
                # Ensure altitude and metadata fields are properly handled
                alt_value = altitude if altitude else "10.00000000186265"
                speed_value = speed if speed else "0.0"
                course_value = course if course else "0.0"

                # First line with altitude
                f.write(f"SITE,{formatted_datetime},{lat},{lon},{alt_value},AGL,0xffffffff,,,,,-1\n")

                # Second line with metadata
                f.write(f"SITE,{formatted_datetime} (2),{lat},{lon},10.00000000186265,AGL,0xffffffff,,,,Course (°);{course_value};Speed (knots);{speed_value},-1\n")

        return f"Success! File saved as: {output_annotations}"

    except Exception as e:
        return f"Error: {str(e)}"


def select_input_file():
    """Open file dialog to select GPS log file."""
    file_path = filedialog.askopenfilename(filetypes=[("GPS Log Files", "*.txt;*.log")])
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)


def select_output_file():
    """Open file dialog to choose output .annotations file."""
    file_path = filedialog.asksaveasfilename(defaultextension=".annotations",
                                             filetypes=[("Annotations Files", "*.annotations")])
    if file_path:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, file_path)


def convert_and_save():
    """Trigger the conversion and update status."""
    input_file = file_entry.get()
    output_annotations = output_entry.get()

    if not input_file:
        messagebox.showerror("Error", "Please select a GPS log file.")
        return

    if not output_annotations:
        messagebox.showerror("Error", "Please choose an output file location.")
        return

    result = convert_gps_to_custom_format(input_file, output_annotations)
    messagebox.showinfo("Conversion Status", result)


# --- Tkinter GUI ---
root = tk.Tk()
root.title("GPS Log to .annotations Converter")
root.geometry("450x250")
root.resizable(False, False)

# File Selection
tk.Label(root, text="Select GPS Log File:").pack(pady=5)
file_entry = tk.Entry(root, width=50)
file_entry.pack(pady=5)
tk.Button(root, text="Browse", command=select_input_file).pack(pady=5)

# Output File Selection
tk.Label(root, text="Choose Output .annotations File:").pack(pady=5)
output_entry = tk.Entry(root, width=50)
output_entry.pack(pady=5)
tk.Button(root, text="Save As", command=select_output_file).pack(pady=5)

# Convert Button
tk.Button(root, text="Convert to .annotations", command=convert_and_save, bg="green", fg="white").pack(pady=15)

# Run GUI
root.mainloop()
