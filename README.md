# DisplayForPCOCalendar

## Purpose

	Displays calendar events from Planning Center Online (PCO) on a TV using Python and your API keys.

## Code Flow

The Planning Center Calendar has tags for Types that are required to be added to every event. 

1. The PCO calendar display loads events using your API key:
	* When the 'RegularEvents' tag (use the ID) is selected, the code will only display events in the next 14 days. 
	* When the 'AlwaysShow' tag (use the ID) is selected, these events will show first in the rotation and allow for any number of dates.
2. The Code looks for an image attachment, and if it finds one, it builds the image and adds it to the image's path.
3. Pygame and PIL are used to lay out the images and display them.

## TODO:

	+ Add more details to readme.md
		+ Images
		+ Config
		+ PCO Developer instructions
	+ Detect if the image is not in the configured format (details to 16x9) or below the minimum size (defaults to 1920x1080) and ignore or provide an error message.
	+ Update the "AlwaysShow" tagID selection to provide for a date limit (months??)
	+ Add complete error Handling
