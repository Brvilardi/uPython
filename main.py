import time
from upython.SevenSegmentDisplay.SSD_5011BS import SSD_5011BS


display = SSD_5011BS(common_cathode=False)


for i in range(10):
    display.set_number(i)
    time.sleep(1)



# Turn the LED off

