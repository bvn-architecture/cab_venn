#%%
print(
    "This file makes a venn diagram of who's tagged all "
    "their trips, none of their trips, and some of their trips."
)
#%%
from matplotlib_venn import venn2
import datetime
import math
import matplotlib as mpl
import matplotlib.pyplot as plt
import os
import pandas as pd
import time

#%% consts
MOST_NAMES_IN_ONE_COLUMN = 35
DOWNLOADS_DIR = os.path.join("Q:\\", "Users", "bdoherty", "Downloads")

#%%
in_files = os.listdir(DOWNLOADS_DIR)  # os.listdir(os.path.join(os.getcwd(), "in"))
guard = 0
while not any(["trip-data" in f for f in in_files]):
    # This is a hack because the OS doesn't always respond right away
    time.sleep(1)
    guard += 1
    print("trying to find a file to work with", guard)
    in_files = os.listdir(DOWNLOADS_DIR)
    if guard > 5:
        raise ValueError(f"haven't found a file to work with yet")

f = [f for f in in_files if "trip-data" in f][0]
to_file_path = os.path.join(os.getcwd(), "in", "trips.xlsx")
if os.path.isfile(to_file_path):
    os.remove(to_file_path)

from_file_path = os.path.join(DOWNLOADS_DIR, f)
os.rename(from_file_path, to_file_path)

#%%
guard = 0
while not os.path.exists(to_file_path):
    time.sleep(1)
    guard += 1
    if guard > 5:
        raise ValueError(f"{to_file_path} isn't showing up")

df = pd.read_excel(to_file_path, index_col=19)
df.Date = pd.to_datetime(df.Date, dayfirst=True)
df.Name = df.Name.apply(lambda x: x.title())
#%%
end = datetime.datetime.now()
start = end - datetime.timedelta(hours=24)

today = set(df[df.Date.between(start, end)].Name)
untagged = set(df[df["Project Number"].isnull()].Name)
tagged = set(df[df["Project Number"].isnull() != True].Name)

today = {x for x in today if "-" not in x}
untagged = {x for x in untagged if "-" not in x}
tagged = {x for x in tagged if "-" not in x}

# comment out this line if you're not feeling tolerent
# untagged = untagged - today


#%%
fig = plt.figure(figsize=(4, 6), dpi=200)
fig.patch.set_facecolor("white")
v = venn2([tagged, untagged], set_labels=("Tagged\nTrips", "Untagged\nTrips"))

temp_tagged = tagged - untagged
xtagged = ""
if len(temp_tagged) < MOST_NAMES_IN_ONE_COLUMN:
    xtagged = "\n".join(temp_tagged)
else:
    num_half_peeps = math.floor(len(temp_tagged) / 2)
    sorted_peeps = sorted(temp_tagged, key=len)
    pairs = zip(sorted_peeps[:num_half_peeps], reversed(sorted_peeps[num_half_peeps:]))
    name_pairs = [f"{x[0]},   {x[1]}," for x in pairs]
    xtagged = "\n".join(name_pairs)

xuntagged = "\n".join((untagged - today) - tagged)
both = "\n".join(untagged & tagged)  # & is intersection

v.get_label_by_id("10").set_text(xtagged)
v.get_patch_by_id("10").set_color("green")
v.get_patch_by_id("10").set_alpha(0.5)

v.get_label_by_id("01").set_text(xuntagged)
v.get_label_by_id("01").set_wrap(True)
v.get_patch_by_id("01").set_color("red")
v.get_patch_by_id("01").set_alpha(0.5)

try:
    v.get_label_by_id("11").set_text(both)
except AttributeError:
    print("nobody in the both category")
except Exception as e:
    print(e, v)

longest_list = max([len(tagged), len(untagged)])
if longest_list < MOST_NAMES_IN_ONE_COLUMN:
    name_font_size = 160 / longest_list
else:
    name_font_size = 160 / math.ceil(longest_list / 2)
# name_font_size = 10
print(f"font size: {name_font_size}")

for text in v.set_labels:
    try:
        text.set_color("black")
        text.set_fontsize(14)
    except AttributeError:
        print("nobody in the both category")
for text in v.subset_labels:
    try:
        text.set_fontsize(name_font_size)
        text.set_color("black")
    except AttributeError:
        print("nobody in the both category")

plt.title("Cabcharge tagging: Who's a hero?", color="black")
fig.set_size_inches(9, 5)
plt.savefig("today's venn", dpi=fig.dpi, bbox_inches="tight")

#%% for emails, copy this into the to field and outlook should just work it out.
print(
    f"Tagged trips:  ({len(tagged)} people)\n",
    "; ".join(tagged),
    "\n\n",
    f"Untagged trips:  ({len(untagged)} people)\n",
    "; ".join(untagged - tagged),
    "\n\n",
    "Both tagged and untagged trips:\n",
    "; ".join(tagged.intersection(untagged)),
    "\n\n",
    "Trips taken today:  ",
    "(there's a bit of leeway for these people!)\n",
    "; ".join(today),
)

# %%
