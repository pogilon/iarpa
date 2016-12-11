import os
import sys

# Default path for various utilities that shouldn't be changed
app_path = os.path.dirname(os.path.realpath(__file__)) + '/'
get_crop_area_path = app_path + 'lib_exec/get-crop-area'
gdal_translate_path = app_path + 'lib_exec/StereoPipeline/bin/gdal_translate'
stereo_path = app_path + 'lib_exec/StereoPipeline/bin/stereo'
bundle_adjust_path = app_path + 'lib_exec/StereoPipeline/bin/bundle_adjust'

# Temporary paths for the different process...
tmp_path = app_path + 'tmp/'
tmp_cropped_images_path = tmp_path + 'cropped_images/'
tmp_cropped_images_visible_path = tmp_path + '/cropped_images_visible/'
tmp_stereo_output_path = tmp_path + 'stereo_output/'
tmp_ba_output_path = tmp_path + 'bundle_adjust/'
tmp_pre_stereo = tmp_stereo_output_path + 'out'
tmp_disparity_debug_path = tmp_path + 'disp_debug/'
tmp_corresponding_heights_path = tmp_path + 'corresponding_heights'

# If true, intermediary files are saved to the disk
is_debug_mode = True

# Maximum disparity (for the stereo algorithm)
max_disp = 288
if(max_disp%16!=0):
    max_disp += 16-(max_disp%16)
max_disp = int(max_disp)

# If True, computes a bundle adjustment before rectifying the pair
use_bundle_adjust = False

# Parameters for the WLS algorithm
wls_lambda = 8000
wls_sigma = 0.25

# If True, removes all heights that doesn't achieve a consensus
height_map_post_process_enabled = True

# How much consensus there must be for the height to be kept
relative_consensus = 0.7

# Block size for the SGBM algorithm
block_size_disp = 15

# In order not to match edges of the rectified image, removes disparity at margin_undefined px of the edges...
margin_undefined = 24

# When computing the final height map, we merge all the height maps we obtained. For each pixel,
# we then have multiple height evaluations.
# We take the biggest set of height evaluations with a range < acceptable_height_deviation
# And final height is the average of this set.
acceptable_height_deviation = 2.0

# The following are time limits imposed to the algorithm for the contest
chain_pairwise_pc_allocated_time = 4000 # How much seconds are allocated to the pairwise 3d map computation
min_enough_pairs = 4 # How much collected pairs are considered enough
max_enough_pairs = 20 # How much pairs we will collect at the maximum
chain_pairwise_pc_allocated_time_not_enough = 5200 # If there isn't enough collected pair, how much seconds
# are allocated to the pairwise 3d map computation.
merge_pcs_allocated_time = 1700 # How much second seconds are allocated to the merge process.


# Pairs to process
pairs_filenames = [
    ['05JAN15WV031000015JAN05135727-P1BS-500497282040_01_P001_________AAE_0AAAAABPABR0.NTF', '06FEB15WV031000015FEB06141035-P1BS-500497283080_01_P001_________AAE_0AAAAABPABP0.NTF'],
    ['11FEB15WV031000015FEB11135123-P1BS-500497282030_01_P001_________AAE_0AAAAABPABR0.NTF', '05JAN15WV031000015JAN05135727-P1BS-500497282040_01_P001_________AAE_0AAAAABPABR0.NTF'],
    ['11JAN15WV031000015JAN11135414-P1BS-500497283010_01_P001_________AAE_0AAAAABPABS0.NTF', '05JAN15WV031000015JAN05135727-P1BS-500497282040_01_P001_________AAE_0AAAAABPABR0.NTF'],
    ['15NOV14WV031000014NOV15135121-P1BS-500171606160_05_P005_________AAE_0AAAAABAABC0.NTF', '05JAN15WV031000015JAN05135727-P1BS-500497282040_01_P001_________AAE_0AAAAABPABR0.NTF'],
    ['19DEC15WV031000015DEC19142039-P1BS-500514410020_01_P001_________AAE_0AAAAABPABW0.NTF', '05JAN15WV031000015JAN05135727-P1BS-500497282040_01_P001_________AAE_0AAAAABPABR0.NTF'],
    ['23JAN15WV031000015JAN23134652-P1BS-500497282020_01_P001_________AAE_0AAAAABPABQ0.NTF', '05JAN15WV031000015JAN05135727-P1BS-500497282040_01_P001_________AAE_0AAAAABPABR0.NTF'],
    ['06FEB15WV031000015FEB06141035-P1BS-500497283080_01_P001_________AAE_0AAAAABPABP0.NTF', '12FEB15WV031000015FEB12140652-P1BS-500497283100_01_P001_________AAE_0AAAAABPABQ0.NTF'],
    ['06FEB15WV031000015FEB06141035-P1BS-500497283080_01_P001_________AAE_0AAAAABPABP0.NTF', '19DEC15WV031000015DEC19142039-P1BS-500514410020_01_P001_________AAE_0AAAAABPABW0.NTF'],
    ['08MAR15WV031000015MAR08134953-P1BS-500497284060_01_P001_________AAE_0AAAAABPABQ0.NTF', '11FEB15WV031000015FEB11135123-P1BS-500497282030_01_P001_________AAE_0AAAAABPABR0.NTF'],
    ['08MAR15WV031000015MAR08134953-P1BS-500497284060_01_P001_________AAE_0AAAAABPABQ0.NTF', '11JAN15WV031000015JAN11135414-P1BS-500497283010_01_P001_________AAE_0AAAAABPABS0.NTF'],
    ['11JAN15WV031000015JAN11135414-P1BS-500497283010_01_P001_________AAE_0AAAAABPABS0.NTF', '11FEB15WV031000015FEB11135123-P1BS-500497282030_01_P001_________AAE_0AAAAABPABR0.NTF'],
    ['11FEB15WV031000015FEB11135123-P1BS-500497282030_01_P001_________AAE_0AAAAABPABR0.NTF', '23JAN15WV031000015JAN23134652-P1BS-500497282020_01_P001_________AAE_0AAAAABPABQ0.NTF'],
    ['12FEB15WV031000015FEB12140652-P1BS-500497283100_01_P001_________AAE_0AAAAABPABQ0.NTF', '11JAN15WV031000015JAN11135414-P1BS-500497283010_01_P001_________AAE_0AAAAABPABS0.NTF'],
    ['11JAN15WV031000015JAN11135414-P1BS-500497283010_01_P001_________AAE_0AAAAABPABS0.NTF', '15NOV14WV031000014NOV15135121-P1BS-500171606160_05_P005_________AAE_0AAAAABAABC0.NTF'],
    ['19DEC15WV031000015DEC19142039-P1BS-500514410020_01_P001_________AAE_0AAAAABPABW0.NTF', '11JAN15WV031000015JAN11135414-P1BS-500497283010_01_P001_________AAE_0AAAAABPABS0.NTF'],
    ['11JAN15WV031000015JAN11135414-P1BS-500497283010_01_P001_________AAE_0AAAAABPABS0.NTF', '23JAN15WV031000015JAN23134652-P1BS-500497282020_01_P001_________AAE_0AAAAABPABQ0.NTF'],
    ['19DEC15WV031000015DEC19142039-P1BS-500514410020_01_P001_________AAE_0AAAAABPABW0.NTF', '12FEB15WV031000015FEB12140652-P1BS-500497283100_01_P001_________AAE_0AAAAABPABQ0.NTF'],
    ['15NOV14WV031000014NOV15135121-P1BS-500171606160_05_P005_________AAE_0AAAAABAABC0.NTF', '23JAN15WV031000015JAN23134652-P1BS-500497282020_01_P001_________AAE_0AAAAABPABQ0.NTF'],
    ['22OCT15WV031000015OCT22140432-P1BS-500497282010_01_P001_________AAE_0AAAAABPABS0.NTF', '27SEP15WV031000015SEP27140912-P1BS-500497284100_01_P001_________AAE_0AAAAABPABQ0.NTF'],
    ['23OCT15WV031100015OCT23141928-P1BS-500497285030_01_P001_________AAE_0AAAAABPABO0.NTF', '27SEP15WV031000015SEP27140912-P1BS-500497284100_01_P001_________AAE_0AAAAABPABQ0.NTF'],
    ['18DEC15WV031000015DEC18140455-P1BS-500515572010_01_P001_________AAE_0AAAAABPABJ0.NTF', '18DEC15WV031000015DEC18140554-P1BS-500515572030_01_P001_________AAE_0AAAAABPABJ0.NTF'],
    ['15SEP15WV031000015SEP15141840-P1BS-500497285060_01_P001_________AAE_0AAAAABPABO0.NTF', '18DEC15WV031000015DEC18140554-P1BS-500515572030_01_P001_________AAE_0AAAAABPABJ0.NTF'],
    ['01SEP15WV031000015SEP01135603-P1BS-500497284040_01_P001_________AAE_0AAAAABPABP0.NTF', '18DEC15WV031000015DEC18140455-P1BS-500515572010_01_P001_________AAE_0AAAAABPABJ0.NTF'],
    ['19JUL15WV031000015JUL19135438-P1BS-500497285010_01_P001_________AAE_0AAAAABPABP0.NTF', '02APR15WV031000015APR02134802-P1BS-500276959010_02_P001_________AAE_0AAAAABPABC0.NTF'],
    ['02APR15WV031000015APR02134802-P1BS-500276959010_02_P001_________AAE_0AAAAABPABC0.NTF', '18DEC15WV031000015DEC18140455-P1BS-500515572010_01_P001_________AAE_0AAAAABPABJ0.NTF'],
    ['30JUN15WV031000015JUN30135323-P1BS-500497282080_01_P001_________AAE_0AAAAABPABP0.NTF', '02APR15WV031000015APR02134802-P1BS-500276959010_02_P001_________AAE_0AAAAABPABC0.NTF'],
    ['02APR15WV031000015APR02134804-P1BS-500497284080_01_P001_________AAE_0AAAAABPABJ0.NTF', '01SEP15WV031000015SEP01135603-P1BS-500497284040_01_P001_________AAE_0AAAAABPABP0.NTF'],
    ['22MAR15WV031000015MAR22141208-P1BS-500497285090_01_P001_________AAE_0AAAAABPABQ0.NTF', '25DEC15WV031000015DEC25141705-P1BS-500526006020_01_P001_________AAE_0AAAAABPAAW0.NTF'],
    ['06FEB15WV031000015FEB06141035-P1BS-500497283080_01_P001_________AAE_0AAAAABPABP0.NTF', '25DEC15WV031000015DEC25141705-P1BS-500526006020_01_P001_________AAE_0AAAAABPAAW0.NTF'],
    ['02APR15WV031000015APR02134718-P1BS-500497282050_01_P001_________AAE_0AAAAABPABJ0.NTF', '02APR15WV031000015APR02134802-P1BS-500276959010_02_P001_________AAE_0AAAAABPABC0.NTF'],
    ['07JAN16WV031000016JAN07142142-P1BS-500537128030_01_P001_________AAE_0AAAAABPABE0.NTF', '07JAN16WV031000016JAN07142152-P1BS-500537128010_01_P001_________AAE_0AAAAABPABA0.NTF'],
    ['07JAN16WV031000016JAN07142152-P1BS-500537128010_01_P001_________AAE_0AAAAABPABA0.NTF', '07JAN16WV031000016JAN07142202-P1BS-500537128020_01_P001_________AAE_0AAAAABPAAY0.NTF'],
    ['25DEC15WV031000015DEC25141655-P1BS-500526006010_01_P001_________AAE_0AAAAABPAAZ0.NTF', '25DEC15WV031000015DEC25141705-P1BS-500526006020_01_P001_________AAE_0AAAAABPAAW0.NTF'],
    ['18DEC15WV031000015DEC18140455-P1BS-500515572010_01_P001_________AAE_0AAAAABPABJ0.NTF', '18DEC15WV031000015DEC18140533-P1BS-500515572050_01_P001_________AAE_0AAAAABPABJ0.NTF'],
    ['18DEC15WV031000015DEC18140510-P1BS-500515572040_01_P001_________AAE_0AAAAABPABJ0.NTF', '18DEC15WV031000015DEC18140544-P1BS-500515572060_01_P001_________AAE_0AAAAABPABJ0.NTF'],
    ['18DEC15WV031000015DEC18140522-P1BS-500515572020_01_P001_________AAE_0AAAAABPABJ0.NTF', '18DEC15WV031000015DEC18140554-P1BS-500515572030_01_P001_________AAE_0AAAAABPABJ0.NTF']
]

# We inverse left and right images and add them as a new pair (usefull of not a lot of good pairs)
nb_unique_pairs = len(pairs_filenames)
for i in xrange(nb_unique_pairs):
    pairs_filenames.append([pairs_filenames[i][1], pairs_filenames[i][0]])
    
    
