# 02 Topic Summary

## Goal
Create a structured summary of all recorded topics in the MCAP bag and identify which topics are important for later analysis.

## Source
The topic list and message counts were taken from `ros2 bag info`.

## Bag Duration
269.341840121 seconds

## Method
Approximate topic frequency was calculated as:

`frequency_hz = message_count / duration_seconds`

## Output
The final topic summary table will be saved in:

`outputs/tables/topic_summary.csv`

## Command Used

```bash
python3 scripts/02_parse_metadata.py