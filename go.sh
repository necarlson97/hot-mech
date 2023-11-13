# Simple launch script
source env/bin/activate

# Regen printout whenever there are changes, run in background
(
    while inotifywait -r -e create -e delete -e modify "./" 2>/dev/null; do
        python -m src.render_templates > /dev/tty 2>&1
    done
) &
# Save the PID of the inotifywait loop
INOTIFY_PID=$!

# Run stats
python -m src.statistician

# Rejoin the inotifywait process
wait $INOTIFY_PID
