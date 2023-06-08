import datetime
import time
# Record a previous time
previous_time = datetime.datetime.now()

# Wait for some time...
time.sleep(10)
# Fetch the current time
current_time = datetime.datetime.now()
    
# Calculate the time difference
time_difference = current_time - previous_time

new=current_time.strftime("%-d/%-m/%y %H:%M")



print(new)
# Print the time difference
print("Time Difference:", time_difference)
