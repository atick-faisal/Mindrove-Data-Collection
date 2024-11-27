# EEG Data Collection with Slideshow

This application is designed to collect EEG data using a MindRove device while presenting a sequence of visual stimuli in a controlled slideshow format. It synchronizes the EEG data collection with visual stimuli presentation and saves both the EEG data and trigger timestamps.

![Screenshot from 2024-11-24 20-19-49](https://github.com/user-attachments/assets/a98f783e-0955-4cad-b41b-7200a22f012d)

## Installation

### Prerequisites

0. Mindrove Headset
1. Python 3.8 or higher
3. Pip (Python package installer)

### Required Python Packages

Install the required packages using pip:

```bash
pip install pillow pandas numpy mindrove
```

### Directory Structure

Create the following directory structure for the project:

```
project_directory/
│
├── main.py            # Main program file
├── data/             # Directory for saved data (created automatically)
├── images/           # Directory containing stimulus images
│   ├── up.webp
│   ├── down.webp
│   ├── select.webp
│   └── cancel.webp
```

### Image Requirements

Place your stimulus images in the `images/` directory. The default code expects:
- up.webp
- down.webp
- select.webp
- cancel.webp

Images can be in any common format (webp, jpg, png), but make sure to update the file extensions in the code if you use different formats.

## Running the Program

1. Connect your MindRove device and ensure it's properly set up.

2. Navigate to the project directory:
```bash
cd path/to/project_directory
```

3. Run the program:
```bash
python main.py
```

## Program Flow

1. **Initial Setup**
   - Enter subject name (defaults to "unnamed")
   - Configure timing parameters:
     - Concentration Duration (default: 500ms)
     - Image Duration (default: 1000ms)
     - Action Duration (default: 2500ms)
     - Relax Duration (default: 1000ms)
     - Rest Duration (default: 1000ms)
   - Set number of repetitions

2. **Slideshow Sequence**
   For each slide:
   1. Concentration phase (green circle)
   2. Image presentation (stimulus + text)
   3. Action phase (white circle)
   4. Relax phase (red circle)
   5. Rest phase (blank screen)

3. **Data Collection**
   - EEG data is continuously collected during the session
   - Trigger timestamps are recorded for each phase transition
   - Data is saved automatically when the session ends

## Output Files

The program generates two CSV files in the `data/` directory:

1. `<subject_name>_<timestamp>.csv`
   - Contains raw EEG data
   - Includes channels CH1-CH8
   - Includes accelerometer data (ACCx, ACCy, ACCz)

2. `<subject_name>_triggers_<timestamp>.csv`
   - Contains trigger timing information
   - Records timestamps for each stage transition
   - Includes slide information for the image presentation phase

## Important Notes

1. The program runs in fullscreen mode
2. There is a 5-second delay before the slideshow starts
3. Make sure the MindRove device is properly connected before starting
4. The program will automatically create the `data` directory if it doesn't exist
5. All data files use timestamps in the format `dd_mm_yy_hh_mm_ss`

## Troubleshooting

1. **MindRove Connection Issues**
   - Ensure the device is properly connected
   - Check that the MindRove SDK is properly installed
   - Verify the device is powered on and has sufficient battery

2. **Image Loading Issues**
   - Verify that all required images are in the `images/` directory
   - Check image file names and extensions match the code
   - Ensure images are in a supported format

3. **Data Saving Issues**
   - Check write permissions for the `data/` directory
   - Ensure sufficient disk space
   - Verify no other program is locking the output files

## Support

For issues related to:
- MindRove hardware/SDK: Contact MindRove support
- Program bugs/features: Create an issue in the project repository

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

<p align="center"><img src="https://raw.githubusercontent.com/catppuccin/catppuccin/main/assets/footers/gray0_ctp_on_line.svg?sanitize=true" /></p>
<p align="center"><a href="https://sites.google.com/view/mchowdhury" target="_blank">Qatar University Machine Learning Group</a>
<p align="center"><a href="https://github.com/atick-faisal/Jetpack-Compose-Starter/blob/main/LICENSE"><img src="https://img.shields.io/static/v1.svg?style=for-the-badge&label=License&message=MIT&logoColor=d9e0ee&colorA=363a4f&colorB=b7bdf8"/></a></p>
