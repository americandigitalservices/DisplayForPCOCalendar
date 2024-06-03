# DisplayForPCOCalendar

![Screenshot 2024-06-03 at 1 26 57 PM (2)](images/sample.png)

## Purpose

	Displays calendar events from Planning Center Online (PCO) on a TV using Python and your API keys.

## Code Flow

The Planning Center Calendar has tags for Types that must be added to every event. 

1. The PCO calendar display loads events using your API key:
	* When the 'RegularEvents' tag (use the ID) is selected, the code will only display events in the next 14 days. 
	* When the 'AlwaysShow' tag (use the ID) is selected, these events will show first in the rotation and allow for any dates.
2. The Code looks for an image attachment, and if it finds one, it builds the image and adds it to the image's path.
3. Pygame and PIL are used to lay out and display the images.

## Setup

*Requires Python 3*

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment:**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Install the requirements:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the Script:**
   ```bash
   python main.py
   ```

## TODO:

	+ Add more details to readme.md
		+ Config
		+ PCO Developer instructions
	+ Detect if the image is not in the configured format (details to 16x9) or below the minimum size (defaults to 1920x1080) and ignore or provide an error message.
	+ Update the "AlwaysShow" tagID selection to provide for a date limit (months??)
	+ Add complete error Handling

