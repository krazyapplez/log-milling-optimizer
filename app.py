import math
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.title("Log Milling Optimization Tool - LT35/LT37")

# Wood-Mizer LT37 throat constraints
LT37_THROAT_WIDTH = 36  # inches
LT37_THROAT_HEIGHT = 22  # inches

# User Inputs
log_diameter = st.number_input("Log Diameter (inches):", min_value=6.0, value=20.0)
log_length = st.number_input("Log Length (inches):", min_value=12.0, value=96.0)
kerf = st.number_input("Blade Kerf (inches):", min_value=0.05, value=0.125)

# Board options selector
board_choices = {
    "2x6": {"width": 6, "height": 2},
    "4x4": {"width": 4, "height": 4},
    "1x8": {"width": 8, "height": 1},
    "Live Edge Slabs": {"width": LT37_THROAT_WIDTH - 1, "height": 2}  # Live edge slabs use max throat width
}

selected_boards = st.multiselect(
    "Select board types to mill:",
    options=list(board_choices.keys()),
    default=["2x6", "4x4"]
)

# Generate board option list from selection
board_options = []
for label in selected_boards:
    dims = board_choices[label]
    board_options.append({"width": dims["width"], "height": dims["height"], "label": label})

# Optimization logic
radius = log_diameter / 2
cant_width = cant_height = radius * math.sqrt(2)
cut_plan = []
y_offset = 0

# Handle oversized logs for Live Edge Slabs
oversized_log = log_diameter > LT37_THROAT_HEIGHT and "Live Edge Slabs" in selected_boards
if oversized_log:
    st.warning("Log is taller than LT37 throat height. Consider flattening one face before slabbing.")
    cant_height = LT37_THROAT_HEIGHT  # Simulate flattening one side

while y_offset + min(b["height"] for b in board_options) <= cant_height:
    row_height = None
    x_offset = 0
    for board in board_options:
        if y_offset + board["height"] <= cant_height:
            if x_offset + board["width"] <= cant_width:
                cut_plan.append({
                    "label": board["label"],
                    "x": x_offset,
                    "y": y_offset,
                    "width": board["width"],
                    "height": board["height"]
                })
                x_offset += board["width"] + kerf
                row_height = board["height"]
    if row_height is None:
        break
    y_offset += row_height + kerf

cut_df = pd.DataFrame(cut_plan)

# Display table
st.subheader("Optimized Cut List")
st.dataframe(cut_df)

# Plot visualization
fig, ax = plt.subplots(figsize=(6, 6))
for cut in cut_plan:
    rect = patches.Rectangle(
        (cut["x"], cut["y"]),
        cut["width"],
        cut["height"]
        ,
        edgecolor='black',
        facecolor='lightgray',
        linewidth=1
    )
    ax.add_patch(rect)
    ax.text(
        cut["x"] + cut["width"] / 2,
        cut["y"] + cut["height"] / 2,
        cut["label"],
        ha='center',
        va='center',
        fontsize=8
    )

ax.set_xlim(0, cant_width)
ax.set_ylim(0, cant_height)
ax.set_aspect('equal')
ax.set_title('Cut Layout Plan')
plt.xlabel('Width (in)')
plt.ylabel('Height (in)')
plt.grid(True)
st.pyplot(fig)

# Summary
total_boards = len(cut_plan)
total_board_feet = sum((cut["width"] * cut["height"] * log_length / 144) for cut in cut_plan)

st.subheader("Yield Summary")
st.write(f"Total Boards: {total_boards}")
st.write(f"Total Board Feet: {total_board_feet:.2f} BF")
